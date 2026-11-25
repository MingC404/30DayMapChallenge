"""Freeze official service evidence for the independent Summit prototype."""
from pathlib import Path
import requests,json,hashlib,datetime,concurrent.futures
ROOT=Path(__file__).resolve().parents[1]/'summit';RAW=ROOT/'data/sources';RAW.mkdir(parents=True,exist_ok=True)
URLS={
 'q_timetable':'https://www.mta.info/schedules/subway/q-train',
 'q_line_map':'https://www.mta.info/maps/subway-line-maps/q-line',
 'path_line_map':'https://www.panynj.gov/path/en/index.html?os=___',
 'path_scenario_week':'https://www.panynj.gov/port-authority/en/press-room/press-release-archives/2026-press-releases/weekly-travel-advisory-for-oct--16-to-22----airtrain-newark-serv.html',
 'portalcut':'https://www.njtransit.com/portalcut',
 'njt_release':'https://www.njtransit.com/press-releases/portal-north-bridge-enters-final-phase-construction-work-begins-put-final-track',
 'path_advisory':'https://www.panynj.gov/port-authority/en/press-room/press-release-archives/2026-press-releases/path-travel-advisory2.html',
 'nyw_advisory':'https://nywaterway.com/UserFiles/Files/DRAFT%20Phase%202%20NY%20Waterway%20Cross%20Honoring%20NJT%20Media%20Advisory.pdf',
 'mne_regular':'https://content.njtransit.com/pdf/schedules/rail/MNE',
 'newark_connection':'https://www.njtransit.com/starting-your-trip-new-york-light-rail',
 'mne_oct_candidate':'https://content.njtransit.com/sites/default/files/pdfs/rail/2026/10/110002/mne.pdf',
 'mne_oct_candidate2':'https://content.njtransit.com/sites/default/files/pdfs/rail/2026/10/110026/mne.pdf',
 'mne_oct_candidate3':'https://content.njtransit.com/sites/default/files/2026-10/mne.pdf',
 'cutover_briefing':'https://media.amtrak.com/wp-content/uploads/2026/09/Portal-North-Bridge-Cutover-Briefing-Document-091726.pdf',
 'nlr_map':'https://content.njtransit.com/sites/default/files/pdfs/light-rail/NLR_052825.pdf',
 'newark_station':'https://www.njtransit.com/station/newark-penn-station',
}
def fetch(item):
 key,url=item
 for p in RAW.glob(key+'.*'):
  if p.suffix in ['.html','.pdf']:
   old=json.loads((RAW/'manifest.json').read_text())
   record=next((r for r in old if r['id']==key and 'file' in r),None)
   if record:return record
 try:
  r=requests.get(url,timeout=45);record={'id':key,'url':url,'resolved_url':r.url,'status':r.status_code,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  if r.ok:
   suffix='.pdf' if r.content[:4]==b'%PDF' else '.html';p=RAW/(key+suffix);p.write_bytes(r.content);record.update(file=p.name,sha256=hashlib.sha256(r.content).hexdigest(),bytes=len(r.content))
  return record
 except requests.RequestException as e:return {'id':key,'url':url,'error':str(e)}
def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex: records=list(ex.map(fetch,URLS.items()))
 (RAW/'manifest.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
