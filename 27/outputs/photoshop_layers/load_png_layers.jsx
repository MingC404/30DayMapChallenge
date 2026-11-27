#target photoshop
// Run from this extracted directory; each PNG is full canvas at identical origin.
var base=new File($.fileName).parent;
var doc=app.documents.add(UnitValue(1800,"px"),UnitValue(2520,"px"),72,"Among the Giants - PNG layers",NewDocumentMode.RGB,DocumentFill.TRANSPARENT);
var empty=doc.activeLayer;
var names=["00_sky_background.png", "01_terrain_pale_ink.png", "02_reference_gps_track.png", "03_candidate_locations.png", "04_entrance_marker.png", "05_grove_dong_yuan_distant.png", "06_new_dense_grove_wang_meng.png", "07_new_single_pine_zhao_mengfu.png", "08_new_sparse_grove_ni_zan.png", "09_main_tree_guo_xi.png", "10_day_kicker.png", "11_title.png", "12_subtitle.png", "13_legend_symbols.png", "14_legend_text.png", "15_entrance_label.png", "16_collage_caption.png", "17_position_note.png", "18_terrain_source.png", "19_art_source.png", "20_signature.png"];
for(var i=0;i<names.length;i++){
 var src=app.open(new File(base+"/"+names[i]));
 var layer=src.activeLayer.duplicate(doc,ElementPlacement.PLACEATBEGINNING);
 layer.name=names[i].replace(/\.png$/i,"");src.close(SaveOptions.DONOTSAVECHANGES);
}
app.activeDocument=doc;empty.remove();
