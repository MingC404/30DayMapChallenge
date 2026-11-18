from PyPDF2 import PdfFileReader as PdfReader
import json
r=PdfReader('17/raw/LightList_V1_2025.pdf');result={'pages':len(r.pages),'title_pages':[r.pages[i].extractText() for i in range(min(3,len(r.pages)))],'samples':[]}
for i,p in enumerate(r.pages):
 t=p.extractText() or ''
 if any(n in t.lower() for n in ['romer shoal','buttermilk channel range front','sandy hook light']):result['samples'].append({'page_pdf_1based':i+1,'text':t})
json.dump(result,open('17/raw/annual_volume_audit.json','w'),indent=2);print('pages',len(r.pages),'sample pages',[x['page_pdf_1based'] for x in result['samples']]);print(result['title_pages'][0][:2000])

