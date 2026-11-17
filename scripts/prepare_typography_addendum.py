"""Prepare Day 09/15 text-only layers without drawing any map geometry."""
from pathlib import Path
import ast, base64, io, json, re, subprocess, os
os.environ.setdefault("MPLCONFIGDIR",str(Path(__file__).resolve().parents[1]/".work/typography-addendum/mpl-cache"))
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.font_manager import FontProperties
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
PATCH=ROOT/'scripts/typography_patches'
CFG=ROOT/'scripts/typography_pass.json'
FONT=Path('C:/Windows/Fonts')


def main():
    cfg=json.loads(CFG.read_text(encoding='utf-8'))
    cfg['patches']=[p for p in cfg['patches'] if p['day'] not in ['09','15']]
    # Recover the original bathymetry reading-area background, not a flat fill.
    svg=ROOT/'09/outputs/top20_anchors/a_landscape_of_surnames_top20.svg'
    original_svg=subprocess.check_output(['git','show',cfg['reference_revision']+':'+svg.relative_to(ROOT).as_posix()]).decode('utf-8')
    root=ET.fromstring(original_svg);ns='{http://www.w3.org/2000/svg}'
    image=next(e for e in root if e.tag==ns+'image' and e.get('data-role')=='real-etopo-ocean')
    bg=Image.open(io.BytesIO(base64.b64decode(image.get('href').split(',',1)[1]))).convert('RGB').resize((4200,4500),Image.Resampling.BICUBIC)
    png='09/outputs/top20_anchors/a_landscape_of_surnames_top20.png'
    old=Image.open(io.BytesIO(subprocess.check_output(['git','show',cfg['reference_revision']+':'+png]))).convert('RGB')
    layout=json.loads((ROOT/'09/data/render_inputs/approved_pre_enlargement.json').read_text(encoding='utf-8'))
    specs={
      'DAY 09 / URBAN\u2013RURAL':('seguisb.ttf',21,'Segoe UI',600,(100,65,1000,125)),
      'A Landscape of Surnames':('georgia.ttf',58,'Georgia',400,(100,140,1750,278)),
      'Twenty leading surnames with twenty selected local occurrences':('segoeui.ttf',25,'Segoe UI',400,(105,280,1950,350))}
    new=old.copy();changes={}
    for item in layout['text_boxes']:
        if item['text'] not in specs:continue
        text=item['text'];name,size,family,weight,rect=specs[text];x,y=item['bounds'][:2]
        mask=Image.new('L',old.size);ImageDraw.Draw(mask).text((x*2,y*2),text,font=ImageFont.truetype(str(FONT/'arial.ttf'),round(item['size']*2)),fill=255,anchor='lt')
        mask=mask.point(lambda v:255 if v else 0).filter(ImageFilter.MaxFilter(3))
        new.paste(bg,(0,0),mask)
        f=ImageFont.truetype(str(FONT/name),round(size*2));draw=ImageDraw.Draw(new)
        color=next(e.get('fill') for e in root.findall(ns+'text') if e.text==text)
        if text.startswith('DAY '):
            for i,char in enumerate(text):draw.text((x*2+f.getlength(text[:i])+i*.08*size*2,y*2),char,font=f,fill=color,anchor='lt')
        else:draw.text((x*2,y*2),text,font=f,fill=color,anchor='lt')
        path=PATCH/('day09_'+('day' if text.startswith('DAY ') else 'subtitle' if text.startswith('Twenty') else 'title')+'.png')
        new.crop(rect).save(path,optimize=True)
        cfg['patches'].append({'day':'09','source':png,'rect':list(rect),'patch':path.relative_to(ROOT).as_posix(),'canvas':list(old.size),'layer':'title'})
        # SVG baseline derives from the same native font and original ink top.
        baseline=y-f.getbbox(text,anchor='ls')[1]/2
        changes[text]={'font-family':family,'font-size':str(size),'font-weight':str(weight),'y':str(baseline)}
        if text.startswith('DAY '):changes[text]['letter-spacing']=str(.08*size)
    # Only the three exact text elements change; preserve all GIS/data-glyph bytes.
    edited=original_svg
    for text,attrs in changes.items():
        match=re.search(r'<text\b[^>]*>'+re.escape(text)+r'</text>',edited);assert match,text
        node=match.group()
        for key,value in attrs.items():
            if re.search(r'\b'+key+r'="[^"]*"',node):node=re.sub(r'\b'+key+r'="[^"]*"',f'{key}="{value}"',node)
            else:node=node.replace('>',f' {key}="{value}">',1)
        edited=edited.replace(match.group(),node,1)
    svg.write_bytes(edited.encode('utf-8'))
    # Day 15 is flat paper in these letter footprints. Render text layers only.
    source=ROOT/'15/scripts/render_final.py';tree=ast.parse(source.read_text(encoding='utf-8-sig'))
    roles={(95,2278):('seguisb.ttf',19.2),(95,2218):('georgia.ttf',51.2),(98,2172):('segoeui.ttf',19.2),
           (96,63):('segoeui.ttf',17.6),(3140,63):('segoeui.ttf',17.6),(96,36):('segoeui.ttf',13.6)}
    colors=json.loads((ROOT/'15/data/layout.json').read_text(encoding='utf-8'))['colors']
    entries=[]
    for call in ast.walk(tree):
        if not isinstance(call,ast.Call) or not isinstance(call.func,ast.Name) or call.func.id!='label':continue
        try:xy=tuple(ast.literal_eval(call.args[0]))
        except (ValueError,TypeError):continue
        if xy not in roles:continue
        text=ast.literal_eval(call.args[1]);size=ast.literal_eval(call.args[2]);color='#82785f'
        if len(call.args)>3:
            color=colors['ink'] if isinstance(call.args[3],ast.Subscript) else ast.literal_eval(call.args[3])
        ha=next((ast.literal_eval(k.value) for k in call.keywords if k.arg=='ha'),'center')
        entries.append((xy,text,size,color,ha))
    assert len(entries)==6
    def layer(updated):
        fig=Figure(figsize=(32,23.5),dpi=90,facecolor='none');canvas=FigureCanvasAgg(fig)
        ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,3200);ax.set_ylim(0,2350);ax.set_aspect('equal');ax.axis('off')
        for xy,text,size,color,ha in entries:
            kw={'fontsize':size,'fontfamily':'DejaVu Serif'}
            if updated:
                name,size=roles[xy];kw={'fontsize':size,'fontproperties':FontProperties(fname=str(FONT/name))}
            draw_xy=(xy[0],2164) if updated and xy==(98,2172) else xy
            ax.text(*draw_xy,text,color=color,ha=ha,va='center',**kw)
        canvas.draw();return Image.fromarray(np.asarray(canvas.buffer_rgba()).copy())
    new_layer=layer(True)
    png='15/outputs/day15_philadelphia_gazetteer.png'
    before=Image.open(io.BytesIO(subprocess.check_output(['git','show',cfg['reference_revision']+':'+png]))).convert('RGB')
    # Both original title/footer slots are plain paper; retain the rule lines outside them.
    # Clear these explicit slots rather than approximating a legacy font raster mask.
    after=before.copy()
    for rect in [(75,45,1100,185),(75,2042,2845,2097)]:
        after.paste(colors['background'],rect)
    after=Image.alpha_composite(after.convert('RGBA'),new_layer).convert('RGB')
    allowed=np.zeros((before.height,before.width),dtype=bool)
    for label,rect in [('title',(75,45,1100,185)),('notes',(75,2042,2845,2097))]:
        path=PATCH/f'day15_{label}.png';patch=after.crop(rect).convert('RGBA')
        a=np.asarray(before.crop(rect));b=np.asarray(after.crop(rect));alpha=np.uint8(np.any(a!=b,axis=2))*255;patch.putalpha(Image.fromarray(alpha));patch.save(path,optimize=True)
        cfg['patches'].append({'day':'15','source':png,'rect':list(rect),'patch':path.relative_to(ROOT).as_posix(),'canvas':list(before.size),'layer':label})
        allowed[rect[1]:rect[3],rect[0]:rect[2]]=True
    assert not np.any(np.any(np.asarray(before)!=np.asarray(after),axis=2)&~allowed)
    cfg['files']['09']=['09/outputs/top20_anchors/a_landscape_of_surnames_top20.png','09/outputs/top20_anchors/a_landscape_of_surnames_top20.gif']
    cfg['files']['15']=[png]
    cfg['preserved_days']=[d for d in cfg['preserved_days'] if d not in ['09','15']]
    CFG.write_bytes(json.dumps(cfg,indent=2).encode('utf-8'))
    print('Prepared three Day 09 headings and Day 15 title/footer letters only.')


if __name__=='__main__':main()
