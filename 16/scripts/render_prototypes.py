"""Three local PNGs from reviewed records and downloaded geographic linework. No GIF/site."""
from pathlib import Path
import sys,json,csv,os
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps'))
os.environ['MPLCONFIGDIR']=str(ROOT/'.mpl-cache')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties
from matplotlib.colors import to_rgb
from shapely.geometry import shape
from shapely.ops import transform,unary_union
from pyproj import Transformer

OUT=ROOT/'outputs/prototypes';OUT.mkdir(parents=True,exist_ok=True)
BG='#F3EDE1';INK='#383832';MUTED='#77766E';FAINT='#A39F93';BASE='#B7B4AA'
DIVIDER='#DCD5C8';GRID='#E6DFD3'
CREDIT='Question by Chiun Heng Chou · Mapping by Ming Cao'
EYEBROW='DAY 16 / COLLABORATIVE MAP'
COLORS={'Mechanical & Equipment':'#C58B52','Congestion':'#B86D7C','Signal & Switch':'#9582AC',
 'Slippery Rails & Weather':'#5E9E98','Track & Infrastructure':'#85985D',
 'Staffing & Operations':'#6D87B3','External Incidents':'#A17B58','Other / Unknown':'#99968D'}
# Reuse these fixed positions for every future cause frame; geography stays aspect-equal.
C_MAP_RECT=(.025,.13,.585,.64)
C_LEGEND_POSITION=(.64,.328)
LABELS={'ACRL':'Atlantic City','MBPJ':'Main / Bergen / Port Jervis','MNE':'Morris & Essex',
        'MOBO':'Montclair–Boonton','NEC':'Northeast Corridor','NJCL':'North Jersey Coast',
        'PVL':'Pascack Valley','RVL':'Raritan Valley'}
plt.rcParams.update({'font.family':'Segoe UI','text.color':INK,'axes.facecolor':BG,
 'figure.facecolor':BG,'savefig.facecolor':BG,'font.size':11,'axes.unicode_minus':False})
SERIF=FontProperties(fname='C:/Windows/Fonts/georgia.ttf')
BOLD=FontProperties(fname='C:/Windows/Fonts/seguisb.ttf')
MONO=FontProperties(fname='C:/Windows/Fonts/consola.ttf')
records=list(csv.DictReader((ROOT/'data/processed/analysis_representatives.csv').open(encoding='utf-8-sig')))
counts={cat:Counter(r['affected_route'] for r in records if r['cause_category']==cat) for cat in COLORS}
raw_counts={cat:sum(int(r['eligible_notices']) for r in csv.DictReader((ROOT/'data/processed/cause_route_counts.csv').open(encoding='utf-8-sig')) if r['category']==cat) for cat in COLORS}
validation=json.loads((ROOT/'data/gis/gis_validation.json').read_text(encoding='utf-8'))
mapping=validation['route_mapping']
project=Transformer.from_crs(4326,32618,always_xy=True).transform
source=json.loads((ROOT/'data/gis/rail_lines.geojson').read_text(encoding='utf-8'))
geoms={f['properties']['LINE_NAME']:transform(project,shape(f['geometry'])).simplify(25) for f in source['features']}
groups={r:unary_union([geoms[n] for n in ns]) for r,ns in mapping.items()}
stsource=json.loads((ROOT/'data/gis/rail_stations.geojson').read_text(encoding='utf-8'))
stations={f['properties']['STATION_ID']:project(*f['geometry']['coordinates']) for f in stsource['features']}
all_geom=unary_union(list(geoms.values()));xmin,ymin,xmax,ymax=all_geom.bounds
EXTENT=(xmin-11000,xmax+15000,ymin-11000,ymax+16000)

def parts(g):
    if g.is_empty:return []
    if g.geom_type=='LineString':return [np.asarray(g.coords)]
    return [p for x in getattr(g,'geoms',[]) for p in parts(x)]
def txt(fig,x,y,s,size=11,color=INK,**kw):
    return fig.text(x,y,s,fontsize=size,color=color,**kw)
def rule(fig,y,x=.05,w=.9):
    fig.add_artist(Line2D([x,x+w],[y,y],transform=fig.transFigure,color=DIVIDER,lw=.65))
