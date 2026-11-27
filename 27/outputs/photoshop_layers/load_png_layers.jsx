#target photoshop
// Run from this extracted directory; each PNG is full canvas at identical origin.
var base=new File($.fileName).parent;
var doc=app.documents.add(UnitValue(1800,"px"),UnitValue(2520,"px"),72,"Among the Giants - PNG layers",NewDocumentMode.RGB,DocumentFill.TRANSPARENT);
var empty=doc.activeLayer;
var names=["00_sky_background.png", "01_terrain_pale_ink.png", "01s0_early_spring.png", "01s1_early_spring.png", "01s2_early_spring.png", "01v0_ridge_valley.png", "01v1_ridge_valley.png", "01v2_ridge_valley.png", "01v3_ridge_valley.png", "01v4_ridge_valley.png", "04_reference_gps_track.png", "05_candidate_locations.png", "06_entrance_marker.png", "07_grove_dong_yuan_distant.png", "08_new_dense_grove_wang_meng.png", "09_new_single_pine_zhao_mengfu.png", "10_new_sparse_grove_ni_zan.png", "11_main_tree_guo_xi.png", "12_waterfall_main_wen.png", "13_waterfall_distant_wen.png", "14_day_kicker.png", "15_title.png", "16_subtitle.png", "17_legend_symbols.png", "18_legend_text.png", "19_entrance_label.png", "25v_collage_caption.png", "21_position_note.png", "22_terrain_source.png", "25v_art_source.png", "24_signature.png"];
for(var i=0;i<names.length;i++){
 var src=app.open(new File(base+"/"+names[i]));
 var layer=src.activeLayer.duplicate(doc,ElementPlacement.PLACEATBEGINNING);
 layer.name=names[i].replace(/\.png$/i,"");src.close(SaveOptions.DONOTSAVECHANGES);
}
app.activeDocument=doc;empty.remove();
