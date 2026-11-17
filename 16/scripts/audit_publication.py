"""Local pre-publication audit. Does not clean, render, stage, deploy, or upload."""
from pathlib import Path
import csv,json,hashlib,re,html,subprocess
from collections import Counter,defaultdict
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent
OUT=ROOT/'outputs/publication_audit';OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def normal(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s))).strip()

def main():
    audit=rows(ROOT/'data/processed/notices_reviewed.csv')
    reps=rows(ROOT/'data/processed/analysis_representatives.csv')
    m=json.loads((ROOT/'outputs/animation_manifest.json').read_text(encoding='utf-8'))
    v=json.loads((ROOT/'outputs/final_validation.json').read_text(encoding='utf-8'))
    assert len(audit)==269 and len(reps)==234
    assert sha(ROOT/m['analysis_source'])==m['analysis_sha256']
    assert len({r['notice_identifier'] for r in reps})==len(reps)
    assert len({r['duplicate_update_group'] for r in reps})==len(reps)
    expected=Counter(r['cause_category'] for r in reps)
    assert dict(expected)==m['category_counts']
    assert sum(expected.values())==234 and expected['Other / Unknown']==2
    assert {r['date'] for r in audit}=={f'2026-11-{d:02d}' for d in range(9,16)}
    assert all(r['date'] in {f'2026-11-{d:02d}' for d in range(9,16)} for r in reps)
    eligible=[r for r in audit if r['include_notice_analysis']=='True']
    assert len(eligible)==258 and len(audit)-len(eligible)==11
    groups=defaultdict(list)
    for r in audit:groups[r['duplicate_update_group']].append(r)
    reductions=0
    for g,rs in groups.items():
        inc=[r for r in rs if r['include_notice_analysis']=='True']
        actual=[r for r in reps if r['duplicate_update_group']==g]
        assert len(actual)==int(bool(inc))
        reductions+=max(0,len(inc)-1)
        if len(rs)>1:
            assert len({(r['date'],r['affected_route'],r['primary_train']) for r in rs})==1
    assert reductions==24
    for f in m['frames']:
        assert f['count']==(len(reps) if f['cause']=='Overview' else expected[f['cause']])
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    required=['Question by Chiun Heng Chou','Mapping by Ming Cao',
      'Service notice statistics derived from NJ Transhit','Independent educational visualization; not affiliated with NJ Transit',
      'November 9–15, 2026','NJ TRANSIT GIS Department','U.S. Census Bureau']
    assert all(s in readme for s in required)
    for cat,n in expected.items():assert f'| {cat} | {n} |' in readme
    assert '**234**' in readme and '**232**' in readme
    artwork=[]
    for name in ('day16_njt_disruptions.gif','day16_njt_disruptions.png'):
        p=ROOT/'outputs'/name
        assert sha(p)==v['outputs'][name]['sha256']
        artwork.append({'file':name,'bytes':p.stat().st_size,'sha256':sha(p)})
    with Image.open(ROOT/'outputs/day16_njt_disruptions.gif') as im:
        assert im.n_frames==9 and im.info['loop']==0
        durations=[];frames=[]
        for i in range(im.n_frames):im.seek(i);durations.append(im.info['duration']);frames.append(im.convert('RGB').tobytes())
    assert sum(durations)==17500 and frames[0]==frames[-1]
    publicfiles=list((REPO/'docs').rglob('*'));publicfiles=[p for p in publicfiles if p.is_file()]
    source_hashes={sha(p):str(p.relative_to(ROOT)) for p in (ROOT/'data').rglob('*') if p.is_file()}
    matching_data=[str(p.relative_to(REPO)) for p in publicfiles if sha(p) in source_hashes]
    assert not matching_data
    txtfiles=[p for p in publicfiles if p.suffix.lower() in ('.html','.htm','.csv','.json','.js','.md','.txt','.css')]
    docs_text=' '.join(normal(p.read_text(encoding='utf-8',errors='replace')) for p in txtfiles)
    matched_notices=[r['notice_identifier'] for r in audit if normal(r['original_text']) in docs_text]
    assert not matched_notices
    registry=json.loads((REPO/'scripts/gallery_entries.json').read_text(encoding='utf-8'))
    assert not any(e['day']=='16' for e in registry)
    assert not any('/16/' in '/'+p.relative_to(REPO/'docs').as_posix() for p in publicfiles)
    sensitive=['16/data/sample/day_2026-11-09.txt','16/data/processed/notices_reviewed.csv',
               '16/data/processed/analysis_representatives.csv','16/data/gis/rail_lines.geojson',
               '16/outputs/publication_audit/njt_copyright.html']
    ignored={}
    for p in sensitive:
        run=subprocess.run(['git','check-ignore','--',p],cwd=REPO,capture_output=True,text=True)
        assert run.returncode==0,p
        ignored[p]=True
    tracked=subprocess.run(['git','ls-files','--','16/data','16/outputs/publication_audit'],cwd=REPO,capture_output=True,text=True,check=True).stdout.strip()
    assert not tracked
    result={'audit_date':'2026-11-16','technical_checks':'PASS',
      'publication_recommendation':'HOLD: rail/hub geometry public-derivative permission and applicability of NJT terms unresolved; NJ Transhit terms unknown',
      'original_notices':269,'eligible_notices':258,'excluded_notices':11,'linked_update_extra_counts_removed':24,
      'verified_update_groups':sum(len(rs)>1 for rs in groups.values()),'representatives':234,
      'unique_notice_and_update_group_ids':True,'category_counts':dict(expected),
      'classifications':'provisional, one direct category per representative; upstream not recounted',
      'time_window':'November 9–15, 2026; original display timezone unknown',
      'readme_required_credits_present':True,'artwork':artwork,'durations_ms':durations,
      'local_docs_files_examined':len(publicfiles),'copied_day16_data_hash_matches_in_docs':matching_data,
      'full_notice_text_matches_in_docs':matched_notices,'day16_in_gallery_registry':False,
      'sensitive_files_git_ignored':ignored,'sensitive_files_git_tracked':False,
      'scope_limit':'Local docs, registry, working tree and Git index checked. Live Pages settings, remote repository histories and unnamed college repository not verified.',
      'terms_snapshots':[{'file':p.name,'sha256':sha(p)} for p in OUT.iterdir() if p.suffix in ('.html','.json') and p.name!='audit_results.json']}
    (OUT/'audit_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
