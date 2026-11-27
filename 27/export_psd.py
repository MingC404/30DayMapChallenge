"""Write 8-bit layered PSD, reopen and compare each layer with its source PNG."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from psd_tools import PSDImage
from psd_tools.constants import Compression
DAY=Path(__file__).resolve().parent;OUT=DAY/'outputs';L=OUT/'photoshop_layers'

def export(manifest,texts):
 w,h=manifest['canvas'];psd=PSDImage.new('RGBA',(w,h),depth=8)
 for r in manifest['layers']:
  psd.create_pixel_layer(Image.open(L/r['file']).convert('RGBA'),name=r['name'],top=0,left=0,compression=Compression.RLE)
 path=OUT/'among_the_giants_layers.psd';psd.save(path)
 reopened=PSDImage.open(path);checks=[];assert len(reopened)==len(manifest['layers'])
 merged=Image.new('RGBA',(w,h),(0,0,0,0))
 for layer,r in zip(reopened,manifest['layers']):
  im=layer.topil().convert('RGBA');source=Image.open(L/r['file']).convert('RGBA')
  assert layer.name==r['name'] and layer.left==0 and layer.top==0 and im.size==(w,h)
  aa=np.array(im);bb=np.array(source);mask=bb[:,:,3]>0
  assert np.array_equal(aa[:,:,3],bb[:,:,3]) and np.array_equal(aa[:,:,:3][mask],bb[:,:,:3][mask])
  merged=Image.alpha_composite(merged,im);checks.append(dict(name=layer.name,bounds=list(layer.bbox),exact_visible_pixels=True))
 ref=np.array(Image.open(OUT/'among_the_giants.png').convert('RGB'),dtype=int)
 err=np.abs(np.array(merged.convert('RGB'),dtype=int)-ref);assert err.max()==0
 compatibility=Image.open(path).convert('RGB');ce=np.abs(np.array(compatibility,dtype=int)-ref)
 assert ce.max()<=1,'Embedded PSD compatibility preview diverges from saved layers.'
 (OUT/'psd_validation.json').write_text(json.dumps(dict(layer_count=len(checks),canvas=[w,h],
  reimported_layer_stack_max_error=int(err.max()),embedded_preview_max_error=int(ce.max()),embedded_preview_mean_error=float(ce.mean()),
  layers=checks,photoshop_application_open_tested=False,text_is_raster_in_psd=True,
  editable_text_script='make_text_editable.jsx'),indent=2),encoding='utf8')
 script='''#target photoshop
// Optional: open PSD, hide raster labels, create native type. Save As afterwards.
app.displayDialogs = DialogModes.NO;
var folder = new File($.fileName).parent;
var doc = app.open(new File(folder + "/among_the_giants_layers.psd"));
var recipes = RECIPE;
for (var i=0;i<recipes.length;i++) {
 var r=recipes[i];
 try { doc.artLayers.getByName(r.layer).visible=false; } catch(e) {}
 var l=doc.artLayers.add();l.name=r.layer+" (editable "+i+")";l.kind=LayerKind.TEXT;
 var t=l.textItem;t.contents=r.text;t.font=r.photoshop_font;
 t.size=UnitValue(r.font_px*72/doc.resolution,"pt");
 t.justification=r.anchor=="rs"?Justification.RIGHT:Justification.LEFT;
 t.position=[UnitValue(r.x,"px"),UnitValue(r.y,"px")];
 var c=new SolidColor();c.rgb.hexValue=r.color.replace("#","");t.color=c;
}
app.displayDialogs=DialogModes.ALL;
alert("Editable text created. Check font metrics, then Save As a new PSD.");
'''.replace('RECIPE',json.dumps(texts,ensure_ascii=True))
 (OUT/'make_text_editable.jsx').write_text(script,encoding='utf8')
 names=json.dumps([r['file'] for r in manifest['layers']])
 importer='''#target photoshop
// Run from this extracted directory; each PNG is full canvas at identical origin.
var base=new File($.fileName).parent;
var doc=app.documents.add(UnitValue(WIDTH,"px"),UnitValue(HEIGHT,"px"),72,"Among the Giants - PNG layers",NewDocumentMode.RGB,DocumentFill.TRANSPARENT);
var empty=doc.activeLayer;
var names=FILES;
for(var i=0;i<names.length;i++){
 var src=app.open(new File(base+"/"+names[i]));
 var layer=src.activeLayer.duplicate(doc,ElementPlacement.PLACEATBEGINNING);
 layer.name=names[i].replace(/\\.png$/i,"");src.close(SaveOptions.DONOTSAVECHANGES);
}
app.activeDocument=doc;empty.remove();
'''.replace('WIDTH',str(w)).replace('HEIGHT',str(h)).replace('FILES',names)
 (L/'load_png_layers.jsx').write_text(importer,encoding='utf8')
 instructions=f'''# Photoshop layer stack\n\nCanvas: {w} x {h} px; origin (0,0); RGBA 8-bit; Normal blend; all layers 100% opacity (art opacity is in each alpha channel).\n\nOpen ../among_the_giants_layers.psd directly, or run load_png_layers.jsx via Photoshop > File > Scripts > Browse to build the same stack from these PNGs.\n\nNumbering is BOTTOM to TOP: 00 is sky; the largest number is on top. Photoshop panel order is the reverse. Do not trim, crop, resize, or auto-align individual PNGs.\n\nEvery tree and grove, terrain, trail, candidates, marker, and label group has its own layer. Text is rasterized in the delivered PSD for exact alignment. ../make_text_editable.jsx opens the PSD and creates native Photoshop text, hides the corresponding raster text layers, and leaves the document unsaved. Check font metrics then Save As. Requires Georgia and Segoe UI. This optional JSX has not been run in Photoshop here.\n\nlayer_manifest.json records order and collage anchors. editable_text.json records wording, fonts, pixel sizes, colors, baselines and justification.\n'''
 (L/'README.md').write_text(instructions,encoding='utf8')

if __name__=='__main__':export(json.loads((L/'layer_manifest.json').read_text()),json.loads((L/'editable_text.json').read_text()))
