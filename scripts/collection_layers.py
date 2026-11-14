"""Recover real drawing layers in memory; accepted source files are read-only.

Original renderers are compiled with exports removed. Full-strength replay must
match the accepted PNG pixel for pixel before any animation is allowed.
"""
import ast,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageChops

def load_tree(path,stop=None):
    source=path.read_text('utf8');tree=ast.parse(source)
    if stop:tree.body=[n for n in tree.body if n.lineno<source[:source.index(stop)].count('\n')+1]
    return source,tree

def exact(image,path):
    with Image.open(path) as original:
        assert image.size==original.size
        assert ImageChops.difference(image.convert('RGB'),original.convert('RGB')).getbbox() is None, 'Replay differs from accepted PNG: '+str(path)

def reduced(image,width):
    return image.convert('RGB').resize((width,round(image.height*width/image.width)),Image.Resampling.LANCZOS)

def shoreline(root,width):
    path=root/'06/scripts/render_final.py';source,tree=load_tree(path)
    class Rewrite(ast.NodeTransformer):
        def visit_Expr(self,node):
            if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='print':return ast.Pass()
            if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and node.value.func.attr in ('save','write_text'):return ast.Pass()
            return self.generic_visit(node)
        def visit_For(self,node):
            if isinstance(node.target,ast.Name) and node.target.id=='path' and isinstance(node.iter,ast.Name) and node.iter.id=='paths':
                return ast.If(test=ast.Name(id='_coast_on',ctx=ast.Load()),body=[node],orelse=[])
            return self.generic_visit(node)
    tree=Rewrite().visit(tree)
    tree.body=[n for n in tree.body if not isinstance(n,ast.If)]
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='render')
    fn.body.append(ast.Return(value=ast.Name(id='page',ctx=ast.Load())))
    namespace={'__file__':str(path),'__name__':'layer_capture','_coast_on':True}
    exec(compile(ast.fix_missing_locations(tree),str(path),'exec'),namespace)
    normal=namespace['render']();exact(normal,root/'06/outputs/a_changing_harbor_edge.png')
    namespace['_coast_on']=False;under=namespace['render']()
    return reduced(under,width),[reduced(normal,width)],['Modern shoreline'],['#087487','#E2E9DE']

def people(root,width):
    path=root/'08/scripts/render_final.py';source,tree=load_tree(path,"im.save(OUT/'a_city_at_stroller_speed.png'")
    def line(marker):return source[:source.index(marker)].count('\n')+1
    # Exact source statement ranges, not rectangular image masks. Props, mats,
    # grass, paths, benches and swing apparatus are retained underneath people.
    spans=[('Child riding the swing','# A seated child holds','figure(325,997'),
     ('Children with ball on lawn','# 2. A child on the picnic lawn','curve([(432,944)'),
     ('Hopping child in chalk clearing','# 1. A balancing child','# 2. A child on the picnic lawn'),
     ('Child and caregiver with ice creams','figure(972,941',"street_anchors.append({'name':'Ice-cream cart'"),
     ('Standing baby cuddle','figure(740,678','# Baby scene 2'),
     ('Crawling baby with caregiver','# Baby scene 2','# Baby scene 3'),
     ('Tummy time with caregiver','poly([(193,852)','ellipse((252,849'),
     ('Tummy time with caregiver','# A seated adult sits','# Ground and contact checks'),
     ('Baby cradled on bench','curve([(1405,581)','curve([(1334,665)')]
    names=['Child riding the swing','Children with ball on lawn','Hopping child in chalk clearing',
     'Child and caregiver with ice creams','Standing baby cuddle','Crawling baby with caregiver',
     'Tummy time with caregiver','Baby cradled on bench']
    ranges=[(names.index(name),line(start),line(end)) for name,start,end in spans]
    namespace={'__file__':str(path),'__name__':'layer_capture','_active_group':None}
    commands=[]
    class Recorder:
        def __init__(self,draw):self.draw=draw
        def __getattr__(self,name):
            method=getattr(self.draw,name)
            if name not in ('polygon','line','ellipse','text','rectangle'):return method
            def call(*args,**kwargs):
                commands.append((namespace['_active_group'],name,args,kwargs));return method(*args,**kwargs)
            return call
    namespace['_Recorder']=Recorder
    def paste(*args,**kwargs):
        commands.append((None,'paste',args,kwargs));namespace['im'].paste(*args,**kwargs)
    namespace['_record_paste']=paste
    body=[]
    for node in tree.body:
        group=next((i for i,a,b in ranges if a<=node.lineno<b),None)
        if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='figure':
            if ast.literal_eval(node.value.args[0]) in (325,425):group=1
        body.append(ast.Assign(targets=[ast.Name(id='_active_group',ctx=ast.Store())],value=ast.Constant(group)))
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='d' for t in node.targets):
            node.value=ast.Call(func=ast.Name(id='_Recorder',ctx=ast.Load()),args=[node.value],keywords=[])
        if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and isinstance(node.value.func.value,ast.Name) and node.value.func.value.id=='im' and node.value.func.attr=='paste':
            node.value.func=ast.Name(id='_record_paste',ctx=ast.Load())
        body.append(node)
    tree.body=body;exec(compile(ast.fix_missing_locations(tree),str(path),'exec'),namespace)
    exact(namespace['im'],root/'08/outputs/a_city_at_stroller_speed.png')
    size=namespace['im'].size
    def replay(groups):
        canvas=Image.new('RGB',size,'white');draw=ImageDraw.Draw(canvas)
        for group,name,args,kwargs in commands:
            if group is None or group in groups:getattr(canvas if name=='paste' else draw,name)(*args,**kwargs)
        return canvas
    # This checks the recorded operation list, not just the original execution.
    exact(replay(set(range(len(names)))),root/'08/outputs/a_city_at_stroller_speed.png')
    base=reduced(replay(set()),width)
    singles=[reduced(replay({i}),width) for i in range(len(names))]
    return base,singles,names,[namespace[k] for k in ['INK','BLUE','CORAL','YELLOW','MUSTARD','SAGE']]

