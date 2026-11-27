# Photoshop layer stack

Canvas: 1800 x 2520 px; origin (0,0); RGBA 8-bit; Normal blend; all layers 100% opacity (art opacity is in each alpha channel).

Open ../among_the_giants_layers.psd directly, or run load_png_layers.jsx via Photoshop > File > Scripts > Browse to build the same stack from these PNGs.

Numbering is BOTTOM to TOP: 00 is sky; the largest number is on top. Photoshop panel order is the reverse. Do not trim, crop, resize, or auto-align individual PNGs.

Every tree and grove, terrain, trail, candidates, marker, and label group has its own layer. Text is rasterized in the delivered PSD for exact alignment. ../make_text_editable.jsx opens the PSD and creates native Photoshop text, hides the corresponding raster text layers, and leaves the document unsaved. Check font metrics then Save As. Requires Georgia and Segoe UI. This optional JSX has not been run in Photoshop here.

layer_manifest.json records order and collage anchors. editable_text.json records wording, fonts, pixel sizes, colors, baselines and justification.
