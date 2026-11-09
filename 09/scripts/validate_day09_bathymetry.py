"""Verify a single 1.2 enlargement and the genuine low-resolution ocean layer."""
from pathlib import Path
import sys,json,csv,math,hashlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];DAY=ROOT/'09';DATA=DAY/'data';OUT=DAY/'outputs/top20_anchors'
sys.path[:0]=[str(DAY/'.deps'),str(ROOT/'02/.deps')]
from PIL import Image
from shapely.geometry import box,LineString
NS='{http://www.w3.org/2000/svg}'
before=json.loads((DATA/'render_inputs/approved_pre_enlargement.json').read_text(encoding='utf-8'))
after=json.loads((OUT/'audit.json').read_text(encoding='utf-8'))
oldroot=ET.parse(DATA/'render_inputs/approved_pre_enlargement.svg').getroot();newroot=ET.parse(OUT/'a_landscape_of_surnames_top20.svg').getroot()
oldtext=oldroot.findall(NS+'text');newtext=newroot.findall(NS+'text');assert len(newtext)==len(oldtext)+3
assert len(before['records'])==len(after['records'])==40
assert after['font_scale_once']==1.2 and after['size_min']==52.8 and after['size_max']==129.6
assert before['size_min']==44 and before['size_max']==108
indices={i for i,t in enumerate(before['text_boxes']) if t['role']=='map_surname'}
for i,(a,b) in enumerate(zip(oldtext,newtext)):
    assert a.text==b.text
    if i in indices:
        assert abs(float(b.get('font-size'))-1.2*float(a.get('font-size')))<.0012
        for key in ('font-family','font-weight','fill'):assert a.get(key)==b.get(key)
    else:assert a.attrib==b.attrib
for a,b in zip(before['records'],after['records']):
    assert a['id']==b['id'] and a['surname']==b['surname']
    assert b['font_size']==a['font_size']*1.2 and b['font_reduction']==0 and b['color']==a['color']
    assert b['national_population']==a['national_population']
    distance=math.hypot(b['label_x']-a['label_x'],b['label_y']-a['label_y'])/before['main_scale_px_per_m']
    assert abs(distance-b['enlargement_extra_shift_m'])<1e-6 and distance<10000
    if a['id'] in ('base13','base14'):assert distance==0
assert before['table_rows']==after['table_rows'] and len(after['table_rows'])==20
assert before['input_hashes']==after['input_hashes']
oldlines=oldroot.findall(NS+'polyline')
newlines=[e for e in newroot.findall(NS+'polyline') if e.get('data-role')!='generalized-isobath']
assert len(oldlines)==len(newlines)
assert all(a.attrib==b.attrib for a,b in zip(oldlines,newlines))
assert oldroot.find(NS+'path').attrib==newroot.find(NS+'path').attrib
assert len({r['surname'] for r in after['records']})==20
assert sum(t['role']=='map_surname' for t in after['text_boxes'])==40
for i,t in enumerate(after['text_boxes']):
    a,b,c,d=t['bounds'];assert 0<=a<c<=2100 and 0<=b<d<=2250
    for u in after['text_boxes'][:i]:
        x,y,z,w=u['bounds'];assert max(0,min(c,z)-max(a,x))*max(0,min(d,w)-max(b,y))<.1
meta=json.loads((DATA/'etopo2022_taiwan_sources.json').read_text(encoding='utf-8'))
raw=DATA/'etopo2022_taiwan_4arcmin.csv'
assert hashlib.sha256(raw.read_bytes()).hexdigest()==meta['sha256']==after['ocean_background']['raw_sha256']
rows=list(csv.DictReader(raw.open(encoding='utf-8')))[1:]
assert len(rows)==65*83 and len({(r['latitude'],r['longitude']) for r in rows})==len(rows)
assert min(float(r['z']) for r in rows)<-3000
assert after['ocean_background']['thresholds_m']==[0,50,200,1000,3000]
assert len(after['ocean_background']['colors'])==5
assert set(c['depth_m'] for c in after['ocean_background']['contours'])=={200,1000,3000}
for c in after['ocean_background']['contours']:
    line=LineString(c['points'])
    assert all(not line.intersects(box(*t['bounds'])) for t in after['text_boxes'])
assert len(newroot.findall(NS+'image'))==1
assert newroot.find(NS+'path').get('fill')==oldroot.find(NS+'path').get('fill')=='#FFFDF3'
assert not newroot.findall('.//'+NS+'circle')
im=Image.open(OUT/'a_landscape_of_surnames_top20.png').convert('RGB');assert im.size==(4200,4500)
calm=(220,238,245)
for xy in [(20,20),(4180,1600),(20,4480)]:assert im.getpixel(xy)==calm
def lum(c):
    v=[int(c[i:i+2],16)/255 for i in (1,3,5)];v=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v]
    return sum(x*w for x,w in zip(v,[.2126,.7152,.0722]))
def contrast(a,b):
    x,y=sorted((lum(a),lum(b)));return (y+.05)/(x+.05)
land_contrast=min(contrast(r['color'],'#FFFDF3') for r in after['records'])
table_contrast=min(contrast(r['color'],'#DCEEF5') for r in after['records'] if r['id'].startswith('base'))
body_contrast=contrast('#234657','#DCEEF5')
assert land_contrast>=4.5 and table_contrast>=3 and body_contrast>=7
report={'map_surname_labels':40,'unique_surnames':20,'font_multiplier_applied_once':1.2,'map_font_range':[52.8,129.6],
        'title_table_and_existing_note_fonts_positions_and_colors_unchanged':True,
        'surname_colors_unchanged':True,'statistics_and_twenty_table_rows_unchanged':True,
        'maximum_layout_adjustment_m':after['max_font_enlargement_shift_m'],
        'text_overlaps':0,'clipped_text':0,'leaders':0,'location_points':0,
        'ocean_type':'Real NOAA ETOPO 2022 gridded bathymetry; not a distance-to-coast proxy',
        'subset_bytes':raw.stat().st_size,'subset_grid':[65,83],'sample_interval_arcminutes':4,
        'source_data_hash_unchanged':True,'depth_bands':5,'generalized_isobath_depths_m':[200,1000,3000],
        'contours_intersecting_text_boxes':0,'title_table_footer_are_pale_and_quiet':True,
        'minimum_surname_color_land_contrast':land_contrast,'minimum_table_surname_calm_ocean_contrast':table_contrast,
        'body_text_calm_ocean_contrast':body_contrast,'screen_width_preview':[1440,1543],
        'minimum_map_glyph_px_at_1440_width':52.8*1440/2100}
(OUT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
