"""Render the final series title system as isolated letter layers, not maps."""
from pathlib import Path
import os, json, io, base64, re, subprocess
os.environ['MPLCONFIGDIR']=str(Path(__file__).resolve().parents[1]/'.work/title-system/mpl-cache')
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'.work/title-system';OUT=ROOT/'scripts/title_system'
FONT=Path('C:/Windows/Fonts');REV=json.loads((WORK/'baseline.json').read_text())['revision']
ENTRIES=json.loads((ROOT/'scripts/gallery_entries.json').read_text(encoding='utf-8'))
CONFIG={'reference_revision':REV,'scope':'DAY / THEME, title, subtitle only; missing subtitles not invented; private Day 13 excluded from release.',
        'patches':[],'files':{},'preserved_days':['07'],'preserved_web_sizes':{'04':'70%','09':'70%','14':'75%','16':'70%'},'title_blocks':[]}


def read(path):
    if path.startswith('13/'):
        source=WORK/'original13.png'
        if not source.exists():source.write_bytes((ROOT/path).read_bytes())
        return Image.open(source).convert('RGB')
    return Image.open(io.BytesIO(subprocess.check_output(['git','show',REV+':'+path],cwd=ROOT))).convert('RGB')


def face(role,size):return ImageFont.truetype(str(FONT/({'day':'seguisb.ttf','title':'georgia.ttf','subtitle':'segoeui.ttf'}[role])),round(size))


def runs(text,font,size):
    # Segoe UI for Latin, existing Noto Sans SC for the single CJK glyph in Day 11.
    result=[]
    for part in re.split(r'([\u3400-\u9fff]+)',text):
        if not part:continue
        f=font
        if '\u3400'<=part[0]<='\u9fff':
            f=ImageFont.truetype(str(FONT/'NotoSansSC-VF.ttf'),round(size));f.set_variation_by_name('Regular')
        result.append((part,f))
    return result


def text_layer(size,x,y,text,role,px,color):
    layer=Image.new('RGBA',size);draw=ImageDraw.Draw(layer);f=face(role,px)
    if role=='day':
        for i,c in enumerate(text):draw.text((x+f.getlength(text[:i])+i*.08*px,y),c,font=f,fill=color,anchor='lt')
        h=f.getbbox(text,anchor='lt')[3];w=f.getlength(text)+max(0,len(text)-1)*.08*px
    else:
        parts=runs(text,f,px);asc=max(-ff.getbbox(t,anchor='ls')[1] for t,ff in parts);desc=max(ff.getbbox(t,anchor='ls')[3] for t,ff in parts);w=0
        for t,ff in parts:draw.text((x+w,y+asc),t,font=ff,fill=color,anchor='ls');w+=ff.getlength(t)
        h=asc+desc
    return layer,(x,y,x+w,y+h)


def block(day,image,x,y,title,subtitle,theme,main=None,day_size=None,sub=None,gap=None,title_lines=None,subtitle_lines=None,color='#383832',muted='#77766e',day_color=None,subtitle_color=None):
    w=image.width;t=main or round(w*.028);d=day_size or round(w*.011);s=sub or round(w*.012);gap=round(t*.18) if gap is None else gap
    combined=Image.new('RGBA',image.size);boxes=[];start=y
    for role,lines,px,c in [('day',['DAY '+day+' / '+theme],d,day_color or muted),('title',title_lines or [title],t,color),('subtitle',subtitle_lines or ([subtitle] if subtitle else []),s,subtitle_color or muted)]:
        if not lines:continue
        for i,line in enumerate(lines):
            layer,bb=text_layer(image.size,x,y,line,role,px,c);combined=Image.alpha_composite(combined,layer);boxes.append({'role':role,'text':line,'size':px,'color':c,'box':list(bb)})
            y=bb[3]+(round(px*.15) if i<len(lines)-1 else 0)
        y+=gap
    for a,b in zip(boxes,boxes[1:]):assert a['box'][3]<=b['box'][1],(day,a,b)
    assert max(b['box'][2] for b in boxes)<=image.width and y<image.height
    CONFIG['title_blocks'].append({'day':day,'canvas':list(image.size),'crop':[max(0,x-5),max(0,start-5),int(max(b['box'][2] for b in boxes)+8),int(max(b['box'][3] for b in boxes)+8)],'layers':boxes,'has_subtitle':bool(subtitle),'subtitle_missing_authorized':not bool(subtitle)})
    return combined


