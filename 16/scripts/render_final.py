"""Local-only 9-frame final GIF. Read existing representatives; no cleaning/network calls.

Opening and closing overview are pixel-identical. Fixed UTM extent, equal aspect,
map/inset positions and 0–20 cause-count scale; no automatic scale or zoom.
"""
from pathlib import Path
import json,csv,hashlib
from collections import Counter
import numpy as np
from PIL import Image
import render_prototypes as a
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from shapely.geometry import shape,box

ROOT=a.ROOT; OUT=ROOT/'outputs';FRAMES=OUT/'frames';FRAMES.mkdir(parents=True,exist_ok=True)
W=H=1440;DPI=120
ORDER=['Mechanical & Equipment','Congestion','Signal & Switch','Slippery Rails & Weather',
       'Track & Infrastructure','Staffing & Operations','External Incidents']
SEQUENCE=[None]+ORDER+[None]
DURATIONS=[2000]*8+[1500]
COUNTS=Counter(r['cause_category'] for r in a.records)
ELIGIBLE_COUNT=sum(r['include_notice_analysis']=='True' for r in csv.DictReader((ROOT/'data/processed/notices_reviewed.csv').open(encoding='utf-8-sig')))
SERVICE_GROUPS=len({r['affected_route'] for r in a.records})
SEVEN_CAUSE_COUNT=sum(COUNTS[c] for c in ORDER)
assert len(a.records)==234 and sum(COUNTS.values())==234
assert sum(COUNTS[c] for c in ORDER)+COUNTS['Other / Unknown']==len(a.records)
assert len({r['duplicate_update_group'] for r in a.records})==len(a.records)
assert max(n for c in ORDER for n in a.counts[c].values())<=20
BOUNDARIES=json.loads((ROOT/'data/gis/census_states/state_borders_clipped_utm.geojson').read_text(encoding='utf-8'))
border_geoms=[shape(f['geometry']) for f in BOUNDARIES['features']]
clip=box(a.EXTENT[0],a.EXTENT[2],a.EXTENT[1],a.EXTENT[3])
assert all(clip.covers(g) for g in border_geoms)
SUBTITLES={
 'Mechanical & Equipment':'Mechanical problems and equipment availability.',
 'Congestion':'Congestion is the directly reported cause.',
 'Signal & Switch':'Reported signal and switch issues.',
 'Slippery Rails & Weather':'This window: slippery rail conditions.',
 'Track & Infrastructure':'Track maintenance, wires and bridge operations.',
 'Staffing & Operations':'Crew, operations, connections and added stops.',
 'External Incidents':'Vehicles on tracks, police and medical assistance.'}
SHORT={'Mechanical & Equipment':'MECHANICAL','Congestion':'CONGESTION','Signal & Switch':'SIGNAL',
       'Slippery Rails & Weather':'SLIPPERY RAILS','Track & Infrastructure':'INFRASTRUCTURE',
       'Staffing & Operations':'OPERATIONS','External Incidents':'EXTERNAL'}

def add_borders(ax):
    layer=LineCollection([p for g in border_geoms for p in a.parts(g)],colors='#D8D1C5',linewidths=.55,zorder=.5,clip_on=True)
    ax.add_collection(layer);layer.set_clip_path(ax.patch)
    return layer

def cause_title(cat):
    if cat is None:return 'Network','Overview'
    return tuple(cat.split(' & ',1)[0:1]+['& '+cat.split(' & ',1)[1]]) if ' & ' in cat else (cat,'')

