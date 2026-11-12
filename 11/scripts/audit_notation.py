from pathlib import Path
import csv,json,collections,unicodedata
D=Path(__file__).resolve().parents[1]/'data'
records=list(csv.DictReader((D/'water_records.csv').open(encoding='utf-8-sig')))
inv=json.loads((D/'rime_inventory_by_site.json').read_text(encoding='utf-8'))
target=['œy','øi','øy']
rows=[]
for r in records:
 if r['final'] not in target:continue
 rows.append(dict(site_original=r['site_original'],water_final=r['final'],unicode_codepoints=' '.join(f'U+{ord(c):04X}' for c in r['final']),all_three_in_same_workbook='；'.join(s for s in target if s in inv[r['site_original']]),source_workbook=r['source_workbook'],source_row=r['source_row'],interpretation_status='保持独立；现有官方凡例不足以确认跨文献等价或实际语音差异'))
with (D/'notation_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={x:dict(water_count=sum(r['final']==x for r in records),workbooks_containing=sum(x in v for v in inv.values()),water_sites=[r['site_original'] for r in records if r['final']==x]) for x in target}
summary['workbooks_with_multiple_target_forms']={k:[x for x in target if x in v] for k,v in inv.items() if sum(x in v for x in target)>1}
(D/'notation_audit_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
