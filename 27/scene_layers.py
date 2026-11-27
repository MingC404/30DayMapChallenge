"""Read-only D18 terrain extension, common-camera PyVista layer rendering."""
from pathlib import Path
import json,math,hashlib
import numpy as np
import rasterio
import pyvista as pv
from PIL import Image

DAY=Path(__file__).resolve().parent; SRC=DAY.parent/'18'
CAMERA=json.loads((DAY/'camera_portrait.json').read_text(encoding='utf8'))
SIZE,HEIGHT=CAMERA['canvas_px'];BG='#f0f0e8';OCHRE='#ba783f';DOT='#53685b'
PRESETS={
 'A':dict(ambient=.77,diffuse=.25,light=(-1700,300,1600),low=(198,209,198),high=(218,223,209)),
 'B':dict(ambient=.67,diffuse=.34,light=(-1300,-900,1500),low=(198,209,198),high=(218,223,209))}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class Scene:
 def __init__(self,foreground_only=False):
  self.paths=[SRC/'oblique/scene_mesh_epsg3826.npz',SRC/'oblique/composition_dem_30m.tif',SRC/'oblique/composition_dem_source.json',SRC/'oblique/camera_c.json',SRC/'research/data/official_communication_points.geojson']
  self.hashes={str(p.relative_to(DAY.parent)):sha(p) for p in self.paths}
  a=np.load(self.paths[0]);self.a=a
  old=a['vertices_epsg3826_egm2008'];oldf=a['faces']
  with rasterio.open(self.paths[1]) as ds:
   assert ds.crs.to_epsg()==3826 and ds.res==(30.,30.)
   z=ds.read(1); t=ds.transform
   assert np.isfinite(z).all() and (z>0).all()
  ny,nx=z.shape
  xx,yy=np.meshgrid(t.c+(np.arange(nx)+.5)*30,t.f-(np.arange(ny)+.5)*30)
  full=np.c_[xx.ravel(),yy.ravel(),z.ravel()]
  cc=np.rint((old[:,0]-t.c)/30-.5).astype(int)
  rr=np.rint((t.f-old[:,1])/30-.5).astype(int)
  assert np.array_equal(z[rr,cc],old[:,2])
  # Retain original vertex array and faces verbatim; append real surrounding cells.
  lookup=np.full(nx*ny,-1,dtype=np.int64);lookup[rr*nx+cc]=np.arange(len(old))
  outside=lookup<0;lookup[outside]=np.arange(len(old),len(old)+outside.sum())
  self.v=np.vstack([old,full[outside]])
  row,col=np.mgrid[:ny-1,:nx-1];i=(row*nx+col).ravel()
  tri=np.stack([np.c_[i,i+1,i+nx+1],np.c_[i,i+nx+1,i+nx]],axis=1).reshape(-1,3)
  # Extend only toward the NW foreground. Do not replace the adopted distant
  # profile with a newly enlarged background or trim any original triangle.
  near=np.all(full[tri,0]<=old[:,0].max()+1e-7,axis=1)&np.all(full[tri,1]>=old[:,1].min()-1e-7,axis=1) if foreground_only else np.ones(len(tri),dtype=bool)
  mapped=lookup[tri[near]];mapped=mapped[~np.all(mapped<len(old),axis=1)]
  self.f=np.vstack([oldf,mapped])
  self.foreground_only=foreground_only
  assert np.array_equal(self.v[:len(old)],old) and np.array_equal(self.f[:len(oldf)],oldf)
  c=json.loads(self.paths[3].read_text(encoding='utf-8-sig'));self.center=np.array(c['target_xyz'])
  self.az=CAMERA['azimuth_deg'];self.elev=CAMERA['elevation_deg'];self.width_world=CAMERA['horizontal_world_width_m'];self.scale=CAMERA['parallel_scale']
  az,el=np.deg2rad([self.az,self.elev]);self.d=np.array([math.sin(az)*math.cos(el),math.cos(az)*math.cos(el),math.sin(el)])
  self.right=np.array([-math.cos(az),math.sin(az),0]);self.up=np.cross(self.d,self.right)
  self.focus=self.right*CAMERA['focus_right_m']+self.up*CAMERA['focus_up_m']
  self.mesh=pv.PolyData(self.world(self.v),np.c_[np.full(len(self.f),3),self.f[:,::-1]].ravel())
  self.mesh=self.mesh.compute_normals(cell_normals=False,point_normals=True,split_vertices=False,consistent_normals=True)
  if self.mesh.point_data['Normals'][:,2].mean()<0:self.mesh.point_data['Normals']*=-1
  props=json.loads(self.paths[4].read_text(encoding='utf8'))['features']
  visitor=next(f['properties'] for f in props if f['properties']['name']=='遊客中心')
  xy=np.array([visitor['twd97_easting'],visitor['twd97_northing']])
  # Original triangle interpolation for landmark height.
  for f in oldf:
   q=old[f];uv=np.linalg.solve((q[1:,:2]-q[0,:2]).T,xy-q[0,:2])
   if uv.min()>=-1e-7 and uv.sum()<=1+1e-7:
    self.entry=np.r_[xy,q[0,2]+uv@(q[1:,2]-q[0,2])+2];break
  self.roots={int(n):r for n,r in zip(a['tree_numbers'],a['tree_xyz'])}

 def world(self,xyz):return (np.asarray(xyz,dtype=float)-self.center)*[1,1,1.2]
 def project(self,xyz,size=SIZE):
  q=self.world(xyz)-self.focus
  return np.stack([size/2+(q@self.right)*size/self.width_world,size*HEIGHT/SIZE/2-(q@self.up)*size/self.width_world],axis=-1)

 def render(self,preset='B',size=SIZE,mode='terrain'):
  cfg=PRESETS[preset]
  mesh=self.mesh.copy()
  zn=np.clip((self.v[:,2]-1400)/800,0,1)
  low=np.array(cfg['low']);high=np.array(cfg['high'])
  mesh['tone']=(low*(1-zn[:,None])+high*zn[:,None]).astype(np.uint8)
  p=pv.Plotter(off_screen=True,window_size=(size,round(size*HEIGHT/SIZE)),lighting='none')
  p.set_background('black');p.enable_parallel_projection()
  actor=p.add_mesh(mesh,scalars='tone',rgb=True,smooth_shading=True,
      ambient=cfg['ambient'],diffuse=cfg['diffuse'],specular=0,show_scalar_bar=False)
  p.add_light(pv.Light(position=cfg['light'],focal_point=(0,0,0),intensity=1))
  if mode not in ('terrain','diagnostic'):
   # Nonzero shader alpha avoids VTK's zero-alpha discard, keeps depth writes,
   # but rounds to zero in 8-bit PNG. Buried-geometry regression is recorded.
   actor.GetShaderProperty().AddFragmentShaderReplacement('//VTK::Light::Impl',True,
      '//VTK::Light::Impl\n gl_FragData[0] = vec4(0.0,0.0,0.0,0.00001);',False)
  if mode in ('diagnostic','boundary'):
   edge=self.mesh.extract_feature_edges(boundary_edges=True,feature_edges=False,manifold_edges=False,non_manifold_edges=False)
   edge.points[:,2]+=.3
   p.add_mesh(edge,color='#d600a6',line_width=3,lighting=False)
  if mode=='trail':
   seg=self.a['track_segments_xyz'].copy();seg[:,:,2]+=1
   line=pv.PolyData(self.world(seg).reshape(-1,3))
   line.lines=np.c_[np.full(len(seg),2),np.arange(len(seg)*2).reshape(-1,2)].ravel()
   p.add_mesh(line,color=OCHRE,line_width=5.5*size/SIZE,render_lines_as_tubes=True,lighting=False)
  if mode=='candidates':
   for root in self.roots.values():p.add_mesh(pv.Sphere(center=self.world(root+[0,0,2]),radius=2.5),color=DOT,lighting=False)
  if mode=='entrance':p.add_mesh(pv.Sphere(center=self.world(self.entry),radius=6),color='#f1e9d5',lighting=False)
  if mode=='buried_probe':
   for root in self.roots.values():p.add_mesh(pv.Sphere(center=self.world(root-[0,0,40]),radius=2),color='red',lighting=False)
  p.camera_position=[self.focus+self.d*4000,self.focus,(0,0,1)]
  p.camera.parallel_scale=self.scale;p.camera.clipping_range=(1,12000)
  raw=p.screenshot(return_img=True,transparent_background=True)
  depth=None
  if mode=='terrain':depth=p.get_image_depth(fill_value=np.nan)
  p.close()
  # VTK MSAA screenshots are black-premultiplied. Unpremultiply for straight PNG.
  alpha=raw[:,:,3].astype(float)/255
  rgb=np.divide(raw[:,:,:3],alpha[:,:,None],out=np.zeros_like(raw[:,:,:3],dtype=float),where=alpha[:,:,None]>0)
  out=np.dstack([np.clip(np.rint(rgb),0,255).astype(np.uint8),raw[:,:,3]])
  return Image.fromarray(out),depth

 def validate(self):
  assert all(sha(DAY.parent/k)==h for k,h in self.hashes.items())
  return dict(input_sha256=self.hashes,original_vertices_retained=1804,original_faces_retained=3440,
      extended_vertices=len(self.v),extended_faces=len(self.f),original_overlap_max_z_difference_m=0,
      azimuth_deg=self.az,elevation_deg=self.elev,parallel_scale=self.scale,orthographic_height_m=2*self.scale,
      focus_local_render_xyz=self.focus.tolist(),horizontal_world_width_m=self.width_world,
      canvas_px=[SIZE,HEIGHT],zoom_out_horizontal_fraction=.05,focus_up_m=225,
      terrain_extension='NW foreground only' if self.foreground_only else 'Full existing D18 extended DSM; all directions',
      candidate_projections={str(n):self.project(r).tolist() for n,r in self.roots.items()},entrance_projection=self.project(self.entry).tolist())

if __name__=='__main__':
 s=Scene();r=DAY/'review';r.mkdir(exist_ok=True)
 for name in PRESETS:
  im,_=s.render(name,600);bg=Image.new('RGBA',im.size,BG);bg.alpha_composite(im);bg.convert('RGB').save(r/('lighting_'+name+'.png'))
 (r/'scene_validation.json').write_text(json.dumps(s.validate(),indent=2),encoding='utf8')
