"""Offline, provisional review of the existing seven-day snapshot. No network calls."""
from pathlib import Path
import csv, re, json, html, hashlib
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/processed'
OUT.mkdir(parents=True, exist_ok=True)
CATEGORIES = ['Mechanical & Equipment', 'Congestion', 'Signal & Switch',
              'Slippery Rails & Weather', 'Track & Infrastructure',
              'Staffing & Operations', 'External Incidents', 'Other / Unknown']
RULES = [
 ('Mechanical & Equipment', r'\b(?:mechanical|mechanial)\s+(?:issues?|problems?)|\bequipment availability(?: issues)?|\ba disabled train\b|\bdisabled train\b'),
 ('Congestion', r'\bcongestion\b'),
 ('Signal & Switch', r'\b(?:Amtrak )?(?:signal|switch)\s+(?:issues?|problems?)\b'),
 ('Slippery Rails & Weather', r'\bslippery rail conditions\b|\b(?:fallen|downed) trees?\b|\b(?:weather|flooding|snow|wheel slippage)\b'),
 ('Track & Infrastructure', r'\b(?:Amtrak )?track maintenance\b|\b(?:Amtrak )?(?:overhead|overheard) wire (?:issues?|problems?)\b|\bopening of the Conrail Delair Bridge for marine traffic\b'),
 ('Staffing & Operations', r'\bcrew availability\b|\b(?:originally scheduled )?engineer (?:availability|not (?:being )?available)\b|\boperational issue\b|\blate connection(?: with train)?\b|\blate train\b|\b(?:accommodat(?:e|ing)|accomodat(?:e|ing)) (?:customers|passengers)\b|\bmaking additional stops\b|\bholding\b'),
 ('External Incidents', r'\b(?:request for (?:police|EMS|medical) assistance|customer assistance|police activity|police (?:removal|attempting|investigating)|(?:motor )?vehicle (?:being )?stuck|unruly customer|trespassers?)\b'),
]

def write_csv(path, rows):
    if not rows: return
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def cause_matches(s):
    found=[]
    for cat, pattern in RULES:
        for m in re.finditer(pattern, s, re.I): found.append((m.start(),m.end(),cat,m.group()))
    return sorted(found)