def render(cat):
    fig=a.plt.figure(figsize=(12,12),dpi=DPI)
    a.txt(fig,.05,.957,a.EYEBROW,10,a.MUTED,fontproperties=a.MONO)
    a.txt(fig,.95,.957,'NOVEMBER 9–15, 2026',10,a.MUTED,ha='right',fontproperties=a.MONO)
    a.txt(fig,.05,.899,'Why Are the Trains Late?',31,fontproperties=a.SERIF)
    a.txt(fig,.05,.865,'An Atlas of NJ Transit Disruptions',15,a.MUTED,fontproperties=a.SERIF)
    a.txt(fig,.05,.829,a.CREDIT,11,a.MUTED)
    a.rule(fig,.803)
    a.txt(fig,.05,.781,'AFFECTED RAIL SERVICES BY REPORTED DISRUPTION CAUSE',9.4,a.MUTED,fontproperties=a.MONO)
    ax=a.map_axes(fig,a.C_MAP_RECT,cat,hubs=True,endpoints=True,grid=True)
    border=add_borders(ax);a.scalebar(ax)
    color=a.COLORS[cat] if cat else a.MUTED
    a.txt(fig,.64,.718,'REPORTED DIRECT CAUSE' if cat else 'SEVEN-DAY SERVICE OVERVIEW',9.5,color,fontproperties=a.MONO)
    top,bottom=cause_title(cat)
    a.txt(fig,.64,.673,top,24,fontproperties=a.SERIF)
    a.txt(fig,.64,.64,bottom,24,fontproperties=a.SERIF)
    subtitle=SUBTITLES[cat] if cat else f'{SERVICE_GROUPS} service groups · same seven-day window.'
    a.txt(fig,.64,.608,subtitle,9.7,a.MUTED)
    n=COUNTS[cat] if cat else len(a.records)
    a.txt(fig,.64,.527,str(n),56,color,fontproperties=a.MONO)
    a.txt(fig,.64,.497,'RETAINED NOTICES',10,color,fontproperties=a.MONO)
    a.txt(fig,.64,.468,f'{n} of {len(a.records)} total · linked updates counted once' if cat else f'{ELIGIBLE_COUNT} eligible notices, after linking known updates',9.7,a.MUTED)
    a.txt(fig,.64,.425,'NOV 09 — NOV 15, 2026',11,fontproperties=a.MONO)
    if cat:
        peak,value=a.counts[cat].most_common(1)[0]
        a.txt(fig,.64,.392,f'{a.LABELS[peak]}: {value} notices.',10,a.INK)
        a.txt(fig,.64,.369,'Service-group extent; exact branch may be unknown.',9.3,a.MUTED)
    else:
        a.txt(fig,.64,.392,f'{SEVEN_CAUSE_COUNT} across seven causes + {COUNTS["Other / Unknown"]} Other / Unknown.',10,a.INK)
        a.txt(fig,.64,.369,'Overview lines are unweighted service extents.',9.3,a.MUTED)
    a.legend(fig,*a.C_LEGEND_POSITION,color,w=.25,note=False)
    a.txt(fig,.64,.257,'METRO DETAIL / REFERENCE HUBS',8.8,a.MUTED,fontproperties=a.MONO)
    inset=a.metro_inset(fig,[.64,.137,.24,.109],cat);ib=add_borders(inset)
    for i,c in enumerate(ORDER):
        xx=.05+i*.13
        fig.add_artist(Rectangle((xx,.113),.117,.004,transform=fig.transFigure,
          facecolor=a.COLORS[c],edgecolor='none',alpha=1 if c==cat else .3))
    a.txt(fig,.05,.095,'Fixed geography · 0–20 count scale for cause frames · Shared tracks show the highest service-group count, never a sum.',9.1,a.MUTED)
    a.rule(fig,.083)
    a.txt(fig,.05,.065,'Notices: NJ Transhit · Rail: NJ TRANSIT GIS Department · State borders: U.S. Census Bureau, 2025',9.3,a.MUTED)
    a.txt(fig,.05,.045,'Linked updates counted once. Highlighted lines indicate affected services,',9.8,a.INK)
    a.txt(fig,.05,.028,'not incident locations or delay probabilities.',9.8,a.INK)
    a.txt(fig,.95,.028,'LOCAL REVIEW · CLASSIFICATIONS PROVISIONAL',8.5,a.MUTED,ha='right',fontproperties=a.MONO)
    # Keep supporting text >=9 pt (10px at a 960px-wide normal web presentation).
    for label in list(fig.texts)+list(ax.texts)+list(inset.texts):
        label.set_fontsize(max(9,label.get_fontsize()))
    # Inspect actual Matplotlib transforms. These must remain identical in every frame.
    fig.canvas.draw()
    alignment={'main_xlim':list(ax.get_xlim()),'main_ylim':list(ax.get_ylim()),
      'main_position':list(ax.get_position().bounds),'main_affine':ax.transData.get_matrix().tolist(),
      'inset_xlim':list(inset.get_xlim()),'inset_ylim':list(inset.get_ylim()),
      'inset_position':list(inset.get_position().bounds),'inset_affine':inset.transData.get_matrix().tolist(),
      'borders_clip_on':border.get_clip_on() and ib.get_clip_on(),'border_zorder':border.get_zorder(),
      'cause_count_scale':[0,20]}
    renderer=fig.canvas.get_renderer()
    for label in list(fig.texts)+list(ax.texts)+list(inset.texts):
        bounds=label.get_window_extent(renderer)
        assert bounds.x0>=0 and bounds.x1<=W and bounds.y0>=0 and bounds.y1<=H, (label.get_text(),bounds)
    rgb=Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:,:,:3].copy())
    assert rgb.size==(W,H)
    a.plt.close(fig)
    return rgb,alignment