def add_patch(day,source,old,new,mask,tag,only=None):
    # The mask is only old/new letters. Other map pixels inside the title area stay exact.
    alpha=np.asarray(mask)>0;ys,xs=np.where(alpha);rect=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
    patch=new.crop(rect).convert('RGBA');patch.putalpha(mask.crop(rect))
    folder=WORK/'private' if day=='13' else OUT;folder.mkdir(parents=True,exist_ok=True);path=folder/f'day{day}_{tag}.png';patch.save(path,optimize=True)
    item={'day':day,'source':source,'rect':rect,'patch':path.relative_to(ROOT).as_posix(),'canvas':list(old.size),'layer':'title'}
    if only:item['only_format']=only
    CONFIG['patches'].append(item)


def old_mask(size,items):
    mask=Image.new('L',size);draw=ImageDraw.Draw(mask)
    for x,y,text,n,name,anchor in items:draw.text((x,y),text,font=ImageFont.truetype(str(FONT/name),round(n)),fill=255,anchor=anchor)
    return mask.point(lambda v:255 if v else 0).filter(ImageFilter.MaxFilter(5))


def compose(day,source,bare,layer,mask,tag='main',only=None):
    old=read(source);new=old.copy();new.paste(bare,(0,0),mask)
    new=Image.alpha_composite(new.convert('RGBA'),layer).convert('RGB');mask=Image.fromarray(np.uint8((np.asarray(mask)>0)|(np.asarray(layer)[:,:,3]>0))*255)
    add_patch(day,source,old,new,mask,tag,only)


def flat(day,source,rect,args,bg=None,tag='main',only=None):
    old=read(source);mask=Image.new('L',old.size);ImageDraw.Draw(mask).rectangle((rect[0],rect[1],rect[2]-1,rect[3]-1),fill=255)
    bare=Image.new('RGB',old.size,bg or old.getpixel((5,5)));layer=block(day,old,**args);compose(day,source,bare,layer,mask,tag,only)


