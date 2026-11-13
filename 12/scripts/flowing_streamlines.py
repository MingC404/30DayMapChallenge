"""Shared continuous-curve Fourier texture; extracted unchanged from the accepted local B test."""
import numpy as np
from scipy.ndimage import gaussian_filter
import wind_field as field

def curve_basis(curves,interp,rng,size,extent,wavelengths,sample_step=.45,footprint=.48):
    W,H=size
    west,south,east,north=extent
    WAVES=np.asarray(wavelengths)
    def xy(ll):
        return np.c_[(ll[:,0]-west)/(east-west)*(W-1),(north-ll[:,1])/(north-south)*(H-1)]
    accum=np.zeros((7,H,W),np.float64); count=0; direction=[]
    for _,_,ll in curves:
        if len(ll)<3: continue
        p=xy(ll)
        q=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
        inside=(p[:,0]>-4)&(p[:,0]<W+4)&(p[:,1]>-4)&(p[:,1]<H+4)
        if inside.sum()<3: continue
        keep=np.flatnonzero(inside)
        # Only original path vertices, subdivided linearly for antialiasing; never reintegrate.
        lo=max(0,keep[0]-1); hi=min(len(p),keep[-1]+2)
        qq=np.arange(q[lo],q[hi-1],sample_step)
        if len(qq)<3: continue
        px=np.interp(qq,q,p[:,0]); py=np.interp(qq,q,p[:,1])
        good=(px>=1)&(px<W-2)&(py>=1)&(py<H-2)
        px=px[good]; py=py[good]; qq=qq[good]
        if len(qq)==0: continue
        count+=1
        local=ll[lo:hi]
        az,_,_=field.GEOD.inv(local[:-1,0],local[:-1,1],local[1:,0],local[1:,1])
        uv=field.uv_at((local[:-1]+local[1:])/2,interp)
        direction.extend(np.cos(np.deg2rad(az)-np.arctan2(uv[:,0],uv[:,1])).tolist())
        phases=rng.uniform(0,2*np.pi,3)
        values=[np.ones(len(qq))]
        for j,wave in enumerate(WAVES):
            angle=2*np.pi*qq/wave+phases[j]
            values.extend([np.cos(angle),np.sin(angle)])
        ix=px.astype(int); iy=py.astype(int); fx=px-ix; fy=py-iy
        for dx,dy,weight in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:
            for j,value in enumerate(values): np.add.at(accum[j],(iy+dy,ix+dx),weight*value)
    accum=gaussian_filter(accum,(0,footprint,footprint))
    norm=np.maximum(accum[0],1e-9)
    response=accum[1:]/norm
    coverage=1-np.exp(-accum[0]*.8)
    return coverage,response,{'curves_intersecting_crop':count,'minimum_signed_tangent_dot':float(np.min(direction)),
                              'reverse_segments':int(np.count_nonzero(np.array(direction)<0))}
