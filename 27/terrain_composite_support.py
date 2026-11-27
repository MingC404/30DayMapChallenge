"""Read-only DEM projection support for 2-D masks, without rendering terrain color."""
import json
from pathlib import Path
import numpy as np
import rasterio

ROOT=Path(__file__).resolve().parent


class Support:
    def __init__(self,width=630):
        self.width=width;self.height=round(width*1.4);self.s=width/1800
        self.cam=json.loads((ROOT/'camera_portrait.json').read_text())
        with rasterio.open(ROOT.parent/'18/oblique/composition_dem_30m.tif') as src:
            self.z=src.read(1).astype(float);self.tf=src.transform
        self.center=np.array(json.loads((ROOT.parent/'18/oblique/camera_c.json').read_text(encoding='utf-8-sig'))['target_xyz'])
        az,el=np.deg2rad([self.cam['azimuth_deg'],self.cam['elevation_deg']])
        self.d=np.array([np.sin(az)*np.cos(el),np.cos(az)*np.cos(el),np.sin(el)])
        self.right=np.array([-np.cos(az),np.sin(az),0]);self.up=np.cross(self.d,self.right)
        self.focus=self.right*self.cam['focus_right_m']+self.up*self.cam['focus_up_m']
        z=self.z;t=self.tf;ny,nx=z.shape
        yy,xx=np.mgrid[:ny,:nx]
        xyz=np.c_[t.c+(xx.ravel()+.5)*30,t.f-(yy.ravel()+.5)*30,z.ravel()]
        rr,cc=np.mgrid[:ny-1,:nx-1];i=(rr*nx+cc).ravel()
        faces=np.stack([np.c_[i,i+1,i+nx+1],np.c_[i,i+nx+1,i+nx]],axis=1).reshape(-1,3)
        old=np.load(ROOT.parent/'18/oblique/scene_mesh_epsg3826.npz')['vertices_epsg3826_egm2008']
        faces=faces[np.all(xyz[faces,0]<=old[:,0].max()+1e-7,axis=1)&np.all(xyz[faces,1]>=old[:,1].min()-1e-7,axis=1)]
        self.depth=np.full((self.height,width),-np.inf)
        self.xyz=np.full((self.height,width,3),np.nan)
        projected=self.project(xyz)
        # This samples only coordinate/depth support, never the existing render's
        # light, pixels, silhouette or mesh geometry. All source files stay read-only.
        for f in faces:
            tri=projected[f];lo=np.maximum(0,np.floor(tri[:,:2].min(0)).astype(int))
            hi=np.minimum([width-1,self.height-1],np.ceil(tri[:,:2].max(0)).astype(int))
            if np.any(hi<lo):continue
            a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-8:continue
            y,x=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];x=x+.5;y=y+.5
            u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
            v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den;w=1-u-v
            depth=u*a[2]+v*b[2]+w*c[2]
            olddepth=self.depth[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
            take=(u>=-1e-6)&(v>=-1e-6)&(w>=-1e-6)&(depth>olddepth)
            olddepth[take]=depth[take]
            coords=self.xyz[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
            coords[take]=(u[:,:,None]*xyz[f[0]]+v[:,:,None]*xyz[f[1]]+w[:,:,None]*xyz[f[2]])[take]
        # Local relative elevation locates concavities near each red-circle anchor.
        sm=z.copy()
        for _ in range(5):
            p=np.pad(sm,1,mode='edge');sm=sum(p[j:j+ny,k:k+nx] for j in range(3) for k in range(3))/9
        self.tpi=z-sm

    def project(self,xyz):
        q=(np.asarray(xyz)-self.center)*[1,1,self.cam['vertical_exaggeration']]-self.focus
        return np.stack([self.width/2+q@self.right*self.width/self.cam['horizontal_world_width_m'],
                         self.height/2-q@self.up*self.width/self.cam['horizontal_world_width_m'],q@self.d],axis=-1)

    def valley_anchor(self,pixel):
        x,y=np.rint(np.asarray(pixel)*self.s).astype(int)
        yy,xx=np.mgrid[max(0,y-9):min(self.height,y+10),max(0,x-9):min(self.width,x+10)]
        pts=self.xyz[yy,xx];valid=np.isfinite(pts[:,:,0])
        if not valid.any():return None
        rr=np.clip(((self.tf.f-pts[:,:,1])/30-.5).astype('int',casting='unsafe'),0,self.z.shape[0]-1)
        cc=np.clip(((pts[:,:,0]-self.tf.c)/30-.5).astype('int',casting='unsafe'),0,self.z.shape[1]-1)
        score=((xx-x)**2+(yy-y)**2)/35+self.tpi[rr,cc]*.8
        score[~valid]=np.inf
        j,i=np.unravel_index(np.argmin(score),score.shape)
        return dict(screen=[int(xx[j,i]),int(yy[j,i])],xyz=pts[j,i].tolist(),tpi=float(self.tpi[rr[j,i],cc[j,i]]))
