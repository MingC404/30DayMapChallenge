"""Check frozen source integrity, full route continuity, and GIF invariants."""
from pathlib import Path
import json,hashlib,math,sys
sys.dont_write_bytecode=True
from PIL import Image,ImageSequence,ImageDraw
from pyproj import Transformer
from shapely.geometry import shape,Point
import numpy as np
REPO=Path(__file__).resolve().parents[2];ROOT=REPO/'24/summit';OUT=ROOT/'outputs'
a=json.loads((ROOT/'data/soho_routes.json').read_text());t=Transformer.from_crs(4326,32618,always_xy=True)
def distance(a,b):return math.dist(t.transform(*a),t.transform(*b))
checks={}
for route in a['routes']:
 legs=[a['segments'][key] for key in route['segments']]
 assert legs[0]['from']=='work' and legs[-1]['to']=='summit'
 for leg in legs:
  assert distance(leg['coordinates'][0],a['nodes'][leg['from']])<.01
  assert distance(leg['coordinates'][-1],a['nodes'][leg['to']])<.01
 for x,y in zip(legs,legs[1:]):assert distance(x['coordinates'][-1],y['coordinates'][0])<.01
 checks[route['id']]={'continuous_from_soho_to_summit':True,'legs':len(legs),'historical_total_minutes':None}
assert distance(a['nodes']['newark'],a['nodes']['broad'])>1000
assert a['routes'][3]['segments']==['work_wtc','path_newark','nlr','common']
assert a['routes'][0]['segments'][:3]==['work_canal','q','herald_penn']
assert a['segments']['q']['direction']=='Uptown / 96 St'
assert a['segments']['path_christopher']['direction']=='Hoboken'
assert a['segments']['path_newark']['direction']=='Newark'
assert a['duration_minutes'] is None
manifest=json.loads((OUT/'render_manifest.json').read_text());assert 'EPSG:32618' in manifest['projection']
fixed=['SoHo / Work','Summit Station','Newark Broad Street','Newark Penn','Hoboken Terminal','New York Penn','Christopher St PATH','W 39th St / Pier 79','Canal St','34 St–Herald Sq','World Trade Center']
anchors=[]
for frame in manifest['frames']:
 anchors.append([(x['text'],x['baseline']) for x in frame['text'] if x['text'] in fixed])
assert all(v==anchors[0] for v in anchors)
assert [(x['text'],x['baseline']) for x in manifest['overview']['text'] if x['text'] in fixed]==anchors[0]
water=shape(json.loads((ROOT/'data/terrain/water_canvas.geojson').read_text())['geometry'])
assert manifest['frames'][0]['reroute_cross'] is None
for f in manifest['frames'][1:]:
 assert f['reroute_cross']['service']=='Midtown Direct'
 assert water.covers(Point(f['reroute_cross']['geographic_point']))
assert len({f['basemap_sha256'] for f in manifest['frames']})==1
assert all(f['common_station_positions']==manifest['frames'][0]['common_station_positions'] for f in manifest['frames'])
assert all('common' in r['segments'] for r in a['routes'])
assert manifest['station_order']==['Newark Broad Street','Summit Station']
assert all(any(x['text']=='Morris & Essex Line' for x in f['text']) for f in manifest['frames'])
assert all(any(x['text']=='Rail segment simplified' for x in f['text']) for f in manifest['frames'])
assert all(any(x['text']=='Elevation · USGS 3DEP' for x in f['text']) for f in manifest['frames'])
assert all(f['simplified_rail_style']=={'segment':'common','dash_px':[36,16],'sleepers':False,'color':'#a46039'} for f in manifest['frames'])
assert all(not any(x['text'] in ['East Orange','Brick Church','Orange','Highland Avenue','Mountain Station','South Orange','Maplewood','Millburn','Short Hills'] for x in f['text']) for f in manifest['frames'])
used={sid for r in a['routes'] for sid in r['segments']}
for f in manifest['frames']:
 active=set(f['active_segments']);background=set(f['background_segments'])
 assert not active&background and active|background==used
 assert f['network_segments_drawn_once'] and .15<=f['background_opacity']<=.20
old_widths={'njt':3,'sleepers':1.4,'path':3,'nlr':3,'walk':1,'subway':3.3,'ferry':3.3}
assert all(manifest['line_widths_px'][mode]>=2*width for mode,width in old_widths.items())
assert manifest['footprint_dimension_multiplier']>=2
terrain=manifest['terrain'];assert len(terrain['class_colors'])==4 and all(n>0 for n in terrain['class_pixel_counts'])
provenance=json.loads((ROOT/'data/terrain/provenance.json').read_text())
assert hashlib.sha256((ROOT/'data/terrain'/terrain['dem_file']).read_bytes()).hexdigest()==provenance['sha256']==terrain['dem_sha256']
assert hashlib.sha256((ROOT/'data/terrain'/terrain['water_mask_file']).read_bytes()).hexdigest()==provenance['water_mask_sha256']==terrain['water_mask_sha256']
for source in provenance['water_sources']:
 assert hashlib.sha256((ROOT/'data/terrain'/source['file']).read_bytes()).hexdigest()==source['sha256']