def main():
    # All sizes are output pixels. The short Day 11 title slot uses an effective
    # width of ~2350px to preserve the fixed encoding note at y=150 and nearby waves.
    plans=[
      ('01','01/outputs/nyc_changing_station_explorer.png',(25,8,850,106),dict(x=34,y=14,title='NYC Changing Station Explorer',subtitle='Changing tables in NYC public restrooms',theme='POINTS',gap=6,color='#27343b',muted='#647079'),'#ffffff'),
      ('03','03/outputs/inside_the_park_jc.png',(55,5,2200,145),dict(x=65,y=16,title='Inside the Park',subtitle=None,theme='POLYGONS',gap=10,color='#29474b',muted='#73887c'),'#fafbf8'),
      ('04','04/outputs/02_citywide_final.png',(55,20,2350,220),dict(x=70,y=30,title='Clusters of Play \u2014 Jersey City & Hoboken',subtitle='400 m straight-line proximity \u00b7 Connections show proximity, not routes.',theme='MY DATA',gap=12,color='#e5eaf0',muted='#788b9c'),'#0e1825'),
      ('05','05/assets/fixed_canvas.png',(40,12,1100,130),dict(x=48,y=20,title='Seeing New York from the Water',subtitle='Lower Manhattan \u00b7 An interpretive paper skyline',theme='SIGHT',gap=8,day_color='#277f8a',color='#163f58',muted='#617c8b'),'#ffffff'),
      ('08','08/outputs/a_city_at_stroller_speed.png',(280,65,4400,565),dict(x=300,y=80,title='A City at Stroller Speed',subtitle='Rittenhouse Square / West Walnut, Philadelphia',theme='UTOPIA',gap=28,color='#344a42',muted='#344a42'),'#ffffff'),
      ('14','14/outputs/atlas_of_impossible_places_camera_preview.gif',(25,20,680,120),dict(x=32,y=22,title='Atlas of Impossible Places',subtitle='Four real cities. Infinite impossible geographies.',theme='BORGESIAN MAP',gap=4,color='#202e34',muted='#202e34'),'#f4f0e5'),
      ('15','15/outputs/day15_philadelphia_gazetteer.png',(75,35,1150,185),dict(x=85,y=40,title='PHILADELPHIA',subtitle='A GAZETTEER OF PLACES',theme='INSIDE OUT',gap=10,day_color='#955b47',color='#49473d',muted='#82785f'),'#f5efdf')]
    for day,source,rect,args,bg in plans:flat(day,source,rect,args,bg)
    # Day 09: unchanged real ocean/reading-area background under the original header.
    source='09/outputs/top20_anchors/a_landscape_of_surnames_top20.png';old=read(source)
    svg=ET.fromstring((ROOT/'09/outputs/top20_anchors/a_landscape_of_surnames_top20.svg').read_text(encoding='utf-8'))
    e=next(e for e in svg if e.get('data-role')=='real-etopo-ocean');bare=Image.open(io.BytesIO(base64.b64decode(e.get('href').split(',',1)[1]))).convert('RGB').resize(old.size,Image.Resampling.BICUBIC)
    mask=Image.new('L',old.size);ImageDraw.Draw(mask).rectangle((95,45,2099,349),fill=255)
    layer=block('09',old,110,60,'A Landscape of Surnames','Twenty leading surnames with twenty selected local occurrences','URBAN\u2013RURAL',gap=22,day_color='#163d50',color='#163d50',muted='#234657');compose('09',source,bare,layer,mask)
    # Day 06/10 source-derived backdrop, restoring only old letters.
    for day,source,args,items in [
      ('06','06/outputs/a_changing_harbor_edge.png',dict(x=115,y=80,title='A Changing Harbor Edge',subtitle='Lower Manhattan \u00b7 Historical chart catalog date: 1844',theme='VINTAGE',gap=20,color='#163f58',muted='#163f58'),[(115,85,'DAY 06 / VINTAGE',34,'arialbd.ttf',None),(107,153,'A Changing Harbor Edge',108,'georgia.ttf',None),(115,300,'Lower Manhattan \u00b7 Historical chart catalog date: 1844',39,'arial.ttf',None)]),
      ('10','10/outputs/heritage_across_east_asia_symbols_a.png',dict(x=130,y=70,title='Heritage Across East Asia',subtitle='How old are East Asia\u2019s UNESCO cultural heritage sites?',theme='PROMPTING ONLY',gap=24,subtitle_color='#423834',color='#423834',muted='#77776e'),[(130,90,'30 DAY MAP CHALLENGE 2026  /  10  PROMPTING ONLY',38,'arialbd.ttf',None),(124,170,'Heritage Across East Asia',166,'georgia.ttf',None),(132,384,'How old are East Asia\u2019s UNESCO cultural heritage sites?',58,'arial.ttf',None)])]:
        old=read(source);compose(day,source,Image.open(WORK/f'bare{day}.png').convert('RGB'),block(day,old,**args),old_mask(old.size,items))
    # Day 11 is backed by its real retained basemap, never a flat painted rectangle.
    source='11/outputs/where_sounds_ripple.png';old=read(source);scene=json.loads((ROOT/'11/data/final_layout.json').read_text(encoding='utf-8'))
    bare=Image.open(ROOT/'11'/scene['basemap']).convert('RGB').resize(old.size,Image.Resampling.LANCZOS)
    mask=old_mask(old.size,[(65,30,'Where Sounds Ripple',60,'georgia.ttf','lt')])
    # Existing subtitle/footer use Noto Sans SC at their frozen ink-top anchors.
    for x,y,text,n in [(65,96,scene['subtitle'],25),(130,1850,'Ming Cao / 2026 Day 11 \u00b7 Senses: Sound',19)]:
        f=ImageFont.truetype(str(FONT/'NotoSansSC-VF.ttf'),n);f.set_variation_by_name('Regular');m=Image.new('L',old.size);ImageDraw.Draw(m).text((x,y),text,font=f,fill=255,anchor='lt');mask=Image.fromarray(np.maximum(np.asarray(mask),np.asarray(m.filter(ImageFilter.MaxFilter(5)))))
    ImageDraw.Draw(mask).rectangle((55,4,959,144),fill=255)
    ImageDraw.Draw(mask).rectangle((120,1846,900,1874),fill=255)
    layer=block('11',old,65,8,'Where Sounds Ripple',scene['subtitle'],'EVERYDAY MAP',main=66,day_size=26,sub=28,gap=10,color='#293d47',muted='#293d47')
    f=ImageFont.truetype(str(FONT/'NotoSansSC-VF.ttf'),19);f.set_variation_by_name('Regular');ImageDraw.Draw(layer).text((130,1850),'Ming Cao / 2026',font=f,fill='#293d47',anchor='lt');compose('11',source,bare,layer,mask)
    # Day 12 title-free true wind render restores old series/day letters only.
    for season in ['January','September']:
        source=f'12/output/The_Shape_of_Wind_{season}.png';old=read(source)
        mask=old_mask(old.size,[(100,70,'30 DAY MAP CHALLENGE 2026',30,'arial.ttf',None),(100,148,'The Shape of Wind',132,'georgia.ttf',None),(100,340,'DAY 12 / POWER',34,'arialbd.ttf',None)])
        layer=block('12',old,100,70,'The Shape of Wind',None,'POWER',gap=20,color='#e9edf0',muted='#d0e0e8')
        compose('12',source,Image.open(WORK/f'bare12-{season}.png').convert('RGB'),layer,mask,season)
        CONFIG['patches'][-1]['only_source']=source
    # Day 16 remains inside the map's upper-left free area, below fixed credits.
    source='16/outputs/day16_njt_disruptions.png';old=read(source);bare=Image.open(WORK/'bare16.png').convert('RGB');rendered=Image.open(WORK/'rendered16.png').convert('RGB');mask=Image.fromarray(np.uint8(np.any(np.asarray(rendered)!=np.asarray(bare),axis=2))*255).filter(ImageFilter.MaxFilter(3))
    layer=block('16',old,45,130,'Why Are the Trains Late?','An Atlas of NJ Transit Disruptions','COLLABORATIVE MAP',gap=8,title_lines=['Why Are the','Trains Late?'],subtitle_lines=['An Atlas of NJ Transit','Disruptions'])
    compose('16',source,bare,layer,mask)
    # Native HTML captures (02/10) and private 13 are added by the browser pass.
    for e in ENTRIES:
        d=e['day']
        if d in ['02','13']:continue
        CONFIG['files'][d]=[a['source'] for a in e['media']+e.get('downloads',[])]
    CONFIG['files']['05'].append('05/assets/fixed_canvas.png')
    CONFIG['files']['16'] += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'16/outputs/frames').glob('*.png'))]
    path=ROOT/'scripts/title_system.json'
    if path.exists():
        prior=json.loads(path.read_text(encoding='utf-8'))
        native=[p for p in prior['patches'] if p['day'] in ['02','13'] or (p['day']=='10' and p.get('only_format')=='gif')]
        if native:
            for p in CONFIG['patches']:
                if p['day']=='10':p['only_format']='png'
            CONFIG['patches']+=native
            CONFIG['title_blocks'] += [b for b in prior['title_blocks'] if b.get('format')]
            for day in ['02','13']:
                if day in prior['files']:CONFIG['files'][day]=prior['files'][day]
            CONFIG['local_sources']=prior.get('local_sources',{})
            CONFIG['private_days']=['13']
    path.write_bytes(json.dumps(CONFIG,ensure_ascii=False,indent=2).encode('utf-8'))
    print('Prepared final title layers for',len(CONFIG['title_blocks']),'native canvases.')


if __name__=='__main__':main()