def clean(s): return html.unescape(re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ', s))).strip()

ROUTE_PATTERNS = [
 ('NJCL',r'North Jersey Coast(?: Line)?|NJCL'), ('NEC',r'Northeast Corridor|NEC'),
 ('RVL',r'Raritan Valley(?: Line)?|RVL'), ('ACRL',r'Atlantic City Rail Line|ACRL'),
 ('MNE',r'Morris(?: and| &)? Essex(?: Line)?|M and E'), ('MBPJ',r'Main[/-]Bergen(?: County)?(?: Line)?|MBPJ'),
 ('MOBO',r'Montclair-Boonton(?: Line)?|MOBO'), ('PVL',r'Pascack Valley(?: Line)?|PVL')]

source=ROOT/'data/sample/alerts_2026-11-09_2026-11-15.csv'
raw=list(csv.DictReader(source.open(encoding='utf-8-sig')))
assert len(raw)==269
records=[]
for r in raw:
    day=r['date']; ordinal=int(r['page_ordinal']); nid=f"NJTLOCAL-{day}-{ordinal:03d}"
    # Independently verify the saved CSV against the preserved HTML, not a new request.
    blocks=re.findall(r'<div class="logs__item">(.*?)</dl></div>',(ROOT/f'data/sample/day_{day}.txt').read_text(encoding='utf-8'),re.S)
    block=blocks[ordinal-1]
    html_text=clean(re.search(r'<dd class="text-muted">(.*?)</dd>',block,re.S)[1])
    encoding_difference=html_text!=r['text']
    assert re.sub(r'[^\x00-\x7f]','',html_text)==re.sub(r'[^\x00-\x7f]','',r['text']), nid
    t=html_text; lower=t.lower()
    # Replacement-train instructions do not describe the primary train's status/cause.
    primary=re.split(r'\bPlease take\b|\bSubstitute bus\b|\bCustomers should\b', t, flags=re.I)[0].strip()
    if nid.endswith('2026-11-09-038'):
        primary=primary.split('MOBO train')[0].strip() # embedded secondary service notice
    head=re.sub(r'^(?:update\s*\d*\s*:|correction\s*:)\s*','',primary,flags=re.I)
    body_route='Unknown'
    for code,pattern in ROUTE_PATTERNS:
        if re.match(r'(?:'+pattern+r')\b',head,re.I): body_route=code; break
    affected=body_route if body_route!='Unknown' else r['route_code'] or 'Unknown'
    train_match=re.search(r'\btrain\s*#\s*(\d+)\b',head,re.I) or re.match(r'MBPJ\s*#\s*(\d+)\b',head,re.I)
    train=train_match[1].zfill(4) if train_match else ''
    # Do not mistake the connection train in an incomplete primary statement for the subject.
    if nid=='NJTLOCAL-2026-11-12-044': train=''
    causal=re.search(r'\b(?:due to|following)\s+(.*)',primary,re.I)
    cause=causal[1].strip().rstrip(' .') if causal else ''
    if not cause and 'track-level boarding' in lower:
        cause='Amtrak track maintenance' # explicit 'for' clause in boarding advisory
    if not cause and re.search(r'\bto accommodat',primary,re.I):
        cause=primary[re.search(r'\bto accommodat',primary,re.I).start()+3:].strip(' .')
    matches=cause_matches(cause)
    direct=matches[0][2] if matches else 'Other / Unknown'
    direct_phrase=matches[0][3] if matches else ('speed restriction' if 'speed restriction' in cause.lower() else 'Unknown')
    # Order in the causal clause, not keyword priority across the whole notice.
    split=re.search(r'\b(?:resulting from|due to)\s+',cause,re.I)
    if not split and direct in ('Congestion','Staffing & Operations','Mechanical & Equipment'):
        split=re.search(r'\bfrom\s+',cause,re.I)
    upstream=''; upstream_cat=''; relation='none explicitly stated'
    if split:
        downstream_matches=cause_matches(cause[:split.start()])
        upstream_text=cause[split.end():]
        upstream_matches=cause_matches(upstream_text)
        if downstream_matches:
            relation='explicit causal chain in same notice'
            upstream=upstream_text.strip(' .')
            upstream_cat=upstream_matches[0][2] if upstream_matches else 'Other / Unknown'
    additional=[]
    for _,_,cat,phrase in matches:
        if cat!=direct and cat not in additional: additional.append(cat)
    restoration=bool(re.search(r'\b(?:will operate today|operating on or close to schedule)\b',primary,re.I))
    canceled=bool(re.search(r'\b(?:is|was|will be)\s+(?:up to is\s+)?cancel(?:led|ed)\b|\bis up to is cancelled\b',primary,re.I))
    delayed=bool(re.search(r'\b(?:up to|operating)\s+(?:is cancelled|\d+|1-hour)',primary,re.I))
    if restoration: typ='restoration'; exclusion='restoration / operating normally'
    elif 'track-level boarding' in lower: typ='accessibility_advisory'; exclusion='boarding advisory; no primary delay/cancellation'
    elif canceled: typ='cancellation'; exclusion=''
    elif delayed: typ='delay'; exclusion=''
    elif re.search(r'will depart.*to accommodat',primary,re.I): typ='delayed_departure'; exclusion=''
    elif re.search(r'will (?:be making|make).*stop',primary,re.I): typ='stopping_pattern_advisory'; exclusion='stopping advisory; no primary delay/cancellation'
    else: typ='unclear_service_change'; exclusion='unclear primary status; excluded pending review'
    include=not bool(exclusion)
    conf='High' if matches else 'Low'
    notes=[]
    if re.search(r'\b(?:overheard|mechanial)\b',cause,re.I):
        conf='Medium'; notes.append('interpreted explicit typo; original retained')
    if nid=='NJTLOCAL-2026-11-12-063':
        notes.append('engineer unavailability explicit; cancellation only implied, not counted')
    if nid=='NJTLOCAL-2026-11-09-037':
        conf='Medium'; notes.append('revised departure 08:06 versus scheduled 07:19; no minutes inferred')
    if nid=='NJTLOCAL-2026-11-09-038':
        notes.append('embedded MOBO #1006 rescheduling retained as text; primary MNE cancellation counted once')
    if body_route!=r['route_code'] and body_route!='Unknown': notes.append('website route corrected using explicit primary route text')
    if not train: notes.append('primary train unknown; connection train not used as subject')
    if restoration or typ.endswith('advisory'): notes.append('kept in audit table, excluded from mapped notice count')
    if not matches and cause: notes.append('reported cause retained without forcing broad category')
    if not include: conf='Not applicable' if not cause else conf
    # Only causal-clause locations. Cancellation site is separately retained, never treated as cause site.
    locs=re.findall(r'\b(?:near|between|east of|at|in)\s+[^.;]+',cause,re.I)
    locs=[v for v in locs if not re.search(r'\b(?:time of departure|originally scheduled)\b',v,re.I)]
    loc=' | '.join(locs)
    precision='Affected rail line only' if affected!='Unknown' else 'System-wide / unknown location'
    detail='no incident location stated' if not loc else 'approximate locality / station vicinity / interval; not geocoded'
    stations=json.loads((ROOT/'data/gis/rail_stations.geojson').read_text(encoding='utf-8'))
    names=[f['properties']['STATION_ID'] for f in stations['features']]
    station_aliases=names+['Ho-Ho-Kus','Newark Broad St','Netherwood','Princton Junction','Metuchen','Elizabeth','Middletown']
    station_candidate=False
    for location in locs:
        if location.lower().startswith('at ') and any(re.search(r'\b'+re.escape(n)+r'\b',location,re.I) for n in station_aliases):
            station_candidate=True
            if re.search(r'\bstation\b',location,re.I):
                precision='Station-level location';detail='station explicitly named in causal clause; geocoding not performed'
            else:
                detail='station-name candidate but locality/process role ambiguous; retained at line precision'
            break
    cancel_loc=re.search(r'cancel(?:led|ed) at ([^.]+?) (?:due to|following)',primary,re.I)
    schedule=re.findall(r'\b\d{1,2}:\d{2}\s*[AP]M\b',primary,re.I)
    records.append(dict(notice_identifier=nid,identifier_provenance='local date + saved-page ordinal; NOT official ID',date=day,
      page_ordinal=ordinal,timestamp_display=r['timestamp_display'],source_url=r['source_url'],raw_route=r['route_code'],
      body_route=body_route,affected_route=affected,route_conflict=body_route not in ('Unknown',r['route_code']),
      primary_train=train,scheduled_times=' | '.join(schedule),reported_cause=cause or 'Unknown',
      direct_cause=direct_phrase,cause_category=direct,upstream_cause=upstream or 'Unknown',upstream_category=upstream_cat or 'Unknown',
      causal_relation=relation,additional_cause_categories=' | '.join(additional),website_cause_slugs=r['website_cause_slugs'],
      classification_basis=('first explicit cause phrase in primary causal clause: '+direct_phrase) if matches else 'no covered explicit cause phrase; no inference from destination or replacement trains',
      classification_confidence=conf,classification_status='provisional agent review; not final / not externally validated',
      notification_type=typ,duplicate_update_group='',group_confidence='',group_basis='',candidate_train_day_group=(f'{day}-{affected}-{train}' if train else 'Unknown'),
      location_precision=precision,incident_location_text=loc or 'Unknown',location_detail=detail,
      station_name_candidate=station_candidate,location_confidence=('High for station reference, not exact point' if precision=='Station-level location' else 'Unknown / approximate'),
      location_role=('upstream cause/context' if loc and upstream and any(v in upstream for v in locs) else 'direct reported cause/process' if loc else 'Unknown'),
      cancellation_location=(cancel_loc[1] if cancel_loc else 'Unknown'),include_notice_analysis=include,
      exclude_reason=exclusion,representative_in_group=False,review_notes='; '.join(notes),
      sample_csv_encoding_difference=encoding_difference,original_text=t,sample_csv_text=r['text']))

# Explicitly reviewed update sequences. No automatic train-day or shared-location merge.
# Each group keeps distinct trains and calendar dates separate. Different causes stay separate.
GROUPS = [
 ('2026-11-09',[32,37],'same MOBO #1006 scheduled departure and cancelled #0808 accommodation'),
 ('2026-11-09',[38,39],'same MNE #0808 departure, mechanical cancellation and replacement update'),
 ('2026-11-10',[11,14],'same #0430 scheduled arrival and trespasser-removal sequence'),
 ('2026-11-10',[12,13],'same #0485 scheduled arrival and trespasser-removal sequence'),
 ('2026-11-11',[3,5],'same #0059 scheduled arrival, Otisville mechanical delay then cancellation'),
 ('2026-11-11',[9,10,12,15,17,18,20],'same #1357 scheduled arrival, vehicle on tracks near Broadway, increasing estimates'),
 ('2026-11-11',[28,30,31],'same #5421 scheduled arrival and Netherwood switch problem'),
 ('2026-11-11',[36,37],'explicit Correction on #6209; scheduled arrival corrected 06:31 to 06:57'),
 ('2026-11-11',[38,41],'same #3818 departure, cancellation followed by restoration'),
 ('2026-11-12',[4,9],'same #0435 scheduled arrival and slippery rail conditions'),
 ('2026-11-12',[8,25],'same #0432 scheduled arrival and slippery rails; #432 padded locally'),
 ('2026-11-12',[20,23],'same #6647 scheduled arrival and slippery rail conditions'),
 ('2026-11-12',[22,33],'same #0853 arrival and Summit switch issue; #853 padded locally'),
 ('2026-11-12',[40,43],'same #3943 scheduled departure and mechanical cancellation; spelling variant'),
 ('2026-11-12',[53,54],'same #0415 scheduled arrival and slippery rails, delay then cancellation'),
 ('2026-11-13',[7,14],'same #3866 arrival and equipment availability; mechanical upstream added'),
 ('2026-11-13',[11,26],'same #1173 departure, cancellation followed by restoration'),
 ('2026-11-13',[28,29],'same #9162 departure and mechanical cancellation; replacement update'),
 ('2026-11-13',[36,37],'same #3722 arrival and mechanical delay; explicit update'),
 ('2026-11-15',[4,5],'same #4682 scheduled arrival, EMS in Hammonton, 20 then 25 minutes'),
]
# #6621 has only one preserved notification in this snapshot, despite Update 3.
# Missing updates are not invented.
lookup={r['notice_identifier']:r for r in records}
for day,ords,basis in GROUPS:
    # Prior groups use date-page ordinals, never global CSV row numbers.
    members=[lookup[f'NJTLOCAL-{day}-{i:03d}'] for i in ords]
    assert len({r['primary_train'] for r in members})==1, (day,ords)
    assert len({r['affected_route'] for r in members})==1
    gid=f'UPDLOCAL-{day}-{min(ords):03d}'
    for r in members:
        r['duplicate_update_group']=gid;r['group_confidence']='High';r['group_basis']=basis
for r in records:
    if not r['duplicate_update_group']:
        r['duplicate_update_group']='SINGLE-'+r['notice_identifier'];r['group_confidence']='Not merged'
        r['group_basis']='no verified matching sequence; shared train-day/location alone is insufficient'
groups=defaultdict(list)
for r in records: groups[r['duplicate_update_group']].append(r)
for gid,rs in groups.items():
    included=[r for r in rs if r['include_notice_analysis']]
    if included:
        # pages reverse chronological; smaller ordinal is latest. Historical disruption notices
        # remain counted even if a later restoration was issued; this is not final service status.
        min(included,key=lambda r:r['page_ordinal'])['representative_in_group']=True
    cats={r['cause_category'] for r in included}
    assert len(cats)<=1, (gid,cats)

write_csv(OUT/'notices_reviewed.csv',records)
inc=[r for r in records if r['include_notice_analysis']]
reps=[r for r in records if r['representative_in_group']]
write_csv(OUT/'analysis_representatives.csv',reps)
group_rows=[dict(group_id=g,notice_ids=' | '.join(r['notice_identifier'] for r in rs),size=len(rs),
                included_notices=sum(r['include_notice_analysis'] for r in rs),basis=rs[0]['group_basis']) for g,rs in groups.items() if len(rs)>1]
write_csv(OUT/'update_groups.csv',group_rows)
cat_rows=[]
for cat in CATEGORIES:
    cat_rows.append(dict(category=cat,raw_classified=sum(r['cause_category']==cat for r in records),
      eligible_notices=sum(r['cause_category']==cat for r in inc),representatives=sum(r['cause_category']==cat for r in reps)))
write_csv(OUT/'category_counts.csv',cat_rows)
route_rows=[]
for cat in CATEGORIES:
    for route in ['ACRL','MBPJ','MNE','MOBO','NEC','NJCL','PVL','RVL','Unknown']:
        route_rows.append(dict(category=cat,route=route,eligible_notices=sum(r['cause_category']==cat and r['affected_route']==route for r in inc),
          representatives=sum(r['cause_category']==cat and r['affected_route']==route for r in reps)))
write_csv(OUT/'cause_route_counts.csv',route_rows)
summary=dict(raw_records=len(records),eligible_notices=len(inc),excluded_notices=len(records)-len(inc),
 update_adjusted_representatives=len(reps),additional_updates=len(inc)-len(reps),
 exclusions=dict(Counter(r['exclude_reason'] for r in records if not r['include_notice_analysis'])),
 notification_types=dict(Counter(r['notification_type'] for r in records)),
 route_corrections=sum(r['route_conflict'] for r in records),
 location_precision=dict(Counter(r['location_precision'] for r in records)),
 confidence=dict(Counter(r['classification_confidence'] for r in inc)),
 multiple_cause_phrases=sum(len(cause_matches(r['reported_cause']))>1 for r in records),
 explicit_upstream=sum(r['causal_relation']!='none explicitly stated' for r in records),
 verified_update_groups=len(group_rows),categories=cat_rows,
 original_csv_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
(OUT/'cleaning_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2,ensure_ascii=False))
