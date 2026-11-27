"""Rebuild the required no-collage low-resolution view and wireframe diagnostic."""
import json
import numpy as np
from PIL import Image,ImageDraw
from scene_layers import Scene,DAY,BG

def main():
 s=Scene();report=s.validate()
 for mode in ['terrain','wireframe','boundary','trail']:
  im,_=s.render('B',720,mode)
  if mode=='terrain':
   report['sky_fraction']=float(np.mean(np.array(im)[:,:,3]==0));b=Image.new('RGBA',im.size,BG);b.alpha_composite(im);b.save(DAY/'review/sky_composition_no_collage.png')
  elif mode=='wireframe':
   b=Image.new('RGBA',im.size,BG);b.alpha_composite(im);ImageDraw.Draw(b).text((15,15),'WIREFRAME + MAGENTA DATA EDGE / SAME CAMERA',fill='#6c245e');b.save(DAY/'review/sky_wireframe.png')
  elif mode=='boundary':
   a=np.array(im)[:,:,3];y,x=np.where(a>0);report.update(boundary_pixels=int(np.count_nonzero(a)),boundary_bbox_px=[int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None);im.save(DAY/'review/sky_boundary_isolated.png')
  else:
   b=Image.open(DAY/'review/sky_composition_no_collage.png').convert('RGBA');b.alpha_composite(im);b.save(DAY/'review/sky_composition_with_track.png')
 (DAY/'review/sky_composition_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
if __name__=='__main__':main()
