"""Audit only works contributing visible pixels to the owner's final PSD/PNG.

No rendering or file export: inspect saved layer alpha, masks, visibility,
opacity and overlying occlusion, then cross-reference retained source records.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops
from psd_tools import PSDImage

ROOT=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    sys.stdout.reconfigure(encoding='utf8')
    spec=json.loads((ROOT/'gallery-entry.json').read_text(encoding='utf8'))
    metadata=json.loads((ROOT/'assets/sources/source_manifest.json').read_text(encoding='utf8'))
    sources={r['file']:r for r in metadata}
    # Layer names are retained from the documented extraction pipeline; copies
    # and transformed instances refer to the same source work, counted once.
    mapping={
        '早春图':('guo_xi_early_spring_6mp.jpg',['Ridge collage - Guo Xi'],['early_spring_main_ridge.png','early_spring_side_ridge.png','early_spring_far_ridge.png'],'assets/cutouts/early_spring_ridge_materials.json'),
        '树色平远图':('guo_xi_old_trees.jpg',['main_tree_guo_xi'],['guo_xi_main_tree.png'],'assets/cutouts/extraction.json'),
        '双松平远图':('zhao_mengfu_twin_pines.jpg',['new_single_pine_zhao_mengfu'],['new_zhao_single_pine.png'],'assets/cutouts/new_materials.json'),
        '江渚风林图':('ni_zan_wind_trees.jpg',['new_sparse_grove_ni_zan'],['new_ni_sparse_grove.png'],'assets/cutouts/new_materials.json'),
        '素庵图':('wang_meng_simple_retreat.jpg',['new_dense_grove_wang_meng'],['new_wang_dense_grove.png'],'assets/cutouts/new_materials.json'),
        '潇湘图':('dong_yuan_xiaoxiang.jpg',['grove_dong_yuan_distant'],['dong_yuan_grove.png'],'assets/cutouts/extraction.json'),
        '松阴飞瀑图':('wen_zhengming_pine_waterfall.jpg',['waterfall_main_wen','waterfall_distant_wen'],['waterfall_wen_main.png','waterfall_wen_far.png'],'assets/cutouts/waterfall_materials.json')}
    psdpath=ROOT/'outputs/among_the_giants_layers.psd';psd=PSDImage.open(psdpath)
    static=json.loads((ROOT/'outputs/final_static_validation.json').read_text(encoding='utf8'))
    assert sha(psdpath)==static['source_psd_sha256']
    assert np.array_equal(np.asarray(psd.topil(apply_icc=False)),np.asarray(Image.open(ROOT/'outputs/among_the_giants_final.png').convert('RGB')))
    assert sha(ROOT/'outputs/among_the_giants_final.png')==sha(ROOT.parent/'docs/assets/27/among_the_giants.png')
    assert sha(ROOT/'outputs/among_the_giants_summit_mist.gif')==sha(ROOT.parent/'docs/assets/27/among_the_giants.gif')
    transmittance=np.ones((psd.height,psd.width),dtype='float32');layers={title:[] for title in mapping}
    for layer in reversed(list(psd.descendants())):
        if layer.is_group():
            assert layer.opacity==255 and not layer.has_mask(),'Unexpected group processing; inspect before crediting.'
            continue
        if not layer.is_visible():continue
        assert str(layer.blend_mode)=='BlendMode.NORMAL'
        image=layer.topil(apply_icc=False)
        alpha=image.getchannel('A') if 'A' in image.getbands() else Image.new('L',image.size,255)
        full=Image.new('L',psd.size);full.paste(alpha,(layer.left,layer.top))
        if layer.has_mask() and not layer.mask.disabled:
            mask=Image.new('L',psd.size,layer.mask.background_color)
            mask.paste(layer.mask.topil().convert('L'),(layer.mask.left,layer.mask.top))
            full=ImageChops.multiply(full,mask)
        a=np.asarray(full,dtype='float32')/255*(layer.opacity/255)
        surviving=a*transmittance
        for title,(_,prefixes,_,_) in mapping.items():
            if any(layer.name.startswith(prefix) for prefix in prefixes):
                layers[title].append(dict(name=layer.name,visible=layer.is_visible(),opacity=layer.opacity,
                    clipped_canvas_pixels=int(np.count_nonzero(a>.02)),
                    surviving_pixels_above_2_percent_alpha=int(np.count_nonzero(surviving>.02)),
                    surviving_alpha_equivalent_pixels=float(surviving.sum())))
        transmittance*=1-a
    records=[]
    for work in spec['collageSources']:
        title=work['title'];file,_,assets,record=mapping[title]
        assert layers[title] and sum(x['surviving_pixels_above_2_percent_alpha'] for x in layers[title])>20
        assert sha(ROOT/'assets/sources'/file)==sources[file]['sha256']
        assert all((ROOT/'assets/cutouts'/asset).is_file() for asset in assets)
        assert (ROOT/record).is_file()
        records.append(dict(**work,source_file='assets/sources/'+file,source_sha256=sources[file]['sha256'],
            extraction_record=record,cutouts=assets,final_psd_layers=layers[title]))
    assert len(records)==7
    report=dict(works=records,unique_visible_works=7,visible_art_layers=sum(len(v) for v in layers.values()),
        source_psd_sha256=sha(psdpath),published_png_matches_saved_psd_composite=True,
        gallery_assets_match_final_working_files=True,
        gif_additions='Three procedural mist overlays only; no additional painting pixels.',
        excluded=['马远《高士观瀑图》：备用松树/急流素材，无最终可见图层。',
                  '唐寅《观瀑图》：仅检查原画，未制作并使用最终拼贴。',
                  '范宽《雪景寒林图》等早期建议：仅作为备选参考，无最终拼贴。'],
        method='Saved PSD layer alpha/mask/opacity, canvas clipping and upper-layer alpha occlusion; retained extraction/source records; published static image comparison. Visible works deduplicated across transformed/copied layers.')
    (ROOT/'review/collage_source_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    for r in records:print(r['title'],[x['name'] for x in r['final_psd_layers']],sum(x['surviving_pixels_above_2_percent_alpha'] for x in r['final_psd_layers']))


if __name__=='__main__':main()
