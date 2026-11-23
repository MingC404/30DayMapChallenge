"""Clean final triptych; exact Day 19 canvas and series typography anchors."""
import json, re, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import render_study as study
from analyze_blocks import REVIEW

REPO=study.ROOT.parent
REFERENCE=REPO/'19/artwork.mjs'

def template():
    source=REFERENCE.read_text(encoding='utf8')
    w,h=map(int,re.search(r'width:(\d+),height:(\d+)',source).groups())
    anchors={}
    for role,string in [('day','DAY 19 / SENSES: SMELL'),('title','Where Smells Wander'),('subtitle','An Interactive Smellscape of SoHo, New York')]:
        match=re.search(re.escape(string)+r"',([\d.]+)\*s,([\d.]+)\*s",source)
        anchors[role]=[float(x) for x in match.groups()]
    return {'canvas':[w,h],'anchors':anchors,'sizes':{'day':w*.011,'title':w*.028,'subtitle':w*.012,'caption':16,'source':14,'author':17},
            'fonts':{'day':'seguisb.ttf','title':'georgia.ttf','subtitle':'segoeui.ttf','caption':'segoeui.ttf','source':'segoeui.ttf','author':'segoeui.ttf'},
            'attribution_baseline':h-77,'author_baseline':h-43,'left':84,'right':w-65,'dpi':round(Image.open(REPO/'19/day19.png').info['dpi'][0]),
            'source':'19/artwork.mjs','reference_png':'19/day19.png','source_sha256':hashlib.sha256(REFERENCE.read_bytes()).hexdigest()}

def main():
    t=template(); W,H=t['canvas']; panels=[study.prepare(c) for c in study.C['candidates']]
    previous=json.loads((study.OUT/'study_metadata.json').read_text())
    for panel,old in zip(panels,previous['panels']): assert panel[4]['bounds_projected_m']==old['bounds_projected_m']
    study.ROAD='#cbc6bc'
    fig=plt.figure(figsize=(W/150,H/150),dpi=150,facecolor=study.BG)
    size=460; top=358; lefts=[84,579,1074]
    for left,panel in zip(lefts,panels):
        ax=fig.add_axes([left/W,(H-top-size)/H,size/W,size/H]); study.draw(ax,panel)
    fig.canvas.draw(); im=Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert('RGB'); plt.close(fig)
    draw=ImageDraw.Draw(im); records=[]
    def font(role): return ImageFont.truetype('C:/Windows/Fonts/'+t['fonts'][role],t['sizes'][role])
    def text(x,y,s,role='caption',color=study.TEXT):
        f=font(role); box=draw.textbbox((x,y),s,font=f,anchor='ls')
        assert 0<=box[0]<box[2]<=W and 0<=box[1]<box[3]<=H,(s,box)
        draw.text((x,y),s,font=f,fill=color,anchor='ls')
        records.append({'text':s,'role':role,'size_px':t['sizes'][role],'baseline':[x,y],'box':box})
    x,y=t['anchors']['day']; f=font('day'); phrase='DAY 21 / OPENSTREETMAP'
    for ch in phrase:
        draw.text((x,y),ch,font=f,fill='#647168',anchor='ls'); x+=f.getlength(ch)+t['sizes']['day']*.08
    text(*t['anchors']['title'],'Three Street Fabrics of Manhattan','title')
    for left,panel in zip(lefts,panels):
        text(left,316,panel[0]['name'],'day')
        text(left,343,panel[0]['intersection'],'caption')
    x,y=1190,H-190; length=size/6
    draw.line((x,y,x+length,y),fill=study.INK,width=2)
    for q in [x,x+length/2,x+length]: draw.line((q,y-5,q,y+5),fill=study.INK,width=1)
    text(x,y+30,'0','caption'); text(x+length-16,y+30,'100 m','caption')
    text(84,t['attribution_baseline'],'© OpenStreetMap contributors · ODbL','source',color='#72796E')
    text(84,t['author_baseline'],'Ming Cao','author',color='#43554A')
    target=study.OUT/'day21_three_street_fabrics_of_manhattan.png'
    im.save(target,dpi=(t['dpi'],t['dpi']))
    report={'template':t,'image_size':[W,H],'panels':[p[4] for p in panels],
            'explanatory_text_location':'Gallery description, not on artwork','text':records,
            'day_line':phrase,'panel_size_px':size,'panel_top_px':top,'panel_left_px':lefts,
            'palette':{'background':study.BG,'buildings':study.INK,'streets':study.ROAD}}
    (study.OUT/'final_metadata.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    (REVIEW/'template_reuse.json').write_text(json.dumps(t,indent=2),encoding='utf8')
    print(target)

if __name__=='__main__': main()
