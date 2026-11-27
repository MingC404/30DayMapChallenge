"""Extract original painting pixels using hand-traced contours and ink-density alpha.
No generative imagery; source files remain unchanged. Coordinates are reproducible.
"""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parent
S=ROOT/'assets/sources'; O=ROOT/'assets/cutouts'; O.mkdir(exist_ok=True)

def extract(filename, crop, polygon, ref_size, name, gain, opacity):
    source=Image.open(S/filename).convert('RGB')
    sx=source.width/ref_size[0]; sy=source.height/ref_size[1]
    box=tuple(round(v*(sx if i%2==0 else sy)) for i,v in enumerate(crop))
    im=source.crop(box)
    points=[(round(x*sx-box[0]),round(y*sy-box[1])) for x,y in polygon]
    outline=Image.new('L',im.size,0); ImageDraw.Draw(outline).polygon(points,fill=255)
    gray=im.convert('L')
    # Estimate the aged silk tone locally. Remove silk, retain the photographed ink.
    bg=np.asarray(gray.filter(ImageFilter.GaussianBlur(40)),dtype=float)
    light=np.asarray(gray,dtype=float)
    density=np.clip((bg-light-10)/35,0,1)
    density=np.minimum(density,np.clip((108-light)/40,0,1))
    if name=='guo_xi_main_tree':
        # Preserve the broad photographed trunk washes as well as fine outlines.
        stem=Image.new('L',im.size,0)
        ImageDraw.Draw(stem).polygon([(365,505),(410,520),(440,550),(465,600),
            (490,650),(470,680),(475,720),(520,765),(540,815),(560,860),
            (580,900),(620,930),(635,970),(605,1005),(550,985),(490,960),
            (460,925),(445,885),(435,840),(400,795),(390,755),(410,710),
            (415,670),(400,630),(385,600),(365,565)],fill=255)
        stem_weight=np.asarray(stem.filter(ImageFilter.GaussianBlur(12)),dtype=float)/255
        density=np.maximum(density,np.clip((115-light)/65,0,1)*stem_weight*.6)
    density=1-(1-density)**gain
    alpha=np.clip(density*np.asarray(outline)/255*opacity*255,0,255).astype(np.uint8)
    alpha[alpha<35]=0
    # Ink becomes a restrained warm green-black; density keeps the original strokes.
    rgb=np.empty((*alpha.shape,4),dtype=np.uint8)
    rgb[:,:,:3]=np.array([32,45,36]); rgb[:,:,3]=alpha
    result=Image.fromarray(rgb); result.save(O/(name+'.png'))
    outline.save(O/(name+'_contour_mask.png'))
    return {'source':filename,'source_size':source.size,'crop_source_pixels':box,
            'polygon_reference_size':ref_size,'polygon':polygon,'gain':gain,'opacity':opacity,
            'source_sha256':hashlib.sha256((S/filename).read_bytes()).hexdigest(),
            'output':name+'.png'}

