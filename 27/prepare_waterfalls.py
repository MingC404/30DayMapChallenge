"""Actual painted watercourses: tight source-pixel contours, no invented water lines."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
DAY=Path(__file__).resolve().parent;S=DAY/'assets/sources';O=DAY/'assets/cutouts'

def extract(file,id,box,poly,name,role,used):
 m=json.loads((S/f'met_{id}.json').read_text(encoding='utf8'));assert m['isPublicDomain']
 source=Image.open(S/file).convert('RGB');part=source.crop(box)
 mask=Image.new('L',part.size,0);ImageDraw.Draw(mask).polygon([(x-box[0],y-box[1]) for x,y in poly],fill=255)
 gray=np.asarray(part.convert('L'),dtype=float)
 lo,hi=np.percentile(gray[np.array(mask)>0],[3,97]);tone=np.clip((gray-lo)/max(hi-lo,1),0,1)
 # Keep negative-space water opaque within its exact drawn course. Removing all
 # pale silk by luminance would erase the water itself. Surrounding silk is clear.
 dark=np.array([67,82,71]);light=np.array([244,244,234])
 rgb=(dark[None,None,:]*(1-tone[:,:,None])+light[None,None,:]*tone[:,:,None]).astype(np.uint8)
 rgba=np.dstack([rgb,np.asarray(mask)]);Image.fromarray(rgba).save(O/(name+'.png'))
 mask.save(O/(name+'_mask.png'))
 return dict(asset=name+'.png',source=file,title=m['title'],artist=m['artistDisplayName'],object_id=id,
  record_url=m['objectURL'],download_url=m['primaryImage'],rights='CC0 / Met Open Access',
  policy='https://www.metmuseum.org/policies/image-resources',source_size=list(source.size),crop_source_pixels=box,
  source_contour=poly,source_sha256=hashlib.sha256((S/file).read_bytes()).hexdigest(),role=role,used=used)

def main():
 records=[]
 records.append(extract('wen_zhengming_pine_waterfall.jpg',45778,(552,1170,688,1565),
  [(570,1175),(584,1188),(600,1210),(619,1230),(630,1260),(646,1300),(657,1345),
   (667,1400),(673,1460),(677,1515),(676,1555),(650,1558),(648,1500),(644,1455),
   (636,1400),(626,1350),(610,1300),(594,1265),(575,1230),(560,1210)],
  'waterfall_wen_main','lower two-ribbon vertical fall; main illustrative cascade',True))
 records.append(extract('wen_zhengming_pine_waterfall.jpg',45778,(553,924,616,1184),
  [(584,928),(594,930),(595,954),(587,979),(592,995),(607,1006),(610,1018),
   (595,1032),(582,1045),(575,1080),(572,1118),(574,1150),(581,1178),
   (570,1174),(562,1150),(560,1115),(562,1082),(566,1051),(577,1030),
   (588,1018),(585,1008),(574,1004),(578,993),(580,974),(580,950)],
  'waterfall_wen_far','upper narrow winding watercourse; distant illustrative cascade',True))
 records.append(extract('ma_yuan_waterfall.jpg',40086,(2630,2220,3005,2520),
  [(2960,2224),(2990,2230),(2960,2280),(2935,2320),(2890,2335),(2850,2385),
   (2800,2410),(2750,2455),(2700,2485),(2660,2510),(2645,2495),(2665,2455),
   (2700,2430),(2740,2410),(2780,2365),(2820,2335),(2855,2300),(2915,2275),
   (2920,2245)],'waterfall_ma_rapids','small rock-bound cascade/rapids alternative, not a tall vertical waterfall',False))
 (O/'waterfall_materials.json').write_text(json.dumps(records,indent=2),encoding='utf8')
 sheet=Image.new('RGB',(1100,700),'#cbd4c5');d=ImageDraw.Draw(sheet)
 for i,r in enumerate(records):
  im=Image.open(O/r['asset']);im.thumbnail((300,580));sheet.paste(im,(40+i*360,80),im);d.text((20+i*360,20),r['asset'],fill='#35473c')
 sheet.save(DAY/'review/waterfall_cutouts.png')
if __name__=='__main__':main()
