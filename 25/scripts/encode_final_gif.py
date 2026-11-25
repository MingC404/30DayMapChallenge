"""Opacity-only animation from independent transparent line and label cutouts."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'outputs'
NAMES=['day25_elevation.png','day25_population.png'];BG=np.array([244,240,231],dtype=np.float32)
hashes={f:hashlib.sha256((O/f).read_bytes()).hexdigest() for f in NAMES}
sources=[np.asarray(Image.open(O/f).convert('RGB')) for f in NAMES]
assert all(a.shape==(1200,1600,3) for a in sources)
line_mask=np.zeros((1200,1600),bool);line_mask[200:1100,500:1200]=True
label_mask=np.zeros_like(line_mask);label_mask[280:420,70:490]=True
fixed_mask=~(line_mask|label_mask)
assert np.array_equal(sources[0][fixed_mask],sources[1][fixed_mask])
base=sources[0].copy();base[~fixed_mask]=BG.astype('uint8')
def cutout(src,region):
 # Exact antialiased endpoint RGB; blank paper is fully transparent.
 alpha=(region&np.any(src!=BG,axis=2)).astype('uint8')*255
 return np.dstack([src,alpha])
lines=[cutout(a,line_mask) for a in sources];labels=[cutout(a,label_mask) for a in sources]
def contribution(layer):
 return (layer[:,:,:3].astype('float32')-BG)*(layer[:,:,3:4].astype('float32')/255)
line_delta=[contribution(a) for a in lines];label_delta=[contribution(a) for a in labels]
def compose(t):
 # Independent opacity contributions over one paper layer; no opaque full-image overlay.
 old_label=max(1-2*t,0);new_label=max(2*t-1,0)
 out=base.astype('float32')+(1-t)*line_delta[0]+t*line_delta[1]+old_label*label_delta[0]+new_label*label_delta[1]
 return Image.fromarray(np.clip(np.rint(out),0,255).astype('uint8'))
for i,t in enumerate([0.,1.]):assert np.array_equal(np.asarray(compose(t)),sources[i])
middle=np.asarray(compose(.5));assert np.array_equal(middle[label_mask],base[label_mask])
assert np.array_equal(middle[fixed_mask],base[fixed_mask])
# Sample actual full-resolution foreground colours: thumbnail palettes lose thin dark lines.
foreground=np.any(sources[0]!=BG,axis=2)|np.any(sources[1]!=BG,axis=2)
samples=[np.asarray(compose(k/60))[foreground][::4] for k in range(61)]
pixels=np.concatenate(samples);pad=(-len(pixels))%1024
pixels=np.pad(pixels,((0,pad),(0,0)),mode='edge').reshape(-1,1024,3)
learned=Image.fromarray(pixels).quantize(colors=253,method=Image.Quantize.MEDIANCUT)
palette=Image.new('P',(1,1))
palette.putpalette([244,240,231,56,59,57,182,106,73]+learned.getpalette()[:253*3])
# 2.05 s endpoints plus 2.95 s intermediate frames each way: exactly 10 s.
schedule=[(0.,2050)]+[(k/60,50) for k in range(1,60)]+[(1.,2050)]+[(k/60,50) for k in range(59,0,-1)]
def quantize_frame(t):
 rgb=compose(t);a=np.asarray(rgb);im=rgb.quantize(palette=palette,dither=Image.Dither.NONE)
 codes=np.array(im)
 for code,color in enumerate([[244,240,231],[56,59,57],[182,106,73]]):codes[np.all(a==color,axis=2)]=code
 out=Image.fromarray(codes);out.putpalette(palette.getpalette());return out
indexed=[quantize_frame(t) for t,_ in schedule]
target=O/'day25_taiwan_two_landscapes.gif'
indexed[0].save(target,save_all=True,append_images=indexed[1:],duration=[ms for _,ms in schedule],loop=0,disposal=1,optimize=False)
durations=[];endpoint_error=[];midpoint_indices=[]
with Image.open(target) as gif:
 assert gif.n_frames==len(schedule) and gif.size==(1600,1200) and gif.info['loop']==0
 fixed_reference=np.asarray(indexed[0].convert('RGB'))[fixed_mask]
 for i,(t,ms) in enumerate(schedule):
  gif.seek(i);assert gif.info['duration']==ms;durations.append(ms)
  decoded=np.asarray(gif.convert('RGB'));expected=np.asarray(indexed[i].convert('RGB'))
  assert np.array_equal(decoded,expected),('GIF compositing mismatch',i)
  assert np.array_equal(decoded[fixed_mask],fixed_reference),('Fixed artwork flicker',i)
  if t in [0.,1.]:endpoint_error.append(float(np.abs(decoded.astype(float)-sources[int(t)]).mean()))
  if t==.5:midpoint_indices.append(i)
 assert sum(durations)==10000
assert hashes=={f:hashlib.sha256((O/f).read_bytes()).hexdigest() for f in NAMES}
static=json.loads((O/'current_static_validation.json').read_text())
assert min(s['top_min_px'] for s in static['frames'][1]['segments'])>210
# Optional in-memory review, written only if explicitly requested; not a delivery artifact.
import sys
if '--review' in sys.argv:
 review=Image.new('RGB',(862*3,647))
 for i,t in enumerate([0,.5,1]):
  idx=next(j for j,(value,_) in enumerate(schedule) if value==t)
  review.paste(indexed[idx].convert('RGB').resize((862,647),Image.Resampling.LANCZOS),(862*i,0))
 review.save(R/'.review_crossfade.png')
report={'passed':True,'file':target.name,'canvas':[1600,1200],'frames':len(schedule),'cycle_ms':10000,'endpoint_hold_ms':2050,'transition_intermediate_ms':2950,'frame_interval_ms':50,'loop':0,'line_opacity':'elevation=1-t; population=t; midpoint both 0.5','annotation_opacity':'old=max(1-2t,0); new=max(2t-1,0); neither visible at midpoint','fixed_artwork_pixel_identical_all_decoded_frames':True,'decoded_frames_match_shared_palette_composites':True,'source_pngs_byte_unchanged':True,'endpoint_mean_absolute_palette_error':endpoint_error,'midpoint_frame_indices':midpoint_indices,'palette':'shared 256 colors sampled at 61 opacity levels; no dithering','loop_boundary_opacity_step':1/60,'geometry':'no morph, translation, resampling or height change; transparent visible-line cutouts from approved PNGs','profile_indices':static['profile_indices'],'shared_baseline_camera':static['shared_baseline_camera'],'gallery_review_width_px':862,'png_sha256':hashes,'gif_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
(O/'final_media_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ['passed','frames','cycle_ms','endpoint_mean_absolute_palette_error','source_pngs_byte_unchanged']},indent=2))
