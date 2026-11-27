"""Choose artistic waterfall placements by displayed slope, never infer real falls."""
import json
from pathlib import Path
import numpy as np
from scene_layers import Scene,DAY

def main():
 s=Scene();z=s.grid_z;t=s.grid_transform
 gy,gx=np.gradient(z,30,30)
 track=s.project(s.a['track_segments_xyz'].reshape(-1,3))[::5]
 def course(xy):
  points=[];xy=np.array(xy,dtype=float)
  for i in range(32):
   points.append([*xy,float(s.ground(xy))])
   c=int(np.clip((xy[0]-t.c)/30,0,z.shape[1]-1));r=int(np.clip((t.f-xy[1])/30,0,z.shape[0]-1))
   d=np.array([-gx[r,c],gy[r,c]]);length=np.linalg.norm(d)
   if length<.06:break
   xy+=d/length*6
  return np.array(points)
 result=[]
 for role,target in [('main',(1400,1580)),('far',(430,1250))]:
  best=None
  for v in s.v[::3]:
   head=s.project(v)
   if np.linalg.norm(head-target)>330:continue
   a=course(v[:2]);p=s.project(a);delta=p[-1]-p[0]
   if len(a)<15 or a[0,2]-a[-1,2]<15 or delta[1]<70 or abs(delta[0])>delta[1]*.65:continue
   dist=np.sqrt(np.min(np.sum((p[::3,None,:]-track[None,:,:])**2,axis=2)))
   if dist<65:continue
   if p[:,0].min()<100 or p[:,0].max()>1690 or p[:,1].min()<950 or p[:,1].max()>2180:continue
   score=np.linalg.norm(head-target)+abs(np.linalg.norm(delta)-(200 if role=='main' else 110))*.5
   if best is None or score<best[0]:best=(score,a,p,dist)
  assert best is not None
  _,a,p,dist=best
  if role=='far':a=a[:18];p=p[:18]
  result.append(dict(role=role,verified_real_location=False,status='Artistic illustrative placement, not a mapped waterfall',
   head_xyz=a[0].tolist(),base_xyz=a[-1].tolist(),head_pixel=p[0].tolist(),base_pixel=p[-1].tolist(),
   dsm_drop_m=float(a[0,2]-a[-1,2]),source_course_pixels=p.tolist(),min_distance_to_reference_track_px=float(dist)))
 (DAY/'assets/waterfall_placements.json').write_text(json.dumps(result,indent=2),encoding='utf8')
 print([(r['role'],r['head_pixel'],r['base_pixel'],r['dsm_drop_m']) for r in result])
if __name__=='__main__':main()
