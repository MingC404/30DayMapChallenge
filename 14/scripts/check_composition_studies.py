"""Inspect saved composition previews without changing image pixels."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps'))
from PIL import Image

def main():
 files=['option_a_river_spine.png','option_b_street_spine.png','option_c_layered_montage.png']
 records=[]
 for name in files:
  path=ROOT/'work/composition_studies'/name
  with Image.open(path) as image:
   image.load();width,height=image.size
   assert width>height and abs(width/height-2)<.02
   records.append(dict(path=str(path.relative_to(ROOT)).replace('\\','/'),width=width,height=height,mode=image.mode,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 report=dict(status='composition_study_only_awaiting_user_selection',tool='built-in image_gen',reference_images_supplied_to_generation=False,reference_research_date_local='2026-11-13',timezone='America/New_York',prompt_file='config/illustrated_montage_prompts.json',postprocessing='none; original generated pixels copied to workspace',recommended='C',formal_map_created=False,images=records)
 (ROOT/'metadata/illustrated_montage_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(json.dumps(report,indent=2))

if __name__=='__main__':main()
