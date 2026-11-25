"""Render the untouched sampled profile and its matching locator."""
from pathlib import Path
import json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import shape,box
from shapely.ops import transform,substring
from pyproj import Transformer
R=Path(__file__).resolve().parents[1];D=R/'data';O=R/'outputs';O.mkdir(exist_ok=True)
BG='#f4f0e7';INK='#383b39';MUTED='#74776e';BLUE='#187caa';WATER='#d9e4e2';GRID='#dcded5'
def main():
 a=np.genfromtxt(D/'samples.csv',delimiter=',',names=True);j=json.loads((D/'analysis.json').read_text());s=a['distance_m'];z=a['dem_elevation_m']
 font=FontProperties(fname='C:/Windows/Fonts/segoeui.ttf',size=12)
 fig=plt.figure(figsize=(1600/150,1200/150),dpi=150,facecolor=BG)
 ax=fig.add_axes([.10,.175,.815,.50],facecolor=BG);ax.set_xlim(0,1000);ax.set_ylim(10,38)
 for y in [15,20,25,30,35]:ax.axhline(y,color=GRID,lw=.6,zorder=0)
 ax.fill_between(s,z,10,color='#e2e4da',alpha=.6,lw=0)
 ax.plot(s,z,color=INK,lw=1.65,zorder=3)
 h=(s>=485)&(s<=530);ax.plot(s[h],z[h],color=BLUE,lw=3.2,zorder=4,solid_capstyle='round')
 # Exact median windows are visible as small dots below the drop annotation.
 u=j['upper_median_m'];l=j['lower_median_m'];ax.plot([545,545],[l,u],color=BLUE,lw=1)
 for v in [l,u]:ax.plot([538,552],[v,v],color=BLUE,lw=1)
 for side in ['left','right','top']:ax.spines[side].set_visible(False)
 ax.spines['bottom'].set_color(GRID);ax.set_xticks([0,250,500,750,1000]);ax.set_yticks([15,20,25,30,35]);ax.tick_params(axis='both',length=0,pad=10,colors=MUTED)
 for t in ax.get_xticklabels()+ax.get_yticklabels():t.set_fontproperties(font)
 ax.set_xlabel('Distance along river (m)  →  downstream',fontproperties=font,color=INK,labelpad=18)
 # Locator in real north-up UTM meters; same exact sampling line and interval.
 project=Transformer.from_crs(4326,26918,always_xy=True).transform
 route=transform(project,shape(json.loads((D/'sample_route.geojson').read_text())['geometry']));fall=substring(route,485,530)
 ma=fig.add_axes([.655,.535,.275,.25],facecolor=BG)
 xmin,ymin,xmax,ymax=route.bounds;cx=(xmin+xmax)/2;cy=(ymin+ymax)/2
 bounds=(cx-420,cy-335,cx+420,cy+335);clip=box(*bounds)
 for f in json.loads((D/'raw/3dhp_60.json').read_text())['features']:
  g=transform(project,shape(f['geometry'])).intersection(clip)
  polys=[g] if g.geom_type=='Polygon' else list(g.geoms) if hasattr(g,'geoms') else []
  for p in polys:
   if p.geom_type=='Polygon':ma.add_patch(Polygon(np.asarray(p.exterior.coords),facecolor=WATER,edgecolor='none'))
 x,y=route.xy;ma.plot(x,y,color=INK,lw=1.2);x,y=fall.xy;ma.plot(x,y,color=BLUE,lw=4,solid_capstyle='round')
 for d,label in [(0,'A'),(1000,'B')]:
  p=route.interpolate(d);ma.plot(p.x,p.y,'o',ms=3,color=INK);ma.text(p.x+17,p.y+14,label,fontproperties=font,color=INK)
 ma.set(xlim=(bounds[0],bounds[2]),ylim=(bounds[1],bounds[3]),aspect='equal');ma.axis('off')
 # North and scale, intentionally within the small map.
 ma.annotate('',xy=(bounds[2]-55,bounds[3]-65),xytext=(bounds[2]-55,bounds[3]-155),arrowprops={'arrowstyle':'-|>','color':INK,'lw':.8})
 ma.text(bounds[2]-55,bounds[3]-35,'N',fontproperties=font,ha='center',color=MUTED)
 ma.plot([bounds[0]+30,bounds[0]+130],[bounds[1]+45]*2,color=INK,lw=1.2);ma.text(bounds[0]+80,bounds[1]+65,'100 m',fontproperties=FontProperties(fname='C:/Windows/Fonts/segoeui.ttf',size=9),ha='center',color=MUTED)
 fig.canvas.draw();im=Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert('RGB');plt.close(fig);draw=ImageDraw.Draw(im)
 def text(x,y,t,size=24,color=INK,file='segoeui.ttf'):
  draw.text((x,y),t,font=ImageFont.truetype('C:/Windows/Fonts/'+file,round(size)),fill=color,anchor='ls')
 x=84;f=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',18)
 for c in 'DAY 26 / WATER':draw.text((x,82),c,font=f,fill=MUTED,anchor='ls');x+=f.getlength(c)+17.6*.08
 text(84,146,'Where the River Drops',44.8,file='georgia.ttf')
 text(84,187,'A profile of the Passaic River at Paterson Great Falls',19.2)
 text(160,370,'DEM elevation (m · NAVD88)',23)
 text(160,421,'A  /  UPSTREAM',19,color=MUTED)
 text(1280,963,'B  /  DOWNSTREAM',19,color=MUTED)
 text(670,360,'Great Falls',28,color=BLUE,file='georgia.ttf')
 text(670,391,'Same blue reach in both views',17,color=MUTED)
 # Leader stops at the top of the waterfall in profile coordinates.
 px=160+500/1000*1304;py=990-(u-10)/28*600
 draw.line([(789,408),(px,py-13)],fill=BLUE,width=2)
 text(937,721,f"{j['dem_estimate_drop_m']:.1f} m",42,color=BLUE,file='georgia.ttf')
 text(938,752,'DEM estimate',22,color=BLUE)
 text(938,784,'Medians just above and below the falls',17,color=MUTED)
 text(1054,268,'PATERSON, NEW JERSEY',18,color=MUTED)
 # Tiny dot legend links the map to the vertical step.
 draw.line([(1060,595),(1093,595)],fill=BLUE,width=5);text(1105,601,'Great Falls reach · 45 m',18,color=BLUE)
 draw.line([(84,1100),(1516,1100)],fill=GRID,width=1)
 text(84,1130,'USGS 3DHP river network · USGS 3DEP 0.61 m DEM (2017 lidar)',16,color=MUTED)
 text(84,1158,'1,000 m of river · sampled every 1 m · original DEM values, unsmoothed',16,color=MUTED)
 text(1516-ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17).getlength('Ming Cao'),1158,'Ming Cao',17,color=MUTED)
 path=O/'where_the_river_drops.png';im.save(path,dpi=(150,150))
 for width in [850,350]:im.resize((width,round(1200*width/1600)),Image.Resampling.LANCZOS).save(R/f'review/gallery_width_{width}.png')
 print(path)
if __name__=='__main__':main()