def surnames(root,width):
    path=root/'09/scripts/render_day09_bathymetry.py'
    source,tree=load_tree(path,"tree.write(OUT/'a_landscape_of_surnames_top20.svg'")
    commands=[];namespace={'__file__':str(path),'__name__':'layer_capture'}
    def capture(draw,metadata,*args,**kwargs):
        if metadata['role']=='map_surname':commands.append((metadata['text'],args,kwargs))
        else:draw.text(*args,**kwargs)
    namespace['_capture_text']=capture
    class Rewrite(ast.NodeTransformer):
        def visit_Call(self,node):
            if isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name) and node.func.value.id=='draw' and node.func.attr=='text' and any(isinstance(n,ast.Name) and n.id=='e' for n in ast.walk(node)):
                return ast.Call(func=ast.Name(id='_capture_text',ctx=ast.Load()),args=[ast.Name(id='draw',ctx=ast.Load()),ast.Name(id='t',ctx=ast.Load())]+node.args,keywords=node.keywords)
            return self.generic_visit(node)
    tree=Rewrite().visit(tree);exec(compile(ast.fix_missing_locations(tree),str(path),'exec'),namespace)
    base_native=namespace['image'];normal=base_native.copy();draw=ImageDraw.Draw(normal)
    for name,args,kwargs in commands:draw.text(*args,**kwargs)
    exact(normal,root/'09/outputs/top20_anchors/a_landscape_of_surnames_top20.png')
    names=list(dict.fromkeys(c[0] for c in commands));assert len(names)==20
    colors=list(dict.fromkeys(c[2]['fill'] for c in commands))
    singles=[]
    for name in names:
        canvas=base_native.copy();draw=ImageDraw.Draw(canvas)
        for other,args,kwargs in commands:
            if other==name:draw.text(*args,**kwargs)
        singles.append(reduced(canvas,width))
    return reduced(base_native,width),singles,names,colors

def animate(root,day,width):
    base,singles,names,colors={'06':shoreline,'08':people,'09':surnames}[day](root,width)
    background=np.asarray(base).astype(np.float32)
    differences=[np.asarray(s).astype(np.float32)-background for s in singles]
    source={'06':'06/outputs/a_changing_harbor_edge.png','08':'08/outputs/a_city_at_stroller_speed.png','09':'09/outputs/top20_anchors/a_landscape_of_surnames_top20.png'}[day]
    with Image.open(root/source) as im:full=reduced(im,width)
    def frame(weights):
        if all(v==1 for v in weights):return full.copy()
        out=background.copy()
        for difference,weight in zip(differences,weights):out+=difference*weight
        return Image.fromarray(np.clip(np.rint(out),0,255).astype('uint8'))
    frames=[];durations=[]
    if day=='06':
        values=[(1-math.cos(math.pi*i/12))/2 for i in range(13)]
        for v in values+values[-2::-1]:frames.append(frame([v]));durations.append(100)
        durations[0]=500;durations[12]=1100
        assert frames[0].tobytes()==base.tobytes()==frames[-1].tobytes()
    else:
        n=len(names);dim=0 if day=='08' else .2
        states=[[1 if j==i else dim for j in range(n)] for i in range(n)]+[[1]*n];previous=states[-1]
        for current in states:
            steps=2 if day=='09' else 4
            for i in range(1,steps+1):frames.append(frame([p+(c-p)*i/steps for p,c in zip(previous,current)]));durations.append(100)
            durations[-1]=500 if day=='09' else 800
            if current==states[-1]:durations[-1]=1600
            previous=current
    # Local verification images are evidence, not alternate final exports.
    work=root/'.work/collection-animation';work.mkdir(parents=True,exist_ok=True)
    base.save(work/(day+'-true-underlay.png'));full.save(work/(day+'-normal.png'))
    return frames,durations,{'categories':names,'method':'original drawing operations replayed over their real underlay; opacity only','full_native_replay_matches_png':True,'palette_rgb':colors,'original_png_unchanged':True}
