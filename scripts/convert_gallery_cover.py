"""Lossless web PNG from an existing approved JPG; never alters source artwork."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'02/.deps'))
from PIL import Image
source,destination=map(Path,sys.argv[1:3])
destination.parent.mkdir(parents=True,exist_ok=True)
with Image.open(source) as im:
    im.convert('RGB').save(destination,format='PNG',optimize=True)
