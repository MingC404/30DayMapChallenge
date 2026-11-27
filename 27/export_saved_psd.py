"""Export Photoshop's saved, full-resolution merged RGB; never rewrite the PSD.

Do not rebuild from the older layer_manifest.json: Photoshop edits supersede it.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from psd_tools import PSDImage
from psd_tools.constants import Resource

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    source=OUT/'among_the_giants_layers.psd';before=sha(source)
    psd=PSDImage.open(source);version=psd.image_resources.get_data(Resource.VERSION_INFO)
    assert psd.has_preview() and version and version.has_composite,'No authoritative saved merged image; stop.'
    assert 'Photoshop' in version.writer,'Expected the Photoshop-saved manual revision.'
    assert psd.color_mode.name=='RGB' and psd.depth==8
    # topil uses Photoshop's merged RGB. The fourth channel in this file is an
    # auxiliary all-zero channel, not the saved composite transparency.
    merged=psd.topil(apply_icc=False)
    assert merged is not None and merged.size==psd.size and merged.mode=='RGB'
    with Image.open(source) as decoder:
        raw=np.asarray(decoder)
        assert np.array_equal(raw[:,:,:3],np.asarray(merged))
        auxiliary_zero=(raw.shape[2]==4 and not raw[:,:,3].any())
    icc=psd.image_resources.get_data(Resource.ICC_PROFILE)
    kwargs={'icc_profile':icc} if icc else {}
    destination=OUT/'among_the_giants_final.png';merged.save(destination,**kwargs)
    with Image.open(destination) as check:
        assert np.array_equal(np.asarray(check),np.asarray(merged)),'PNG differs from saved Photoshop RGB; stop.'
    inventory=[]
    for layer in psd.descendants():
        inventory.append(dict(name=layer.name,kind=layer.kind,visible=layer.visible,
                              effective_visible=layer.is_visible(),opacity=layer.opacity,
                              blend=str(layer.blend_mode),bbox=list(layer.bbox),mask=layer.has_mask()))
    assert sha(source)==before,'PSD source changed unexpectedly.'
    report=dict(source=str(source.relative_to(ROOT)).replace('\\','/'),source_psd_sha256=before,
                png=str(destination.relative_to(ROOT)).replace('\\','/'),png_sha256=sha(destination),
                canvas=list(psd.size),export_method='Photoshop-saved full-resolution merged RGB, not third-party layer recomposition',
                writer=version.writer,saved_layer_state=inventory,source_psd_unchanged=True,
                png_vs_photoshop_saved_composite_max_error=0,auxiliary_zero_channel_ignored=bool(auxiliary_zero),
                icc_profile_embedded=bool(icc),rgb_channel_values_preserved=True,
                psd_has_external_layer_resources=any('lnk' in str(k).lower() for k in psd.tagged_blocks))
    (OUT/'final_static_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    small=merged.copy();small.thumbnail((630,882));small.save(ROOT/'review/hand_edited_psd_check.png')
    print('Final PNG exactly matches Photoshop-saved merged RGB; original PSD unchanged.')


if __name__=='__main__':main()
