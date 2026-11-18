from lxml import etree as E
import json
p=E.parse('17/raw/enc_catalog.xml'); ns={'g':'http://www.isotc211.org/2005/gmd','c':'http://www.isotc211.org/2005/gco'}
out=[]
for m in p.findall('.//g:MD_Metadata',ns):
 def t(q): return m.xpath(q,namespaces=ns)
 names=t('.//g:CI_Citation/g:title/c:CharacterString/text()')
 if not names:continue
 name=names[0]
 if name[2:3] not in ['4','5','6']:continue
 positions=m.xpath('.//*[local-name()="pos"]/text()')
 if not positions:continue
 coords=[list(map(float,v.split())) for v in positions]
 w,e=min(v[1] for v in coords),max(v[1] for v in coords)
 s,n=min(v[0] for v in coords),max(v[0] for v in coords)
 if e< -74.2 or w> -73.85 or n<40.4 or s>40.72:continue
 out.append({'cell':name,'title':t('.//g:alternateTitle/c:CharacterString/text()'),'edition':t('.//g:edition/c:CharacterString/text()'),'dates':t('.//g:CI_Date/g:date/c:Date/text()'),'urls':t('.//g:URL/text()'),'bbox':[w,s,e,n]})
json.dump(out,open('17/raw/enc_selected_catalog.json','w'),indent=2);print(json.dumps(out,indent=2))