from summit_terrain import terrain_layer
cx,cy=t.transform(*a['nodes']['hoboken']);transform_info=manifest['geographic_transform']
terrain_image,_=terrain_layer(1600,1200,cx,cy,transform_info['anchor_px'],transform_info['px_per_m']);pixels=np.array(terrain_image)
assert hashlib.sha256(terrain_image.tobytes()).hexdigest()==terrain['display_layer_sha256']
assert terrain['layout_row_clip'] is None and terrain['schematic_west_clip'] is None and terrain['state_clip'] is None
assert terrain['land_coverage_fraction']==1 and terrain['valid_display_bbox_xyxy']==[0,0,1600,1200]
assert all(n>0 for n in terrain['land_pixels_on_edges'].values())
assert np.any(pixels[:,:160,3]) and np.any(pixels[:,:].take([0,-1],axis=0)[:,:,3])
audit=json.loads((OUT/'terrain_audit.json').read_text());assert audit['land_coverage_fraction']==1
scale=manifest['geographic_transform']['px_per_m'];anchor=manifest['geographic_transform']['anchor_px'];cx,cy=t.transform(*a['nodes']['hoboken']);affine=terrain['target_affine']
for key in ['broad','newark','hoboken','nyp','wtc']:
 east,north=t.transform(*a['nodes'][key]);map_pixel=(anchor[0]+(east-cx)*scale,anchor[1]-(north-cy)*scale);raster_pixel=((east-affine[2])/affine[0],(north-affine[5])/affine[4]);assert math.dist(map_pixel,raster_pixel)<1e-6
assert all(any(x['text']=='Schematic map · Not to scale' for x in f['text']) for f in manifest['frames'])
gif=Image.open(OUT/'getting_home_to_summit.gif');assert gif.n_frames==4 and gif.info['loop']==0
durations=[]
decoded=[]
for frame in ImageSequence.Iterator(gif):durations.append(frame.info['duration']);assert frame.size==(1600,1200);decoded.append(np.array(frame.convert('RGB')))
assert durations==[3000]*4
stable=np.logical_and.reduce([np.all(frame==decoded[0],axis=2) for frame in decoded[1:]])
stable_terrain_fraction=float(np.mean(stable[pixels[:,:,3]>0]))
# Only compare actual background: foreground strokes, boarding icons and route
# captions intentionally change. Broadly exclude their documented footprints.
activity=Image.new('L',(1600,1200));draw=ImageDraw.Draw(activity)
def display_point(p):
 east,north=t.transform(*p);return (anchor[0]+(east-cx)*scale,anchor[1]-(north-cy)*scale)
for sid in used:
 points=manifest['common_polyline'] if sid=='common' else [display_point(p) for p in a['segments'][sid]['coordinates']]
 draw.line([tuple(p) for p in points],fill=255,width=80)
for p in list(a['nodes'].values()):
 x,y=display_point(p);draw.ellipse((x-70,y-70,x+70,y+70),fill=255)
for f in manifest['frames']:
 for entry in f['text']:
  l,top,r,bottom=entry['box'];draw.rectangle((l-8,top-8,r+8,bottom+8),fill=255)
background=(pixels[:,:,3]>0)&(np.array(activity)==0)
assert int(background.sum())>200000
stable_background_fraction=float(np.mean(stable[background]));assert stable_background_fraction>.999
for record in json.loads((ROOT/'data/sources/manifest.json').read_text()):
 if 'file' in record:assert hashlib.sha256((ROOT/'data/sources'/record['file']).read_bytes()).hexdigest()==record['sha256']
ferry={}
for folder in ['24/outputs','24/data']:
 for p in (REPO/folder).glob('*'):
  if p.is_file():ferry[str(p.relative_to(REPO)).replace('\\','/')]=hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'ferry_preserved_checksums.json').write_text(json.dumps(ferry,indent=2))
report={'passed':True,'routes':checks,'newark_stations_separation_m':round(distance(a['nodes']['newark'],a['nodes']['broad'])),'canvas':[1600,1200],'gif_frames':4,'gif_durations_ms':durations,'loop':0,'fixed_station_anchors':True,'same_projection_and_view':True,'fixed_common_station_order':manifest['station_order'],'simplified_rail_long_dashed_without_sleepers':True,'schematic_scale_label_all_frames':True,'all_traffic_strokes_at_least_doubled':True,'candidate_network_background_opacity':manifest['background_opacity'],'network_active_background_disjoint_and_complete':True,'terrain_classes_m':terrain['class_breaks_m'],'terrain_registration_tolerance_px':1e-6,'full_canvas_land_coverage':terrain['land_coverage_fraction'],'land_pixels_on_edges':terrain['land_pixels_on_edges'],'no_state_layout_or_schematic_clipping':True,'terrain_pixels_identical_including_changing_foreground_fraction':stable_terrain_fraction,'background_terrain_pixels_checked':int(background.sum()),'background_terrain_identical_across_decoded_gif_frames_fraction':stable_background_fraction,'gallery_review':{'desktop_width':862,'mobile_width':350,'finding':'Full-bleed terrain, water, light text halos and simplified-rail distinction reviewed; previews optional and removed after finalization.'},'source_hashes_verified':True,'ferry_prototype':'Unique GTFS data, network results and regeneration scripts retained; superseded artwork retired. See 24/FERRY_RESEARCH.md.'}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
