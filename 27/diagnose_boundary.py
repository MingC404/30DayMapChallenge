"""Same-camera outer-edge tests, with all real terrain in the shared depth buffer."""
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scene_layers import Scene,BG,DAY

def main():
 report={}
 for before in (True,False):
  tag='before' if before else 'after';s=Scene(foreground_only=before)
  im,_=s.render('A',720,'diagnostic');bg=Image.new('RGBA',im.size,BG);bg.alpha_composite(im)
  d=ImageDraw.Draw(bg);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
  d.text((18,15),tag.upper()+' / MAGENTA = DATA BOUNDARY',font=font,fill='#8a006d')
  bg.convert('RGB').save(DAY/'review'/('boundary_'+tag+'.png'))
  edges,_=s.render('A',720,'boundary');visible=int(np.count_nonzero(np.array(edges)[:,:,3]))
  edges.save(DAY/'review'/('boundary_'+tag+'_isolated.png'))
  report[tag]={'visible_boundary_pixels':visible,**s.validate()}
 assert report['before']['visible_boundary_pixels']>0
 assert report['after']['visible_boundary_pixels']==0
 (DAY/'review/boundary_diagnosis.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 print({k:v['visible_boundary_pixels'] for k,v in report.items()})
if __name__=='__main__':main()
