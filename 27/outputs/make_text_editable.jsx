#target photoshop
// Optional: open PSD, hide raster labels, create native type. Save As afterwards.
app.displayDialogs = DialogModes.NO;
var folder = new File($.fileName).parent;
var doc = app.open(new File(folder + "/among_the_giants_layers.psd"));
var recipes = [{"layer": "day_kicker", "text": "DAY 27 / NEW TOOL", "x": 94, "y": 90, "font_px": 20, "color": "#59675a", "font_file": "segoeui.ttf", "photoshop_font": "SegoeUI", "anchor": "ls"}, {"layer": "title", "text": "Among the Giants", "x": 94, "y": 174, "font_px": 64, "color": "#35473c", "font_file": "georgia.ttf", "photoshop_font": "Georgia", "anchor": "ls"}, {"layer": "subtitle", "text": "The giant-tree trail at Lalashan, Taiwan", "x": 94, "y": 222, "font_px": 27, "color": "#35473c", "font_file": "segoeui.ttf", "photoshop_font": "SegoeUI", "anchor": "ls"}, {"layer": "legend_text", "text": "Reference GPS track", "x": 158, "y": 295, "font_px": 22, "color": "#35473c", "font_file": "segoeui.ttf", "photoshop_font": "SegoeUI", "anchor": "ls"}, {"layer": "legend_text", "text": "Candidate tree locations", "x": 518, "y": 295, "font_px": 22, "color": "#35473c", "font_file": "segoeui.ttf", "photoshop_font": "SegoeUI", "anchor": "ls"}, {"layer": "entrance_label", "text": "Entrance / Visitor center", "x": 1488, "y": 2377, "font_px": 23, "color": "#35473c", "font_file": "segoeui.ttf", "photoshop_font": "SegoeUI", "anchor": "rs"}, {"layer": "collage_caption", "text": "Tree, ridge and waterfall collage from classical ink paintings.", "x": 94, "y": 2350, "font_px": 23, "color": "#35473c", "font_file": "segoeui.ttf", "photoshop_font": "SegoeUI", "anchor": "ls"}, {"layer": "position_note", "text": "Candidate locations unverified \u00b7 artistic tree forms \u00b7 GPS: Taiwan Outdoors \u00b7 not for navigation", "x": 94, "y": 2385, "font_px": 20, "color": "#59675a", "font_file": "segoeui.ttf", "photoshop_font": "SegoeUI", "anchor": "ls"}, {"layer": "terrain_source", "text": "Copernicus GLO-30 DSM (nominal 30 m) \u00b7 EPSG:3826 / EGM2008 \u00b7 \u00a9 OpenStreetMap contributors", "x": 94, "y": 2435, "font_px": 18, "color": "#59675a", "font_file": "segoeui.ttf", "photoshop_font": "SegoeUI", "anchor": "ls"}, {"layer": "art_source", "text": "Early Spring, The National Palace Museum, Taipei, CC BY 4.0 @ www.npm.gov.tw (adapted). Other art: The Met CC0 / Commons PD.", "x": 94, "y": 2466, "font_px": 15, "color": "#59675a", "font_file": "segoeui.ttf", "photoshop_font": "SegoeUI", "anchor": "ls"}, {"layer": "signature", "text": "Ming Cao", "x": 1706, "y": 2466, "font_px": 23, "color": "#35473c", "font_file": "segoeui.ttf", "photoshop_font": "SegoeUI", "anchor": "rs"}];
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
