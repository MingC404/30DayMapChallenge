"""Explicit-path cleanup, gated on valid final exports; no directories removed."""
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT=Path(__file__).resolve().parent
TARGETS={
 'outputs/photoshop_layers.zip':['add_ridge_mist.py','build_layers.py','compose_once.py','review/cleanup_report.json'],
 'outputs/gallery_size_check.png':['add_ridge_mist.py','build_layers.py','compose_early_spring.py','compose_once.py','compose_ridge_valley.py'],
 'review/boundary_mist_check.png':['compose_boundary_mist.py'],
 'review/composition_tweak_low.png':['compose_once.py'],
 'review/early_spring_painting_inspection.png':[],
 'review/early_spring_ridge_cutout_inspection.png':[],
 'review/final_feather_check.png':['final_feather.py'],
 'review/hand_edited_psd_check.png':['export_saved_psd.py'],
 'review/ridge_valley/ridge_detail_check.png':[],
 'review/final_animation/motion_check.png':['animate_final_mist.py'],
 'assets/sources/guo_xi_early_spring.jpg':[],
 'assets/sources/npm_early_spring_download.json':[],
 'assets/sources/npm_early_spring_iiif_1.txt':[],
}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    static=json.loads((ROOT/'outputs/final_static_validation.json').read_text())
    gif=json.loads((ROOT/'outputs/final_gif_validation.json').read_text())
    assert static['png_vs_photoshop_saved_composite_max_error']==0
    assert gif['static_region_max_error']==0 and gif.get('text_margin_max_error',gif.get('protected_content_core_max_error'))==0
    protected={ROOT/static['source']:static['source_psd_sha256'],ROOT/static['png']:static['png_sha256'],
               ROOT/gif['path']:gif['output_sha256']}
    assert all(sha(path)==digest for path,digest in protected.items())
    texts={}
    for p in ROOT.rglob('*'):
        if not p.is_file() or any(k in p.parts for k in ('.venv','.uv-cache','__pycache__')):continue
        if p.suffix in ('.py','.md','.json','.jsx'):
            texts[p.relative_to(ROOT).as_posix()]=p.read_text(encoding='utf8',errors='replace')
    for rel,content in texts.items():
        if not rel.endswith('.md'):continue
        for link in re.findall(r'\]\(([^)]+)\)',content):
            if '://' in link:continue
            path=(ROOT/rel).parent/link.split('#')[0]
            if path.resolve().is_relative_to(ROOT):
                assert path.resolve().relative_to(ROOT).as_posix() not in TARGETS
    archive=ROOT/'outputs/photoshop_layers.zip'
    if archive.exists():
        with zipfile.ZipFile(archive) as z:
            assert not any(n.lower().endswith(('.psd','.psb')) for n in z.namelist())
            for n in z.namelist():
                if n.lower().endswith('.png'):
                    duplicate=ROOT/'outputs/photoshop_layers'/n
                    assert duplicate.is_file() and hashlib.sha256(z.read(n)).hexdigest()==sha(duplicate)
    removed=[]
    for rel,allowed in TARGETS.items():
        path=(ROOT/rel).resolve()
        assert path.is_relative_to(ROOT) and path not in protected
        if not path.exists():continue
        assert path.is_file()
        refs=[k for k,v in texts.items() if path.name in v and k not in ('cleanup_final_outputs.py','review/final_cleanup_report.json')]
        assert set(refs)<=set(allowed),(rel,refs)
        # Allowed references were inspected: all are generated-output writes,
        # except the dated cleanup journal's historical preservation note.
        removed.append(dict(path=rel,bytes=path.stat().st_size,sha256=sha(path),
                            references_checked=refs,reference_class='Output writers / historical audit only; no current input or README link.'))
    # Validation and dependency audit finish before any file is removed.
    for r in removed:(ROOT/r['path']).unlink()
    assert all(sha(path)==digest for path,digest in protected.items())
    report=dict(scope='27 only',removed=removed,count=len(removed),bytes_removed=sum(r['bytes'] for r in removed),
        required_final_files_unchanged=True,temporary_frame_files_created=False,psd_kept_original=True,
        animation_inputs_kept=True,source_licenses_kept=True,d18_changed=False,gallery_changed=False,
        uncertain_files_retained=['All referenced historical previews and layer PNGs','.venv/','.uv-cache/','Original art and extraction masks','D18 camera and source references'])
    (ROOT/'review/final_cleanup_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(f"Removed {len(removed)} explicit files, {report['bytes_removed']/1024/1024:.2f} MiB; all final files unchanged.")


if __name__=='__main__':main()
