"""Build a local, static Leaflet dashboard; no Python dependencies required."""
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data_raw/family/Public_Restrooms_20261024.csv'
OUTPUT = ROOT / 'outputs/nyc_changing_station_explorer.html'
CATEGORIES = [
    ('unspecified', 'Restroom with changing table', '#72B8AC'),
    ('women', 'In women’s restrooms', '#F29B87'),
    ('men', 'In men’s restrooms', '#72B9E6'),
    ('all_gender', 'In all-gender restrooms', '#AC94DB'),
]
OLD_LABELS = ['Yes', "Yes, in women's restroom only", "Yes, in men's restroom only",
              'Yes, in single-stall all gender restroom only']


def basemap_style():
    """Default monochrome streets; borough boundaries are a separate line layer."""
    style = json.loads((ROOT / 'data_raw/basemap/openfreemap_positron.json').read_text(encoding='utf-8'))
    for layer in style['layers']:
        name, kind = layer['id'], layer['type']
        paint = layer.setdefault('paint', {})
        if kind == 'background':
            paint['background-color'] = '#FFFFFF'
        elif kind == 'fill':
            paint['fill-color'] = '#FFFFFF' if name == 'water' else '#F5F5F5'
            if name in {'building', 'park', 'landcover_wood'}:
                layer.setdefault('layout', {})['visibility'] = 'none'
        elif kind == 'line':
            if name == 'waterway':
                paint['line-color'] = '#E3E3E3'
            elif name.startswith(('highway', 'tunnel', 'road')):
                paint['line-color'] = '#DADADA' if 'casing' in name else '#F9F9F9'
            elif name.startswith('railway'):
                layer.setdefault('layout', {})['visibility'] = 'none'
            elif name.startswith('boundary'):
                paint['line-color'] = '#DDDDDD'
        elif kind == 'symbol':
            paint['text-color'] = '#A0A0A0'
            paint['text-halo-color'] = '#FFFFFF'
            # Retain only a few city labels; no street shields, POIs or water labels.
            if name not in {'label_city', 'label_city_capital'}:
                layer.setdefault('layout', {})['visibility'] = 'none'
    return style


def normalize(raw):
    return raw.strip().strip('"').strip()


MISSING_VALUES = {'', 'n/a', 'na', 'null', 'none', 'nan', 'not reported',
                  'not available', 'not applicable', 'unknown', '-', '--'}


def clean_value(value):
    if value is None:
        return ''
    text = str(value).strip()
    return '' if normalize(text).lower() in MISSING_VALUES else text


INFO_FIELDS = {'name': 'Facility Name', 'hours': 'Hours of Operation', 'open': 'Open',
               'accessibility': 'Accessibility', 'restroomType': 'Restroom Type',
               'locationType': 'Location Type', 'operator': 'Operator',
               'notes': 'Additional Notes', 'status': 'Status',
               'raw': 'Changing Stations', 'website': 'Website', 'address': 'Address'}


def information(row):
    result = {key: clean_value(row.get(source)) for key, source in INFO_FIELDS.items()}
    result['location'], result['access'] = note_fields(result['notes'])
    return result


def placement_matches(raw):
    """Parse only an explicit affirmative placement clause, never other fields.

    Full-match grammar allows combinations, but rejects unrecognized/negative
    qualifiers. Unknown labels remain excluded for review, rather than guessing.
    """
    label = normalize(raw).lower().replace('’', "'")
    if label == 'yes':
        return ['unspecified']
    token = r"(?:single-stall )?(?:women's|men's|all[ -]gender)(?: restrooms?)?"
    match = re.fullmatch(r'yes, in (?:both )?(' + token + r'(?: (?:and|&) ' + token + r')*)(?: only)?', label)
    if not match:
        return []
    clause = match.group(1)
    result = []
    for key, expression in [('women', r"\bwomen's\b"), ('men', r"\bmen's\b"), ('all_gender', r'\ball[ -]gender\b')]:
        if re.search(expression, clause):
            result.append(key)
    # A trailing "only" preserves the explicitly enumerated set; never strip it
    # from the raw label shown in the popup.
    return result


LOCATION_NOTES = {
    "Restrooms for adult are in the basement.\nRestrooms for children are located on the 2nd floor in the Children's room and require keys.",
    'Located within the David Rubenstein Atrium at Lincoln Center.',
    'Restroom next to Black Box Coffee.',
    '2 all Gender Restroom available in public American Folk Art Museum - Enclosed portion of Covered Plaza',
    'Red Hook Library is in a temporary interim space 362 Van Brunt Street\nBrooklyn, NY 11231',
    'Changing Table outside restroom', "Changing Table in Children's room", 'Changing Table inside community room',
    'MTA station with bathrooms located outside of fare gates and open to the wider public',
}


def note_fields(note):
    # Notes are shown verbatim; these tags only choose their information-card heading.
    location = note if note in LOCATION_NOTES else ''
    access = note if ('key' in note.lower() or note in {
        'Security will grant access to restrooms.',
        'MTA station with bathrooms located outside of fare gates and open to the wider public',
        'This unit is free to use.', 'This unit costs $.25 to use.', 'The unit costs $.25 to use.'
    }) else ''
    if note.startswith('Each restroom is accessible by key.'):
        location = note
    return location, access


