"""One low-resolution framing check, then one full layer export. No asset changes."""
from pathlib import Path
import sys,json,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scene_layers import Scene,SIZE,HEIGHT,BG
from export_psd import export
DAY=Path(__file__).resolve().parent;OUT=DAY/'outputs';L=OUT/'photoshop_layers';W,H=SIZE,HEIGHT

def main():
 s=Scene(foreground_only=True)
 manifest=json.loads((L/'layer_manifest.json').read_text(encoding='utf8'))
 texts=json.loads((L/'editable_text.json').read_text(encoding='utf8'))
 assert s.width_world==945 and s.scale==661.5 and s.elev==42 and s.az==315
 assert s.validate()['all_reference_track_vertices_in_frame']
 if '--preview' in sys.argv:
  im,_=s.render('B',450,'composition');b=Image.new('RGBA',im.size,BG);b.alpha_composite(im)
  excluded={'background','terrain','trail','candidates','entrance'}
  for r in manifest['layers']:
   if r['kind'] in excluded or r['name']=='entrance_label':continue
   art=Image.open(L/r['file']).convert('RGBA').resize(im.size,Image.Resampling.LANCZOS)
   b=Image.alpha_composite(b,art)
  b.convert('RGB').save(DAY/'review/composition_tweak_low.png')
  return
 # Same existing geometry/materials; one final export, no studies or alternatives.
 for r in manifest['layers']:
  mode={'terrain':'terrain','trail':'trail','candidates':'candidates','entrance':'entrance'}.get(r['kind'])
  if mode:
   im,_=s.render('B',mode=mode)
   if mode=='terrain':
    a=np.array(im);a[:,:,:3]=np.clip(a[:,:,:3].astype(float)+np.random.default_rng(27).normal(0,.45,(H,W,1)),0,255).astype(np.uint8);im=Image.fromarray(a)
   im.save(L/r['file'])
  if r['name']=='entrance_label':
   xy=s.project(s.entry);t=next(t for t in texts if t['layer']=='entrance_label');t['x']=round(xy[0])-14;t['y']=round(xy[1])-22
   im=Image.new('RGBA',(W,H),(0,0,0,0));ImageDraw.Draw(im).text((t['x'],t['y']),t['text'],font=ImageFont.truetype('C:/Windows/Fonts/'+t['font_file'],t['font_px']),fill=t['color'],anchor=t['anchor']);im.save(L/r['file'])
 composite=Image.new('RGBA',(W,H),(0,0,0,0))
 for r in manifest['layers']:composite=Image.alpha_composite(composite,Image.open(L/r['file']).convert('RGBA'))
 composite.convert('RGB').save(OUT/'among_the_giants.png')
 composite.convert('RGB').resize((390,546),Image.Resampling.LANCZOS).save(OUT/'gallery_size_check.png')
 (L/'editable_text.json').write_text(json.dumps(texts,indent=2),encoding='utf8')
 report=s.validate();report.update(scale_locked=True,low_resolution_previews=1,full_resolution_exports=1,
  existing_art_layers_unchanged=True,no_asset_search=True,no_dem_reconstruction=True)
 (DAY/'review/composition_tweak_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 export(manifest,texts)
 with zipfile.ZipFile(OUT/'photoshop_layers.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in L.iterdir():z.write(p,'photoshop_layers/'+p.name)
 print('PNG and layered PSD exported; existing collage layers unchanged.')

if __name__=='__main__':main()
