"""Verify final geometry, playback, fixed typography and gallery-sized motion."""
from pathlib import Path
import json,hashlib,math,xml.etree.ElementTree as ET,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
try:
 from shapely.geometry import Polygon,LineString,Point
 from shapely.ops import unary_union
except ImportError:
 sys.path.append(str(Path(__file__).resolve().parent.parent/'02/.deps'))
 from shapely.geometry import Polygon,LineString,Point
 from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent;WORK=ROOT/'.work';WORK.mkdir(exist_ok=True)
report=json.loads((ROOT/'render_report.json').read_text());route=json.loads((ROOT/'data/route.json').read_text());landings=report['landings'];scale=report['scale_px_per_m']
assert report['title']=='The Wanderer' and report['inspiration']=="Inspired by Baudelaire’s flâneur."
source=REPO/report['source'];r=ET.parse(source).getroot();ways={w.attrib['id']:[n.attrib['ref'] for n in w.findall('nd')] for w in r.findall('way')}
ll={n.attrib['id']:(float(n.attrib['lon']),float(n.attrib['lat'])) for n in r.findall('node')}
def metric(p):return ((p[0]+75.172)*85300,(p[1]-39.9495)*111100)
def poly(w):return Polygon([metric(ll[n]) for n in ways[w]])
space=unary_union([poly(w) for w in ['1552110983','1552114162']]).difference(unary_union([poly(w) for w in ['1532419267','905637615','1532425175','1532425176','1532419266','1532419262','83143746','1532425180']]))
buildings=[]
for w in r.findall('way'):
 t={n.attrib['k']:n.attrib['v'] for n in w.findall('tag')}
 if 'building' in t and len(ways[w.attrib['id']])>3:buildings.append(poly(w.attrib['id']).buffer(0))
source_edges=plaza_edges=sidewalk_edges=0
for i,(a,b,wid) in enumerate(zip(route['route_node_ids'],route['route_node_ids'][1:],route['route_way_ids'])):
 line=LineString([metric(p) for p in route['lonlat'][i:i+2]])
 if wid=='plaza_relation_21276677':assert space.buffer(.01).covers(line);plaza_edges+=1
 elif wid=='walnut_north_sidewalk_trace':assert line.intersection(unary_union(buildings)).length==0;sidewalk_edges+=1
 else:
  refs=ways[wid];assert any({a,b}=={u,v} for u,v in zip(refs,refs[1:])),(a,b,wid);source_edges+=1
assert space.covers(Point(metric(report['artist_lonlat'])))
assert hashlib.sha256(source.read_bytes()).hexdigest()==report['source_sha256']
windows=[x['s'] for x in landings if x['mode']=='windows'];assert all(b>a for a,b in zip(windows,windows[1:]))
assert all(a['side']!=b['side'] for a,b in zip(landings,landings[1:]))
choreography=[]
for stop in report['stops']:
 pp=[p for p in landings if p['caption']==stop['caption']];ds=np.diff([p['s'] for p in pp])
 assert (ds[[0,1,3]]>0).all() and ds[2]<0
 assert sum(p['frames'] for p in pp)*100==3400
 choreography.append({'caption':stop['caption'],'forward_and_back_m':(ds/scale).round(3).tolist(),'held_landings':len(pp)})
g=Image.open(ROOT/'the_wanderer.gif');assert g.size==(1080,1080)
mask=Image.new('L',g.size,0);md=ImageDraw.Draw(mask)
for rec in landings:
 x,y=np.array(rec['p'])*.6;md.ellipse((x-17,y-17,x+17,y+17),fill=255)
md.rectangle((50,201,730,229),fill=255)
fixed=np.asarray(mask)==0;reference=np.asarray(g.convert('RGB')).copy()
# Fixed crops compare five consecutive ground contacts for each mode.
starts=[4,next(i for i,p in enumerate(landings) if p['mode']=='open' and p['s']>windows[-1]),next(i for i,p in enumerate(landings) if p['mode']=='pause')]
times=np.r_[0,np.cumsum([p['frames']*100 for p in landings])]
targets={int(times[i+j]):(row,j) for row,i in enumerate(starts) for j in range(5)}
review=Image.new('RGB',(1150,835),'#f4f0e7');rd=ImageDraw.Draw(review);f=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23)
centers=[]
for row,(idx,label) in enumerate(zip(starts,['Windows / slow forward steps','Open path / fast strides','Ginkgo / held steps, then half a step back'])):
 rd.text((25,15+row*275),label,font=f,fill='#353e38');centers.append(np.mean([np.array(p['p'])*.6 for p in landings[idx:idx+5]],axis=0))
