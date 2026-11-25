"""Final static candidate: source-backed regions, inward feathering, short leaders."""
from pathlib import Path
import sys,json,argparse,hashlib
sys.dont_write_bytecode=True
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from pyproj import Transformer
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/tasting';OUT=ROOT/'outputs';LAY=OUT/'layers'
LAY.mkdir(parents=True,exist_ok=True)
T=json.loads((ROOT/'data/template.json').read_text());W,H=T['canvas'];S=3
PAPER='#f3eedf';LAND='#e3d1aa';BORDER='#d2c5a6';INK='#234d3c';MUTED='#71816b';VEIN='#f0e7cb'
DARK={'Green':'#386b50','Black':'#a14b34','Oolong':'#327e8b','Yellow':'#b18b22','White':'#8b86b3','Dark':'#634b3e','Scented green':'#b54f79'}
PALE={'Green':'#a8c69b','Black':'#d6a389','Oolong':'#9ec7c5','Yellow':'#e0c777','White':'#c5bbdb','Dark':'#baa38e','Scented green':'#d8a5bb'}
PALE['Mixed']='#c9bda5'
tx=Transformer.from_crs(4326,'+proj=merc +lon_0=108 +datum=WGS84 +units=m',always_xy=True);cx,cy=tx.transform(108,23)
def xy(lon,lat):
 x,y=tx.transform(lon,lat);return 800+(np.asarray(x)-cx)*.00017,650-(np.asarray(y)-cy)*.00017
def raster_geometry(g):
 mask=Image.new('L',(W*S,H*S));d=ImageDraw.Draw(mask)
 for rings in ([g['coordinates']] if g['type']=='Polygon' else g['coordinates']):
  for i,ring in enumerate(rings):
   a=np.asarray(ring);x,y=xy(a[:,0],np.clip(a[:,1],-80,80));d.polygon(list(zip(x*S,y*S)),fill=255 if i==0 else 0)
 return mask
land_geo=json.loads((DATA/'raw/ne_50m_admin_0_countries.geojson').read_text(encoding='utf8'))
fig=plt.figure(figsize=(W/150,H/150),dpi=150,facecolor=PAPER);ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,W);ax.set_ylim(H,0);ax.set_aspect('equal');ax.axis('off')
landmask=Image.new('L',(W*S,H*S))
for f in land_geo['features']:
 g=f['geometry'];polys=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
 visible=False
 for rings in polys:
  a=np.array(rings[0])
  if a[:,0].max()<60 or a[:,0].min()>155 or a[:,1].max()<-10:continue
  x,y=xy(a[:,0],np.clip(a[:,1],-80,80));ax.add_patch(Polygon(np.column_stack([x,y]),facecolor=LAND,edgecolor=BORDER,lw=.35));visible=True
 if visible:landmask=ImageChops.lighter(landmask,raster_geometry(g))
fig.canvas.draw();base=Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert('RGBA');plt.close(fig)
base.save(LAY/'basemap.png',dpi=(T['dpi'],T['dpi']))
# Keep coastline clipping at high resolution, then enforce it again at export resolution.
lm=landmask.resize((W,H),Image.Resampling.LANCZOS)
lm=np.asarray(lm)>192
regions=json.loads((DATA/'final_regions.geojson').read_text(encoding='utf8'))['features']
audit=json.loads((DATA/'final_region_audit.json').read_text(encoding='utf8'));rows=[r for r in audit if r['shown'] and r['kind']=='regional_tea'];drinks=[r for r in audit if r['shown'] and r['kind']=='tea_drink']
area_layers={c:Image.new('RGBA',(W,H)) for c in PALE};coverage=[];region_masks={}
for f in regions:
 p=f['properties'];raw=raster_geometry(f['geometry'])
 # Feather only inwards: multiply the blur by the original region and land masks.
 alpha=ImageChops.multiply(raw.filter(ImageFilter.GaussianBlur(1.1*S)),raw)
 alpha=ImageChops.multiply(alpha,landmask).resize((W,H),Image.Resampling.LANCZOS)
 aa=np.asarray(alpha).copy();inside=np.asarray(raw.resize((W,H),Image.Resampling.LANCZOS))>128;aa[~lm | ~inside]=0
 rgba=Image.new('RGBA',(W,H),PALE[p['tea_class']]);rgba.putalpha(Image.fromarray(aa))
 rgba.save(LAY/('region_'+p['id']+'.png'))
 region_masks[p['display_region']]=aa>64
 area_layers[p['tea_class']]=Image.alpha_composite(area_layers[p['tea_class']],rgba)
 coverage.append(dict(id=p['id'],visible_pixels=int((aa>64).sum()),non_land_pixels=int(((aa>0)&~lm).sum())))
