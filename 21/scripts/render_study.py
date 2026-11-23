"""Fetch cached OSM geometry and render adjustable first-pass windows."""
from pathlib import Path
import json, argparse, datetime
import requests
import xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import Polygon, LineString, box
from shapely.ops import transform, polygonize, unary_union
from shapely import make_valid
from pyproj import Transformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/'config.json').read_text())
BG='#f3efe6'; INK='#50514e'; ROAD='#b9b5ac'; TEXT='#42443f'
TX=Transformer.from_crs(4326,C['crs'],always_xy=True)
INV=Transformer.from_crs(C['crs'],4326,always_xy=True)
OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)

def fetch(c):
    p=ROOT/'data'/f"{c['slug']}_osm.json"
    if p.exists(): return json.loads(p.read_text())
    lon,lat=c['center_lonlat'] or c['seed_lonlat']; x,y=TX.transform(lon,lat)
    w,s=INV.transform(x-650,y-650); e,n=INV.transform(x+650,y+650)
    bb=f'{s},{w},{n},{e}'
    q=f'[out:json][timeout:120];(way[highway]({bb});way[building]({bb});relation[building]({bb}););out body geom;'
    for endpoint in ['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter']:
        try:
            r=requests.post(endpoint,data={'data':q},timeout=180); r.raise_for_status(); data=r.json()
            if 'remark' in data: raise RuntimeError(data['remark'])
            data['retrieved_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
            data['endpoint']=endpoint; data['query']=q
            p.write_text(json.dumps(data),encoding='utf8'); return data
        except Exception as ex: print(endpoint,str(ex),flush=True)
    endpoint='https://api.openstreetmap.org/api/0.6/map'
    r=requests.get(endpoint,params={'bbox':f'{w},{s},{e},{n}'},headers={'User-Agent':'30DayMapChallenge-Day21/1.0'},timeout=180)
    r.raise_for_status(); tree=ET.fromstring(r.content)
    (ROOT/'data'/f"{c['slug']}_osm.xml").write_bytes(r.content)
    nodes={int(el.attrib['id']):{'lon':float(el.attrib['lon']),'lat':float(el.attrib['lat'])} for el in tree.findall('node')}
    ways={}
    for el in tree.findall('way'):
        ids=[int(nd.attrib['ref']) for nd in el.findall('nd')]
        ways[int(el.attrib['id'])]={'type':'way','id':int(el.attrib['id']),'nodes':ids,'geometry':[nodes[i] for i in ids],'tags':{t.attrib['k']:t.attrib['v'] for t in el.findall('tag')}}
    els=list(ways.values())
    for el in tree.findall('relation'):
        tags={t.attrib['k']:t.attrib['v'] for t in el.findall('tag')}
        if 'building' not in tags: continue
        members=[]; complete=True
        for m in el.findall('member'):
            a=m.attrib; ref=int(a['ref'])
            if a['type']=='way':
                if ref not in ways: complete=False; break
                members.append({'type':'way','ref':ref,'role':a.get('role',''),'geometry':ways[ref]['geometry']})
        if complete: els.append({'type':'relation','id':int(el.attrib['id']),'tags':tags,'members':members})
    data={'elements':els,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'endpoint':endpoint,'url':r.url,'osm_base_timestamp':tree.attrib.get('timestamp')}
    p.write_text(json.dumps(data),encoding='utf8'); return data

def poly_parts(g):
    if g.geom_type=='Polygon': yield g
    elif hasattr(g,'geoms'):
        for p in g.geoms: yield from poly_parts(p)

def prepare(c):
    data=fetch(c); els=data['elements']; roads=[]; buildings=[]
    if c['center_lonlat']:
        center=c['center_lonlat']; method='configured override'
    else:
        sets=[]; coords={}
        for name in c['streets']:
            ids=set()
            for el in els:
                if el['type']=='way' and el.get('tags',{}).get('name')==name:
                    ids.update(el['nodes'])
                    coords.update({i:(g['lon'],g['lat']) for i,g in zip(el['nodes'],el['geometry'])})
            sets.append(ids)
        common=sets[0]&sets[1]
        if not common: raise RuntimeError(f"No shared intersection node: {c['name']}")
        center=min((coords[i] for i in common),key=lambda p:(p[0]-c['seed_lonlat'][0])**2+(p[1]-c['seed_lonlat'][1])**2)
        method='shared OSM street node'
    x,y=TX.transform(*center); half=C['window_m']/2; bounds=box(x-half,y-half,x+half,y+half)
    relation_ways={m['ref'] for el in els if el['type']=='relation' and el.get('tags',{}).get('building','no')!='no' for m in el.get('members',[]) if m['type']=='way'}
    for el in els:
        tags=el.get('tags',{}); geom=el.get('geometry',[])
        if el['type']=='way' and len(geom)>1:
            pts=[(p['lon'],p['lat']) for p in geom]
            if tags.get('highway') in {'motorway','trunk','primary','secondary','tertiary','unclassified','residential','living_street','service','pedestrian','motorway_link','trunk_link','primary_link','secondary_link','tertiary_link'} and tags.get('area')!='yes':
                roads.append(transform(TX.transform,LineString(pts)).intersection(bounds))
            if tags.get('building','no')!='no' and el['id'] not in relation_ways and pts[0]==pts[-1] and len(pts)>3:
                buildings.append(transform(TX.transform,make_valid(Polygon(pts))).intersection(bounds))
        elif el['type']=='relation' and tags.get('building','no')!='no':
            rings={}
            for role in ['outer','inner']:
                lines=[LineString([(p['lon'],p['lat']) for p in m['geometry']]) for m in el.get('members',[]) if m.get('role','outer')==role and len(m.get('geometry',[]))>1]
                rings[role]=unary_union(list(polygonize(unary_union(lines)))) if lines else Polygon()
            buildings.append(transform(TX.transform,make_valid(rings['outer'].difference(rings['inner']))).intersection(bounds))
    buildings=[p for g in buildings for p in poly_parts(g) if not p.is_empty]
    roads=[g for g in roads if not g.is_empty]
    meta={'name':c['name'],'center_lonlat':center,'center_method':method,'bounds_projected_m':list(bounds.bounds),'crs':C['crs'],'building_polygons':len(buildings),'street_segments':len(roads),'retrieved_at_utc':data['retrieved_at_utc']}
    print(json.dumps(meta),flush=True)
    return c,bounds,buildings,roads,meta

def draw(ax,d):
    c,b,buildings,roads,_=d; ax.set_facecolor(BG)
    for g in roads:
        parts=[g] if g.geom_type=='LineString' else getattr(g,'geoms',[])
        for p in parts:
            if p.geom_type=='LineString': ax.plot(*p.xy,color=ROAD,lw=.55,zorder=1,solid_capstyle='round')
    for p in buildings:
        # Orient rings so compound paths preserve courtyard holes.
        from shapely.geometry.polygon import orient
        p=orient(p,sign=1)
        vertices=[]; codes=[]
        for ring in [p.exterior,*p.interiors]:
            a=np.asarray(ring.coords); vertices.extend(a); codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(a)-2)+[MPath.CLOSEPOLY])
        ax.add_patch(PathPatch(MPath(vertices,codes),facecolor=INK,edgecolor='none',zorder=2))
    w,s,e,n=b.bounds; ax.set(xlim=(w,e),ylim=(s,n),aspect='equal'); ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values(): spine.set_color('#d5d0c5'); spine.set_linewidth(.5)

