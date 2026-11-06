"""Optional reproduction of the original affine fit; does not overwrite assets.

The final renderer does not call this script. It uses the frozen parameters.
"""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02/.deps'))
import numpy as np
from pyproj import Transformer

def reproduce():
    points=json.loads((ROOT/'06/assets/shoreline_control_points.json').read_text())
    fitted=[p for p in points if p['role']=='fit']
    projection=Transformer.from_crs(4326,32618,always_xy=True)
    design=np.array([[p['pixel_x'],p['pixel_y'],1] for p in fitted],float)
    target=np.array([projection.transform(p['lon'],p['lat']) for p in fitted])
    matrix=np.eye(3)
    matrix[:2,:]=np.linalg.lstsq(design,target,rcond=None)[0].T
    return matrix

if __name__=='__main__':
    print(json.dumps(dict(pixel_to_utm=reproduce().tolist(),writes_files=False),indent=2))
