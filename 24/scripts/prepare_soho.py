"""Extend verified Summit service patterns to one illustrative SoHo workplace."""
from pathlib import Path
import json,csv
ROOT=Path(__file__).resolve().parents[1]/'summit';D=ROOT/'data'
def main():
 a=json.loads((D/'routes.json').read_text());n=a['nodes'];s=a['segments']
 n.update(work=[-73.9996,40.7233],canal=[-74.0018,40.7188],union=[-73.9906,40.7357],herald=[-73.9877,40.7496],christopher=[-74.0070,40.7329],wtc=[-74.0114,40.7126])
 def leg(id,mode,start,end,via,basis,direction=None):
  s[id]={'mode':mode,'from':start,'to':end,'coordinates':[n[start]]+via+[n[end]],'geometry_basis':basis}
  if direction:s[id]['direction']=direction
 leg('work_canal','walk','work','canal',[[-73.9999,40.7229],[-74.0018,40.7190]],'Illustrative Broadway/Spring workplace, walk south along Broadway to Canal Q entrance')
 leg('q','subway','canal','herald',[[-73.9973,40.7257],n['union'],[-73.9896,40.7411]],'MTA Q weekday line map and timetable effective 2026-05-17; Canal–14 St Union Sq–34 St Herald Sq, express','Uptown / 96 St')
 leg('herald_penn','walk','herald','nyp',[[-73.9886,40.7488],[-73.9919,40.7503]],'Generalized W 33rd Street access from Herald Square to NY Penn')
 leg('herald_ferry','walk','herald','ferry39',[[-73.9890,40.7501],[-73.9998,40.7546],[-74.0062,40.7560]],'Generalized W 34th Street–12th Avenue–W 39th Street / Pier 79 access; no platform/walking times')
 leg('work_christopher','walk','work','christopher',[[-74.0038,40.7251],[-74.0065,40.7257],[-74.0082,40.7317]],'Generalized walk through SoHo to Christopher Street PATH via Houston/Hudson/Christopher streets')
 leg('path_christopher','path','christopher','hobpath',[[-74.0120,40.7330],[-74.0200,40.7341]],'HOB–33 weekday service, board at Christopher Street, select Hoboken-bound (not Journal Square)','Hoboken')
 leg('work_wtc','walk','work','wtc',[[-74.0018,40.7188],[-74.0052,40.7148],[-74.0090,40.7131]],'Generalized Broadway/Vesey Street access to WTC PATH')
 leg('path_newark','path','wtc','newark',[[-74.0340,40.7167],[-74.0430,40.7196],[-74.0630,40.7324],[-74.1000,40.7430],[-74.1540,40.7390]],'Station-based Newark–WTC corridor via Exchange Place, Grove Street, Journal Square and Harrison','Newark')
 # Split the common M&E section at Broad Street for one shared compressed diagram.
 old=s['west']['coordinates'];b=n['broad'];idx=min(range(len(old)),key=lambda i:(old[i][0]-b[0])**2+(old[i][1]-b[1])**2)
 leg('joint_broad','njt','joint','broad',old[1:idx],'NJT M&E corridor, joint to Newark Broad Street')
 s['common']=dict(s['broad_west']);s['common']['display_basis']='Fixed compressed station diagram; station order and broad relative directions retained'
 a['routes']=[
  {'id':'usual','title':'Usual: Q + Midtown Direct','segments':['work_canal','q','herald_penn','usual_east','joint_broad','common'],'status':'Usual pattern; regular M&E reference 2026-11-17. Midtown Direct not running on cutover weekday.'},
  {'id':'path','title':'Walk + PATH via Hoboken','segments':['work_christopher','path_christopher','walk_hobpath','hoboken_east','joint_broad','common'],'status':'Weekday HOB–33 line and cutover M&E service-plan verified; no historical timed itinerary.'},
  {'id':'ferry','title':'Q + ferry via Hoboken','segments':['work_canal','q','herald_ferry','ferry','walk_hobferry','hoboken_east','joint_broad','common'],'status':'Q weekday pattern and dated W39–Hoboken ferry cutover plan verified; no historical timed itinerary.'},
  {'id':'newark','title':'PATH + light rail via Newark','segments':['work_wtc','path_newark','nlr','common'],'status':'PATH weekday topology and continuing M&E plan verified; NLR station link verified; no historical timed itinerary.'}
 ]
 a['workplace_note']='Illustrative origin at Broadway / Spring Street, not a claimed personal office address.'
 a['display']='Hybrid schematic: geographic Manhattan/Hudson/Newark; common Broad–Summit leg compressed, fixed in every frame.'
 for r in a['routes']:
  assert s[r['segments'][0]]['from']=='work' and s[r['segments'][-1]]['to']=='summit'
  for x,y in zip(r['segments'],r['segments'][1:]):assert s[x]['to']==s[y]['from']
 (D/'soho_routes.json').write_text(json.dumps(a,indent=2))
 evidence=json.loads((D/'evidence.json').read_text())
 evidence['current_origin']={'label':'SoHo / Work','coordinates':n['work'],'basis':a['workplace_note']}
 evidence['soho_access']=[
  {'route':'usual','direction':'Canal St Q platform, uptown / 96 St to 34 St–Herald Sq; walk to New York Penn','sources':['q_timetable','q_line_map'],'scope':'Q timetable effective 2026-05-17 and weekday station map updated 2026-02-26; ordinary service pattern, no historical day-of incident reconstruction'},
  {'route':'path','direction':'Walk to Christopher Street, select Hoboken-bound HOB–33 service','sources':['path_line_map','path_advisory','path_scenario_week'],'scope':'Weekday station/line topology plus dated cutover service plan; indexed official pages readable, retained direct PATH HTML is a small shell'},
  {'route':'ferry','direction':'Q uptown to Herald Square, walk to W 39th Street, NY Waterway to Hoboken NJ Transit Terminal','sources':['q_timetable','q_line_map','nyw_advisory'],'scope':'Retains the terminal pair specifically supported by the October cutover advisory; no alternate downtown ferry or fare eligibility assumed'},
  {'route':'newark','direction':'Walk to WTC, Newark-bound PATH to Newark Penn, NLR Broad Street branch, westbound M&E to Summit','sources':['path_line_map','path_scenario_week','nlr_map','newark_connection','mne_regular'],'scope':'Weekday network/service-plan level; no historical through-journey departure/transfer times established'}]
 evidence['fare_scope']='No cross-honoring assumed at Christopher Street or World Trade Center. Existing announcement restricts PATH acceptance to designated Hoboken/33rd Street arrangements.'
 (D/'evidence.json').write_text(json.dumps(evidence,indent=2))
 with (D/'route_verification.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.writer(f);w.writerow(['route','origin','destination','legs','direction','verification','total_minutes'])
  for r in a['routes']:w.writerow([r['id'],'SoHo / Work','Summit Station',' > '.join(r['segments']),'; '.join(s[k].get('direction','') for k in r['segments'] if s[k].get('direction')),r['status'],'not established'])
 print('Prepared four complete SoHo–Summit journeys.')
if __name__=='__main__':main()