shading=Image.new('RGBA',(W,H))
for c,layer in area_layers.items():
 layer.save(LAY/('regions_'+c.lower().replace(' ','_')+'.png'));shading=Image.alpha_composite(shading,layer)
shading.save(LAY/'regions.png');Image.fromarray(lm.astype('uint8')*255).save(LAY/'land_mask.png')
common=Image.new('RGBA',(W*S,H*S));draw=ImageDraw.Draw(common);texts=[];leaders=[];anchors=[];badges=[]
def font(role):return ImageFont.truetype('C:/Windows/Fonts/'+T['fonts'][role],round(T['sizes'][role]*S))
def text(x,y,s,role='caption',color=INK,id=None):
 f=font(role);bb=[v/S for v in draw.textbbox((x*S,y*S),s,font=f,anchor='ls')]
 assert 0<=bb[0]<bb[2]<=W and 0<=bb[1]<bb[3]<=H,(s,bb)
 draw.text((x*S,y*S),s,font=f,fill=color,anchor='ls');texts.append(dict(id=id,text=s,role=role,box=bb))
x,y=T['anchors']['day'];f=font('day')
for ch in 'DAY 23 / SENSES: TASTE':draw.text((x*S,y*S),ch,font=f,fill=MUTED,anchor='ls');x+=f.getlength(ch)/S+T['sizes']['day']*.08
text(*T['anchors']['title'],'A Tasting Map of Tea','title')
text(*T['anchors']['subtitle'],'Selected regional teas and tea drinks across Asia','subtitle',MUTED)
for lon,lat,label in [(75,18,'INDIA'),(107,40,'CHINA'),(137,41,'JAPAN'),(101,16,'THAILAND'),(121,13,'PHILIPPINES'),(113,-2,'INDONESIA')]:text(*xy(lon,lat),label,'source','#9b9d81')
positions={'assam':(575,490),'darjeeling':(245,620),'yame':(1275,470),'nilgiri':(295,855),'uji-matcha':(1380,340),'cn-2662':(1090,470),'cn-2666':(830,350),'cn-2668':(642,596),'cn-2710':(1080,560),'cn-2663':(1080,650),'cn-2705':(776,615),'cn-2721':(874,615),'tw-beauty':(1135,752)}
positions.update({'assam':(540,535),'darjeeling':(300,615),'cn-2662':(1030,479),'cn-2710':(1025,557),'cn-2663':(990,625),'tw-beauty':(1110,679),'nuwara-eliya':(345,925),'shan-tuyet':(666,725)})
names={'cn-2662':'Anji Bai Cha','cn-2666':'Huoshan Huang Ya','cn-2663':'Anxi Tieguanyin','cn-2705':'Hengxian jasmine tea','cn-2710':'Fuding white tea','cn-2721':'Yingde black tea'}
DIRECT={'cn-2668','cn-2705','cn-2721'}
NO_LEADERS={'assam','darjeeling','cn-2662','cn-2710','cn-2663','tw-beauty'}
DIRECT.update(NO_LEADERS)
wrapped_names={'cn-2668':["Pu'er (ripe)"],'cn-2705':['Hengxian','jasmine tea'],'cn-2721':['Yingde','black tea']}
wrapped_notes={'cn-2668':['Mellow,','sweet'],'cn-2705':['Jasmine'],'cn-2721':['Sweet']}
wrapped_names.update({'assam':['Assam black tea'],'darjeeling':['Darjeeling tea'],'cn-2662':['Anji Bai Cha'],'cn-2710':['Fuding white tea'],'cn-2663':['Anxi Tieguanyin'],'tw-beauty':['Oriental Beauty']})
wrapped_notes.update({'assam':['Malty aroma'],'darjeeling':['Muscat grape','aroma'],'cn-2662':['Brisk, mellow'],'cn-2710':['Floral'],'cn-2663':['Fruity'],'tw-beauty':['Honeyed']})
placements=[]
class_labels={c:Image.new('RGBA',(W*S,H*S)) for c in DARK}
ITEMS=LAY/'items';ITEMS.mkdir(exist_ok=True)
class MirrorDraw:
 """Record each item separately while leaving the approved class composite intact."""
 def __init__(self,*targets):self.targets=targets
 def __getattr__(self,name):
  def call(*args,**kwargs):
   result=None
   for target in self.targets:result=getattr(target,name)(*args,**kwargs)
   return result
  return call
