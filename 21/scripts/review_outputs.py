"""Build equal-display-width reference comparisons and validate final exports."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]; REVIEW=ROOT/'review'
def main():
    gallery=json.loads((REVIEW/'gallery_validation.json').read_text())
    metadata=json.loads((ROOT/'outputs/final_metadata.json').read_text())
    im=Image.open(ROOT/'outputs/day21_three_street_fabrics_of_manhattan.png')
    assert im.size==(1600,1200) and im.mode=='RGB'
    assert abs(im.info['dpi'][0]-300)<.1
    previous=json.loads((ROOT/'outputs/study_metadata.json').read_text())
    assert [p['bounds_projected_m'] for p in metadata['panels']]==[p['bounds_projected_m'] for p in previous['panels']]
    for p in metadata['panels']:
        w,s,e,n=p['bounds_projected_m']; assert e-w==600 and n-s==600
    for width in [1440,390]:
        images=[Image.open(REVIEW/f'gallery-{name}-{width}.png').convert('RGB') for name in ['reference','d21']]
        measurements=[r for r in gallery['viewports'] if r['viewport_width']==width]
        assert abs(measurements[0]['display_width']-measurements[1]['display_width'])<.1
        # Fractional CSS origins can make screenshot bounds differ by one pixel.
        w=round(measurements[0]['display_width']); h=round(measurements[0]['display_height'])
        images=[im.resize((w,h),Image.Resampling.LANCZOS) for im in images]
        sheet=Image.new('RGB',(2*w+24,h+50),'#e4e1d9'); d=ImageDraw.Draw(sheet)
        f=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
        d.text((12,13),'Reference / Day 19 — same display width',font=f,fill='#42443f')
        d.text((w+24,13),'Day 21 — same display width',font=f,fill='#42443f')
        sheet.paste(images[0],(0,50)); sheet.paste(images[1],(w+24,50))
        sheet.save(REVIEW/f'equal_width_comparison_{width}.png')
    gallery['visual_review']={
        'desktop':'The actual Day 21 gallery row shows the clean triptych alongside the exact supplied English description. Title, place labels, scale, OSM attribution and author remain on the artwork; all explanations and evidence callouts are removed.',
        'mobile':'Description remains readable in the gallery header above the 350 CSS px image. Fine footprint detail and small artwork labels are inspected via the functioning full-size PNG link.',
        'reference_choice':'Day 20 was inspected but uses a custom full-bleed northeast title arrangement. Day 19 is the latest completed landscape work with the unmodified standard series title hierarchy, complete author line and a compatible canvas.'}
    gallery['export_checks']={'size':[1600,1200],'mode':'RGB','dpi':300,'bounds_equal_to_preview':True,'all_windows_600_m':True}
    labels=[r['text'] for r in metadata['text']]
    assert len(labels)==11,labels
    assert not any(s in ' '.join(labels).lower() for s in ['draft','preview','interior gap','in these samples','similar street grids'])
    (REVIEW/'gallery_validation.json').write_text(json.dumps(gallery,indent=2),encoding='utf8')
    print('Verified RGB PNG, 300 dpi, original extents, template canvas, and equal-width comparisons.')

if __name__=='__main__': main()
