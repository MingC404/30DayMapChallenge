"""Reproduce the two approved final PNGs, or verify them without replacing files."""
import argparse,gc,json,subprocess,sys
from PIL import Image
from shapely.geometry import shape
from shapely import prepare
from numba import set_num_threads
import project as p
import render_final as render

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot',choices=['January','September'])
    parser.add_argument('--fetch',action='store_true',help='Reuse/resume official CDS downloader if necessary')
    parser.add_argument('--verify',action='store_true',help='Render in memory and compare exact RGB; do not overwrite PNGs')
    args=parser.parse_args();set_num_threads(8)
    sources={x.name:p.digest(x) for x in (p.ROOT/'data/cache').glob('*.nc')}
    land=shape(json.loads((p.ROOT/render.CFG['coastline_file']).read_text())['features'][0]['geometry']);prepare(land)
    canvas=render.RectCanvas(land)
    for spec in p.FINAL['snapshots']:
        if args.snapshot and spec['name']!=args.snapshot:continue
        if args.fetch:
            subprocess.run([sys.executable,'-B',str(p.ROOT/'scripts/fetch_era5.py'),'--config',spec['request_config']],check=True)
        interp,info=p.read_data(spec);render.CACHE=p.ROOT/spec['cache_directory'];render.CACHE.mkdir(exist_ok=True,parents=True)
        print('Rendering approved static snapshot',spec['name'],flush=True)
        image,stats=render.render_texture(canvas,interp,20.,info['sha256'],
            line_indices=p.FINAL['selected_original_indices'],line_appearance=p.FINAL['appearance'])
        page,bounds=render.text_overlay(canvas,image,20.,spec['data_label'],p.FINAL['appearance'])
        target=p.ROOT/spec['png']
        if args.verify:
            import numpy as np
            with Image.open(target) as existing:
                assert page.size==existing.size and np.array_equal(np.asarray(page),np.asarray(existing.convert('RGB')))
            assert p.digest(target)==spec['approved_png_sha256']
        else:
            target.parent.mkdir(exist_ok=True)
            pending=target.with_suffix('.pending.png');page.save(pending)
            assert p.digest(pending)==spec['approved_png_sha256'],'Unexpected difference from approved PNG; existing output is preserved'
            pending.replace(target)
        report={'snapshot':spec['name'],'time_utc':spec['time_utc'],'size':list(page.size),'data_sha256':info['sha256'],
            'drawn_curves':398,'appearance':p.FINAL['appearance'],'configuration':render.CFG,'text_bounds_px':bounds,
            'png_sha256':p.digest(target),'png_bytes':target.stat().st_size,'approved_png_exactly_reproduced':True,
            'geometry_layers':stats['layers'],'lic':stats['lic']}
        p.write_report(f"{spec['name']}_static.json",report)
        print(spec['name'],'exactly matches approved PNG',flush=True)
        del image,page,interp;gc.collect()
    assert all(p.digest(p.ROOT/'data/cache'/name)==sha for name,sha in sources.items())

if __name__=='__main__':main()
