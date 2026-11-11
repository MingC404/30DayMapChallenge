"""Offline property/component preparation and human-reviewed historical dating.

No date extraction heuristics, midpoint calculation, or inscription-year fallback.
Edit data/historical_evidence.tsv to review a historical assignment.
"""
from pathlib import Path
import csv,json,hashlib,sys,math,collections
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'.deps'),str(ROOT.parent/'02/.deps')]
from shapely.geometry import shape,Point
RAW=ROOT/'data/raw';DATA=ROOT/'data'
UNITS={'CN':'CHN','JP':'JPN','KR':'KOR','KP':'PRK','VN':'VNM'}
UNKNOWN={
 '449':('Middle Pleistocene and later; official ages are in years ago','700,000–200,000 years ago and later occupation are documented; no comparable calendar-year onset assigned in this pass.'),
 '704':('Temple founded 478 BCE; repeatedly rebuilt with later mansion and cemetery','The temple foundation does not date the principal surviving three-part ensemble; a comparable ensemble phase remains unreviewed.'),
 '707':('7th-century foundations and later palatial ensembles','Separate Jokhang, Potala and Norbulingka histories; no uniform principal formation interval reviewed.'),
 '734':('Villages existed by the 11th century; standing-house dates unreviewed','Settlement origin does not date the principal surviving gassho-house ensemble.'),
 '778':('Temples, academy and later resort buildings from different eras','No dominant landscape formation phase established from the retained multi-period history.'),
 '1001':('Irrigation c. 256 BCE; Taoist foundation 142 CE and later temples','Two distinct component traditions; choosing the irrigation origin for all temples would mislead.'),
 '1091':('Later Koguryo-period tombs; precise site-specific range unreviewed','A kingdom lifespan in the summary is not sufficient evidence for the tomb construction interval.'),
 '1111':('Terraces developed over approximately 1300 years','Relative duration is not a securely anchored construction interval; no subtraction from inscription or download year.'),
 '1113':('13th–20th centuries in OUV; 15th–20th in short description','Official fields disagree about the initial century; leave classification Unknown pending dossier review.'),
 '1142':('9th-century shrines, later pilgrimage networks and living practice','Source dates different aspects but no common principal formation interval has been reviewed.'),
 '1279':('Temple-building tradition from 1st to early 20th century','Very broad tradition does not establish the dominant formation phase of this assembled architectural landscape.'),
 '1305':('Buildings from nine dynasties; exact ensemble range unreviewed','Do not infer numeric boundaries or component dates from dynasty names or the property name.')
}
# Explicit shared calendar intervals, not region-dependent Ancient/Medieval labels.
CLASSES=[('before_1','Before 1 CE',None,1,'#482B32'),('1_599','1–599 CE',1,600,'#6C3B40'),('600_1199','600–1199 CE',600,1200,'#914C45'),('1200_1599','1200–1599 CE',1200,1600,'#B7654D'),('1600_1799','1600–1799 CE',1600,1800,'#BD773F'),('1800_plus','1800 CE onward',1800,None,'#BF8438')]
UNKNOWN_COLOR='#676D6B'
def classify(start):
    if start is None:return 'Unknown'
    for key,label,lo,hi,color in CLASSES:
        if (lo is None or start>=lo) and (hi is None or start<hi):return key
    raise ValueError(start)
