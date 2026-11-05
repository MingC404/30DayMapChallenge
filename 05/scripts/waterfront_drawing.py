"""One extendable water-level cityscape, from cached NYC footprints and heights.

Native SVG geometry and PNG use the same commands. No invented infill buildings.
"""
from pathlib import Path
import sys,json,math,html,csv
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'02/.deps'))
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import shape,Point,LineString,Polygon,box
from shapely.ops import transform,unary_union,nearest_points
from pyproj import Transformer,Geod

DATA=ROOT/'05/data';OUT=ROOT/'05/outputs';OUT.mkdir(exist_ok=True)
W,H=2600,1500
WHITE='#FFFFFF';NAVY='#163F58';TEAL='#277F8A';SEA='#E6F3F6';GOLD='#AE8D51';MUTED='#617C8B'
class Drawing:
    def __init__(self):
        self.im=Image.new('RGB',(W,H),WHITE);self.d=ImageDraw.Draw(self.im)
        self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
                '<title>Seeing New York from the Water — Lower Manhattan, lookout 03</title>',
                '<desc>Local cityscape derived from official NYC building footprints and roof heights. Simplified landmark crowns are illustrative. Not a surveyed skyline or visibility model.</desc>',
                '<rect width="2600" height="1500" fill="#FFFFFF"/>'];self.tx=self.ty=0
    def group(self,name,x=0,y=0):self.s.append(f'<g id="{name}" transform="translate({x:.4f} {y:.4f})">');self.tx=x;self.ty=y
    def end(self):self.s.append('</g>');self.tx=self.ty=0
    def poly(self,pts,fill=None,stroke=None,width=1,close=True):
        p=list(pts)
        if len(p)<2:return
        tag='polygon' if close else 'polyline';st=' '.join(f'{x:.3f},{y:.3f}' for x,y in p)
        self.s.append(f'<{tag} points="{st}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')
        q=[(x+self.tx,y+self.ty) for x,y in p]
        if fill:self.d.polygon(q,fill=fill)
        if stroke:self.d.line(q+([q[0]] if close else []),fill=stroke,width=width,joint='curve')
    def line(self,p,color,width=1):self.poly(p,stroke=color,width=width,close=False)
    def rect(self,x,y,w,h,fill,stroke=None,width=1):self.poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],fill,stroke,width)
    def circle(self,x,y,r,fill=None,stroke=None,width=1):
        self.s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}"/>')
        x+=self.tx;y+=self.ty;self.d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=stroke,width=width)
    def text(self,x,y,s,size=26,color=NAVY,serif=False,bold=False,anchor='start'):
        fam='Georgia' if serif else 'Arial';file=('georgia' if serif else 'arial')+('b' if serif and bold else 'bd' if bold else '')+'.ttf'
        font=ImageFont.truetype('C:/Windows/Fonts/'+file,size)
        self.s.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color}">{html.escape(s)}</text>')
        self.d.text((x+self.tx,y+self.ty),s,font=font,fill=color,anchor={'start':'ls','middle':'ms','end':'rs'}[anchor])

