"""Build local-only SVG and compact JS data with the static renderer's exact projection.
No dependency on a CDN, browser projection, web tiles, or fetch/file permissions.
"""
from pathlib import Path
import sys,json,csv,html,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path[:0]=[str(ROOT/'.deps'),str(ROOT.parent/'02/.deps'),str(ROOT/'scripts')]
import render_heritage as m
from shapely.geometry import shape,box
from shapely.ops import unary_union
from pyproj import Geod
OUT=ROOT/'interactive';OUT.mkdir(exist_ok=True)
def path(g):
    if g.is_empty:return ''
    if hasattr(g,'geoms'):return ''.join(path(p) for p in g.geoms)
    def ring(cs,close=False):
        cs=list(cs)
        return 'M'+'L'.join(f'{x:.3f},{y:.3f}' for x,y in cs)+('Z' if close else '')
    if g.geom_type=='Polygon':return ring(g.exterior.coords,True)+''.join(ring(r.coords,True) for r in g.interiors)
    if g.geom_type in ['LineString','LinearRing']:return ring(g.coords)
    return ''
def main():
    statics={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'outputs').glob('*.png')}
    layout=m.render('A',export_layout=True)
    props=list(csv.DictReader((ROOT/'data/heritage_historical.csv').open(encoding='utf-8-sig')))
    sites=list(csv.DictReader((ROOT/'data/component_sites.csv').open(encoding='utf-8-sig')))
    manifest=json.loads((ROOT/'data/manifest.json').read_text(encoding='utf-8'))
    raw=json.loads((ROOT/'data/raw/unesco.json').read_text(encoding='utf-8'))
    raw_by_id={r['id_no']:r for r in raw}
    properties={}
    for r in props:
        r=dict(r)
        for key in ['start_year','end_year','representative_year']:r[key]=int(r[key]) if r[key] else None
        r['inscription_year']=int(r['inscription_year'])
        r['country_region']=' / '.join(raw_by_id[r['unesco_id']]['states_names'])
        assert r['source_url']==f"https://whc.unesco.org/en/list/{r['unesco_id']}/"
        properties[r['unesco_id']]=r
    by_ref={r['component_ref']:r for r in sites}
    points=[]
    for ref in layout['drawn_component_refs']:
        r=by_ref[ref];x,y=m.xy(float(r['longitude']),float(r['latitude']))
        codes=properties[r['unesco_id']]['iso_codes'].split(' | ')
        local={'CN':'China','JP':'Japan','KR':'Republic of Korea','KP':"Democratic People's Republic of Korea",'VN':'Viet Nam'}
        study=[c for c in codes if c in local]
        assert len(study)==1 # Each selected transnational property has one in-scope state.
        country='Macao, China' if r['unesco_id']=='1110' else local[study[0]]
        points.append({'ref':ref,'id':r['unesco_id'],'name':r['component_name'],'country':country,'x':round(x,5),'y':round(y,5),'lon':float(r['longitude']),'lat':float(r['latitude'])})
    countries=[]
    world=json.loads((ROOT/'data/raw/ne_50m_admin_0_countries.geojson').read_text(encoding='utf-8'))
    for f in world['features']:
        g=shape(f['geometry'])
        if g.intersects(box(65,-5,160,65)):countries.append(m.screen(g))
    land=unary_union(countries);frame=box(-2400,-1800,4800,3600)
    pieces=[f'<path fill="{m.LAND}" fill-rule="evenodd" d="{path(land.intersection(frame))}"/>']
    pieces.extend(f'<path fill="none" stroke="{m.BORDER}" stroke-width=".5" d="{path(g.boundary.intersection(frame))}"/>' for g in countries)
    pieces.append(f'<path fill="none" stroke="{m.COAST}" stroke-width=".75" d="{path(land.boundary.intersection(frame))}"/>')
    # Faint geography moves; title, legend, prose, credits and timeline stay fixed.
    fixed=[];geolabels=[];scale=[]
    for r in layout['text_boxes']:
        node=f'<text x="{r["x"]}" y="{r["baseline"]}" font-size="{r["size"]}" font-family="{r["family"]}" font-weight="{r["weight"]}" fill="{r["color"]}">{html.escape(r["text"])}</text>'
        if r['text'] in ['Japanese Archipelago','East China Sea','South China Sea','Taiwan']:geolabels.append(node)
        elif r['text'].startswith('500 km'):scale.append(node)
        else:fixed.append(node)
    p=m.xy(132,28.5);end=Geod(ellps='WGS84').fwd(132,28.5,90,500000);q=m.xy(end[0],end[1])
    scale.append(f'<path d="M{p[0]},{p[1]}L{q[0]},{q[1]}" fill="none" stroke="{m.INK}" stroke-width="1.5"/>')
    # Legend symbols use the same center, radius, fill and fine pale stroke as A.
    colors={c['key']:c['color'] for c in manifest['class_breaks']};colors['Unknown']=manifest['unknown_color']
    for i,c in enumerate(manifest['class_breaks']):fixed.append(f'<circle cx="1778" cy="{1110+79+i*45+12}" r="7" fill="{c["color"]}" stroke="{m.BG}" stroke-width=".5"/>')
    fixed.append(f'<circle cx="1778" cy="1534" r="7" fill="{colors["Unknown"]}" stroke="{m.BG}" stroke-width=".5"/>')
    data={'width':m.W,'height':m.H,'radius':m.SYMBOLS['A']['radius'],'colors':colors,'properties':properties,'sites':points,
          'basemap':''.join(pieces),'fixed':''.join(fixed),'labels':''.join(geolabels),'scale':''.join(scale),
          'timeline':{'min_start':min(r['start_year'] for r in properties.values() if r['start_year'] is not None),'max_start':max(r['start_year'] for r in properties.values() if r['start_year'] is not None),'max_end':max(r['end_year'] for r in properties.values() if r['end_year'] is not None),
                      'years':[-13000,-5000,-1000,1,600,1200,1600,1800,2000],'positions':[0,.12,.23,.34,.47,.60,.74,.86,1]}}
    js='window.HERITAGE = '+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+';\n'
    (OUT/'data.js').write_text(js,encoding='utf-8')
    assert statics=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'outputs').glob('*.png')},'Static artwork changed'
    report={'reference':'Static symbol A; both existing PNGs preserved','properties':len(properties),'site_records':len(points),'official_links_checked':len(properties),'coordinates':'Same pyproj transformation as static renderer; rounded to 0.00001 layout px only','timeline':data['timeline'],'static_png_sha256':statics,'external_runtime_dependencies':[],'build':'python3.14.exe 10/scripts/build_interactive.py'}
    (OUT/'build_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