def write_csv(path,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    source=json.loads((RAW/'unesco.json').read_text(encoding='utf-8'))
    evidence=list(csv.DictReader((DATA/'historical_evidence.tsv').open(encoding='utf-8'),delimiter='\t'))
    reviewed={r['unesco_id']:r for r in evidence};assert len(reviewed)==len(evidence)
    selected=sorted([r for r in source if r['category']=='Cultural' and set(r.get('iso_codes') or []) & UNITS.keys()],key=lambda r:int(r['id_no']))
    assert set(reviewed).isdisjoint(UNKNOWN)
    assert {r['id_no'] for r in selected}==set(reviewed)|set(UNKNOWN),'Unreviewed or unexpected property'
    world=json.loads((RAW/'ne_50m_admin_0_countries.geojson').read_text(encoding='utf-8'))
    geoms={f['properties']['ADM0_A3']:shape(f['geometry']) for f in world['features']}
    properties=[];sites=[];outside=[]
    for r in selected:
        uid=r['id_no'];known=uid in reviewed;e=reviewed.get(uid)
        if known:
            # Each judgment cites a manually inspected source field and an exact text anchor.
            assert e['evidence_anchor'].casefold() in (r.get(e['source_field']) or '').casefold(),f'Evidence mismatch {uid}'
            start,end=int(e['start_year']),int(e['end_year']);assert start<=end and start!=0 and end!=0
            period=e['historical_period'];method=e['dating_method'];role=e['interval_role'];note=e['uncertainty_note']
        else:start=end=None;period,note=UNKNOWN[uid];method='Unknown; no comparable phase assigned';role='unresolved'
        cls=classify(start)
        row={'unesco_id':uid,'property_name':r['name_en'],'inscription_year':int(r['date_inscribed']),
         'historical_period':period,'start_year':start,'end_year':end,
         'representative_year':start if known and start==end else None,
         'dating_method':method,'interval_role':role,
         'source_url':f'https://whc.unesco.org/en/list/{uid}/',
         'source_field':e['source_field'] if known else 'short_description_en / justification_en',
         'evidence_anchor':e['evidence_anchor'] if known else '',
         'confidence':'High: explicit calendar marker' if known and start==end else 'Moderate: explicit period, approximate bounds' if known else 'Unknown: unclassified in this review',
         'uncertainty_note':note,'historical_class':cls,'color_basis':'lower bound of selected documented formation-phase interval; NOT inscription year' if known else 'Unknown',
         'iso_codes':' | '.join(sorted(r['iso_codes'])),'components_global':r['components_count'],'components_in_scope':0}
        components=json.loads(r['components_list']);assert len(components)==r['components_count']
        for c in sorted(components,key=lambda c:c['ref']):
            lon,lat=c['longitude'],c['latitude'];assert all(isinstance(v,(float,int)) and math.isfinite(v) for v in [lon,lat])
            assert -180<=lon<=180 and -90<=lat<=90 and (lon,lat)!=(0,0)
            local={'unesco_id':uid,'component_ref':c['ref'],'component_name':c['name'],'longitude':lon,'latitude':lat}
            if len(r['iso_codes'])>1 and not any(geoms[UNITS[k]].covers(Point(lon,lat)) for k in set(r['iso_codes']) & UNITS.keys()):outside.append(local);continue
            row['components_in_scope']+=1
            sites.append({**local,'property_name':row['property_name'],'inscription_year':row['inscription_year'],'historical_class':cls,'historical_period':period,'start_year':start,'end_year':end,'dating_inheritance':'property-level phase; no component-specific age asserted','source_url':row['source_url']})
        properties.append(row)
    assert len(properties)==87 and len({r['unesco_id'] for r in properties})==87
    assert len(sites)==590 and len({r['component_ref'] for r in sites})==590 and len(outside)==27
    signature=lambda rows:sorted((r['component_ref'],float(r['longitude']),float(r['latitude'])) for r in rows)
    coordinate_hash=hashlib.sha256(json.dumps(signature(sites)).encode()).hexdigest()
    # Frozen after a record-for-record comparison with the verified Revision 02 coordinates.
    assert coordinate_hash=='4777f0ce3a7482d1b8a3b211cd0c74d09b0cba043b4a4c108b798cb355426469','Verified coordinates changed'
    write_csv(DATA/'heritage_historical.csv',properties);write_csv(DATA/'component_sites.csv',sites)
    write_csv(DATA/'components_outside_scope.csv',outside)
    fc={'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Point','coordinates':[s['longitude'],s['latitude']]},'properties':s} for s in sites]}
    (DATA/'component_sites.geojson').write_text(json.dumps(fc,ensure_ascii=False,indent=2),encoding='utf-8')
    class_order=[c[0] for c in CLASSES]+['Unknown']
    coverage={k:{'properties':sum(r['historical_class']==k for r in properties),'site_records':sum(r['historical_class']==k for r in sites)} for k in class_order}
    manifest={'snapshot_date':'2026-11-10','property_count':87,'component_records':590,'unique_coordinate_pairs':len({(s['longitude'],s['latitude']) for s in sites}),
     'dated_properties':len(reviewed),'unknown_properties':len(UNKNOWN),'unknown_ids':sorted(UNKNOWN,key=int),'coverage_by_class':coverage,
     'component_coordinate_signature_sha256':coordinate_hash,
     'calendar':'Negative integers = BCE; positive = CE; no year zero. Century bounds are precision envelopes, not precise event dates.',
     'classification':'Explicit calendar bins of the LOWER BOUND of a manually selected formation-phase interval. Never an arithmetic midpoint or inscription date.',
     'class_breaks':[{'key':k,'label':l,'lower_inclusive':lo,'upper_exclusive':hi,'color':co} for k,l,lo,hi,co in CLASSES],
     'unknown_color':UNKNOWN_COLOR,'evidence_table':'data/historical_evidence.tsv','no_component_specific_dates_assigned':True,
     'sources':{'unesco':{'url':'https://data.unesco.org/api/explore/v2.1/catalog/datasets/whc001/exports/json','path':'data/raw/unesco.json','sha256':hashlib.sha256((RAW/'unesco.json').read_bytes()).hexdigest()},
      'basemap':{'url':'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson','path':'data/raw/ne_50m_admin_0_countries.geojson','sha256':hashlib.sha256((RAW/'ne_50m_admin_0_countries.geojson').read_bytes()).hexdigest()}}}
    (DATA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'dated':len(reviewed),'unknown':len(UNKNOWN),'distribution':coverage},indent=2))
if __name__=='__main__':main()
