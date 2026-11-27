"""Portrait pale-ink edition; deliverable layers share canvas and origin."""
from pathlib import Path
import json,time,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scene_layers import Scene,SIZE,HEIGHT,BG,OCHRE,DOT,PRESETS
DAY=Path(__file__).resolve().parent;OUT=DAY/'outputs';L=OUT/'photoshop_layers';REVIEW=DAY/'review'
W,H=SIZE,HEIGHT;INK='#35473c';MUTED='#59675a';SELECTED='A'
def blank():return Image.new('RGBA',(W,H),(0,0,0,0))
def font(n,file):return ImageFont.truetype('C:/Windows/Fonts/'+file,n)

def main():
 started=time.perf_counter();OUT.mkdir(exist_ok=True);L.mkdir(exist_ok=True);REVIEW.mkdir(exist_ok=True)
 scene=Scene();layers=[];texts=[];placements=[]
 previous=json.loads((L/'layer_manifest.json').read_text())['layers'] if (L/'layer_manifest.json').exists() else []
 def put(name,im,kind,**details):
  assert im.size==(W,H) and im.mode=='RGBA'
  filename=f'{len(layers):02d}_{name}.png';im.save(L/filename)
  layers.append(dict(file=filename,name=name,kind=kind,origin=[0,0],size=[W,H],**details))
 def textlayer(name,items):
  im=blank();d=ImageDraw.Draw(im)
  for x,y,s,n,c,f,anchor in items:
   d.text((x,y),s,font=font(n,f),fill=c,anchor=anchor)
   texts.append(dict(layer=name,text=s,x=x,y=y,font_px=n,color=c,font_file=f,
    photoshop_font='Georgia' if f=='georgia.ttf' else 'SegoeUI',anchor=anchor))
  put(name,im,'text_raster_with_live_text_recipe')
 for preset in PRESETS:
  im,_=scene.render(preset,600);bg=Image.new('RGBA',im.size,BG);bg.alpha_composite(im)
  bg.convert('RGB').save(REVIEW/('lighting_'+preset+'.png'))
 put('sky_background',Image.new('RGBA',(W,H),BG),'background')
 terrain,_=scene.render(SELECTED);ta=np.array(terrain);rng=np.random.default_rng(27)
 ta[:,:,:3]=np.clip(ta[:,:,:3].astype(float)+rng.normal(0,.45,(H,W,1)),0,255).astype(np.uint8)
 put('terrain_pale_ink',Image.fromarray(ta),'terrain',lighting=SELECTED)
 assert np.all(ta[-1,:,3]==255),'Foreground must naturally cover the bottom edge.'
 boundary,_=scene.render(SELECTED,mode='boundary')
 visible_boundary=int(np.count_nonzero(np.array(boundary)[:,:,3]));assert visible_boundary==0
 boundary.save(REVIEW/'boundary_after_full_resolution_isolated.png')
 for mode,name in [('trail','reference_gps_track'),('candidates','candidate_locations'),('entrance','entrance_marker')]:
  im,_=scene.render(SELECTED,mode=mode);put(name,im,mode)
 probe,_=scene.render(SELECTED,600,'buried_probe');buried=int(np.count_nonzero(np.array(probe)[:,:,3]))
 assert buried==0,'Buried symbols leak through terrain.'
 def collage(name,asset,width,opacity=1,pos=None,anchor=None,foot=None,offset=(0,0)):
  cut=Image.open(DAY/'assets/cutouts'/asset).convert('RGBA')
  cut=cut.resize((width,round(cut.height*width/cut.width)),Image.Resampling.LANCZOS)
  if opacity!=1:cut.putalpha(cut.getchannel('A').point(lambda a:round(a*opacity)))
  if anchor is not None:
   p=scene.project(scene.roots[anchor]);foot=np.array(foot)
   pos=np.rint(p+offset-foot*np.array(cut.size)).astype(int).tolist()
  im=blank();im.alpha_composite(cut,tuple(pos));put(name,im,'painting_collage',asset=asset)
  rec=dict(layer=name,asset=asset,pixel_top_left=pos,size=list(cut.size),opacity=opacity,
   candidate_vicinity=anchor,artistic_offset_px=list(offset),foot_fraction=foot.tolist() if isinstance(foot,np.ndarray) else foot)
  if anchor is not None:rec.update(candidate_projected_px=p.tolist(),artistic_foot_px=(np.array(pos)+foot*np.array(cut.size)).tolist())
  placements.append(rec)
 collage('grove_dong_yuan_distant','dong_yuan_grove.png',330,.70,pos=[1280,1120])
 collage('new_dense_grove_wang_meng','new_wang_dense_grove.png',370,.64,pos=[1100,780])
 collage('new_single_pine_zhao_mengfu','new_zhao_single_pine.png',185,.90,anchor=16,foot=(.35,.97),offset=(16,-8))
 collage('new_sparse_grove_ni_zan','new_ni_sparse_grove.png',300,.83,pos=[120,1940])
 collage('main_tree_guo_xi','guo_xi_main_tree.png',310,1,anchor=1,foot=(.76,.93),offset=(28,-8))
 textlayer('day_kicker',[(94,90,'DAY 27 / NEW TOOL',20,MUTED,'segoeui.ttf','ls')])
 textlayer('title',[(94,174,'Among the Giants',64,INK,'georgia.ttf','ls')])
 textlayer('subtitle',[(94,222,'The giant-tree trail at Lalashan, Taiwan',27,INK,'segoeui.ttf','ls')])
 symbols=blank();d=ImageDraw.Draw(symbols);d.line((96,287,142,287),fill=OCHRE,width=6);d.ellipse((486,281,498,293),fill=DOT)
 put('legend_symbols',symbols,'legend_symbols')
 textlayer('legend_text',[(158,295,'Reference GPS track',22,INK,'segoeui.ttf','ls'),(518,295,'Candidate tree locations',22,INK,'segoeui.ttf','ls')])
 entry=scene.project(scene.entry)
 textlayer('entrance_label',[(round(entry[0])-14,round(entry[1])-22,'Entrance / Visitor center',23,INK,'segoeui.ttf','rs')])
 textlayer('collage_caption',[(94,H-170,'Tree collage from classical ink paintings',23,INK,'segoeui.ttf','ls')])
 textlayer('position_note',[(94,H-135,'Candidate locations unverified · tree forms are artistic · not for navigation',20,MUTED,'segoeui.ttf','ls')])
 textlayer('terrain_source',[(94,H-85,'Copernicus GLO-30 DSM (nominal 30 m) · EPSG:3826 / EGM2008 · © OpenStreetMap contributors',18,MUTED,'segoeui.ttf','ls')])
 textlayer('art_source',[(94,H-54,'Art: Guo Xi, Zhao Mengfu, Ni Zan, Wang Meng / The Met, CC0 · Dong Yuan / Commons, public domain',16,MUTED,'segoeui.ttf','ls')])
 textlayer('signature',[(W-94,H-54,'Ming Cao',23,INK,'segoeui.ttf','rs')])
 composite=blank()
 for r in layers:composite=Image.alpha_composite(composite,Image.open(L/r['file']).convert('RGBA'))
 preview=composite.convert('RGB');preview.save(OUT/'among_the_giants.png')
 preview.resize((390,546),Image.Resampling.LANCZOS).save(OUT/'gallery_size_check.png')
 for preset in PRESETS:
  base=Image.open(REVIEW/('lighting_'+preset+'.png')).convert('RGBA').resize((W,H),Image.Resampling.LANCZOS)
  for r in layers[2:]:base=Image.alpha_composite(base,Image.open(L/r['file']).convert('RGBA'))
  base.resize((450,630),Image.Resampling.LANCZOS).convert('RGB').save(REVIEW/('lighting_'+preset+'_with_collage.png'))
 manifest=dict(canvas=[W,H],origin=[0,0],color_mode='RGBA 8-bit',blend='Normal',order='bottom_to_top',layers=layers,
  text_layers='PSD contains raster labels for exact preview; optional JSX creates editable Photoshop type.',placements=placements)
 (L/'layer_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
 (L/'editable_text.json').write_text(json.dumps(texts,indent=2),encoding='utf8')
 report=scene.validate();report.update(lighting_selected=SELECTED,lighting_reason='Paler valleys and quieter relief behind ink lines',
  bottom_edge_terrain_coverage=1.0,buried_probe_visible_pixels=buried,layer_count=len(layers),layer_composite_exact=True,
  visible_mesh_boundary_pixels_full_resolution=visible_boundary,
  collage_placements=placements,elapsed_render_seconds=round(time.perf_counter()-started,2))
 (OUT/'render_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 verify=blank()
 for r in layers:verify=Image.alpha_composite(verify,Image.open(L/r['file']).convert('RGBA'))
 diff=np.abs(np.array(verify.convert('RGB'),dtype=int)-np.array(Image.open(OUT/'among_the_giants.png'),dtype=int));assert diff.max()==0
 from export_psd import export
 export(manifest,texts)
 current={r['file'] for r in layers}
 for r in previous:
  if r['file'] not in current:
   stale=(L/r['file']).resolve();assert stale.parent==L.resolve()
   if stale.exists():stale.unlink()
 with zipfile.ZipFile(OUT/'photoshop_layers.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in L.iterdir():z.write(p,'photoshop_layers/'+p.name)
 print(json.dumps(dict(canvas=[W,H],layers=len(layers),png_composite_max_error=int(diff.max()),seconds=round(time.perf_counter()-started,2))))

if __name__=='__main__':main()
