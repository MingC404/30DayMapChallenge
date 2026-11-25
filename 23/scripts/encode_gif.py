"""Five fixed-layout tasting frames from the approved PNG's registered layers."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs';LAY=OUT/'layers'
CONFIG=ROOT/'data/tasting/animation_themes.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def opacity(im,factor):
 im=im.copy();im.putalpha(im.getchannel('A').point(lambda x:round(x*factor)));return im
def make_frames():
 config=json.loads(CONFIG.read_text());m=json.loads((ROOT/'review/final_metadata.json').read_text());t=m['template'];size=tuple(m['canvas'])
 rows=[r for r in json.loads((ROOT/'data/tasting/final_region_audit.json').read_text(encoding='utf8')) if r['shown']]
 regions=json.loads((ROOT/'data/tasting/final_regions.geojson').read_text(encoding='utf8'))['features']
 ids={r['id'] for r in rows};assigned=[id for g in config['themes'] for id in g['ids']]
 assert len(assigned)==len(set(assigned)) and set(assigned)|set(config['overview_only'])==ids
 assert set(assigned).isdisjoint(config['overview_only'])
 base=Image.open(LAY/'basemap.png').convert('RGBA');static=Image.open(LAY/'labels_static.png').convert('RGBA')
 items={id:Image.open(LAY/'items'/(id+'.png')).convert('RGBA') for id in ids}
 frames=[];records=[]
 for group in config['themes']+[config['overview']]:
  overview=group is config['overview'];active=ids if overview else set(group['ids']);frame=base.copy();region_states={}
  for f in regions:
   p=f['properties'];factor=1.0 if overview or group.get('keep_static_region_colors') or p['display_region'] in config['shared_neutral_regions'] or active.intersection(p['tea_ids']) else config['inactive_region_opacity']
   frame=Image.alpha_composite(frame,opacity(Image.open(LAY/('region_'+p['id']+'.png')).convert('RGBA'),factor));region_states[p['id']]=factor
  # Overview uses the exact approved merged labels; theme frames use item layers.
  if overview:frame=Image.alpha_composite(frame,Image.open(LAY/'labels.png').convert('RGBA'))
  else:
   for r in rows:frame=Image.alpha_composite(frame,opacity(items[r['id']],1 if r['id'] in active else config['inactive_label_opacity']))
   frame=Image.alpha_composite(frame,static)
  stamp=Image.new('RGBA',(size[0]*3,size[1]*3));d=ImageDraw.Draw(stamp);role=config['theme_label']['role'];font=ImageFont.truetype('C:/Windows/Fonts/'+t['fonts'][role],round(t['sizes'][role]*3));x,y=config['theme_label']['position']
  d.text((x*3,y*3),group['title'],font=font,anchor='ls',fill='#234d3c');frame=Image.alpha_composite(frame,stamp.resize(size,Image.Resampling.LANCZOS)).convert('RGB')
  frames.append(frame);records.append(dict(title=group['title'],duration_ms=group['duration_ms'],active_ids=sorted(active),region_opacities=region_states))
 return frames,records,config
def main():
 frames,records,config=make_frames();w,h=frames[0].size
 # One global palette, no dithering: unchanged pixels cannot shimmer on frame changes.
 strip=Image.new('RGB',(w,h*len(frames)))
 for i,frame in enumerate(frames):strip.paste(frame,(0,i*h))
 palette=strip.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
 quantized=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
 path=OUT/'day23_a_tasting_map_of_tea.gif'
 quantized[0].save(path,save_all=True,append_images=quantized[1:],duration=[r['duration_ms'] for r in records],loop=0,optimize=False,disposal=1)
 record=dict(canvas=[w,h],frames=records,total_duration_ms=sum(r['duration_ms'] for r in records),loop=0,theme_position=config['theme_label'],global_palette=True,dither=False,static_png_sha256=sha(OUT/'day23_a_tasting_map_of_tea.png'),gif_sha256=sha(path),config_sha256=sha(CONFIG),inactive_label_opacity=config['inactive_label_opacity'],inactive_region_opacity=config['inactive_region_opacity'],overview_only=config['overview_only'])
 (ROOT/'review/animation_metadata.json').write_text(json.dumps(record,indent=2),encoding='utf8')
 if '--review' in sys.argv:
  for width in [862,350]:
   preview=Image.new('RGB',(width*2,round(h*width/w)*3),'#f3eedf')
   for i,f in enumerate(quantized):preview.paste(f.convert('RGB').resize((width,round(h*width/w)),Image.Resampling.LANCZOS),((i%2)*width,(i//2)*round(h*width/w)))
   preview.save(ROOT/f'review/animation_{width}.png')
 print(path)
if __name__=='__main__':main()
