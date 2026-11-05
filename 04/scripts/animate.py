"""Render the approved dark design as an 18–20 second GIF; fixed city extent."""
from pathlib import Path
import json,copy,math,time
import night_light as art
from PIL import Image,ImageDraw
OUT=art.OUT;SIZE=(1440,1200);STEP=100
def ease(t):return t*t*(3-2*t)
state={'sources':{},'daycare':{},'reveal':0,'stage':'01 / BEFORE THE LIGHT','final':False,'focus_label':False}
timeline=[]
def keep(ms=STEP):timeline.append((copy.deepcopy(state),ms))
keep(1000)
def group(ids,demo=False):
    stage_prefix='02 / HAMILTON PARK' if demo else '03 / GROUPS JOIN'
    state['focus_label']=demo
    for pid in ids:state['sources'][pid]={'core':0,'halo':0,'line':0}
    for phase,n in [('core',3 if demo else 2),('halo',5 if demo else 3),('line',5 if demo else 3)]:
        state['stage']=stage_prefix
        for i in range(1,n+1):
            for pid in ids:state['sources'][pid][phase]=ease(i/n)
            keep()
    # New daycare are revealed in a staggered sequence; shared ones remain at 1.
    linked=sorted({e['daycare_id'] for e in art.edges if e['playground_id'] in ids},key=lambda uid:art.by_d[uid]['p'].distance(art.by_p[ids[0]]['p']))
    new=[uid for uid in linked if state['daycare'].get(uid,0)<1]
    n=max(2,len(new)*2) if demo else 6
    for i in range(1,n+1):
        for j,uid in enumerate(new):
            start=(j/max(1,len(new)))*.65
            alpha=ease(max(0,min(1,(i/n-start)/.35)))
            state['daycare'][uid]=max(state['daycare'].get(uid,0),alpha)
        keep()
    for uid in new:state['daycare'][uid]=1
    if demo:keep(1000)
group([art.FOCUS],True)
remaining=[p['id'] for p in art.playgrounds if p['id']!=art.FOCUS]
batches=[remaining[i:i+8] for i in range(0,len(remaining),8)]
for batch in batches:group(batch)
assert set(state['sources'])==set(art.by_p)
assert {uid for uid,v in state['daycare'].items() if v==1}==art.matched
state['stage']='04 / ALL GROUPS LIT';state['focus_label']=False;keep(800)
state['stage']='05 / FINAL REVEAL';state['final']=True
for i in range(1,9):state['reveal']=ease(i/8);keep()
state['stage']='FINAL / ALL GROUPS';keep(3500)
print(f'Timeline: {len(timeline)} frames, {sum(ms for _,ms in timeline)/1000:.1f}s',flush=True)
# One global palette prevents palette changes from making the fixed map shimmer.
final_rgb=art.render(True,state,save=False).resize(SIZE,Image.Resampling.LANCZOS)
sample=final_rgb.resize((720,600),Image.Resampling.LANCZOS)
swatches=Image.new('RGB',(720,680),art.PAPER);swatches.paste(sample,(0,0));dr=ImageDraw.Draw(swatches)
for row,end in enumerate((art.CYAN,art.GOLD,art.PURPLE,art.DIM)):
    for x in range(720):dr.line((x,600+row*20,x,619+row*20),fill=art.mix(art.LAND,end,x/719))
palette=swatches.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
frames=[];durations=[];review_indices=[0,17,len(timeline)//2,len(timeline)-1];review=[]
for i,(current,ms) in enumerate(timeline):
    rgb=art.render(True,current,save=False).resize(SIZE,Image.Resampling.LANCZOS)
    frame=rgb.quantize(palette=palette,dither=Image.Dither.NONE)
    frames.append(frame);durations.append(ms)
    if i in review_indices:review.append(frame.convert('RGB'))
    if i%20==0 or i==len(timeline)-1:print(f'Rendered {i+1}/{len(timeline)}',flush=True)
gif=OUT/'clusters_of_play.gif'
frames[0].save(gif,save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=1,optimize=False)
final_rgb.save(OUT/'gif_final_frame.png')
sheet=Image.new('RGB',(1440,1200),art.PAPER)
for i,im in enumerate(review):sheet.paste(im.resize((720,600),Image.Resampling.LANCZOS),((i%2)*720,(i//2)*600))
sheet.save(OUT/'gif_review.png')
# Reopen encoded output and verify timings, fixed dimensions, and retained final colors.
with Image.open(gif) as check:
    assert check.size==SIZE and check.info['loop']==0
    total=0
    for i in range(check.n_frames):check.seek(i);total+=check.info['duration']
    assert total==sum(durations)
    assert check.info['duration']>=3500
    last=check.convert('RGB')
    assert last.tobytes()==frames[-1].convert('RGB').tobytes()
    report={'file':gif.name,'size':SIZE,'encoded_frames':check.n_frames,'duration_ms':total,'final_hold_ms':check.info['duration'],'loop':0,'bytes':gif.stat().st_size,'daycare':len(art.daycare),'playgrounds':len(art.playgrounds),'matched':len(art.matched),'unmatched':len(art.unmatched),'links':len(art.edges),'fixed_extent':True,'all_playgrounds_used_for_final_classification':True,'first_demo':art.FOCUS,'remaining_batches':batches,'phases':['core','expanding glow','growing connections','staggered daycare','batched groups','unmatched reveal'],'global_palette':True,'gif_created':True}
(OUT/'gif_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
validation_path=OUT/'validation.json'
if validation_path.exists():
    validation=json.loads(validation_path.read_text(encoding='utf8'));validation['gif_created']=True;validation['gif']=report
    validation_path.write_text(json.dumps(validation,indent=2),encoding='utf8')
print(json.dumps(report,indent=2),flush=True)
