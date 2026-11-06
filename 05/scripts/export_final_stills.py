"""Export the full unscrolled artwork and the midpoint locator, without raw data."""
from waterfront_drawing import *
import preview_locator_journey as locator

WIDTH,HEIGHT,PAD=5839,1500,400
def export():
    c=Drawing();c.im=Image.new('RGB',(WIDTH,HEIGHT),WHITE);c.d=ImageDraw.Draw(c.im)
    for name in ['back','middle','front']:
        layer=Image.open(OUT/f'final_skyline_{name}.png').convert('RGBA').crop((PAD,0,PAD+WIDTH,HEIGHT))
        c.im.paste(layer,(0,0),layer)
    c.d=ImageDraw.Draw(c.im)
    c.rect(0,0,WIDTH,260,WHITE)
    c.text(80,65,'DAY 05  /  SIGHT',23,TEAL)
    c.text(80,155,'Seeing New York from the Water',78,serif=True)
    c.text(84,210,'Lower Manhattan · An interpretive paper skyline',25,MUTED)
    c.rect(80,1040,WIDTH-160,300,SEA)
    c.line([(80,1040),(WIDTH-80,1040)],'#6699AB',3)
    for x,y,length in [(180,1130,135),(830,1260,180),(1520,1165,140),(2380,1230,170),(3100,1155,130),(3830,1280,180),(4510,1195,165),(5180,1250,150)]:
        c.line([(x,y),(x+length*.3,y-2),(x+length*.6,y+1),(x+length,y)],'#B0D3E1',2)
    c.rect(0,260,79,1080,WHITE);c.rect(WIDTH-79,260,80,1080,WHITE)
    c.text(84,1390,'An interpretive skyline · Three-layer parallax.',25,MUTED)
    c.line([(80,1420),(WIDTH-80,1420)],'#C8DCE4',1)
    c.text(84,1462,'NYC OTI buildings · NYC DCP · NYC Ferry · Wikidata / LPC / Skyscraper Museum',20,MUTED)
    c.text(WIDTH-80,1462,'Ming Cao',29,NAVY,serif=True,anchor='end')
    c.im.save(OUT/'seeing_new_york_scroll.jpg',quality=97,subsampling=0,dpi=(180,180))
    m,_=locator.draw_locator(.5);x,y,w,h=locator.CARD
    m.im.crop((x,y,x+w,y+h)).save(OUT/'seeing_new_york_locator.jpg',quality=97,subsampling=0,dpi=(180,180))
    svg='\n'.join(m.s).replace(f'width="{locator.GIF_W}" height="{locator.GIF_H}" viewBox="0 0 {locator.GIF_W} {locator.GIF_H}"',f'width="{w}" height="{h}" viewBox="{x} {y} {w} {h}"',1)
    (OUT/'final_locator_middle.svg').write_text(svg,encoding='utf8')
    print('Exported full scroll (5839 x 1500), midpoint locator (496 x 225).')
if __name__=='__main__':export()
