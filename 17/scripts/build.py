"""Rebuild and validate every final deliverable, from either the repo root or Day 17."""
from pathlib import Path
import subprocess,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent
def run(command):
 print('RUN', ' '.join(map(str,command)),flush=True)
 subprocess.run(list(map(str,command)),cwd=REPO,check=True)
for script in ['build_scene.py','build_html.py','export_media.py']:
 run([sys.executable,'-B',ROOT/'scripts'/script])
run([sys.executable,'-B',ROOT/'scripts/verify_sources.py'])
run(['node',ROOT/'scripts/verify_final.cjs'])
run([sys.executable,'-B',ROOT/'scripts/verify_media.py'])
print('All final Day 17 PNG / GIF / MP4 / HTML outputs rebuilt and verified.')
