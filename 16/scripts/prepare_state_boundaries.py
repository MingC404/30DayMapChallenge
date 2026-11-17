"""Derive only shared interstate borders, never polygon coastlines or clip-box edges."""
from pathlib import Path
import sys,json,zipfile,io,hashlib,itertools
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps'))
import shapefile
from shapely.geometry import shape,box,mapping
from shapely.ops import transform,unary_union
from pyproj import CRS,Transformer
import render_prototypes as atlas

DATA=ROOT/'data/gis/census_states'
ZIP=DATA/'cb_2025_us_state_500k.zip'
URL='https://www2.census.gov/geo/tiger/GENZ2025/shp/cb_2025_us_state_500k.zip'
PAGE='https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.2025.html'

def lines(g):
    if g.is_empty:return []
    if g.geom_type=='LineString':return [g]
    return [p for child in getattr(g,'geoms',[]) for p in lines(child)]

def main():
    with zipfile.ZipFile(ZIP) as z:
        stem=next(n[:-4] for n in z.namelist() if n.endswith('.shp'))
        prj=z.read(stem+'.prj').decode()
        crs=CRS.from_wkt(prj)
        reader=shapefile.Reader(shp=io.BytesIO(z.read(stem+'.shp')),shx=io.BytesIO(z.read(stem+'.shx')),dbf=io.BytesIO(z.read(stem+'.dbf')),encoding='utf-8')
        states=[]
        project=Transformer.from_crs(crs,32618,always_xy=True).transform
        clip=box(atlas.EXTENT[0],atlas.EXTENT[2],atlas.EXTENT[1],atlas.EXTENT[3])
        for sr in reader.iterShapeRecords():
            # Initial lon/lat bounding filter only; final selection uses unchanged map extent.
            if not box(*sr.shape.bbox).intersects(box(-77,38,-72,43)):continue
            g=shape(sr.shape.__geo_interface__)
            projected=transform(project,g)
            if projected.intersects(clip):states.append((sr.record.as_dict(),g,projected))
    features=[];checks=[]
    for (a,ga,pa),(b,gb,pb) in itertools.combinations(states,2):
        # Intersect ORIGINAL borders first, then project and clip the line. Do not
        # take boundary(clipped_polygon), which would manufacture map-frame edges.
        shared=ga.boundary.intersection(gb.boundary)
        line=unary_union(lines(transform(project,shared).intersection(clip)))
        if line.is_empty:continue
        assert clip.covers(line)
        props={'state_a':a['NAME'],'state_b':b['NAME'],'abbr_a':a['STUSPS'],'abbr_b':b['STUSPS'],
               'length_km':round(line.length/1000,3),'geometry_role':'shared interstate boundary; not coastline'}
        features.append({'type':'Feature','properties':props,'geometry':mapping(line)})
        checks.append(props)
    assert {'New Jersey','New York','Pennsylvania'}<=set(a['NAME'] for a,_,_ in states)
    assert features
    geo={'type':'FeatureCollection','name':'Census 2025 shared interstate borders, clipped to fixed atlas frame',
         'crs':{'type':'name','properties':{'name':'EPSG:32618'}},'features':features}
    (DATA/'state_borders_clipped_utm.geojson').write_text(json.dumps(geo),encoding='utf-8')
    meta={'source_agency':'U.S. Census Bureau','product':'2025 Cartographic Boundary, States, 1:500,000',
      'source_url':URL,'documentation_url':PAGE,'source_crs':crs.to_string(),'render_crs':'EPSG:32618',
      'source_zip_sha256':hashlib.sha256(ZIP.read_bytes()).hexdigest(),
      'source_saved_utc':datetime.fromtimestamp(ZIP.stat().st_mtime,timezone.utc).isoformat(),
      'fixed_map_extent_utm':list(atlas.EXTENT),'states_in_frame':[a['NAME'] for a,_,_ in states],
      'method':'pairwise intersection of unmodified source state polygon boundaries; project; intersect exact map box; no coastline/exterior polygon outlines; no synthetic box boundary',
      'border_pairs':checks,'all_border_geometry_within_frame':True,
      'limitations':'Small-scale generalized cartography, not legal/survey boundaries; no claim to complete offshore jurisdiction boundaries.'}
    (DATA/'provenance.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(json.dumps(meta,indent=2))

if __name__=='__main__':main()