def main():
    frames=[];alignment=[]
    for i,cat in enumerate(SEQUENCE):
        rgb,check=render(cat)
        label='overview' if cat is None else SHORT[cat].lower().replace(' ','_')
        rgb.save(FRAMES/f'{i:02d}_{label}.png',optimize=True)
        frames.append(rgb);alignment.append(check)
    assert all(x==alignment[0] for x in alignment)
    assert frames[0].tobytes()==frames[-1].tobytes()
    frames[0].save(OUT/'day16_njt_disruptions.png',optimize=True)
    # One shared adaptive palette for all frames: stable type/basemap colors and no dithering.
    sample=Image.new('RGB',(960,960),a.BG)
    for i,im in enumerate(frames):
        sample.paste(im.resize((320,320),Image.Resampling.LANCZOS),((i%3)*320,(i//3)*320))
    # Reserve exact theme colors; downsampled palette training must not shift the
    # category number colors or the paper background to a nearby median-cut shade.
    protected=[a.BG,a.INK,a.MUTED,a.FAINT,a.BASE,a.DIVIDER,a.GRID,'#D8D1C5','#898C82']+list(a.COLORS.values())
    adaptive_n=256-len(protected)
    palette=sample.quantize(colors=adaptive_n,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    rgb_palette=palette.getpalette()[:adaptive_n*3]
    rgb_palette.extend(int(color[j:j+2],16) for color in protected for j in (1,3,5))
    palette.putpalette(rgb_palette)
    quantized=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
    quantized[0].save(OUT/'day16_njt_disruptions.gif',save_all=True,append_images=quantized[1:],
      duration=DURATIONS,loop=0,disposal=1,optimize=True)
    manifest={'canvas':[W,H],'projection':'EPSG:32618','fixed_map_extent_utm':list(a.EXTENT),
      'main_map_rectangle':list(a.C_MAP_RECT),'legend_position':list(a.C_LEGEND_POSITION),
      'count_scale':[0,20],'line_width_points':'0.65 + 4.1 * n / 20',
      'overview_line_width_points':1.6,'overview_quantitative_line_width':False,
      'total_retained_notices':len(a.records),'eligible_notices':ELIGIBLE_COUNT,'category_counts':dict(COUNTS),
      'frames':[{'cause':cat or 'Overview','duration_ms':ms,'count':COUNTS[cat] if cat else len(a.records)} for cat,ms in zip(SEQUENCE,DURATIONS)],
      'total_duration_ms':sum(DURATIONS),'loop':0,'transitions':'direct cuts; no movement or rescaling',
      'palette':'one 256-color shared palette, exact theme colors reserved; no dithering; delta-frame compression',
      'credit':a.CREDIT,'frame_alignment':alignment,'opening_closing_rgb_identical':True,
      'analysis_source':'data/processed/analysis_representatives.csv',
      'analysis_sha256':hashlib.sha256((ROOT/'data/processed/analysis_representatives.csv').read_bytes()).hexdigest(),
      'count_rule':'one representative per verified update group; one direct-cause category per representative; unknown included only in total',
      'minimum_supporting_font_points':9,'publication_status':'LOCAL ONLY; NJ Transhit reuse permission unresolved'}
    (OUT/'animation_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    # A normal 960px web-display review, not an alternate published cover.
    frames[0].resize((960,960),Image.Resampling.LANCZOS).save(OUT/'web_readability_preview_960.png')
    print(json.dumps({'counts':dict(COUNTS),'total':len(a.records),'duration_ms':sum(DURATIONS),
      'gif_bytes':(OUT/'day16_njt_disruptions.gif').stat().st_size,'png_bytes':(OUT/'day16_njt_disruptions.png').stat().st_size},indent=2))

if __name__=='__main__':main()