def coordinate_check(row):
    try:
        lat, lon = float(row['Latitude']), float(row['Longitude'])
    except (ValueError, TypeError):
        return None, 'missing_or_non_numeric'
    if not math.isfinite(lat) or not math.isfinite(lon):
        return None, 'missing_or_non_numeric'
    if 40.45 <= lon <= 40.95 and -74.30 <= lat <= -73.65:
        return None, 'suspected_swapped'
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None, 'outside_world_range'
    # Broad NYC envelope: flag anomalous records without silently correcting them.
    if not (40.45 <= lat <= 40.95 and -74.30 <= lon <= -73.65):
        return None, 'outside_nyc_envelope'
    return [lat, lon], 'valid'


def main():
    with SOURCE.open(encoding='utf-8-sig', newline='') as source:
        rows = list(csv.DictReader(source))
    category_keys = [key for key, _, _ in CATEGORIES]
    reasons = ['valid', 'missing_or_non_numeric', 'suspected_swapped', 'outside_world_range', 'outside_nyc_envelope']
    labels, unclear = Counter(), Counter()
    coords = Counter({reason: 0 for reason in reasons})
    excluded_yes = Counter({reason: 0 for reason in reasons if reason != 'valid'})
    old_counts, counts, points = [0]*4, [0]*4, []
    classification_changes = []
    raw_labels = Counter(row['Changing Stations'] for row in rows)
    for row_id, row in enumerate(rows):
        raw = row['Changing Stations']
        label = normalize(raw)
        labels[label] += 1
        xy, reason = coordinate_check(row)
        coords[reason] += 1
        matches = placement_matches(raw)
        old_key = dict(zip(OLD_LABELS, ['unspecified', 'women', 'men', 'all_gender'])).get(label)
        if set(matches) != ({old_key} if old_key else set()):
            classification_changes.append(dict(row=row_id, raw=raw, previous=old_key, matches=matches))
        if not matches:
            if label != 'No':
                unclear[label or '<blank>'] += 1
            continue
        try:
            lat, lon = float(row['Latitude']), float(row['Longitude'])
            if -90 <= lat <= 90 and -180 <= lon <= 180 and label in OLD_LABELS:
                old_counts[OLD_LABELS.index(label)] += 1
        except (ValueError, TypeError):
            pass
        if xy is None:
            excluded_yes[reason] += 1
            continue
        for key in matches:
            counts[category_keys.index(key)] += 1
        points.append(dict(id=row_id, lat=xy[0], lon=xy[1], matches=matches,
                           singleStall=bool(re.search(r'\bsingle-stall\b', label.lower())),
                           **information(row)))
    all_information = [information(row) for row in rows]
    coverage = {key: dict(all_records=sum(bool(r[key]) for r in all_information),
                          mapped_records=sum(bool(p[key]) for p in points))
                for key in [*INFO_FIELDS, 'location', 'access']}
    coverage['changingTable'] = dict(all_records=sum(bool(placement_matches(row['Changing Stations'])) for row in rows), mapped_records=len(points))
    coverage['singleStall'] = dict(all_records=sum(bool(placement_matches(row['Changing Stations'])) and 'single-stall' in normalize(row['Changing Stations']).lower() for row in rows), mapped_records=sum(p['singleStall'] for p in points))
    boroughs = json.loads((ROOT / 'data_raw/boundaries/nyc_boroughs_simplified.geojson').read_text(encoding='utf-8'))
    report = dict(source=str(SOURCE.relative_to(ROOT)), total_records=len(rows),
                  confirmed_yes=len(points)+sum(excluded_yes.values()), no=labels['No'],
                  unclear_labels=dict(unclear), coordinate_checks_all_records=dict(coords),
                  excluded_confirmed_yes=dict(excluded_yes),
                  original_world_range_counts=old_counts, reference_counts=[659,83,27,26],
                  dashboard_counts=dict(zip(category_keys, counts)), matching_records=len(points),
                  overlapping_records=sum(len(p['matches']) > 1 for p in points),
                  raw_changing_station_labels=dict(raw_labels),
                  label_evidence=[dict(raw=raw, count=count, matches=placement_matches(raw)) for raw,count in raw_labels.items()],
                  classification_changes=classification_changes,
                  field_inventory={field:dict(nonblank=sum(bool(r[field].strip()) for r in rows),
                                             examples=list(dict.fromkeys(r[field] for r in rows if r[field].strip()))[:5]) for field in rows[0]},
                  mapped_field_coverage=coverage, missing_value_tokens=sorted(MISSING_VALUES),
                  note_conflicts=[dict(name=r['Facility Name'], label=r['Changing Stations'], note=r['Additional Notes']) for r in rows if normalize(r['Changing Stations']) == 'No' and r['Additional Notes'].startswith('Changing Table')],
                  operational_statuses=dict(Counter(r['Status'] or '<blank>' for r in rows)),
                  data_updated_date='Not reported in project; filename date is not a verified update date',
                  address_field='Absent', boundary_layer='NYC DCP 26b land-only boroughs; local GeoJSON; simplified 15m')
    payload = json.dumps(dict(initialSelectedKeys=[], boroughs=boroughs, fieldCoverage=coverage, basemapStyle=basemap_style(), categories=[dict(key=k,name=n,description='Restroom type not specified.' if k=='unspecified' else '',color=c,count=counts[i]) for i,(k,n,c) in enumerate(CATEGORIES)], points=points), ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    template = (ROOT / 'scripts/explorer_template.html').read_text(encoding='utf-8')
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(template.replace('__DATA__', payload), encoding='utf-8')
    from prepare_pages import sync_pages_if_enabled
    sync_pages_if_enabled()
    # Keep both earlier audits unchanged for comparison.
    (OUTPUT.parent / 'nyc_changing_station_audit_v4.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print('Saved:', OUTPUT)


if __name__ == '__main__':
    main()
