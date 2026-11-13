"""Symmetric streamline LIC, plus a noise-control correlation diagnostic."""
import math
import numpy as np
from scipy.ndimage import map_coordinates
from numba import njit, prange


@njit(cache=True)
def bilinear(array, x, y):
    h,w=array.shape
    if x<0 or y<0 or x>w-1.001 or y>h-1.001: return np.nan
    ix=int(x); iy=int(y); fx=x-ix; fy=y-iy
    return ((1-fx)*(1-fy)*array[iy,ix]+fx*(1-fy)*array[iy,ix+1]+(1-fx)*fy*array[iy+1,ix]+fx*fy*array[iy+1,ix+1])


@njit(cache=True, parallel=True)
def lic_convolve(noise, vx, vy, half_steps=40, step=.8):
    h,w=noise.shape
    result=np.zeros((h,w),np.float32)
    for iy in prange(h):
        for ix in range(w):
            if not np.isfinite(vx[iy,ix]):
                result[iy,ix]=.5
                continue
            total=noise[iy,ix]; weight=1.
            for sign in (-1,1):
                x=float(ix); y=float(iy)
                for k in range(1,half_steps+1):
                    a=bilinear(vx,x,y); b=bilinear(vy,x,y)
                    if not np.isfinite(a+b): break
                    mag=math.sqrt(a*a+b*b)
                    if mag<1e-8: break
                    # RK2 midpoint; normalize after interpolating projected components.
                    xm=x+sign*step*a/mag*.5; ym=y+sign*step*b/mag*.5
                    a=bilinear(vx,xm,ym); b=bilinear(vy,xm,ym)
                    if not np.isfinite(a+b): break
                    mag=math.sqrt(a*a+b*b)
                    if mag<1e-8: break
                    x+=sign*step*a/mag; y+=sign*step*b/mag
                    sample=bilinear(noise,x,y)
                    if not np.isfinite(sample): break
                    wk=.5*(1+math.cos(math.pi*k/(half_steps+1)))
                    total+=wk*sample; weight+=wk
            result[iy,ix]=total/weight
    return result


def correlations(texture, vx, vy, valid):
    # Independence control: white noise should lack LIC's preferential correlation.
    y,x=np.mgrid[0:texture.shape[0]:7,0:texture.shape[1]:7]
    xx=vx[::7,::7]; yy=vy[::7,::7]
    mag=np.maximum(np.hypot(xx,yy),1e-12)
    dx=xx/mag*8; dy=yy/mag*8
    base=texture[::7,::7]
    along=map_coordinates(texture,[y+dy,x+dx],order=1,mode='constant',cval=np.nan)
    cross=map_coordinates(texture,[y+dx,x-dy],order=1,mode='constant',cval=np.nan)
    keep=valid[::7,::7] & np.isfinite(along) & np.isfinite(cross)
    return {'along_8px':float(np.corrcoef(base[keep],along[keep])[0,1]),
            'across_8px':float(np.corrcoef(base[keep],cross[keep])[0,1])}