smallframes=[];durations=[];gallerypal=None;total=0;outside=0;captured=set();title_hashes=set()
for idx in range(g.n_frames):
 g.seek(idx);im=g.convert('RGB');duration=g.info.get('duration',100)
 diff=np.any(np.asarray(im)!=reference,axis=2);outside+=int(np.count_nonzero(diff&fixed))
 title_hashes.add(hashlib.sha256(im.crop((45,20,700,197)).tobytes()).hexdigest())
 for t,(row,j) in targets.items():
  if total<=t<total+duration and t not in captured:
   x,y=centers[row];crop=im.crop((round(x-125),round(y-110),round(x+125),round(y+110))).resize((215,189),Image.Resampling.LANCZOS)
   review.paste(crop,(25+j*225,55+row*275));rd.text((25+j*225,245+row*275),f'{(t-times[starts[row]])/1000:.1f} s',font=f,fill='#70786e');captured.add(t)
 small=im.resize((390,390),Image.Resampling.LANCZOS)
 if gallerypal is None:gallerypal=small.quantize(colors=256)
 smallframes.append(small.quantize(palette=gallerypal,dither=Image.Dither.NONE));durations.append(duration);total+=duration
assert total==report['duration_ms'] and outside==0 and len(title_hashes)==1
assert len(captured)==15
smallframes[0].save(WORK/'gallery_size_check.gif',save_all=True,append_images=smallframes[1:],duration=durations,loop=0,optimize=True,disposal=1)
review.save(WORK/'motion_review.png')
png=Image.open(ROOT/'the_wanderer.png');assert png.size==(1800,1800)
stride={}
for mode in ('windows','tables','shade','trees','pool','musician','open'):
 delta=[landings[i+1]['s']-p['s'] for i,p in enumerate(landings[:-1]) if p['mode']==mode and landings[i+1]['mode']==mode]
 if delta:stride[mode]={'median_screen_px_per_300ms':round(float(np.median(delta)),2),'samples':len(delta)}
fast=stride['open']['median_screen_px_per_300ms'];assert fast/stride['windows']['median_screen_px_per_300ms']>=8
assert all(fast>stride[k]['median_screen_px_per_300ms']*3 for k in stride if k!='open')
# At 390 px the median leading-foot advances are still distinct; a pause is held longer.
gallery_stride={k:round(v['median_screen_px_per_300ms']*390/1800,2) for k,v in stride.items()}
v={'title':report['title'],'inspiration':report['inspiration'],'scene':report['scene'],'png_size':png.size,'gif_size':g.size,
 'encoded_frames':g.n_frames,'duration_ms':total,'loop':g.info.get('loop',0),
 'fixed_map_pixels_changed_outside_feet_and_caption':outside,'title_and_inspiration_identical_across_frames':True,
 'mapped_footway_edges':source_edges,'verified_plaza_connectors':plaza_edges,'traced_building_free_walnut_sidewalk':sidewalk_edges,
 'pool_way_ids':report['pool_osm_way_ids'],'artist_inside_source_paved_space':True,
 'windows_progress_strictly_forward':True,'feet_alternate':True,'pause_choreography':choreography,'stride_comparison':stride,
 'gallery_390_px_advance_per_300ms':gallery_stride,'footprint_enlargement':report['footprint_enlargement'],
 'source_hash_unchanged':True,'gallery_check_sizes':[390,390],
 'file_bytes':{p.name:p.stat().st_size for p in [ROOT/'the_wanderer.png',ROOT/'the_wanderer.gif']}}
(ROOT/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(v,ensure_ascii=False,indent=2))
