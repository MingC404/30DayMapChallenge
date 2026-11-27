"""Local transparent mist and scan-derived waterfalls, aligned to the map canvas."""
import json,math
import numpy as np
from PIL import Image
from scene_layers import DAY,SIZE,HEIGHT

def mist_layers():
 yy,xx=np.mgrid[:HEIGHT,:SIZE];result=[]
 # Only the diagnosed left distant edge corner, not the ridge crest or whole rim.
 locations=[('mist_distant_edge',[(142,766,145,27,.68),(285,757,105,19,.26)]),
  ('mist_valley_mouths',[(1320,1810,135,24,.30),(1390,1804,95,17,.19),(421,1360,80,15,.17)])]
 for name,lobes in locations:
  opacity=np.zeros((HEIGHT,SIZE),float)
  for x,y,sx,sy,amp in lobes:opacity+=amp*np.exp(-.5*(((xx-x)/sx)**2+((yy-y)/sy)**2))
  opacity=np.clip(opacity*(.93+.07*np.sin(xx/47+yy/23)),0,.76)
  rgba=np.zeros((HEIGHT,SIZE,4),np.uint8);rgba[:,:,:3]=[239,242,232];rgba[:,:,3]=np.rint(opacity*255).astype(np.uint8)
  result.append((name,Image.fromarray(rgba),{'lobes':lobes,'purpose':'local illustrative mist, no terrain geometry edits'}))
 return result

def waterfall_layers():
 plans=json.loads((DAY/'assets/waterfall_placements.json').read_text());result=[]
 for p in plans:
  main=p['role']=='main';name='waterfall_main_wen' if main else 'waterfall_distant_wen'
  file='waterfall_wen_main.png' if main else 'waterfall_wen_far.png'
  im=Image.open(DAY/'assets/cutouts'/file).convert('RGBA')
  if not main:im.putalpha(im.getchannel('A').point(lambda a:round(a*.63)))
  sh=np.array([18,5] if main else [31,4],float)
  sb=np.array([113,385] if main else [22,254],float)
  th=np.array(p['head_pixel']);tb=np.array(p['base_pixel']);v=sb-sh;w=tb-th
  angle=math.atan2(w[1],w[0])-math.atan2(v[1],v[0]);scale=np.linalg.norm(w)/np.linalg.norm(v)
  mat=scale*np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
  inv=np.linalg.inv(mat);shift=th-mat@sh;offset=-inv@shift
  coeff=(inv[0,0],inv[0,1],offset[0],inv[1,0],inv[1,1],offset[1])
  layer=im.transform((SIZE,HEIGHT),Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC)
  result.append((name,layer,{**p,'asset':file,'source_head_pixel':sh.tolist(),'source_base_pixel':sb.tolist(),'matrix':mat.tolist(),'translation':shift.tolist()}))
 return result
