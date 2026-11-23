from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
DURATION_MS=1000
NAMES=['day22_merc.png','day22_eqearth.png']
def gif_save(images,path):
    source=Image.new('RGB',(images[0].width,images[0].height*2))
    for i,im in enumerate(images):source.paste(im,(0,i*im.height))
    palette=source.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
    indexed=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in images]
    indexed[0].save(path,save_all=True,append_images=indexed[1:],duration=[DURATION_MS]*2,loop=0,disposal=2,optimize=False)
def main():
    hashes={n:hashlib.sha256((ROOT/'outputs'/n).read_bytes()).hexdigest() for n in NAMES}
    images=[Image.open(ROOT/'outputs'/n).convert('RGB') for n in NAMES]
    assert all(im.size==(1600,1200) for im in images)
    target=ROOT/'outputs/day22_the_pacific_reprojected.gif';gif_save(images,target)
    with Image.open(target) as g:
        assert g.n_frames==2 and g.info['loop']==0
        durations=[]
        for i in range(2):g.seek(i);durations.append(g.info['duration']);assert g.info['duration']==DURATION_MS
    assert hashes=={n:hashlib.sha256((ROOT/'outputs'/n).read_bytes()).hexdigest() for n in NAMES}
    report={'size':[1600,1200],'frames':2,'duration_ms':durations,'cycle_ms':sum(durations),'loop':0,'transition':'direct cut','png_sha256':hashes,'confirmed_pngs_unchanged':True,'gif_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    (ROOT/'review/final_media_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    previous=ROOT/'review/animation_validation.json'
    if previous.exists():
        d=json.loads(previous.read_text(encoding='utf8'));d['gif']['duration_ms']=durations;previous.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