def map_axes(fig,rect,cat,hubs=False,endpoints=False,grid=False):
    ax=fig.add_axes(rect);ax.set_xlim(EXTENT[:2]);ax.set_ylim(EXTENT[2:]);ax.set_aspect('equal');ax.axis('off')
    if grid:
        # UTM grid is a geographic reference, not a density field.
        for x in np.arange(420000,620000,25000):ax.axvline(x,color=GRID,lw=.45,zorder=0)
        for y in np.arange(4350000,4650000,25000):ax.axhline(y,color=GRID,lw=.45,zorder=0)
    ax.add_collection(LineCollection([p for g in geoms.values() for p in parts(g)],colors=BASE,linewidths=.75,zorder=1))
    color=COLORS[cat] if cat is not None else MUTED
    if cat is None:
        # Overview is a non-quantitative service extent, not counts forced into 0–20.
        ax.add_collection(LineCollection([p for g in groups.values() for p in parts(g)],
          colors='#898C82',linewidths=1.6,zorder=2,capstyle='round',joinstyle='round'))
    # A notice belongs to one service group. Geometry is not an independent counting unit.
    # Shared routes are overpainted in ascending order: the top stroke shows max, never sum.
    for route,n in sorted((counts[cat] if cat is not None else {}).items(),key=lambda kv:(kv[1],kv[0])):
        if route not in groups:continue
        width=.65+4.1*n/20
        # Bake intensity against background and draw opaque: overlapping services cannot
        # accumulate opacity and look like a larger, invented segment-level count.
        intensity=.8+.2*n/20
        stroke=tuple((1-intensity)*b+intensity*c for b,c in zip(to_rgb(BG),to_rgb(color)))
        ax.add_collection(LineCollection(parts(groups[route]),colors=stroke,linewidths=width,
          zorder=2+n/100,capstyle='round',joinstyle='round'))
    if hubs:
        # At full extent, use a metro inset for the four tightly packed northern hubs.
        label_hub(ax,'Trenton',(-13,4),size=9)
    if endpoints:
        for name,offset in [('Port Jervis',(-5,9)),('Atlantic City',(7,-4)),('30th Street Station',(-7,-10))]:
            label_hub(ax,name,offset,size=8,display='Philadelphia · 30th St' if '30th' in name else name)
    return ax
def label_hub(ax,name,offset,size=8,display=None):
    x,y=stations[name];ax.scatter([x],[y],s=12,facecolors=BG,edgecolors=INK,linewidths=.7,zorder=20)
    ax.annotate(display or name,(x,y),xytext=offset,textcoords='offset points',fontsize=size,color=MUTED,
      ha='right' if offset[0]<0 else 'left',va='center',zorder=21)
def metro_inset(fig,rect,cat):
    ax=map_axes(fig,rect,cat);ax.set_aspect('equal');ax.set_xlim(564000,590000);ax.set_ylim(4502000,4525000)
    # Locations remain the downloaded GIS station coordinates; labels use leaders.
    for name,offset in [('New York Penn Station',(10,19)),('Secaucus Junction',(-13,14)),
                        ('Hoboken Terminal',(14,-12)),('Newark Penn Station',(-4,-15))]:
        x,y=stations[name]
        ax.scatter([x],[y],s=17,facecolors=BG,edgecolors=INK,linewidths=.8,zorder=20)
        ax.annotate(name,(x,y),xytext=offset,textcoords='offset points',fontsize=7.3,color=INK,
          ha='right' if offset[0]<0 else 'left',arrowprops={'arrowstyle':'-','color':FAINT,'lw':.5},zorder=21)
    for sp in ax.spines.values():sp.set_visible(True);sp.set_edgecolor(DIVIDER);sp.set_linewidth(.5)
    ax.axis('on');ax.set_xticks([]);ax.set_yticks([])
    return ax
def scalebar(ax):
    x=EXTENT[0]+10000;y=EXTENT[2]+6000
    ax.plot([x,x+25000],[y,y],color=MUTED,lw=1)
    for xx in (x,x+25000):ax.plot([xx,xx],[y-1200,y+1200],color=MUTED,lw=.7)
    ax.text(x+12500,y+3500,'25 km',ha='center',fontsize=7.5,color=MUTED)
    ax.text(EXTENT[1]-8000,EXTENT[3]-7000,'N ↑',ha='right',fontsize=9,color=MUTED)
def legend(fig,x,y,color,w=.29,note=True):
    txt(fig,x,y,'RETAINED NOTICES PER SERVICE GROUP',8.4,MUTED,fontproperties=MONO)
    for k,n in enumerate([1,5,10,20]):
        xx=x+k*w/3
        fig.add_artist(Line2D([xx,xx+.033],[y-.024,y-.024],transform=fig.transFigure,
          color=color,lw=.65+4.1*n/20,alpha=.8+.2*n/20,solid_capstyle='round'))
        txt(fig,xx+.0165,y-.048,str(n),8,MUTED,ha='center',fontproperties=MONO)
    if note:txt(fig,x,y-.077,'Same scale in every panel and frame.',8.4,MUTED)
