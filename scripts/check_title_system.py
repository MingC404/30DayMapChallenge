"""Check actual final raster exports and create a local-only title contact sheet.

The sheet includes private Day 13 and must stay in the ignored .work directory.
It crops actual final images, at a common whole-canvas display width; no mockups.
"""
from pathlib import Path
import json, hashlib, math
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'.work/title-system'
CFG=json.loads((ROOT/'scripts/title_system.json').read_text(encoding='utf-8'))
ENTRIES=json.loads((ROOT/'scripts/gallery_entries.json').read_text(encoding='utf-8'))


def main():
    reports=json.loads((ROOT/'.work/typography-pass/pixel_validation.json').read_text())
    byfile={r['file']:r for r in reports};views=[];checks=[]
    for entry in ENTRIES:
        day=entry['day']
        for media in entry['media']+entry.get('downloads',[]):
            file=media['source'];path=ROOT/file;image=Image.open(path);image.seek(0)
            if file not in byfile:raise AssertionError(('Missing pixel/timing verification',file))
            report=byfile[file]
            assert report['sha256']==hashlib.sha256(path.read_bytes()).hexdigest(),file
            assert report['non_target_pixels_changed']==0
            blocks=[b for b in CFG['title_blocks'] if b['day']==day]
            fmt=path.suffix[1:]
            block=next((b for b in blocks if b.get('format')==fmt),None) or next(b for b in blocks if not b.get('format'))
            roles=block['layers'];names=[r['role'] for r in roles]
            assert names[0]=='day' and names[1]=='title'
            assert names==sorted(names,key={'day':0,'title':1,'subtitle':2}.get)
            assert any(r['role']=='subtitle' for r in roles) or day in ['03','12','13']
            assert roles[0]['text'].startswith('DAY '+day+' / ')
            if day=='11':assert roles[0]['text']=='DAY 11 / SENSES: SOUND'
            effective=2350 if day=='11' else block['canvas'][0]
            targets={'day':.011,'title':.028,'subtitle':.012}
            for role in roles:
                assert abs(role['size']/effective/targets[role['role']]-1)<.09,(day,role)
            for a,b in zip(roles,roles[1:]):
                assert abs(a['box'][0]-b['box'][0])<2
                assert a['box'][3]<=b['box'][1]+1,(day,'overlap',a,b)
            sx=image.width/block['canvas'][0];sy=image.height/block['canvas'][1]
            rect=[round(block['crop'][0]*sx),round(block['crop'][1]*sy),round(block['crop'][2]*sx),round(block['crop'][3]*sy)]
            assert rect[0]>=0 and rect[1]>=0 and rect[2]<=image.width and rect[3]<=image.height,(file,rect)
            crop=image.convert('RGB').crop(rect)
            # Constant whole-canvas width preserves real relative font sizes.
            zoom=900/image.width
            crop=crop.resize((max(1,round(crop.width*zoom)),max(1,round(crop.height*zoom))),Image.Resampling.LANCZOS)
            views.append((day,path.suffix[1:].upper(),image.size,crop))
            checks.append({'day':day,'file':file,'status':'PASS','roles':names,'subtitle_missing_authorized':day in ['03','12','13'],
                           'effective_width':effective,'no_title_overlap_or_clipping':True,'pixel_and_animation_checks':report})
    cols=4;cw=940;ch=180;rows=math.ceil(len(views)/cols)
    sheet=Image.new('RGB',(cols*cw,105+rows*ch),'#e8e4dc');d=ImageDraw.Draw(sheet)
    title=ImageFont.truetype('C:/Windows/Fonts/georgia.ttf',34)
    label=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
    d.text((24,15),'Day 01–16 / Final title blocks',font=title,fill='#383832')
    d.text((24,63),'ACTUAL FINAL EXPORTS · common canvas display width · Day 07 skipped · Day 13 LOCAL ONLY · missing subtitles retained as approved',font=label,fill='#77766e')
    for i,(day,fmt,size,crop) in enumerate(views):
        x=(i%cols)*cw+20;y=105+(i//cols)*ch
        d.text((x,y),f'DAY {day} / {fmt} / {size[0]} × {size[1]}'+(' / PRIVATE' if day=='13' else ''),font=label,fill='#77766e')
        assert crop.height<=ch-37,(day,crop.size)
        sheet.paste(crop,(x,y+30))
    output=WORK/'title_block_contact_sheet_final.png';sheet.save(output,optimize=True)
    (WORK/'final_title_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':'PASS','actual_exports':len(views),'completed_days':15,'contact_sheet':str(output),
                      'gif_frames_checked':sum(r['frames'] for r in reports if r['file'].endswith('.gif'))},ensure_ascii=True))


if __name__=='__main__':main()
