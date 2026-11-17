from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json
out=Path('typography_review');entries=json.loads(Path('scripts/gallery_entries.json').read_text(encoding='utf-8'));by={e['day']:e for e in entries};sheet=Image.new('RGB',(2400,2100),'#e8e4dc');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20);title=ImageFont.truetype('C:/Windows/Fonts/georgia.ttf',35)
d.text((30,20),'Typography audit / current final artwork',font=title,fill='#383832')
views=[(e,m) for e in entries for m in e['media']]
d.text((30,65),'15 completed days / 16 views; Day 07: no completed artwork. GIFs show opening frames; Day 13: local only.',font=font,fill='#77766e')
for n,(e,m) in enumerate(views):
 day=e['day'];x=30+n%4*595;y=110+n//4*495
 label='DAY '+day+(' / LOCAL ONLY' if day=='13' else '')+(' / '+m['label'] if day=='12' else '')
 d.text((x,y),label,font=font,fill='#383832')
 p=Path(m['source']);im=Image.open(p);im.seek(0);thumb=ImageOps.contain(im.convert('RGB'),(565,430));sheet.paste(thumb,(x+(565-thumb.width)//2,y+33))
sheet.save(out/'contact_sheet_current.png')