def route_list(fig,x,y,cat,w=.3,row=.033,size=9):
    vals=counts[cat]
    for i,(route,label) in enumerate(LABELS.items()):
        yy=y-i*row;n=vals[route]
        txt(fig,x,yy,label,size,MUTED if not n else INK)
        txt(fig,x+w,yy,str(n),size,COLORS[cat] if n else FAINT,ha='right',fontproperties=MONO)
        fig.add_artist(Line2D([x,x+w*n/20],[yy-.010,yy-.010],transform=fig.transFigure,color=COLORS[cat],lw=1.5,alpha=.7))
def footer(fig,y=.055):
    rule(fig,y+.044)
    txt(fig,.05,y+.023,'Notices: NJ Transhit archive  ·  Geometry: NJ TRANSIT GIS Department',8.4,MUTED)
    txt(fig,.05,y+.005,'Affected rail services, not incident locations or delay probabilities. Shared geometry shows the highest service-group count.',7.8,MUTED)
    txt(fig,.05,y-.013,'Linked updates counted once; classifications provisional. Local internal review only · reuse permission unresolved.',7.8,MUTED)
def save(fig,name):
    fig.savefig(OUT/name,dpi=160);plt.close(fig)

def render_prototypes():
    # A — geographic overview with the quantitative sidebar and a genuine geographic inset.
    cat='Mechanical & Equipment'
    fig=plt.figure(figsize=(11,12))
    txt(fig,.05,.957,EYEBROW,9,MUTED,fontproperties=MONO)
    txt(fig,.05,.898,'Why Are the Trains Late?',30,fontproperties=SERIF)
    txt(fig,.05,.867,'An Atlas of NJ Transit Disruptions',15,MUTED,fontproperties=SERIF)
    txt(fig,.05,.835,CREDIT,10,MUTED)
    rule(fig,.81)
    txt(fig,.05,.78,'A / GEOGRAPHIC NETWORK',8.5,MUTED,fontproperties=MONO)
    txt(fig,.95,.78,'09–15 NOV 2026',8.5,MUTED,fontproperties=MONO,ha='right')
    ax=map_axes(fig,[.035,.185,.54,.57],cat,hubs=True,endpoints=True,grid=True);scalebar(ax)
    txt(fig,.65,.728,'01 / REPORTED CAUSE',8.5,COLORS[cat],fontproperties=MONO)
    txt(fig,.65,.69,'Mechanical',22,fontproperties=SERIF)
    txt(fig,.65,.66,'& Equipment',22,fontproperties=SERIF)
    txt(fig,.65,.595,str(sum(counts[cat].values())),42,COLORS[cat],fontproperties=MONO)
    txt(fig,.65,.567,f'retained notices · from {raw_counts[cat]} eligible',9,MUTED)
    route_list(fig,.65,.515,cat,w=.285,row=.031,size=8.7)
    legend(fig,.065,.145,COLORS[cat],w=.255,note=False)
    txt(fig,.65,.27,'METRO DETAIL / REFERENCE HUBS',7.5,MUTED,fontproperties=MONO)
    metro_inset(fig,[.65,.12,.23,.14],cat)
    txt(fig,.065,.165,'Service-group extent; individual branch may be unknown.',7.7,MUTED)
    footer(fig,.047);save(fig,'day16_geographic_network.png')

    # B — four highest-count direct causes after the same exclusions/update adjustment.
    cats=sorted(COLORS,key=lambda c:-sum(counts[c].values()))[:4]
    fig=plt.figure(figsize=(17,10))
    txt(fig,.04,.954,EYEBROW,9,MUTED,fontproperties=MONO)
    txt(fig,.04,.886,'Why Are the Trains Late?',33,fontproperties=SERIF)
    txt(fig,.04,.846,'An Atlas of NJ Transit Disruptions',15,MUTED,fontproperties=SERIF)
    txt(fig,.96,.892,'09–15 NOV 2026',10,MUTED,ha='right',fontproperties=MONO)
    txt(fig,.96,.856,CREDIT,9,MUTED,ha='right')
    rule(fig,.817,.04,.92)
    txt(fig,.04,.786,'B / SMALL MULTIPLES     Four leading direct-cause categories · identical geography and 0–20 count scale',9,MUTED)
    for i,cat in enumerate(cats):
        x=.04+i*.235
        if i: fig.add_artist(Line2D([x-.012,x-.012],[.19,.755],transform=fig.transFigure,color=DIVIDER,lw=.5))
        title=cat.replace(' & ',' &\n') if cat!='Congestion' else cat
        txt(fig,x,.741,f'{i+1:02d}',9,COLORS[cat],fontproperties=MONO)
        txt(fig,x+.033,.742,title,14,va='top',fontproperties=SERIF,linespacing=1.15)
        txt(fig,x,.637,f'{sum(counts[cat].values()):02d}',31,COLORS[cat],fontproperties=MONO)
        txt(fig,x+.055,.641,'retained notices',8.4,MUTED)
        ax=map_axes(fig,[x-.003,.20,.218,.405],cat)
        # Two endpoints are fixed reference points, not event markers.
        for hub in ('New York Penn Station','Trenton'):
            xx,yy=stations[hub];ax.scatter([xx],[yy],s=5,c=MUTED,zorder=20)
        peak,n=counts[cat].most_common(1)[0]
        txt(fig,x,.18,f'Largest service group: {peak} / {n}',8.5,COLORS[cat],fontproperties=MONO)
        txt(fig,x,.158,f'{raw_counts[cat]} eligible notices before update linking',8,MUTED)
    legend(fig,.05,.115,INK,w=.23,note=False)
    txt(fig,.40,.10,'Line width encodes count; each cause has its own color. Other causes remain in the analysis table.',8.5,MUTED)
    txt(fig,.40,.078,'All panels: same network extent, projection and numeric scale. Dots are reference hubs only.',8.5,MUTED)
    txt(fig,.04,.034,'NJ Transhit · NJ TRANSIT GIS Department  /  Affected services, not incident sites or delay probabilities.',8,MUTED)
    txt(fig,.04,.017,'Linked updates counted once. Shared geometry shows the highest service-group count; counts are never added on shared tracks.',8,MUTED)
    txt(fig,.96,.034,'PROVISIONAL · INTERNAL REVIEW ONLY',8,MUTED,ha='right',fontproperties=MONO)
    save(fig,'day16_small_multiples.png')

    # C — a static master frame. No animation is created.
    cat='Slippery Rails & Weather'
    fig=plt.figure(figsize=(12,12))
    txt(fig,.05,.957,EYEBROW,9,MUTED,fontproperties=MONO)
    txt(fig,.95,.957,'STATIC FRAME CONCEPT  /  04 OF 08',9,MUTED,ha='right',fontproperties=MONO)
    txt(fig,.05,.899,'Why Are the Trains Late?',31,fontproperties=SERIF)
    txt(fig,.05,.865,'An Atlas of NJ Transit Disruptions',15,MUTED,fontproperties=SERIF)
    txt(fig,.05,.829,CREDIT,10,MUTED)
    rule(fig,.803)
    txt(fig,.05,.781,'C / ANIMATED GIF FRAME CONCEPT',8.5,MUTED,fontproperties=MONO)
    ax=map_axes(fig,C_MAP_RECT,cat,hubs=True,endpoints=True,grid=True);scalebar(ax)
    txt(fig,.64,.718,'REPORTED DIRECT CAUSE',8.5,COLORS[cat],fontproperties=MONO)
    txt(fig,.64,.673,'Slippery Rails',24,fontproperties=SERIF)
    txt(fig,.64,.64,'& Weather',24,fontproperties=SERIF)
    txt(fig,.64,.608,'This window: slippery rail conditions.',9,MUTED)
    txt(fig,.64,.527,'24',56,COLORS[cat],fontproperties=MONO)
    txt(fig,.64,.497,'RETAINED NOTICES',9,COLORS[cat],fontproperties=MONO)
    txt(fig,.64,.468,'28 eligible notices · linked updates counted once',8.5,MUTED)
    txt(fig,.64,.425,'NOV 09 — NOV 15, 2026',11,fontproperties=MONO)
    txt(fig,.64,.392,'Morris & Essex accounts for 16 of 24.',10,INK)
    txt(fig,.64,.369,'Combined service group; branch unknown.',8.5,MUTED)
    legend(fig,*C_LEGEND_POSITION,COLORS[cat],w=.25,note=False)
    txt(fig,.64,.257,'METRO DETAIL / REFERENCE HUBS',7.5,MUTED,fontproperties=MONO)
    metro_inset(fig,[.64,.137,.24,.109],cat)
    # The fixed sequence rail is a layout cue, not a playback widget or actual GIF.
    for i,(c,col) in enumerate(COLORS.items()):
        xx=.05+i*.114
        fig.add_artist(Rectangle((xx,.119),.101,.004,transform=fig.transFigure,color=col,alpha=1 if c==cat else .28))
    txt(fig,.05,.099,'MECHANICAL  /  CONGESTION  /  SIGNAL  /  SLIPPERY RAILS  /  INFRASTRUCTURE  /  OPERATIONS  /  EXTERNAL  /  OTHER',7.2,MUTED,fontproperties=MONO)
    footer(fig,.039);save(fig,'day16_gif_frame_concept.png')
    print('Rendered 3 PNGs:',OUT)


if __name__ == "__main__":
    render_prototypes()
