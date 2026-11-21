"""Remove only named superseded exports and reproducible temporary extracts."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
FILES=[
 'outputs/new_york_day_and_night_v1.png','outputs/preview.png',
 'outputs/preview_daytime.png','outputs/preview_nighttime.png',
 'research/type_references.png','research/day_zip_tail.bin',
 'research/landscan-usa-2021-day.zip','research/landscan-usa-2021-night.zip',
 'research/landscan-usa-2021-conus-day.tif','research/landscan-usa-2021-conus-night.tif',
 'review/night_blue_trial.png','review/blue_background_trial.gif',
 'review/blue_compare.png','review/light_compare.png']
def main():
    previous=[]
    record=ROOT/'review/cleanup_record.json'
    if record.exists():previous=json.loads(record.read_text(encoding='utf-8'))['removed']
    for name in FILES:
        p=(ROOT/name).resolve()
        assert p.is_relative_to(ROOT) and (not p.exists() or p.is_file()),p
        if not p.exists():continue
        if name.startswith('research/landscan-'):
            period='night' if 'night' in name else 'day'
            assert (ROOT/f'research/landscan-usa-2021-{period}-assets.zip').is_file()
        with p.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
        previous.append({'path':name,'bytes':p.stat().st_size,'sha256':sha})
        p.unlink()
    record.write_text(json.dumps({'removed':previous,'reason':'Old parallel-map/preview exports have no remaining publishing or validation references. Blue candidates are rejected trial exports. Full CONUS TIFFs and inner ZIPs are reproducible extracts; original ORNL archives, 18 source hashes, metadata, cropped TIFFs and analysis tables remain. Final card screenshots and JSON audits are retained as QA evidence.','freed_bytes':sum(r['bytes'] for r in previous)},indent=2),encoding='utf-8')
    print(f'Cleanup record: {len(previous)} named files, {sum(r["bytes"] for r in previous):,} bytes.')
if __name__=='__main__':main()
