"""Verify the accepted GIF and exact decoded hold PNGs; never render or rewrite it."""
from pathlib import Path
import sys,json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps'))
from PIL import Image,ImageChops

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify(extract=False):
 report=json.loads((ROOT/'data/release.json').read_text(encoding='utf-8'));gif=ROOT/report['gif']['path'];assert digest(gif)==report['gif']['sha256']
 duration=0;matched={};palette_frames=0
 with Image.open(gif) as image:
  assert image.size==(720,655) and image.info.get('loop')==0
  for index in range(image.n_frames):
   image.seek(index);dt=image.info['duration'];rgb=image.convert('RGB');palette_frames+=1
   for state,spec in report['keyframes'].items():
    if duration<=spec['sample_time_ms']<duration+dt:
     path=ROOT/spec['path']
     if extract:rgb.save(path)
     else:
      saved=Image.open(path).convert('RGB');assert saved.size==rgb.size and ImageChops.difference(saved,rgb).getbbox() is None
     matched[state]=dict(path=spec['path'],sample_time_ms=spec['sample_time_ms'],decoded_frame_index=index,sha256=digest(path))
   duration+=dt
 assert duration==14400 and set(matched)==set('ABC')
 sources=json.loads((ROOT/'data/sources.json').read_text(encoding='utf-8'))
 for spec in sources:assert digest(ROOT/f"data/{spec['key']}.json")==spec['sha256']
 config=json.loads((ROOT/'data/animation.json').read_text(encoding='utf-8'));assert digest(ROOT/config['clip_manifest'])==config['audit_manifest_sha256']
 if extract:
  report['keyframes']=matched;report['verification']={'duration_ms':duration,'decoded_frames':palette_frames,'loop':0,'exact_decoded_hold_pngs':True,'source_data_hashes_match':True};(ROOT/'data/release.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(f'PASS: accepted GIF SHA-256 unchanged; {duration} ms, infinite loop; A/B/C PNGs equal decoded hold frames; four OSM data hashes and clip manifest verified.')

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--extract-keyframes',action='store_true',help='Extract hold PNGs from GIF, without altering GIF bytes');args=parser.parse_args();verify(args.extract_keyframes)
