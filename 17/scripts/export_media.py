"""Export one shared 12-second canvas composition to MP4 (30fps) and compact GIF (20fps).
Temporary PNG frames and palette are held outside the repository and removed on success.
"""
from pathlib import Path
import sys,os,tempfile,subprocess,shutil,json,re,hashlib
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent

def find_ffmpeg():
 if os.environ.get('FFMPEG_BINARY'):return os.environ['FFMPEG_BINARY']
 if shutil.which('ffmpeg'):return shutil.which('ffmpeg')
 try:import imageio_ffmpeg;return imageio_ffmpeg.get_ffmpeg_exe()
 except (ImportError, AttributeError):
  tools=Path(tempfile.gettempdir())/'day17-runtime'
  if tools.exists():sys.path.insert(0,str(tools));import imageio_ffmpeg;return imageio_ffmpeg.get_ffmpeg_exe()
  raise RuntimeError('Install imageio-ffmpeg==0.6.0 or put ffmpeg on PATH.')

def encode():
 exe=find_ffmpeg()
 def ff(args):
  p=subprocess.run([exe,'-hide_banner','-loglevel','error','-y',*args],cwd=REPO,text=True,capture_output=True)
  if p.returncode:raise RuntimeError(p.stderr)
 with tempfile.TemporaryDirectory(prefix='day17-render-') as scratch:
  subprocess.run(['node',str(ROOT/'scripts/render_frames.cjs'),scratch],cwd=REPO,check=True)
  frames=str(Path(scratch)/'frame_%04d.png');palette=str(Path(scratch)/'palette.png')
  ff(['-framerate','30','-i',frames,'-frames:v','360','-an','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'day17_loop.mp4')])
  vf='fps=20,scale=900:1080:flags=lanczos'
  ff(['-framerate','30','-i',frames,'-vf',vf+',palettegen=max_colors=128:stats_mode=diff','-frames:v','1',palette])
  ff(['-framerate','30','-i',frames,'-i',palette,'-lavfi',vf+'[x];[x][1:v]paletteuse=dither=none:diff_mode=rectangle','-frames:v','240','-loop','0','-gifflags','+transdiff',str(ROOT/'day17_loop.gif')])
  probe=subprocess.run([exe,'-hide_banner','-i',str(ROOT/'day17_loop.mp4'),'-f','null','-'],capture_output=True,text=True)
  if probe.returncode:raise RuntimeError(probe.stderr)
 from PIL import Image
 poster=Image.open(ROOT/'day17.png').convert('RGB');poster.save(ROOT/'day17.png',dpi=(300,300),optimize=True)
 im=Image.open(ROOT/'day17_loop.gif');duration=sum(im.seek(i) or im.info.get('duration',0) for i in range(im.n_frames));assert duration==12000
 report={'duration_seconds':12,'gif':{'size':list(im.size),'frames':im.n_frames,'duration_ms':duration,'bytes':(ROOT/'day17_loop.gif').stat().st_size,'palette_colors':128,'dither':'none'},'mp4':{'size':[1080,1296],'frames':360,'fps':30,'bytes':(ROOT/'day17_loop.mp4').stat().st_size,'codec':'H.264','pixel_format':'yuv420p','decode_ok':True},'png':{'size':[3000,3600],'mode':'continuous data snapshot at 0.15 s'},'seam_method':'Only non-dividing-period navigation halos fade over first/last 1.2 s. Original SIGSEQ is not rescaled. Two beam rotations are explicitly artistic 12-second turns.','ffmpeg_version':subprocess.run([exe,'-version'],capture_output=True,text=True).stdout.splitlines()[0]}
 (ROOT/'data/media_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':encode()


