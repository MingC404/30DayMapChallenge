"""Shared, self-contained configuration/data access for the final two snapshots."""
import hashlib,json
import numpy as np
import wind_field as field
import render_final as drawing

ROOT=field.ROOT
FINAL=json.loads((ROOT/'config/final.json').read_text(encoding='utf-8'))

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def snapshot(name):
    return next(s for s in FINAL['snapshots'] if s['name'].lower()==name.lower())

def read_data(spec):
    request=json.loads((ROOT/spec['request_config']).read_text())
    path=ROOT/'data/cache'/request['cache_filename']
    return field.load_field(path,request,spec['time_utc'],ROOT/f"metadata/{spec['name']}_data.json")

def selected_curves(spec,interp,data_hash):
    drawing.CACHE=ROOT/spec['cache_directory'];drawing.CACHE.mkdir(exist_ok=True,parents=True)
    curves=[]
    for i,layer in enumerate(drawing.CFG['streamline_layers']):
        lines,_=drawing.paths_for_layer(layer,i,interp,data_hash)
        ids=FINAL['selected_original_indices'][layer['name']]
        assert len(ids)==len(set(ids)) and all(len(lines[j])>=3 for j in ids)
        curves.extend((layer['name'],j,lines[j]) for j in ids)
    assert len(curves)==398
    return curves

def protected_inputs():
    paths=list((ROOT/'data/cache').glob('*.nc'))
    paths+=[ROOT/s['png'] for s in FINAL['snapshots'] if (ROOT/s['png']).exists()]
    return {p.relative_to(ROOT).as_posix():digest(p) for p in paths}

def verify_unchanged(before):
    for name,value in before.items(): assert digest(ROOT/name)==value,f'Protected file changed: {name}'

def write_report(name,report):field.write_json(ROOT/'metadata'/name,report)
