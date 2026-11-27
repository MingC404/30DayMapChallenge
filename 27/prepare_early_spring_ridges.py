"""Extract three distinct rock/treetop details from the NPM CC BY 4.0 file."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'assets/sources/guo_xi_early_spring_6mp.jpg'
OUT=ROOT/'assets/cutouts'

DETAILS=[
    dict(name='early_spring_main_ridge',role='Main summit crag and its sparse pines',
         crop=[370,50,620,300],opacity=.72,
         polygon=[[373,53],[562,53],[576,113],[615,149],[617,222],
                  [602,284],[448,297],[377,262]]),
    dict(name='early_spring_side_ridge',role='Left upper outcrop, rock rim and sparse treetops',
         crop=[120,270,355,450],opacity=.64,
         polygon=[[123,273],[320,273],[321,345],[352,390],[352,429],[313,447],[130,443]]),
    dict(name='early_spring_far_ridge',role='Upper right crag with a few thin skyline pines',
         crop=[587,135,740,285],opacity=.30,
         polygon=[[590,138],[737,138],[737,260],[700,282],[594,267]])]


def main():
    source=Image.open(SOURCE).convert('RGB');sx=source.width/900;sy=source.height/1287
    records=[]
    for detail in DETAILS:
        box=tuple(round(v*(sx if i%2==0 else sy)) for i,v in enumerate(detail['crop']))
        part=source.crop(box);gray=part.convert('L')
        # Local bright silk estimate removes ground while retaining darker ink,
        # including fine treetops. A hand outline excludes unrelated painting.
        pixels=np.asarray(gray,dtype=float)
        # Estimate silk per scanline, suppressing horizontal weave/scan bands
        # instead of turning those bands into a rectangular gray collage ground.
        background=np.percentile(pixels,85,axis=1)[:,None]
        ink=np.maximum(0,background-pixels-13)
        alpha=np.clip(ink/49,0,1)**.85*detail['opacity']
        mask=Image.new('L',part.size)
        ImageDraw.Draw(mask).polygon([(round(x*sx)-box[0],round(y*sy)-box[1]) for x,y in detail['polygon']],fill=255)
        mask=mask.filter(ImageFilter.GaussianBlur(3))
        yy=np.arange(part.height)[:,None]/part.height
        foot=np.clip((1-yy)/.25,0,1);foot=foot*foot*(3-2*foot)
        alpha*=np.asarray(mask)/255*foot
        rgba=np.zeros((part.height,part.width,4),dtype='uint8')
        rgba[:,:,:3]=[62,75,64];rgba[:,:,3]=np.rint(alpha*255).astype('uint8')
        Image.fromarray(rgba).save(OUT/(detail['name']+'.png'))
        Image.fromarray(rgba[:,:,3]).save(OUT/(detail['name']+'_mask.png'))
        records.append(dict(**detail,source_file=str(SOURCE.relative_to(ROOT)),source_size=list(source.size),
                            crop_source_pixels=list(box),reference_size=[900,1287],
                            output='assets/cutouts/'+detail['name']+'.png',
                            license='CC BY 4.0',source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                            processing='Hand outline; local silk subtraction; gray-green ink; rock feet fade into slope.'))
    (OUT/'early_spring_ridge_materials.json').write_text(json.dumps(records,indent=2),encoding='utf8')
    print('Extracted three distinct ridge/treetop RGBA assets.')


if __name__=='__main__':main()
