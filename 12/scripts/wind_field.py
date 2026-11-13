"""Validated ERA5 data and physically scaled geographic streamline integration."""
from pathlib import Path
import hashlib
import json
import numpy as np
import xarray as xr
from scipy.interpolate import RegularGridInterpolator
from pyproj import Geod
ROOT = Path(__file__).resolve().parents[1]
REQUEST_CONFIG = json.loads((ROOT / 'config/era5_request.json').read_text(encoding='utf-8'))
DATA = ROOT / 'data/cache' / REQUEST_CONFIG['cache_filename']
CALM_M_S = .08
R = 6371000.0
GEOD = Geod(a=R, b=R)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def load_field(data_path=None, request_config=None, expected_time='2025-01-15T06:00:00', validation_path=None):
    data_path=DATA if data_path is None else Path(data_path)
    request_config=REQUEST_CONFIG if request_config is None else request_config
    if not data_path.is_file():
        raise RuntimeError('Real ERA5 cache missing. Run fetch_era5.py first.')
    ds = xr.open_dataset(data_path)
    time_name = 'valid_time' if 'valid_time' in ds.coords else 'time'
    times = np.asarray(ds[time_name].values).reshape(-1)
    assert len(times) == 1 and times[0] == np.datetime64(expected_time), 'Unexpected time'
    assert {'u10', 'v10'}.issubset(ds.data_vars), 'Expected u10/v10'
    lat = np.sort(ds.latitude.values)
    lon = np.sort(ds.longitude.values)
    assert np.allclose(np.diff(lat), .25) and np.allclose(np.diff(lon), .25), 'Unexpected spacing'
    north, west, south, east = request_config['request']['area']
    assert np.allclose([lon[0], lon[-1], lat[0], lat[-1]], [west, east, south, north]), 'Unexpected extent'
    fields = []
    for name in ['u10', 'v10']:
        assert ds[name].attrs.get('units') in ['m s**-1', 'm s-1', 'm/s'], 'Unexpected wind units'
        a = ds[name].squeeze(drop=True)
        assert set(a.dims) == {'latitude', 'longitude'}, 'Unresolved dimensions'
        a = a.sortby('latitude').sortby('longitude').transpose('latitude', 'longitude').values
        assert np.isfinite(a).all(), 'Missing wind values'
        fields.append(a)
    speed = np.hypot(*fields)
    info = {'sha256': hashlib.sha256(data_path.read_bytes()).hexdigest(),
            'dataset': 'reanalysis-era5-single-levels', 'time_utc': str(times[0]),
            'dimensions': dict(ds.sizes), 'coordinates': {k: {'dims': list(v.dims), 'values': np.asarray(v.values).astype(str).tolist()} for k,v in ds.coords.items()},
            'variables': {k: {'dims': list(v.dims), 'attrs': {a:str(b) for a,b in v.attrs.items()}} for k,v in ds.data_vars.items()},
            'spacing_degrees': [.25, .25], 'speed_min_max_m_s': [float(speed.min()), float(speed.max())],
            'speed_scale_m_s': [0, float(5*np.ceil(speed.max()/5))],
            'validation': 'passed; finite physical u/v; exact single hour and requested extent'}
    info['extent_wsen'] = [west, south, east, north]
    ds.close()
    write_json(ROOT / 'metadata/data_validation.json' if validation_path is None else Path(validation_path), info)
    interp = [RegularGridInterpolator((lat, lon), a, bounds_error=False, fill_value=np.nan) for a in fields]
    return interp, info


def uv_at(points, interp):
    return np.column_stack([f(points[:, ::-1]) for f in interp])


def derivative(points, interp):
    uv = uv_at(points, interp)
    speed = np.linalg.norm(uv, axis=1)
    out = np.rad2deg(uv / np.maximum(speed[:, None], 1e-30) / R)
    out[:, 0] /= np.cos(np.deg2rad(points[:, 1]))
    out[speed < CALM_M_S] = np.nan
    return out


def integrate(seeds, length_km, interp, step=2000):
    lat, lon = interp[0].grid
    halves, reasons = [], {}
    for sign in [-1, 1]:
        p = seeds.copy()
        history = [p.copy()]
        active = np.ones(len(p), dtype=bool)
        remaining = length_km*1000/2
        while remaining > 1e-6:
            h = min(step, remaining)*sign
            k1 = derivative(p, interp)
            k2 = derivative(p+h*k1/2, interp)
            k3 = derivative(p+h*k2/2, interp)
            k4 = derivative(p+h*k3, interp)
            q = p+h*(k1+2*k2+2*k3+k4)/6
            inside = ((q[:,0] >= lon[0]) & (q[:,0] <= lon[-1]) & (q[:,1] >= lat[0]) & (q[:,1] <= lat[-1]))
            valid = np.isfinite(q).all(axis=1) & inside
            ended = active & ~valid
            reasons['boundary_or_calm'] = reasons.get('boundary_or_calm', 0)+int(ended.sum())
            active &= valid
            q[~active] = np.nan
            history.append(q.copy())
            p = q
            remaining -= abs(h)
        reasons['length_budget'] = reasons.get('length_budget', 0)+int(active.sum())
        halves.append(np.array(history))
    lines = []
    for i in range(len(seeds)):
        back = halves[0][:,i]
        forward = halves[1][1:,i]
        line = np.concatenate([back[np.isfinite(back).all(axis=1)][::-1], forward[np.isfinite(forward).all(axis=1)]])
        lines.append(line)
    return lines, reasons


def diagnostics(lines, interp):
    lengths, errors = [], []
    for line in lines:
        if len(line)<2:
            lengths.append(0.)
            continue
        a, b = line[:-1], line[1:]
        az, _, dist = GEOD.inv(a[:,0], a[:,1], b[:,0], b[:,1])
        mid = (a+b)/2
        uv = uv_at(mid, interp)
        wind_az = np.rad2deg(np.arctan2(uv[:,0], uv[:,1]))
        errors.extend(np.abs((az-wind_az+180)%360-180).tolist())
        lengths.append(float(dist.sum()/1000))
    return {'length_km_min_median_max': np.percentile(lengths,[0,50,100]).tolist(),
            'tangent_error_deg_p50_p95_max': np.percentile(errors,[50,95,100]).tolist(),
            'lines':len(lines), 'segments':len(errors)}