def save_item(id,layer):layer.resize((W,H),Image.Resampling.LANCZOS).save(ITEMS/(id+'.png'))
def leaf(draw,x,y,color,scale=.30):
 angle=np.deg2rad(-27)
 def p(u,v):return ((x+scale*(u*np.cos(angle)-v*np.sin(angle)))*S,(y+scale*(u*np.sin(angle)+v*np.cos(angle)))*S)
 t=np.linspace(0,1,65);u=13*np.sin(np.pi*t);v=25-50*t
 points=[p(a,b) for a,b in zip(u,v)]+[p(-a,b) for a,b in zip(u[::-1],v[::-1])]
 draw.polygon(points,fill=color);draw.line([p(0,20),p(0,-20)],fill=VEIN,width=2)
def cup(draw,x,y):
 # An open vessel, handle and saucer differ from a slender solid leaf.
 draw.arc(((x+6)*S,(y-6)*S,(x+15)*S,(y+5)*S),-95,100,fill=INK,width=3*S)
 draw.rounded_rectangle(((x-10)*S,(y-9)*S,(x+9)*S,(y+8)*S),radius=3*S,fill=PAPER,outline=INK,width=2*S)
 draw.line(((x-8)*S,(y-5)*S,(x+7)*S,(y-5)*S),fill='#b68c5c',width=3*S)
 draw.line(((x-13)*S,(y+12)*S,(x+13)*S,(y+12)*S),fill=INK,width=2*S)
