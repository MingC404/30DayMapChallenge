"""One 14 s / 15 fps GIF; PNG is copied from the decoded final GIF, never rerendered.
All frames, encoder palettes and staging media live in an auto-cleaned OS temp directory.
"""
from pathlib import Path
import sys,os,tempfile,subprocess,shutil,json,hashlib,time
import numpy as np
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent

def ffmpeg_binary():
 if os.environ.get('FFMPEG_BINARY'):return os.environ['FFMPEG_BINARY']
 if shutil.which('ffmpeg'):return shutil.which('ffmpeg')
 try:import imageio_ffmpeg
 except ImportError:
  # Reuse an existing optional runtime; never install or write into another Day.
  existing=Path(tempfile.gettempdir())/'day17-runtime'
  if not existing.exists():raise RuntimeError('Install imageio-ffmpeg or set FFMPEG_BINARY.')
  sys.path.insert(0,str(existing));import imageio_ffmpeg
 return imageio_ffmpeg.get_ffmpeg_exe()

def digest(image):return hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
def inspect_diff(a,b):
 x=np.asarray(a.convert('RGB'),dtype=np.int16);y=np.asarray(b.convert('RGB'),dtype=np.int16);d=np.abs(x-y)
 return {'changed_pixels':int(np.any(d,axis=2).sum()),'maximum_channel_delta':int(d.max()),'mean_absolute_channel_delta':float(d.mean())}
def encode():
 started=time.monotonic();exe=ffmpeg_binary()
 def ff(args):
  r=subprocess.run([exe,'-hide_banner','-loglevel','error','-y','-threads','1',*args],cwd=REPO,text=True,capture_output=True)
  if r.returncode:raise RuntimeError(r.stderr)
 with tempfile.TemporaryDirectory(prefix='day19-render-') as temporary:
  scratch=Path(temporary);print('Rendering into an automatically cleaned OS temporary directory.',flush=True)
  subprocess.run(['node',str(ROOT/'scripts/render_frames.cjs'),str(scratch)],cwd=REPO,check=True)
  render=json.loads((scratch/'render-report.json').read_text());frames=render['art']['frames'];fps=render['art']['fps'];pattern=str(scratch/'frame_%04d.png');palette=str(scratch/'palette.png')
  with Image.open(scratch/'frame_0000.png') as first,Image.open(scratch/f'frame_{frames-1:04d}.png') as last:original_seam=inspect_diff(first,last)
  print('Creating a fixed 256-color palette and encoding the GIF.',flush=True)
  ff(['-framerate',str(fps),'-i',pattern,'-vf','palettegen=max_colors=256:reserve_transparent=0:stats_mode=full','-frames:v','1',palette])
  candidate=scratch/'final.gif'
  ff(['-framerate',str(fps),'-i',pattern,'-i',palette,'-lavfi','[0:v][1:v]paletteuse=dither=none:diff_mode=rectangle','-frames:v',str(frames),'-loop','0','-final_delay','7','-gifflags','+transdiff',str(candidate)])
  poster_index=render['posterIndex'];rects=[tuple(round(v) for v in (r[0],r[1],r[0]+r[2],r[1]+r[3])) for r in render['textRects']]
  durations=[];poster=None;first_rgb=None;last_rgb=None;static_hashes=None
  print('Validating decoded frames, stationary typography and exact poster identity.',flush=True)
  with Image.open(candidate) as gif:
   actual_frames=gif.n_frames;size=gif.size;loop=gif.info.get('loop')
   assert actual_frames==frames,(actual_frames,frames)
   for i in range(actual_frames):
    gif.seek(i);rgb=gif.convert('RGB');durations.append(gif.info.get('duration',0));hashes=[digest(rgb.crop(r)) for r in rects]
    if i==0:first_rgb=rgb.copy();static_hashes=hashes
    assert hashes==static_hashes,('Text region changed in GIF frame',i)
    if i==poster_index:poster=rgb.copy()
    if i==actual_frames-1:last_rgb=rgb.copy()
  total_ms=sum(durations);assert total_ms==14000,total_ms;assert size==(1600,1200),size;assert loop==0
  seam=inspect_diff(first_rgb,last_rgb)
  assert seam['mean_absolute_channel_delta']<.15,('Loop seam is not smooth',seam)
  poster_file=scratch/'final.png';poster.save(poster_file,format='PNG',optimize=True,dpi=(300,300))
  with Image.open(poster_file) as png:assert ImageChops.difference(png.convert('RGB'),poster).getbbox() is None
  route=render['route'];route_summary={k:v for k,v in route.items() if k!='legs'}
  stats=render['frameStats'];assert all(f['leaks']==0 and f['geometryFields']==1 and f['contours']==1 for f in stats)
  manifest={
   'title':'Where Smells Wander','theme':'DAY 19 / SENSES: SMELL','subtitle':'An Interactive Smellscape of SoHo, New York','author':'Ming Cao',
   'gif':{'file':'day19_loop.gif','width':size[0],'height':size[1],'frames':frames,'nominal_fps':fps,'duration_ms':total_ms,'effective_fps':frames/(total_ms/1000),'frame_delays_ms':sorted(set(durations)),'loop':loop,'bytes':candidate.stat().st_size,'palette_colors':256,'dither':'none'},
   'png':{'file':'day19.png','width':size[0],'height':size[1],'gif_frame_index':poster_index,'gif_timestamp_ms':sum(durations[:poster_index]),'nominal_time_seconds':poster_index/fps,'bytes':poster_file.stat().st_size,'decoded_rgb_sha256':digest(poster),'exact_decoded_gif_match':True,'selection':'Maximum mixed-evidence support score among actual captured animation frames, with at least 100 amber and 100 violet model cells.'},
   'typography':{'day':'Segoe UI Semibold 600, 1.1% width, 0.08em tracking','title':'Georgia Regular 400, 2.8% width','subtitle':'Segoe UI Regular 400, 1.2% width','stationary_regions':render['textRects'],'all_decoded_frames_stationary':True,'selected_street_text_overlap_cells':render['textOverlapCells']},
   'route':route_summary,'evidence':render['evidence'],'representative_frame':render['posterStats'],
   'validation':{'original_canvas_seam':original_seam,'decoded_gif_seam':seam,'all_source_positions_in_model_open_streets':True,'all_frames_one_geometry':True,'all_frames_zero_blocked_support':True,'all_frames_no_cursor_or_controls':True,'seam_method':'Closed model-open street circuit; periodic pre-roll; 1.25 s closing hold at initial point. No crossfade or position reset.'},
   'temporary_frames':{'count':frames,'location':'OS TemporaryDirectory outside repository','automatic_cleanup_on_success_or_failure':True},
   'reproduction':{'command':'python -B 19/scripts/export_media.py','render_module':'artwork.mjs + shared app.mjs/core.mjs/worker.mjs','ffmpeg':subprocess.run([exe,'-version'],capture_output=True,text=True).stdout.splitlines()[0],'immutable_inputs_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['core.mjs','worker.mjs','data/context-buildings.json','data/context-streets.json','data/context-metadata.json','research/soho/selected-extent.geojson','research/soho/selected-pois.json','research/soho/selected-311.json']}},'elapsed_seconds':round(time.monotonic()-started,2)
  }
  shutil.copyfile(candidate,ROOT/'day19_loop.gif');shutil.copyfile(poster_file,ROOT/'day19.png');(ROOT/'data/media_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'gif':manifest['gif'],'png':manifest['png'],'seam':seam,'temporary_directory_removed':not scratch.exists(),'elapsed_seconds':manifest['elapsed_seconds']},ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':encode()
