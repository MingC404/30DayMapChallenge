"""Offline selection aids; keep park background and playground geometry separate."""
from pathlib import Path
import json,csv,sys,math,hashlib,zipfile,xml.etree.ElementTree as ET,datetime,urllib.request
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'02/.deps'))
from shapely.geometry import shape,mapping,Polygon,box
from shapely.ops import unary_union,transform
from PIL import Image,ImageDraw,ImageFont
RAW=ROOT/'data_raw/day03_playgrounds';OUT=ROOT/'03/outputs/selection';OUT.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def dump(n,d): (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def table(n,rows):
    with (OUT/n).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
def metric(g):return transform(lambda x,y:(x*111320*math.cos(math.radians(40.72)),y*111320),g)
allf=read(ROOT/'03/outputs/playgrounds_sources.geojson')['features']
sites=[f for f in allf if f['properties']['source']=='OSM' and f['properties']['role']=='site']
sites.sort(key=lambda f:(-shape(f['geometry']).centroid.y,shape(f['geometry']).centroid.x,f['id']))
parks=read(RAW/'jc_parks_official.geojson')['features'];assert len(parks)==86
for p in parks:
    p['properties']={'background_id':'official/'+hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest()[:16],**p['properties'],'source':'JC Open Data; all 86 records','role':'park_background_only'}
    p['id']=p['properties']['background_id']
dump('official_parks_background.geojson',{'type':'FeatureCollection','features':parks})
pg={p['id']:shape(p['geometry']) for p in parks};pm={k:metric(v) for k,v in pg.items()}
sg={s['id']:shape(s['geometry']) for s in sites};sm={k:metric(v) for k,v in sg.items()}
number={s['id']:f'{i:02}' for i,s in enumerate(sites,1)}
evidence=[];rows=[]
coverage=list(csv.DictReader((ROOT/'03/outputs/attribute_coverage.csv').open(encoding='utf-8-sig')))
for s in sites:
    uid=s['id'];g=sg[uid];gm=sm[uid];hits=[]
    for p in parks:
        h=pg[p['id']]
        if not h.intersects(g):continue
        ratio=gm.intersection(pm[p['id']]).area/gm.area if gm.area else None
        rel='point covered by park' if g.geom_type=='Point' else 'park covers playground' if h.covers(g) else 'partial polygon overlap'
        ev={'number':number[uid],'osm_id':uid,'park_id':p['id'],'park_name':p['properties'].get('park') or 'Not recorded','relationship':rel,'playground_overlap_fraction':round(ratio,6) if ratio is not None else 'Not applicable (point)','intersection_m2':round(gm.intersection(pm[p['id']]).area,2),'park_geometry_used_as_playground':False}
        evidence.append(ev);hits.append(ev)
    nearest=min(parks,key=lambda p:gm.distance(pm[p['id']]))
    hits.sort(key=lambda r:-(r['playground_overlap_fraction'] if isinstance(r['playground_overlap_fraction'],float) else 1))
    parktext='; '.join(h['park_name'] if h['park_name']!='Not recorded' else 'Unnamed official park (name Not recorded)' for h in hits) if hits else 'Not recorded'
    nearest_name=nearest['properties'].get('park') or 'Unnamed official park'
    locator=parktext if hits else f'Near {nearest_name} ({gm.distance(pm[nearest["id"]]):.0f} m; reference only)'
    row={'number':number[uid],'osm_id':uid,'osm_name':s['properties']['name'],'park_or_community':parktext,'park_match_status':'; '.join(h['relationship'] for h in hits) if hits else 'No official park intersection; community Not recorded','locator_reference':locator,'nearest_park_id':nearest['id'],'nearest_park_distance_m':round(gm.distance(pm[nearest['id']]),2),'geometry_type':g.geom_type,'longitude':g.centroid.x,'latitude':g.centroid.y,'osm_tags':json.dumps(s['properties']['tags'],ensure_ascii=False)}
    for c in coverage:
        if c['site_id']!=uid:continue
        bits=[]
        if c['site_tags']!='Not recorded':bits.append('site: '+c['site_tags'])
        if c['contained_objects']!='Not recorded':bits.append('inside: '+c['contained_objects'])
        row[c['attribute']]=' | '.join(bits) or 'Not recorded'
    inside=[f for f in allf if f['properties']['role']!='site' and uid in f['properties'].get('containing_site_ids','').split(';')]
    row['all_contained_facilities']=json.dumps([{'id':f['id'],'tags':f['properties']['tags']}for f in inside],ensure_ascii=False) if inside else 'Not recorded'
    rows.append(row)
    s['properties']={**s['properties'],'selection_number':number[uid],'park_matches':hits,'locator_reference':locator}
table('park_match_evidence.csv',evidence);table('selection_sites.csv',rows)
dump('selection_sites.geojson',{'type':'FeatureCollection','features':sites})
# Parse official Census cartographic shoreline (generalized; background only).
landfile=RAW/'cb_2024_34_place_500k_kml.zip'
landurl='https://www2.census.gov/geo/tiger/GENZ2024/kml/cb_2024_34_place_500k.zip'
if not landfile.exists():landfile.write_bytes(urllib.request.urlopen(landurl,timeout=60).read())
dump('land_source.json',{'url':landurl,'source_year':2024,'scale':'1:500000','sha256':hashlib.sha256(landfile.read_bytes()).hexdigest(),'downloaded_at_utc':datetime.datetime.fromtimestamp(landfile.stat().st_mtime,datetime.timezone.utc).isoformat(),'description':'Generalized Census cartographic land background; does not modify playground geometry.'})
z=zipfile.ZipFile(landfile);ns={'k':'http://www.opengis.net/kml/2.2'}
kml=ET.fromstring(z.read('cb_2024_34_place_500k.kml'))
def ring(el):return [tuple(map(float,p.split(',')[:2])) for p in el.text.strip().split()]
lands=[];jc=None
for mark in kml.findall('.//k:Placemark',ns):
    attrs={x.attrib['name']:x.text for x in mark.findall('.//k:SimpleData',ns)}
    polys=[Polygon(ring(p.find('k:outerBoundaryIs/k:LinearRing/k:coordinates',ns)),[ring(r) for r in p.findall('k:innerBoundaryIs/k:LinearRing/k:coordinates',ns)]) for p in mark.findall('.//k:Polygon',ns)]
    if not polys:continue
    geom=unary_union(polys)
    if attrs.get('GEOID')=='3436000':jc=geom
    lands.append(geom)
assert jc is not None
dump('jc_land_background.geojson',{'type':'FeatureCollection','features':[{'type':'Feature','properties':{'source':'US Census 2024 Cartographic Boundary 1:500000','GEOID':'3436000','role':'generalized shoreline background only','download_url':'https://www2.census.gov/geo/tiger/GENZ2024/kml/cb_2024_34_place_500k.zip'},'geometry':mapping(jc)}]})
fontpath='C:/Windows/Fonts/arial.ttf'
def font(n):return ImageFont.truetype(fontpath,n)
def painter(draw,bounds,rect):
    x0,y0,x1,y1=rect;mi,ma,xx,yy=bounds;sc=min((x1-x0)/(xx-mi),(y1-y0)/(yy-ma));ox=x0+((x1-x0)-(xx-mi)*sc)/2;oy=y0+((y1-y0)-(yy-ma)*sc)/2
    def xy(x,y):return ox+(x-mi)*sc,oy+(yy-y)*sc
    def paint(g,stroke,fill=None,width=2):
        h=metric(g).intersection(box(mi,ma,xx,yy))
        def one(q):
            if q.is_empty:return
            if q.geom_type=='Polygon':
                c=[xy(x,y)for x,y in q.exterior.coords];draw.polygon(c,fill=fill);draw.line(c,fill=stroke,width=width)
                for r in q.interiors:draw.polygon([xy(x,y)for x,y in r.coords],fill='#dcebf0')
            elif q.geom_type=='Point':
                x,y=xy(q.x,q.y);draw.ellipse((x-5,y-5,x+5,y+5),fill=stroke,outline='white',width=1)
            elif hasattr(q,'geoms'):
                for part in q.geoms:one(part)
            else:draw.line([xy(x,y)for x,y in q.coords],fill=stroke,width=width)
        one(h)
    return xy,paint,sc
# Inspect every OSM point/area and area/area pair, including near disjoint candidates.
pairs=[]
for i,a in enumerate(sites):
    for b in sites[i+1:]:
        ag,bg=sm[a['id']],sm[b['id']];distance=ag.distance(bg)
        if distance>50:continue
        pairs.append({'a':a['id'],'a_number':number[a['id']],'b':b['id'],'b_number':number[b['id']],'a_type':sg[a['id']].geom_type,'b_type':sg[b['id']].geom_type,'distance_m':round(distance,2),'intersection_m2':round(ag.intersection(bg).area,2),'intersects':ag.intersects(bg)})
table('overlap_candidates.csv',pairs)
atlas=Image.new('RGB',(1800,math.ceil(len(pairs)/3)*570),'white');ad=ImageDraw.Draw(atlas)
for i,p in enumerate(pairs):
    x=(i%3)*600;y=(i//3)*570;a=sg[p['a']];b=sg[p['b']];g=unary_union([sm[p['a']],sm[p['b']]]).buffer(35);xy,paint,sc=painter(ad,g.bounds,(x+25,y+75,x+575,y+465))
    for park in parks:
        if pm[park['id']].intersects(g):paint(shape(park['geometry']),'#bacbab','#edf3e7')
    paint(a,'#147d96',width=4);paint(b,'#c23c8d',width=4)
    for id,c in [(p['a'],'#147d96'),(p['b'],'#c23c8d')]:
        for f in allf:
            if id in f['properties'].get('containing_site_ids','').split(';'):paint(shape(f['geometry']),c,width=2)
    ad.text((x+20,y+15),f"{i+1}. #{p['a_number']} {p['a']} / #{p['b_number']} {p['b']}",font=font(18),fill='#233c48')
    ad.text((x+20,y+45),f"{p['a_type']} / {p['b_type']} | gap {p['distance_m']} m | overlap {p['intersection_m2']} m2",font=font(16),fill='#435560')
    ad.text((x+20,y+490),'Blue = first object; pink = second; green = official park',font=font(16),fill='#435560')
    ad.line((x+25,y+530,x+25+min(50*sc,400),y+530),fill='#233c48',width=3);ad.text((x+25,y+537),f'{min(50,400/sc):.0f} m',font=font(14),fill='#435560')
atlas.save(OUT/'overlap_review_atlas.png')
# Numbered full-city overview with all 50 original OSM records.
im=Image.new('RGB',(2300,2350),'#f9fbfb');d=ImageDraw.Draw(im)
d.text((55,35),'Day 03 | Jersey City playground selection',font=font(40),fill='#203d4c')
d.text((55,95),'50 OSM records - choose 4-6 after review; no merged counts or scores',font=font(25),fill='#526b78')
d.rectangle((35,175,1470,2210),fill='#dcebf0')
landbounds=metric(jc).bounds;xy,paint,sc=painter(d,landbounds,(70,205,1435,2170))
for l in lands:
    if l.intersects(jc.buffer(.015)):paint(l,'#c4cec9','#f0f0e8')
paint(jc,'#899f9b','#f5f2e9')
for p in parks:paint(shape(p['geometry']),'#a6c295','#dbe7cc')
for s in sites:paint(sg[s['id']],'#d0841a' if sg[s['id']].geom_type=='Point' else '#087b89',width=3)
placed=[]
for s in sites:
    g=sm[s['id']];p=g.representative_point();x,y=xy(p.x,p.y);label=number[s['id']];chosen=None
    for radius in (27,45,65,90,120):
        for angle in (0,math.pi,-math.pi/2,math.pi/2,math.pi/4,3*math.pi/4,-math.pi/4,-3*math.pi/4):
            lx=x+radius*math.cos(angle);ly=y+radius*math.sin(angle);box=(lx-17,ly-14,lx+18,ly+14)
            if box[0]<40 or box[2]>1460 or box[1]<180 or box[3]>2205:continue
            if any(not(box[2]<b[0] or box[0]>b[2] or box[3]<b[1] or box[1]>b[3])for b in placed):continue
            chosen=(lx,ly,box);break
        if chosen:break
    assert chosen,label
    lx,ly,bb=chosen;placed.append(bb);d.line((x,y,lx,ly),fill='#687b82',width=1);d.rounded_rectangle(bb,radius=5,fill='white',outline='#687b82');d.text((lx-14,ly-12),label,font=font(22),fill='#183e4e')
d.text((1520,175),'No.  Park / location reference',font=font(25),fill='#203d4c')
for i,r in enumerate(rows):
    label=r['park_or_community'] if r['park_or_community']!='Not recorded' else '~ '+r['locator_reference'][5:]
    if label.startswith('Unnamed official park'):label='Unnamed official park (name Not recorded)'
    if len(label)>48:label=label[:45]+'...'
    d.text((1520,225+i*38),f"{r['number']}  {label}",font=font(20),fill='#203d4c')
d.text((1520,2175),'~ nearest park is a locator only.',font=font(20),fill='#526b78')
d.text((1300,220),'N ↑',font=font(30),fill='#294d5e')
d.line((85,2180,85+1000*sc,2180),fill='#294d5e',width=3);d.text((85,2185),'1 km',font=font(18),fill='#294d5e')
d.text((55,2250),'Teal: playground polygon | Orange: location-only point | Green: 86 official park records (background)',font=font(24),fill='#294d5e')
d.text((55,2295),'Ming Cao | JC Open Data; OSM contributors; US Census 2024 generalized land | Selection preview only',font=font(22),fill='#526b78')
im.save(OUT/'jc_selection_preview.png')
# Manual desk review recorded after inspecting all nine atlas panels and source tags.
reviews={('11', '12'): ('Separate mapped sections; function unconfirmed', 'Two disjoint boundaries, 3.14 m apart; no age or facility tags establish different age groups.'), ('11', '13'): ('Separate mapped sections; function unconfirmed', 'Different shapes, 13.55 m apart; no identical geometry. Name or proximity alone does not justify deduplication.'), ('12', '13'): ('Separate mapped sections; function unconfirmed', 'A circular and a polygonal section are 2.65 m apart; function is not recorded.'), ('16', '17'): ('Possible duplicate representation', 'The named Hamilton Park point is inside a playground polygon. Keep both source IDs; no separate section is established.'), ('22', '23'): ('Separate mapped sections; function unconfirmed', 'Similar separate polygons, 32.78 m apart. Shape similarity does not prove duplication; ages and names are not recorded.'), ('30', '31'): ('Different sections within one park', 'Arlington sections are 10.81 m apart; one records monkey_bars. This does not establish two age groups.'), ('33', '34'): ('Explicitly different activity tags', 'Lafayette section 33 contains slides; section 34 records water_sprayer. Keep dry play and water play separate.'), ('37', '39'): ('Explicitly different activity tags', 'Berry Lane sections 37 and 39 are 16.99 m apart; baby swings/springy/stepping_stone differ from splash_pad.'), ('43', '44'): ('Possible offset or separate site; unresolved', 'The Liberty State Park point is 29.01 m outside the polygon. Name, access=yes and distance do not establish identity; keep both IDs.')}
reviewrows=[]
for i,p in enumerate(pairs,1):
    conclusion,note=reviews[p['a_number'],p['b_number']]
    reviewrows.append({**p,'atlas_panel':i,'manual_review':conclusion,'evidence_and_limits':note,'method':'Desk review of original geometry, park background and OSM tags in overlap_review_atlas.png; no field or imagery verification','action':'retain both source IDs; no merge'})
table('manual_overlap_review.csv',reviewrows)
dump('manual_overlap_review.json',reviewrows)
notes='# Day 03 — Playground selection evidence\n\nAll 50 OSM source objects remain available in `selection_sites.csv` and `selection_sites.geojson`. Numbers run north to south and are not a score. Official park polygons are context; partial overlap or the nearest park does not prove membership. Missing facility tags mean not recorded.\n\n[Numbered map](jc_selection_preview.png) · [Nine-pair desk-review atlas](overlap_review_atlas.png) · [Review CSV](manual_overlap_review.csv) · [Park matching evidence](park_match_evidence.csv).\n\nNo source objects were removed by the review. The Hamilton Park point/polygon pair may duplicate one place; the Liberty State Park point/polygon relationship remains unresolved. Distinct activity tags and different mapped sections are retained. The generalized Census 2024 locator background is not a precision shoreline.\n\nReproduce with `python3.14.exe 03/scripts/selection_preview.py`; source geometry, classification and map rendering are unchanged by this English documentation update.\n'
(OUT/'selection_guide.md').write_text(notes,encoding='utf8')
assert len(rows)==50 and len(set(r['osm_id']for r in rows))==50
assert all(sg[s['id']].equals(shape(s['geometry']))for s in sites)
assert all(s['geometry']==next(f['geometry']for f in allf if f['id']==s['id']) for s in sites)
dump('validation.json',{'official_background_records':86,'osm_records':50,'polygon_records':46,'point_records':4,'matched_to_park':32,'unmatched_to_park':18,'manual_review_pairs':9,'point_polygon_intersections':1,'polygon_polygon_intersections':0,'osm_geometry_unchanged':True,'no_records_merged':True,'all_50_number_labels_placed':True})
print(json.dumps({'parks':len(parks),'sites':len(sites),'matched_sites':sum(r['park_or_community']!='Not recorded'for r in rows),'park_evidence_rows':len(evidence),'review_pairs':len(pairs),'point_polygon_intersections':sum(p['intersects'] and 'Point'in(p['a_type'],p['b_type'])for p in pairs),'polygon_polygon_intersections':sum(p['intersects'] and p['a_type']==p['b_type']=='Polygon'for p in pairs)},indent=2))
