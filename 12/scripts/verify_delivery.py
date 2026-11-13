"""Read-only validation of the final four files, links, animation and Git exclusions."""
import argparse,hashlib,json,re,subprocess,sys
import numpy as np
from PIL import Image
import project as p

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser',action='store_true',help='Also test playback with an installed Chromium browser')
    args=parser.parse_args();results={}
    expected=set()
    for spec in p.FINAL['snapshots']:
        png=p.ROOT/spec['png'];gif=p.ROOT/spec['gif'];expected.update([png.name,gif.name])
        assert p.digest(png)==spec['approved_png_sha256']
        with Image.open(png) as im:im.load();assert im.size==(3840,3520) and im.format=='PNG'
        report=json.loads((p.ROOT/f"metadata/{spec['name']}_gif.json").read_text())
        assert report['time_utc']==spec['time_utc'] and report['png_sha256']==p.digest(png)
        assert report['gif_sha256']==p.digest(gif) and report['direction']['reverse_segments']==0
        durations=[];hashes=[];previous=None;changes=[]
        with Image.open(gif) as im:
            assert im.n_frames>1 and im.info['loop']==0
            size=im.size
            for i in range(im.n_frames):
                im.seek(i);durations.append(im.info['duration']);a=np.array(im.convert('RGB'))
                hashes.append(hashlib.sha256(a.tobytes()).hexdigest())
                if previous is not None:changes.append(int(np.any(a!=previous,axis=2).sum()))
                previous=a
        assert len(set(hashes))==len(hashes)==report['frames'] and min(changes)>1000
        assert sum(durations)/1000==report['duration_s'] and list(size)==report['size']
        assert report['all_fixed_pixels_and_text_identical'] and report['loop_endpoint_exact']
        if args.browser:
            subprocess.run([sys.executable,'-B',str(p.ROOT/'scripts/check_gif_browser.py'),
                '--gif',spec['gif'],'--report',f"metadata/{spec['name']}_browser.json"],check=True)
        browser_path=p.ROOT/f"metadata/{spec['name']}_browser.json"
        if browser_path.exists():
            browser=json.loads(browser_path.read_text())
            assert browser['playback_verified'] and browser['gif_sha256']==p.digest(gif)
        static_path=p.ROOT/f"metadata/{spec['name']}_static.json"
        reproduced=None
        if static_path.exists():
            check=json.loads(static_path.read_text());reproduced=check['approved_png_exactly_reproduced']
            assert reproduced and check['png_sha256']==p.digest(png)
        results[spec['name']]={'png_bytes':png.stat().st_size,'gif_bytes':gif.stat().st_size,
            'png_size':[3840,3520],'gif_size':list(size),'gif_frames':len(hashes),'gif_distinct_frames':len(set(hashes)),
            'duration_s':sum(durations)/1000,'fps':report['fps'],'png_exact_reproduction_verified':reproduced,
            'browser_playback_verified':browser_path.exists(),'direction_reverse_segments':0,
            'adjacent_changed_pixels_min_median_max':np.percentile(changes,[0,50,100]).tolist()}
    assert {q.name for q in (p.ROOT/'output').iterdir()}==expected,'Unexpected non-final output remains'
    links=[]
    for name in ['README.md','METHODS.md']:
        for ref in re.findall(r'\]\(([^)]+)\)',(p.ROOT/name).read_text(encoding='utf-8')):
            if '://' in ref or ref.startswith('#'):continue
            assert (p.ROOT/ref.split('#')[0]).exists(),f'Broken {name} link: {ref}'
            links.append(ref)
    repository=p.ROOT.parent
    artifacts=[q for q in (p.ROOT/'data/cache').rglob('*') if q.is_file() and q.name!='.gitkeep']
    for path in artifacts:
        check=subprocess.run(['git','check-ignore','-q',str(path)],cwd=repository)
        assert check.returncode==0,f'Cache is eligible for accidental commit: {path}'
    tracked=subprocess.check_output(['git','ls-files','--','12/data/cache'],cwd=repository,text=True).splitlines()
    assert all(x.endswith('/.gitkeep') for x in tracked),'Raw/derived cache is already tracked'
    report={'files':results,'output_exactly_four_files':True,'relative_links_verified':links,
            'cache_files_ignored':len(artifacts),'tracked_large_cache_files':False,
            'no_mp4':not any((p.ROOT/'output').glob('*.mp4'))}
    p.write_report('final_validation.json',report)
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