for category in DARK:
 for r in [r for r in rows if r['tea_class']==category]:
  item=Image.new('RGBA',(W*S,H*S));draw=MirrorDraw(ImageDraw.Draw(class_labels[category]),ImageDraw.Draw(item))
  id=r['id'];lx,ly=positions[id];gx,gy=xy(*r['coordinate'])
  start=len(texts)
  if id in DIRECT:
   yy=ly
   for s in wrapped_names[id]:text(lx,yy,s,'caption' if id not in NO_LEADERS else 'day',id=id);yy+=20
   for s in wrapped_notes[id]:text(lx,yy+3,s,'subtitle',id=id);yy+=23
   if id in NO_LEADERS:
    origin={'assam':'Assam','darjeeling':'Darjeeling / West Bengal','cn-2662':'Anji / Zhejiang','cn-2710':'Fuding / Fujian','cn-2663':'Anxi / Fujian','tw-beauty':'Emei / Northern Taiwan'}[id]
    text(lx,yy+3,origin,'source',MUTED,id=id)
  else:
   text(lx,ly,names.get(id,r['tea']),'day',id=id)
   if r['flavor']:text(lx,ly+28,r['flavor'],'subtitle',id=id)
   if id=='shan-tuyet':text(lx,ly+25,'Hoang Su Phi / N. Vietnam','source',MUTED,id=id)
   elif id=='nuwara-eliya':text(lx,ly+51,'Nuwara Eliya / Central Province','source',MUTED,id=id)
   else:text(lx,ly+51,r['original_place']+' · '+r['display_region'],'source',MUTED,id=id)
  leaf(draw,lx-15,ly-7,DARK[category]);badges.append(dict(id=id,center=[lx-15,ly-7],scale=.30))
  bb=np.array([min(t['box'][0] for t in texts[start:]),min(t['box'][1] for t in texts[start:]),max(t['box'][2] for t in texts[start:]),max(t['box'][3] for t in texts[start:])])
  xx1,yy1,xx2,yy2=map(int,bb)
  mask=region_masks[r['display_region']]
  ratio=float(mask[max(0,yy1):min(H,yy2+1),max(0,xx1):min(W,xx2+1)].mean())
  placements.append(dict(id=id,display_region=r['display_region'],direct=id in DIRECT,label_bbox=bb.tolist(),bbox_region_coverage=ratio))
  if id in DIRECT:save_item(id,item);continue
  # Closest label-block edge keeps the geographic-to-label connection short.
  target=np.array([np.clip(gx,bb[0]-11,bb[2]+11),np.clip(gy,bb[1]-11,bb[3]+11)])
  if bb[0]-11<gx<bb[2]+11 and bb[1]-11<gy<bb[3]+11:
   choices=[(abs(gx-bb[0]+11),np.array([bb[0]-11,gy])),(abs(gx-bb[2]-11),np.array([bb[2]+11,gy])),(abs(gy-bb[1]+11),np.array([gx,bb[1]-11])),(abs(gy-bb[3]-11),np.array([gx,bb[3]+11]))];target=min(choices,key=lambda a:a[0])[1]
  points=[np.array([gx,gy]),target]
  if id=='tw-beauty':points=[np.array([gx,gy]),np.array([1073.,620.]),np.array([1073.,735.]),target]
  radius=1.8
  direction=(points[1]-points[0])/np.linalg.norm(points[1]-points[0])
  drawn=[points[0]+direction*radius]+points[1:]
  draw.line([tuple(p*S) for p in drawn],fill=MUTED,width=2)
  bounds=((gx-radius)*S,(gy-radius)*S,(gx+radius)*S,(gy+radius)*S)
  draw.ellipse(bounds,fill=DARK[category])
  leaders.append(dict(id=id,points=[p.tolist() for p in points],length_px=float(sum(np.linalg.norm(b-a) for a,b in zip(points,points[1:])))))
  anchors.append(dict(id=id,lon=r['coordinate'][0],lat=r['coordinate'][1],pixel=[float(gx),float(gy)],radius=radius,treatment=r['treatment']))
  save_item(id,item)
drink_layer=Image.new('RGBA',(W*S,H*S));draw=ImageDraw.Draw(drink_layer);drink_symbols=[]
for r in drinks:
 item=Image.new('RGBA',(W*S,H*S));draw=MirrorDraw(ImageDraw.Draw(drink_layer),ImageDraw.Draw(item))
 id=r['id'];gx,gy=xy(*r['coordinate']);cup(draw,gx,gy);drink_symbols.append(dict(id=id,pixel=[float(gx),float(gy)],lon=r['coordinate'][0],lat=r['coordinate'][1],symbol='cup',shaded=False))
 if id=='masala-chiya':
  text(230,504,'Masala chiya','day',id=id);text(230,532,'Milk, sugar,','subtitle',id=id);text(230,555,'spices','subtitle',id=id);text(230,579,'Kathmandu / Nepal','source',MUTED,id=id)
 else:
  text(690,825,'Thai iced tea','day',id=id);text(690,853,'Milk, sugar, ice','subtitle',id=id);text(690,877,'Cha yen / Bangkok','source',MUTED,id=id)
 save_item(id,item)
