"""Verify final encoded GIF, static-region pixels, totals, clipping and source hashes."""
from pathlib import Path
import csv,json,hashlib
from collections import Counter
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import render_prototypes as a
from shapely.geometry import shape,box
ROOT=a.ROOT;OUT=ROOT/'outputs'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rect_mask(mask,rect):
    x,y,w,h=rect
    left=max(0,int(x*1440)-3);right=min(1440,int((x+w)*1440)+4)
    top=max(0,int((1-y-h)*1440)-3);bottom=min(1440,int((1-y)*1440)+4)
    mask[top:bottom,left:right]=False

def main():
    m=json.loads((OUT/'animation_manifest.json').read_text(encoding='utf-8'))
    records=list(csv.DictReader((ROOT/m['analysis_source']).open(encoding='utf-8-sig')))
    assert digest(ROOT/m['analysis_source'])==m['analysis_sha256']
    counts=Counter(r['cause_category'] for r in records)
    assert dict(counts)==m['category_counts'] and len(records)==234
    assert len({r['duplicate_update_group'] for r in records})==234
    assert counts['Other / Unknown']==2
    assert sum(n for c,n in counts.items() if c!='Other / Unknown')==232
    borders=json.loads((ROOT/'data/gis/census_states/state_borders_clipped_utm.geojson').read_text(encoding='utf-8'))
    bbox=box(a.EXTENT[0],a.EXTENT[2],a.EXTENT[1],a.EXTENT[3])
    assert all(bbox.covers(shape(f['geometry'])) for f in borders['features'])
    assert all(shape(f['geometry']).intersection(bbox.boundary).length<.01 for f in borders['features'])
    assert len(borders['features'])==3
    assert all(x==m['frame_alignment'][0] for x in m['frame_alignment'])
    assert m['frame_alignment'][0]['borders_clip_on'] and m['frame_alignment'][0]['border_zorder']<1
    with Image.open(OUT/'day16_njt_disruptions.gif') as gif:
        assert gif.n_frames==9 and gif.size==(1440,1440) and gif.info['loop']==0
        decoded=[];durations=[]
        for i in range(gif.n_frames):
            gif.seek(i);decoded.append(np.asarray(gif.convert('RGB')).copy());durations.append(gif.info['duration'])
    assert durations==[f['duration_ms'] for f in m['frames']]
    assert sum(durations)==17500
    assert np.array_equal(decoded[0],decoded[-1])
    # Static header, source/caveat, positions and all pixels outside the dynamic panels
    # must be identical AFTER GIF palette encoding and disposal/compositing.
    static=np.ones((1440,1440),dtype=bool)
    rect_mask(static,m['frame_alignment'][0]['main_position'])
    rect_mask(static,m['frame_alignment'][0]['inset_position'])
    rect_mask(static,(.62,.25,.38,.49)) # changing sidebar and count-legend color
    rect_mask(static,(.045,.11,.91,.009)) # category sequence strip
    differences=[int(np.count_nonzero(np.any(frame!=decoded[0],axis=2)&static)) for frame in decoded]
    assert max(differences)==0,differences
    cover=np.asarray(Image.open(OUT/'day16_njt_disruptions.png').convert('RGB'))
    assert cover.shape==(1440,1440,3)
    assert np.array_equal(cover,np.asarray(Image.open(OUT/'frames/00_overview.png').convert('RGB')))
    quantization_mae=float(np.abs(cover.astype(float)-decoded[0].astype(float)).mean())
    assert quantization_mae<2
    color_errors={}
    for i,f in enumerate(m['frames']):
        if f['cause']=='Overview':continue
        target=np.array(tuple(int(a.COLORS[f['cause']][j:j+2],16) for j in (1,3,5)))
        # Sidebar contains actual unblended category color in the main number.
        crop=decoded[i][int(.43*1440):int(.5*1440),int(.64*1440):int(.88*1440)]
        error=float(np.linalg.norm(crop.astype(float)-target,axis=2).min())
        assert error<=6,(f['cause'],error)
        color_errors[f['cause']]=round(error,3)
    # Visual diagnostic only; original output dimensions stay fixed.
    contact=Image.new('RGB',(1080,1152),a.BG)
    draw=ImageDraw.Draw(contact)
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14)
    for i,frame in enumerate(decoded):
        x=(i%3)*360;y=(i//3)*384
        contact.paste(Image.fromarray(frame).resize((360,360),Image.Resampling.LANCZOS),(x,y))
        draw.text((x+8,y+361),f"{i+1:02d} {m['frames'][i]['cause']} / {m['frames'][i]['count']}",font=font,fill=a.INK)
    contact.save(OUT/'animation_contact_sheet.png')
    report={'status':'PASS','canvas':[1440,1440],'frames':9,'durations_ms':durations,'total_duration_ms':sum(durations),
      'loop':0,'opening_closing_decoded_identical':True,'all_frame_transforms_identical':True,
      'decoded_static_region_differing_pixels':differences,'interstate_borders_clipped':True,
      'no_synthetic_clip_box_border':True,'borders_below_rail':True,'mutually_exclusive_direct_category_sum':234,
      'seven_cause_sum':232,'other_unknown_in_overview':2,'category_color_nearest_rgb_errors':color_errors,
      'opening_png_vs_gif_mean_rgb_error':round(quantization_mae,4),
      'minimum_supporting_font_points':m['minimum_supporting_font_points'],
      'minimum_supporting_font_px_at_960_width':10,
      'network_performance_note':'Static local byte size only; no public deployment/network benchmark.',
      'outputs':{name:{'bytes':(OUT/name).stat().st_size,'sha256':digest(OUT/name)} for name in ['day16_njt_disruptions.gif','day16_njt_disruptions.png']}}
    (OUT/'final_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
