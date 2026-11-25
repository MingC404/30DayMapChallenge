"""Shared D26 palette, fonts and supersampled drawing primitives."""
from PIL import ImageFont
BG='#f4f0e7';INK='#383b39';MUTED='#74776e';BLUE='#187caa';GRID='#dcded5';FILL='#e2e4da';WATER='#d9e4e2'
S=2
FONT='C:/Windows/Fonts/'
cache={}
def font(size,file='segoeui.ttf'):
 key=(size,file)
 if key not in cache:cache[key]=ImageFont.truetype(FONT+file,round(size*S))
 return cache[key]
def text(draw,x,y,t,size=24,color=INK,file='segoeui.ttf',anchor='ls'):
 draw.text((round(x*S),round(y*S)),t,font=font(size,file),fill=color,anchor=anchor)
def line(draw,points,color=INK,width=1):draw.line([(round(x*S),round(y*S)) for x,y in points],fill=color,width=round(width*S),joint='curve')
def dot(draw,x,y,r=4,color=BLUE):draw.ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S),fill=color)
