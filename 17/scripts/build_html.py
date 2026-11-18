"""Bundle final scene and all runtime resources into one offline HTML."""
from pathlib import Path
import json,base64
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'src'
data=json.loads((SRC/'scene.json').read_text(encoding='utf-8'))
data['images']={p.stem:'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode('ascii') for p in (SRC/'assets').glob('*.png')}
html=(SRC/'template.html').read_text(encoding='utf-8-sig')
for key,value in {'__CSS__':(SRC/'style.css').read_text(encoding='utf-8-sig'),'__DATA__':json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/'),'__MODEL__':(SRC/'model.js').read_text(encoding='utf-8-sig'),'__APP__':(SRC/'app.js').read_text(encoding='utf-8-sig')}.items():html=html.replace(key,value)
(ROOT/'day17.html').write_text(html,encoding='utf-8');print('Built standalone 17/day17.html')
