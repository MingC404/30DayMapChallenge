"""Offline checks for final exports, land topology and publication hygiene."""
from pathlib import Path
import sys,json,hashlib,subprocess,re,csv,io
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02/.deps'))
from PIL import Image
from shapely.geometry import shape,Point,LineString
from shapely.ops import unary_union
from prepare_modern_land import water_polygon,FILES

def run():
    manifest=json.loads((ROOT/'06/outputs/render_manifest.json').read_text())
    assert manifest['registration_recomputed'] is False
    for rel,value in manifest['source_sha256'].items():
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==value,rel
    for suffix in ['png','jpg']:
        im=Image.open(ROOT/f'06/outputs/a_changing_harbor_edge.{suffix}')
        im.verify()
        assert Image.open(ROOT/f'06/outputs/a_changing_harbor_edge.{suffix}').size==(4620,3030)
    land=json.loads((ROOT/'06/assets/modern_land.geojson').read_text())
    original_features=json.loads((ROOT/'06/assets/modern_shoreline_local.geojson').read_text())['features']
    final_edges=unary_union([shape(f['geometry']) for f in json.loads((ROOT/'06/assets/modern_shoreline.geojson').read_text())['features']])
    # Vertex/midpoint distances avoid unstable tiny-buffer overlays at coincident
    # DCP/OSM island edges while checking the retained original segments.
    maximum_line_difference=0.0
    for feature in original_features:
        coordinates=feature['geometry']['coordinates']
        samples=coordinates+[((a[0]+b[0])/2,(a[1]+b[1])/2) for a,b in zip(coordinates,coordinates[1:])]
        maximum_line_difference=max(maximum_line_difference,max(Point(*p).distance(final_edges) for p in samples))
    assert maximum_line_difference<1e-9
    nj=shape(land['features'][1]['geometry']);nyc=shape(land['features'][0]['geometry'])
    water=unary_union([water_polygon(p)[0] for p in FILES])
    assert nj.is_valid and nyc.is_valid
    assert nj.intersection(water).area<1e-12
    # Known modern land/water checks use contemporary coordinates, not historical fit.
    tests=[('Jersey City inland',nj,(-74.038,40.716),True),
      ('Hudson River',nj,(-74.029,40.710),False),
      ('Upper Bay',nj,(-74.034,40.702),False),
      ('Morris Canal Basin',nj,(-74.041,40.710),False),
      ('Liberty Island',nyc,(-74.04454,40.68924),True),
      ('Governors Island',nyc,(-74.019,40.689),True)]
    for name,g,p,value in tests:assert g.covers(Point(*p))==value,name
    params=json.loads((ROOT/'06/assets/shoreline_affine_parameters.json').read_text())
    assert abs(params['metrics']['heldout_error_m']-92.4303916997106)<1e-7
    # Every tracked Day01-05 visual/data asset remains byte-identical to HEAD.
    tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
    unchanged=0
    for rel in tracked:
        p=Path(rel)
        if p.parts[0] not in ['01','02','03','04','05']:continue
        if p.suffix.lower() not in ['.png','.jpg','.gif','.svg','.html','.geojson','.osm','.xml']:continue
        current_bytes=(ROOT/p).read_bytes()
        original_bytes=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT)
        if p.suffix.lower() in ['.svg','.html','.geojson','.osm','.xml']:
            current_bytes=current_bytes.replace(b'\r\n',b'\n')
            original_bytes=original_bytes.replace(b'\r\n',b'\n')
        current=hashlib.sha256(current_bytes).digest()
        original=hashlib.sha256(original_bytes).digest()
        assert current==original,rel
        unchanged+=1
    # Only three explanatory fields change in the Day03 review JSON/CSV.
    rel='03/outputs/selection/manual_overlap_review.json'
    old=json.loads(subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT))
    new=json.loads((ROOT/rel).read_text(encoding='utf8'))
    allowed={'manual_review','evidence_and_limits','method'}
    assert len(old)==len(new)==9
    for a,b in zip(old,new):assert {k:v for k,v in a.items() if k not in allowed}=={k:v for k,v in b.items() if k not in allowed}
    # The computational/rendering prefixes of both report generators are identical.
    for rel,marker in [('03/scripts/inventory.py',"report=['# Day 03"),('03/scripts/selection_preview.py','reviews={')]:
        a=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT).decode('utf8')
        b=(ROOT/rel).read_text(encoding='utf8')
        marker_b='report=' if rel.endswith('inventory.py') else 'reviews='
        assert a[:a.index(marker)].rstrip()==b[:b.index(marker_b)].rstrip(),rel
    # Check local Markdown links in changed/new documentation only.
    scope=['README.md']+[f'{i:02}/README.md' for i in range(1,7)]+[
      '03/outputs/inventory_report.md','03/outputs/selection/selection_guide.md',
      'docs/source_language_exceptions.md','data_raw/vintage_ny_harbor/README.md']
    link_count=0
    for rel in scope:
        p=ROOT/rel;t=p.read_text(encoding='utf8')
        assert not re.search('[\u4e00-\u9fff]',t),rel
        for target in re.findall(r'\]\(([^)]+)\)',t):
            if re.match(r'^[a-zA-Z]+:',target) or target.startswith('#'):continue
            target=target.split('#')[0]
            assert (p.parent/target).exists(),(rel,target)
            link_count+=1
    all_paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
    source_exceptions=[]
    for rel in sorted(set(all_paths)):
        p=ROOT/rel
        assert not re.search('[\u4e00-\u9fff]',rel),rel
        if not p.is_file() or p.suffix not in ['.py','.md','.json','.geojson','.html','.csv','.js','.cjs','.txt','.css','.svg']:continue
        try:t=p.read_text(encoding='utf-8-sig')
        except UnicodeError:continue
        if not re.search('[\u4e00-\u9fff]',t):continue
        assert rel.startswith('data_raw/') or rel in ['02/outputs/waterfront_walks_preview.html',
          'docs/02/index.html','03/outputs/jc_city_boundary.geojson','04/data/background.json'],rel
        source_exceptions.append(rel)
    assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT).strip()
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    report=dict(final_dimensions_px=[4620,3030],input_hashes_match=True,
       registration_recomputed=False,shoreline_width_multiplier=2.5,
       land_valid=True,no_nj_fill_in_source_water=True,land_water_spot_checks=len(tests),original_shoreline_retained=True,
       original_shoreline_maximum_sample_distance_degrees=maximum_line_difference,
       unchanged_day01_05_visual_data_files=unchanged,day03_review_ids_geometry_values_unchanged=True,
       report_generator_computational_prefixes_unchanged=True,local_markdown_links_checked=link_count,
       authored_chinese_remaining=False,preserved_third_party_language_files=source_exceptions,
       git_whitespace_check_passed=True,index_untouched=True,
       display_review='Reviewed full resolution and a 1600 px wide rendering: full-bleed, five readable point labels, solid visible shores, no separate sidebar.')
    (ROOT/'06/outputs/validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':run()
