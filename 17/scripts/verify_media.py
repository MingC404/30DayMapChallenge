"""Validate encoded formats and quantify the decoded GIF seam without keeping test frames."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
import json,numpy as np
from PIL import Image
from export_media import find_ffmpeg
import subprocess,re
R=Path(__file__).resolve().parents[1];g=Image.open(R/'day17_loop.gif');assert g.size==(900,1080) and g.n_frames==240 and g.info.get('loop')==0
first=None;prev=None;diffs=[];duration=0
for i in range(g.n_frames):
 g.seek(i);duration+=g.info['duration'];a=np.asarray(g.convert('RGB'),dtype=np.int16)
 if first is None:first=a.copy()
 if prev is not None:diffs.append(float(np.abs(a-prev).mean()))
 prev=a
assert duration==12000
seam=float(np.abs(first-prev).mean());assert seam<=max(diffs)*1.3,(seam,max(diffs))
p=Image.open(R/'day17.png');assert p.size==(3000,3600) and p.mode in ('RGB','RGBA')
ff=find_ffmpeg();v=subprocess.run([ff,'-hide_banner','-i',str(R/'day17_loop.mp4'),'-f','null','-'],capture_output=True,text=True);assert v.returncode==0,v.stderr
assert '00:00:12.00' in v.stderr and '1080x1296' in v.stderr
report={'passed':True,'gif_frames':240,'gif_duration_ms':duration,'gif_size_bytes':(R/'day17_loop.gif').stat().st_size,'gif_decoded_seam_mean_absolute_channel_difference':seam,'gif_max_normal_adjacent_difference':max(diffs),'gif_seam_not_an_outlier':True,'mp4_decode_ok':True,'mp4_duration_seconds':12,'png_dimensions':list(p.size)}
(R/'data/media_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