drink_layer=drink_layer.resize((W,H),Image.Resampling.LANCZOS);drink_layer.save(LAY/'labels_tea_drinks.png')
draw=ImageDraw.Draw(common)
text(84,1015,'Regional teas','day')
for i,c in enumerate(DARK):
 x=84+(i%4)*175;y=1050+(i//4)*34
 draw.ellipse((x*S,(y-12)*S,(x+14)*S,(y+2)*S),fill=PALE[c]);leaf(draw,x+7,y-5,DARK[c],.25);text(x+26,y,c)
text(850,1015,'Tea drinks','day');cup(draw,860,1040)
text(886,1048,'Cups mark drinking examples.','caption',MUTED)
text(850,1078,'Shading groups selected teas by broader region.','caption',MUTED)
draw.rectangle((824*S,1094*S,839*S,1107*S),fill=PALE['Mixed'])
text(850,1106,'Neutral shading: multiple tea types in one region.','caption',MUTED)
text(84,T['attribution_baseline'],'Sources: official tea records, tourism sources, GIZ, MICHELIN | Natural Earth / GeoNames / geoBoundaries. Details: README.','source',MUTED)
text(84,T['author_baseline'],'Ming Cao','author')
static=common.resize((W,H),Image.Resampling.LANCZOS);static.save(LAY/'labels_static.png')
labels=Image.new('RGBA',(W,H))
for c,layer in class_labels.items():
 layer=layer.resize((W,H),Image.Resampling.LANCZOS);layer.save(LAY/('labels_'+c.lower().replace(' ','_')+'.png'));labels=Image.alpha_composite(labels,layer)
labels=Image.alpha_composite(labels,drink_layer)
for placement in placements:
 if placement['direct']:
  row=next(r for r in rows if r['id']==placement['id'])
  channel=np.asarray(Image.open(LAY/('labels_'+row['tea_class'].lower().replace(' ','_')+'.png')))[:,:,3]>64
  x1,y1,x2,y2=map(int,placement['label_bbox']);window=np.zeros_like(channel);window[y1:y2+1,x1:x2+1]=True;ink=channel & window
  placement['glyph_region_coverage']=float(region_masks[placement['display_region']][ink].mean())
labels=Image.alpha_composite(labels,static);labels.save(LAY/'labels.png')
final=Image.alpha_composite(Image.alpha_composite(base,shading),labels).convert('RGB');path=OUT/'day23_a_tasting_map_of_tea.png';final.save(path,dpi=(T['dpi'],T['dpi']))
if '--review' in sys.argv:
 for width in [862,350]:final.resize((width,round(H*width/W)),Image.Resampling.LANCZOS).save(ROOT/f'review/final_{width}.png')
metadata=dict(template=T,canvas=[W,H],projection='Mercator; lon_0=108; map center (108,23) at pixel (800,650); 0.00017 px/metre',texts=texts,anchors=anchors,badges=badges,leaders=leaders,placements=placements,palette=dict(paper=PAPER,land=LAND,leaves=DARK,regions=PALE),coverage=coverage,feather='Gaussian 1.1 px, multiplied by original display region and land mask',display_regions=len(regions),tea_count=len(rows),direct_label_count=sum(p['direct'] for p in placements),input_sha256={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [DATA/'final_regions.geojson',DATA/'final_region_audit.json',ROOT/'data/template.json',DATA/'raw/ne_50m_admin_0_countries.geojson']},png_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
metadata.update(tea_drinks=drink_symbols,drink_count=len(drinks),requested_leader_free_ids=sorted(NO_LEADERS))
(ROOT/'review/final_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf8');print(path)
