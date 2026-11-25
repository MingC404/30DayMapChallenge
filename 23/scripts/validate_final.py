"""Validate broader regions, one neutral Fujian, labels and deterministic export."""
from pathlib import Path
import json,hashlib,subprocess,sys
import numpy as np
from PIL import Image,ImageChops
from shapely.geometry import shape,Point,LineString,box
ROOT=Path(__file__).resolve().parents[1];LAY=ROOT/'outputs/layers';OUT=ROOT/'outputs'
m=json.loads((ROOT/'review/final_metadata.json').read_text(encoding='utf8'))
audit=json.loads((ROOT/'data/tasting/final_region_audit.json').read_text(encoding='utf8'))
ff=json.loads((ROOT/'data/tasting/final_regions.geojson').read_text(encoding='utf8'))['features']
assert len(audit)==47 and len(m['placements'])==15 and len(ff)==14
assert len(m['tea_drinks'])==2
requested={'assam','darjeeling','cn-2662','cn-2663','cn-2710','tw-beauty'}
assert not requested.intersection(a['id'] for a in m['leaders'])
assert len(m['badges'])==15 and all(p['symbol']=='cup' and not p['shaded'] for p in m['tea_drinks'])
assert not {'thai-iced-tea','masala-chiya'}.intersection(id for f in ff for id in f['properties']['tea_ids'])
assert not next(r for r in audit if r['id']=='shan-tuyet')['flavor']
for r in audit:
 if r['shown']:assert r['source'] and r['coordinate_source'] and (r['flavor_source'] or r['id']=='shan-tuyet')
fujian=[f for f in ff if f['properties']['display_region']=='Fujian']
assert len(fujian)==1 and fujian[0]['properties']['tea_class']=='Mixed'
assert set(fujian[0]['properties']['tea_ids'])=={'cn-2663','cn-2710'}
assert set(fujian[0]['properties']['classes'])=={'White','Oolong'}
for f in ff:
 g=shape(f['geometry']);assert g.is_valid
 for id in f['properties']['tea_ids']:
  r=next(r for r in audit if r['id']==id);assert g.covers(Point(*r['coordinate']))
  assert r['original_origin'] and r['display_region'] and r['boundary_source']
land=np.asarray(Image.open(LAY/'land_mask.png'))>0;visibility=[]
for f in ff:
 a=Image.open(LAY/('region_'+f['properties']['id']+'.png'));alpha=np.asarray(a)[:,:,3]
 assert not (alpha[~land]>0).any()
 b=np.asarray(a.resize((862,647),Image.Resampling.LANCZOS))[:,:,3];pixels=int((b>64).sum())
 assert pixels>=20,(f['properties']['display_region'],pixels)
 visibility.append(dict(region=f['properties']['display_region'],gallery_pixels=pixels))
for i,t in enumerate(m['texts']):
 for u in m['texts'][i+1:]:assert box(*t['box']).intersection(box(*u['box'])).area==0,(t['text'],u['text'])
for a in m['badges']:
 x,y=a['center']
 for t in m['texts']:assert not box(x-5,y-8,x+5,y+8).intersects(box(*t['box'])),('leaf/text',a['id'],t['text'])
for a in m['tea_drinks']:
 x,y=a['pixel']
 for t in m['texts']:assert not box(x-13,y-9,x+15,y+12).intersects(box(*t['box'])),('cup/text',a['id'],t['text'])
for lead in m['leaders']:
 line=LineString(lead['points'])
 for t in m['texts']:assert not line.intersects(box(*t['box'])),(lead['id'],t['text'])
 for other in m['leaders']:
  if lead['id']!=other['id']:assert not line.intersects(LineString(other['points'])),(lead['id'],other['id'])
 anchor=next(a for a in m['anchors'] if a['id']==lead['id']);assert lead['points'][0]==anchor['pixel']
direct=[p for p in m['placements'] if p['direct']]
assert len(direct)==9
assert all(p['glyph_region_coverage']>=.90 for p in direct if p['id'] not in requested)
adjacency={}
for p in direct:
 if p['id'] not in requested:continue
 f=next(f for f in ff if f['properties']['display_region']==p['display_region'])
 mask=np.asarray(Image.open(LAY/('region_'+f['properties']['id']+'.png')))[:,:,3]>64
 ys,xs=np.where(mask);x1,y1,x2,y2=p['label_bbox']
 dist=float(np.sqrt((xs-np.clip(xs,x1,x2))**2+(ys-np.clip(ys,y1,y2))**2).min())
 assert dist<=100,(p['id'],dist)
 adjacency[p['id']]=dist
positions={p['id']:p['label_bbox'] for p in m['placements']}
assert positions['cn-2710'][1]<positions['cn-2663'][1]
assert positions['assam'][0]>positions['darjeeling'][2]
inside=sum(p['glyph_region_coverage']>=.999 for p in direct)
im=Image.open(LAY/'basemap.png').convert('RGBA')
for name in ['regions.png','labels.png']:im=Image.alpha_composite(im,Image.open(LAY/name))
png=OUT/'day23_a_tasting_map_of_tea.png'
entry=json.loads((ROOT/'gallery-entry.json').read_text(encoding='utf8'))
assert entry['day']=='23' and entry['title']=='A Tasting Map of Tea' and entry['author']=='Ming Cao'
assert len(entry['media'])==1 and (ROOT.parent/entry['media'][0]['source']).resolve()==png.with_suffix('.gif').resolve()
assert entry['media'][0]['path']=='assets/23/'+png.with_suffix('.gif').name and entry['media'][0]['alt']
assert any((ROOT.parent/d['source']).resolve()==png.resolve() for d in entry['downloads'])
assert entry['description'].count('.')==2
assert ImageChops.difference(im.convert('RGB'),Image.open(png)).getbbox() is None
ref=json.loads((ROOT/'data/render_reference.json').read_text())
assert hashlib.sha256(np.asarray(Image.open(LAY/'basemap.png').convert('RGBA')).tobytes()).hexdigest()==ref['confirmed_base_pixels_sha256']
record=dict(canvas=[1600,1200],reviewed=len(audit),teas=len(m['placements']),tea_drinks=len(m['tea_drinks']),display_regions=len(ff),neutral_shared_region='Fujian',no_non_land_shading=True,composite_exact=True,no_text_collisions=True,no_leader_text_or_leader_collisions=True,basemap_unchanged=True,direct_labels=len(direct),fully_contained_direct_labels=inside,requested_six_leader_free=True,direct_label_distance_from_region_px=adjacency,leaf_cup_layers_separate=True,direct_label_coverage={p['id']:p['glyph_region_coverage'] for p in direct},gallery_visibility=visibility,png_sha256=hashlib.sha256(png.read_bytes()).hexdigest())
record['gallery_entry_prepared']=True
if '--check-rebuild' in sys.argv:
 before=hashlib.sha256(png.read_bytes()).hexdigest();subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/render_final.py')],check=True);assert hashlib.sha256(png.read_bytes()).hexdigest()==before;record['deterministic_repeat_png_identical']=True
(ROOT/'review/final_validation.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
