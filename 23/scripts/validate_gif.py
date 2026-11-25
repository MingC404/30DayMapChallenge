"""Check decoded GIF timing, group synchronization, fixed pixels and reproducibility."""
from pathlib import Path
import json,hashlib,sys,subprocess
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image,ImageChops,ImageDraw
from encode_gif import make_frames
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs';LAY=OUT/'layers'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
expected,records,config=make_frames();path=OUT/'day23_a_tasting_map_of_tea.gif';gif=Image.open(path)
assert gif.n_frames==5 and gif.size==(1600,1200) and gif.info['loop']==0
palette=Image.new('P',(1,1));palette.putpalette(gif.getpalette());decoded=[];durations=[]
for i,frame in enumerate(expected):
 gif.seek(i);actual=gif.convert('RGB');decoded.append(np.asarray(actual));durations.append(gif.info['duration'])
 quantized=frame.quantize(palette=palette,dither=Image.Dither.NONE).convert('RGB')
 assert ImageChops.difference(actual,quantized).getbbox() is None,('Decoded content mismatch',i)
assert durations==[2000,2000,2000,2000,3000]
ids={p.stem for p in (LAY/'items').glob('*.png')};assigned=[id for r in records[:4] for id in r['active_ids']]
assert len(assigned)==16 and len(set(assigned))==16
assert ids==set(assigned)|{'shan-tuyet'}
assert set(records[3]['active_ids'])=={'masala-chiya','thai-iced-tea'}
assert all(v==1 for v in records[3]['region_opacities'].values())
assert all(r['region_opacities']['fujian']==1 for r in records)
# Every pixel outside variable items, region shading and the theme heading stays fixed.
variable=np.asarray(Image.open(LAY/'regions.png'))[:,:,3]>0
for p in (LAY/'items').glob('*.png'):variable|=np.asarray(Image.open(p))[:,:,3]>0
variable[195:240,75:450]=True
assert all(np.array_equal(decoded[0][~variable],f[~variable]) for f in decoded[1:])
assert all(np.array_equal(decoded[0][:190],f[:190]) and np.array_equal(decoded[0][990:],f[990:]) for f in decoded[1:])
# Heading does not intersect any existing annotation; original static PNG stays intact.
m=json.loads((ROOT/'review/final_metadata.json').read_text());assert all(t['box'][3]<195 or t['box'][1]>240 or t['box'][0]>450 for t in m['texts'])
assert sha(OUT/'day23_a_tasting_map_of_tea.png')=='3e225571f9209fc3256f81b70847900d0c3337045c867a7e2deed91d88618f93'
record=dict(frames=5,durations_ms=durations,total_duration_ms=sum(durations),loop=0,canvas=list(gif.size),decoded_frames_match_expected=True,fixed_title_legend_basemap_pixels=True,each_assigned_item_appears_in_one_theme=True,shan_tuyet_overview_only=True,shared_fujian_always_neutral=True,milk_spice_retains_static_region_fills=True,theme_position_fixed=True,approved_static_png_unchanged=True,gif_sha256=sha(path),gif_bytes=path.stat().st_size)
if '--check-rebuild' in sys.argv:
 before=sha(path);subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/encode_gif.py')],check=True);assert sha(path)==before;record['deterministic_repeat_gif_identical']=True
(ROOT/'review/animation_validation.json').write_text(json.dumps(record,indent=2),encoding='utf8');print(json.dumps(record,indent=2))
