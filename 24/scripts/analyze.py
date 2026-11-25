"""Analyze a frozen official feed; all artifacts confined to day 24."""
from pathlib import Path
import csv,io,zipfile,json,hashlib,datetime,itertools
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data'; O=ROOT/'outputs'
DATE='20261117'
def save(name,obj): (O/name).write_text(json.dumps(obj,indent=2),encoding='utf8')
def main():
 z=zipfile.ZipFile(D/'gtfs.zip')
 def table(n): return list(csv.DictReader(io.StringIO(z.read(n+'.txt').decode('utf-8-sig'))))
 tables={n:table(n) for n in ['feed_info','calendar','calendar_dates','routes','trips','stops','stop_times','shapes']}
 day=datetime.datetime.strptime(DATE,'%Y%m%d'); weekday=day.strftime('%A').lower()
 services={r['service_id'] for r in tables['calendar'] if r['start_date']<=DATE<=r['end_date'] and r[weekday]=='1'}
 for r in tables['calendar_dates']:
  if r['date']==DATE:
   if r['exception_type']=='1': services.add(r['service_id'])
   else: services.discard(r['service_id'])
 routes={r['route_id']:r for r in tables['routes'] if r['route_type']=='4'}
 trips={r['trip_id']:r for r in tables['trips'] if r['service_id'] in services and r['route_id'] in routes}
 times=[r for r in tables['stop_times'] if r['trip_id'] in trips]
 ids={r['stop_id'] for r in times}; stops={r['stop_id']:r for r in tables['stops'] if r['stop_id'] in ids}
 # Exact name + coordinate identity is the feed's landing evidence. No proximity-only merging.
 groups={}; membership={}
 for sid,s in stops.items():
  key=(s['stop_name'].strip().casefold(),s['stop_lat'],s['stop_lon'])
  groups.setdefault(key,[]).append(sid)
 landings={}
 for key,sids in groups.items():
  lid=min(sids,key=int); s=stops[lid]
  landings[lid]={'name':s['stop_name'],'lon':float(s['stop_lon']),'lat':float(s['stop_lat']),'stop_ids':sids,'basis':'Identical normalized stop_name and coordinates' if len(sids)>1 else 'Single active ferry stop_id; all feed stops audited separately','routes':{}}
  for sid in sids: membership[sid]=lid
 for t in times:
  lid=membership[t['stop_id']]; rid=trips[t['trip_id']]['route_id']; p=landings[lid]['routes'].setdefault(rid,{'board':False,'alight':False})
  p['board'] |= t.get('pickup_type','0') in ('','0'); p['alight'] |= t.get('drop_off_type','0') in ('','0')
 def edges(exclude=None):
  e={}
  for lid,l in landings.items():
   if lid==exclude:continue
   for a,b in itertools.permutations(l['routes'],2):
    if l['routes'][a]['alight'] and l['routes'][b]['board']:e.setdefault((a,b),[]).append(lid)
  return e
 nodes=sorted({r['route_id'] for r in trips.values()})
 def components(e):
  remaining=set(nodes); out=[]
  while remaining:
   stack=[min(remaining)]; found=set()
   while stack:
    a=stack.pop()
    if a in found:continue
    found.add(a); stack += [b for b in nodes if (a,b) in e or (b,a) in e if b not in found]
   remaining-=found;out.append(sorted(found))
  return out
 baseline=edges(); results=[]
 for lid,l in landings.items():
  if len(l['routes'])<2:continue
  e=edges(lid); lost=sorted(set(baseline)-set(e))
  results.append({'landing_id':lid,'landing':l['name'],'routes':sorted(l['routes']),'lost_directed_connections':[list(x) for x in lost],'lost_undirected_pairs':[list(x) for x in lost if x[0]<x[1]],'components':components(e),'components_count':len(components(e))})
 results.sort(key=lambda r:(-r['components_count'],-len(r['lost_undirected_pairs']),r['landing']))
 chosen=results[0]
 save('analysis.json',{'date':DATE,'weekday':weekday,'feed':tables['feed_info'][0],'sha256':hashlib.sha256((D/'gtfs.zip').read_bytes()).hexdigest(),'service_ids':sorted(services),'trip_count':len(trips),'stop_time_count':len(times),'routes':routes,'landings':landings,'baseline_components':components(baseline),'connections':[{'from':a,'to':b,'landing_ids':v} for (a,b),v in sorted(baseline.items())],'results':results,'selected':chosen})
 with (O/'landing_closures.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows({k:json.dumps(v) if isinstance(v,list) else v for k,v in r.items()} for r in results)
 with (O/'stop_grouping.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.writer(f);w.writerow(['stop_id','stop_name','lat','lon','active_ferry','landing_id','basis'])
  for s in tables['stops']:w.writerow([s['stop_id'],s['stop_name'],s['stop_lat'],s['stop_lon'],s['stop_id'] in ids,membership.get(s['stop_id'],''),'Exact identity audit; inactive/bus stops excluded' if s['stop_id'] not in ids else landings[membership[s['stop_id']]]['basis']])
 save('render_data.json',{'trips':list(trips.values()),'shapes':tables['shapes']})
 print(json.dumps({'baseline':components(baseline),'results':results},indent=2))
if __name__=='__main__': main()
