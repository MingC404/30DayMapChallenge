"""Optional one-time geometry preparation; needs shapely and pyproj.

Dashboard builds use the retained simplified file and need only Python stdlib.
"""
import json
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import shape, mapping
from shapely.ops import transform

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'data_raw/boundaries'


def main():
    source = json.loads((DIRECTORY / 'nyc_boroughs_raw.geojson').read_text(encoding='utf-8'))
    forward = Transformer.from_crs(4326, 32618, always_xy=True).transform
    backward = Transformer.from_crs(32618, 4326, always_xy=True).transform
    features = []
    for feature in source['features']:
        original = transform(forward, shape(feature['geometry']))
        simplified = original.simplify(15, preserve_topology=True)
        assert simplified.is_valid and not simplified.is_empty
        largest = max(original.geoms, key=lambda polygon: polygon.area) if original.geom_type == 'MultiPolygon' else original
        label = transform(backward, largest.representative_point())
        features.append(dict(type='Feature', properties=dict(
            name=feature['properties']['boroname'],
            label=[round(label.y, 6), round(label.x, 6)]),
            geometry=mapping(transform(backward, simplified))))
    result = dict(type='FeatureCollection', features=features)
    # Quantize coordinates to six decimals after simplification (~0.1 metre).
    def rounded(value):
        if isinstance(value, float):
            return round(value, 6)
        if isinstance(value, (list, tuple)):
            return [rounded(item) for item in value]
        if isinstance(value, dict):
            return {key: rounded(item) for key, item in value.items()}
        return value
    target = DIRECTORY / 'nyc_boroughs_simplified.geojson'
    target.write_text(json.dumps(rounded(result), separators=(',', ':')), encoding='utf-8')
    print('Saved:', target, target.stat().st_size, 'bytes; five land-only boroughs; 15m tolerance')


if __name__ == '__main__':
    main()
