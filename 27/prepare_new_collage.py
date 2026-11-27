"""Three new cutouts from three previously unused Met CC0 paintings.
Only original scan-derived ink is retained; no generative reconstruction.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
DAY=Path(__file__).resolve().parent;S=DAY/'assets/sources';O=DAY/'assets/cutouts'

def cut(filename,object_id,ref,crop,poly,name,role,gain):
 meta=json.loads((S/f'met_{object_id}.json').read_text(encoding='utf8'))
 assert meta['isPublicDomain'] and meta['primaryImage']
 im=Image.open(S/filename).convert('RGB');sx=im.width/ref[0];sy=im.height/ref[1]
 box=tuple(round(c*(sx if i%2==0 else sy)) for i,c in enumerate(crop))
 part=im.crop(box);rgb=np.asarray(part,dtype=float);gray=part.convert('L')
 outline=Image.new('L',part.size,0)
 ImageDraw.Draw(outline).polygon([(round(x*sx-box[0]),round(y*sy-box[1])) for x,y in poly],fill=255)
 # Background removal follows scan contrast; alpha clears gaps between fine twigs.
 field=np.asarray(gray.filter(ImageFilter.GaussianBlur(25)),dtype=float)
 light=np.asarray(gray,dtype=float)
 density=np.clip((field-light-6)/65,0,1)
 density=1-(1-density)**gain
 alpha=density*np.asarray(outline)/255
 # Do not retain collector's red seals, including stamps printed across foliage.
 red=(rgb[:,:,0]>rgb[:,:,1]*1.22)&(rgb[:,:,0]>rgb[:,:,2]*1.22)
 alpha[red]=0;alpha[alpha<.09]=0
 if name=='new_zhao_single_pine':
  # Exclude a disconnected twig of the neighbouring pine, not part of this tree.
  hh,ww=alpha.shape;alpha[round(hh*.13):round(hh*.34),:round(ww*.18)]=0
 rgba=np.zeros((*alpha.shape,4),np.uint8);rgba[:,:,:3]=[39,55,44];rgba[:,:,3]=np.rint(alpha*255).astype(np.uint8)
 out=O/(name+'.png');Image.fromarray(rgba).save(out);outline.save(O/(name+'_contour_mask.png'))
 return dict(name=name,role=role,source=filename,object_id=object_id,title=meta['title'],artist=meta['artistDisplayName'],
  collection='The Metropolitan Museum of Art',accession=meta['accessionNumber'],record_url=meta['objectURL'],
  download_url=meta['primaryImage'],rights='CC0 / Met Open Access, official API isPublicDomain=true',
  policy_url='https://www.metmuseum.org/policies/image-resources',source_size=list(im.size),
  source_sha256=hashlib.sha256((S/filename).read_bytes()).hexdigest(),crop_source_pixels=box,
  contour_reference_size=ref,contour=poly,gain=gain,cutout=str(out.relative_to(DAY)),
  nonzero_alpha_pixels=int(np.count_nonzero(rgba[:,:,3])),alpha_bbox=list(Image.fromarray(rgba[:,:,3]).getbbox()))

def main():
 records=[]
 records.append(cut('zhao_mengfu_twin_pines.jpg',40508,(1600,388),(1200,10,1378,306),
  [(1280,12),(1300,13),(1320,22),(1342,30),(1348,46),(1335,53),(1355,66),
   (1368,80),(1350,85),(1332,76),(1315,73),(1310,90),(1320,100),(1325,118),
   (1350,127),(1368,145),(1363,166),(1342,167),(1337,157),(1310,152),
   (1295,137),(1295,165),(1305,200),(1313,240),(1300,273),(1280,294),
   (1255,299),(1253,280),(1267,251),(1268,218),(1260,180),(1256,151),
   (1255,116),(1260,90),(1248,70),(1232,70),(1220,80),(1208,85),(1201,72),
   (1215,52),(1241,39),(1252,23),(1270,20)],
  'new_zhao_single_pine','single tree / right-hand pine',2.3))
 records.append(cut('ni_zan_wind_trees.jpg',41154,(685,1100),(60,440,380,875),
  [(145,445),(170,450),(175,480),(190,480),(214,495),(222,510),(242,500),
   (252,480),(278,490),(285,520),(306,520),(320,502),(337,515),(355,510),
   (363,535),(375,560),(363,578),(346,590),(350,615),(333,635),(318,647),
   (306,660),(295,670),(286,710),(282,750),(270,800),(268,850),(252,865),
   (235,865),(214,857),(200,865),(181,870),(169,850),(153,853),(136,856),
   (117,860),(100,857),(90,836),(96,798),(91,768),(82,746),(62,734),
   (65,710),(89,704),(120,710),(129,733),(147,746),(157,771),(164,800),
   (175,839),(177,790),(160,736),(147,695),(135,660),(122,630),(111,603),
   (90,600),(82,580),(74,600),(63,574),(71,556),(89,555),(84,535),
   (75,515),(88,500),(100,498),(115,510),(128,490),(144,490),(134,475)],
  'new_ni_sparse_grove','sparse grove / foreground riverbank trees',2.0))
 records.append(cut('wang_meng_simple_retreat.jpg',39550,(559,1100),(230,585,397,750),
  [(234,610),(235,600),(247,596),(256,590),(267,594),(277,592),(285,599),
   (298,596),(311,609),(323,612),(338,606),(354,614),(360,625),(376,625),
   (386,633),(395,636),(391,650),(380,661),(369,669),(380,678),(390,691),
   (380,702),(367,704),(368,719),(361,734),(349,741),(338,743),(328,737),
   (318,742),(307,737),(292,742),(280,739),(269,730),(254,728),(246,715),
   (240,704),(234,687),(238,669),(230,659),(231,646),(240,634),(230,624)],
  'new_wang_dense_grove','dense grove / pine crowns above and right of hermitage',1.8))
 (O/'new_materials.json').write_text(json.dumps(records,indent=2),encoding='utf8')
 # Contact sheet is QA only; not a rectangular collage asset in the map.
 sheet=Image.new('RGB',(1500,850),'#dce2d5');d=ImageDraw.Draw(sheet)
 for i,r in enumerate(records):
  p=Image.open(DAY/r['cutout']);p.thumbnail((470,750));sheet.paste(p,(i*500+15,60),p)
  d.text((i*500+15,15),r['name'],fill='#35473c')
 sheet.save(DAY/'review/new_materials_contact_sheet.png')
 print([(r['name'],r['nonzero_alpha_pixels']) for r in records])
if __name__=='__main__':main()