def main():
    main_outline=[(455,270),(480,275),(510,250),(550,220),(590,200),
        (640,180),(700,180),(760,170),(770,190),(750,210),(700,210),
        (670,240),(650,265),(700,265),(720,290),(725,330),(730,360),
        (755,390),(740,400),(710,390),(690,370),(675,340),(640,340),
        (600,360),(540,365),(520,400),(510,455),(495,490),(490,540),
        (500,590),(520,640),(560,680),(610,715),(645,740),(650,770),
        (600,750),(565,735),(550,770),(560,820),(580,870),(600,900),
        (630,935),(650,970),(635,1005),(590,1010),(550,985),(500,980),
        (460,950),(450,910),(440,850),(420,790),(390,760),(390,730),
        (405,690),(420,670),(410,630),(390,600),(370,560),(350,520),
        (330,500),(280,475),(235,470),(180,475),(145,490),(100,510),
        (65,520),(45,490),(90,450),(150,425),(210,420),(230,390),
        (260,350),(300,330),(330,340),(300,375),(320,390),(350,380),
        (380,390),(380,365),(420,350),(445,330),(455,300)]
    main_tree=extract('guo_xi_old_trees.jpg',(1740,290,2550,1370),
        [(x+1740,y+290) for x,y in main_outline],
        (3508,1872),'guo_xi_main_tree',2.1,1.0)
    # Foreground left woodland; omit hill, sky, boats, seals and surrounding banks.
    grove=extract('dong_yuan_xiaoxiang.jpg',(140,169,330,283),
        [(141,200),(142,177),(157,170),(171,185),(190,175),(203,181),
         (218,193),(236,175),(250,195),(270,189),(287,206),(306,208),
         (320,225),(328,245),(321,280),(305,278),(288,267),(277,268),
         (263,257),(251,260),(237,254),(226,258),(212,249),(198,256),
         (183,247),(174,253),(159,248),(145,247)],
        (1500,531),'dong_yuan_grove',1.45,.72)
    bent_outline=[(290,70),(325,64),(375,73),(420,50),(430,84),(395,103),
        (450,115),(460,130),(420,145),(380,170),(360,190),(355,230),
        (344,270),(380,300),(405,315),(439,341),(468,352),(493,345),
        (520,370),(550,360),(580,388),(617,384),(647,394),(690,370),
        (730,360),(739,391),(713,420),(678,438),(654,470),(628,552),
        (614,568),(607,480),(568,483),(539,510),(518,487),(477,475),
        (450,490),(427,478),(400,450),(365,460),(330,484),(314,515),
        (315,559),(299,595),(270,640),(240,680),(215,719),(196,755),
        (150,778),(106,780),(115,747),(153,719),(177,674),(180,626),
        (177,570),(169,535),(140,508),(118,506),(110,470),(145,465),
        (178,445),(199,413),(235,390),(260,352),(259,315),(275,300),
        (280,273),(271,253),(230,250),(213,238),(180,248),(163,249),
        (150,267),(109,275),(80,299),(46,306),(55,280),(92,261),
        (125,232),(149,214),(170,200),(174,163),(190,143),(207,151),
        (225,184),(266,198),(299,207),(316,185),(328,154),(330,129),
        (310,121),(286,98)]
    bent=extract('guo_xi_old_trees.jpg',(2360,570,3150,1380),
        [(x+2360,y+570) for x,y in bent_outline],(3508,1872),'guo_xi_bent_tree',2.25,.92)
    sparse_outline=[(120,82),(151,55),(180,51),(197,39),(221,42),(255,48),
        (286,41),(313,60),(317,84),(281,88),(269,108),(275,128),
        (296,133),(315,160),(308,184),(319,212),(329,238),(322,266),
        (328,310),(316,343),(328,375),(319,403),(325,439),(301,473),
        (274,474),(253,458),(230,454),(203,450),(184,455),(154,475),
        (105,480),(90,467),(93,441),(106,408),(120,379),(150,351),
        (171,328),(166,305),(187,290),(220,273),(228,250),(216,230),
        (186,223),(160,227),(137,236),(104,243),(88,260),(68,275),
        (41,289),(31,272),(41,249),(70,222),(97,198),(112,180),
        (139,172),(158,156),(169,140),(154,121),(127,119),(109,122),
        (103,108)]
    sparse=extract('guo_xi_old_trees.jpg',(1380,430,1730,920),
        [(x+1380,y+430) for x,y in sparse_outline],(3508,1872),'guo_xi_sparse_trees',1.8,.70)
    pine=extract('ma_yuan_waterfall.jpg',(180,100,746,609),
        [(182,100),(302,100),(360,130),(423,144),(453,177),(492,182),
         (566,185),(616,215),(583,255),(532,277),(485,302),(515,329),
         (572,345),(628,360),(675,396),(670,419),(704,445),(718,468),
         (736,508),(736,550),(700,546),(663,498),(642,469),(607,444),
         (570,415),(530,401),(494,387),(465,368),(437,354),(399,354),
         (378,373),(357,391),(335,421),(325,449),(318,493),(305,531),
         (282,565),(251,584),(214,601),(181,604)],
        (1022,900),'ma_yuan_pine',1.45,.78)
    (O/'extraction.json').write_text(json.dumps([main_tree,grove,bent,sparse,pine],indent=2),encoding='utf8')

if __name__=='__main__':main()