def footer(fig,left,bottom,panel_width,fig_width):
    # Scale bar length derives from the panel's physical width, at 600 m extent.
    bar=fig.add_axes([left,bottom,panel_width*100/C['window_m'],.025]); bar.set_xlim(0,100); bar.set_ylim(0,1); bar.axis('off')
    bar.plot([0,100],[.5,.5],color=INK,lw=1.4)
    for x in [0,50,100]: bar.plot([x,x],[.25,.75],color=INK,lw=.8)
    fig.text(left,bottom-.018,'0',fontsize=8,color=TEXT)
    fig.text(left+panel_width*100/C['window_m'],bottom-.018,'100 m',fontsize=8,color=TEXT,ha='center')
    fig.text(.96,bottom-.018,'© OpenStreetMap contributors',ha='right',fontsize=8,color=TEXT)

def main():
    ds=[prepare(c) for c in C['candidates']]
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':TEXT})
    fig=plt.figure(figsize=(15,6.25),facecolor=BG)
    fig.text(.04,.925,'MANHATTAN / THREE STREET FABRICS',fontsize=20,weight='medium')
    fig.text(.04,.88,'DAY 21 · OPENSTREETMAP     /     FIRST-PASS STUDY     /     600 × 600 m EACH · NORTH UP',fontsize=9,color='#77776e')
    pw=.29; ph=pw*15/6.25
    for i,d in enumerate(ds):
        left=.04+i*.315; ax=fig.add_axes([left,.15,pw,ph]); draw(ax,d)
        fig.text(left,.113,f"0{i+1}  {d[0]['name']}",fontsize=12)
        fig.text(left,.082,d[0]['intersection'],fontsize=8,color='#77776e')
    footer(fig,.04,.035,pw,15)
    fig.savefig(OUT/'day21_comparison_preview.png',dpi=200,facecolor=BG); plt.close(fig)
    for d in ds:
        fig=plt.figure(figsize=(6,7.2),facecolor=BG)
        fig.text(.075,.94,d[0]['name'].upper(),fontsize=20)
        fig.text(.075,.902,d[0]['intersection']+'  /  600 × 600 m · NORTH UP',fontsize=9)
        ax=fig.add_axes([.075,.17,.85,.85*6/7.2]); draw(ax,d)
        fig.text(.075,.12,'DAY 21 · OPENSTREETMAP / CANDIDATE PREVIEW',fontsize=8,color='#77776e')
        footer(fig,.075,.065,.85,6)
        fig.savefig(OUT/f"day21_{d[0]['slug']}_preview.png",dpi=200,facecolor=BG); plt.close(fig)
    (OUT/'study_metadata.json').write_text(json.dumps({'window_m':C['window_m'],'crs':C['crs'],'panels':[d[4] for d in ds],'style':{'background':BG,'buildings':INK,'streets':ROAD}},indent=2))

if __name__=='__main__': main()
