# Day 23 / Senses: Taste

## A Tasting Map of Tea

[Final GIF](outputs/day23_a_tasting_map_of_tea.gif) | [Static overview PNG](outputs/day23_a_tasting_map_of_tea.png) | [Tea source table](TEA_CATALOGUE.md) | [Region decisions](PRODUCTION_AREAS.md) | [CSV audit](data/tasting/final_region_audit.csv) | [Gallery copy](GALLERY_BLURB.md) | [Gallery entry JSON](gallery-entry.json) | [Cleanup](CLEANUP.md)

A static map by Ming Cao showing **15 selected regional teas and two tea drinks** across Asia. Four additions extend the retained 43-row source catalogue to 47 records. Fifteen regional teas use 14 broader display regions; Thai iced tea and masala chiya use cups without area shading. This is a selection, not a consumption ranking, exhaustive inventory or map of planted tea acreage.

### Reading the map

Small solid leaves identify regional teas and their processing classes. Open cups with handles and saucers identify drinking examples: **Thai iced tea / cha yen** near Bangkok and **Masala chiya** near Kathmandu. The two cup positions are illustrative city drinking locations, not origins, exclusive distributions or tea-growing places. Ingredient descriptions are not encoded as tea classes.

Shading provides regional orientation and grouping. It is **not** an expanded GI, a production footprint or a claim that tea grows everywhere inside a province. Specific origins and tasting descriptions remain governed by the source table. The legend reads: **Shading groups selected teas by broader region.** Fujian has one neutral region for Fuding white tea and Anxi Tieguanyin, with colored leaves distinguishing white tea and oolong; no arbitrary division is drawn.

The six requested callouts now have **no leaders**: Darjeeling, Assam, Anxi Tieguanyin, Fuding white tea, Anji Bai Cha and Oriental Beauty. Their labels sit on or beside their regions at standard font sizes. Darjeeling is west / southwest of Assam and explicitly names West Bengal; Fuding is above Anxi. The three previous direct labels remain. Other regional teas retain short anchored leaders where space requires them.

### New records and evidence

- **Nuwara Eliya tea**, Sri Lanka: [Sri Lanka Tea Board certification regulations](https://www.srilankateaboard.lk/wp-content/uploads/2023/08/Nuwala_Eliya.pdf), section 1(d), describe a fragrant and delicate regional tea. Section 2 and the annexes define gardens and factories in the agro-climatic region. The label uses **Delicate, fragrant** from this same regional product. The [George Steuart product catalogue](https://gsteas.lk/assets/doc/GS-Tea-Products-Booklet-V3.pdf), Nuwara Eliya BOP regional collection, corroborates the black-tea class, without supplying different tasting words. Central Province is the parent administrative display grouping, not the certification extent.
- **Shan Tuyet green tea**, northern Vietnam: the [Vietnam National Authority of Tourism Hoang Su Phi introduction](https://dantoc.vietnamtourism.gov.vn/en/green-tea-in-hoang-su-phi-ha-giang/) identifies this green product and producing communes. It gives no specific tasting description for that green tea, so the map labels **only tea and place**; no flavor from a white, black or unspecified Shan Tuyet product is transferred. The archived source-era Ha Giang province outline is used for orientation. It is explicitly historical, not a statement of current Vietnamese administrative boundaries. Hoang Su Phi is the representative named place.
- **Thai iced tea / cha yen**, Thailand: [MICHELIN Guide's Bangkok barista interviews](https://guide.michelin.com/jp/en/article/features/iconic-dishes-thai-milk-tea-explained), 26 April 2025, establish the name, milk-based iced preparation and Bangkok drinking examples. The label **Milk, sugar, ice** summarizes ingredients and service. It does not generalize a particular venue's vanilla, spices or coloring to every cup. The [Thai Public Relations Department](https://www.prd.go.th/th/content/category/detail/id/31/iid/261059) provides an additional name / preparation reference; it is not used as a locally downloaded archive.
- **Masala chiya**, Nepal: [GIZ NepalTrade issue 3, May 2012](https://enhancedif.org/system/files/uploads/nepal-trade-issue-3-english.pdf), PDF page 12, describes a Nepali-style preparation simmering milk, water, CTC tea, sugar and spices, then straining. The label is **Milk, sugar, spices**, and the source notes recipe variation. [ECS Nepal's on-location Kathmandu teashop account](https://www.ecs.com.np/food/sauni-euta-chiya) supports the illustrative city context; it does not claim a unique Kathmandu recipe. The native script in the table is a transliteration, not an official registration quote.

The tourism HTML and NepalTrade PDF are archived in `data/tasting/production_sources/`. Direct local requests for the Tea Board PDF timed out, and MICHELIN returned HTTP 403; both were verified through the browsing tool. Concise evidence and retrieval limitations are preserved in `browser_verified_evidence.json`, without claiming full local archives. `additional_places.json` retains the GeoNames CC BY 4.0 anchors and selected records. The original 43 entries, source PDFs, flavor descriptions and omission decisions remain available. Assam keeps **Malty aroma** and Darjeeling **Muscat grape aroma** from the documented Tea Board / first-party Golden Tips references.

### Original origins and display regions

China: Anji -> Zhejiang; Huoshan -> Anhui; Fuding and Anxi -> Fujian; Yingde -> Guangdong; Hengzhou -> Guangxi; Pu'er -> Yunnan. India: Dibrugarh -> Assam; Darjeeling -> West Bengal; Nilgiris -> Tamil Nadu. These are parent-region display groupings, not newly asserted GI extents.

Japan: Fukuoka / Yame -> the seven-prefecture Kyushu region listed by [official Kyushu tourism](https://www.visit-kyushu.com/en/destinations/); Kyoto / Uji -> the [METI Kansai Bureau](https://www.kansai.meti.go.jp/english/what_is_metikansai.html) seven-prefecture economic region (Fukui, Shiga, Kyoto, Osaka, Hyogo, Nara and Wakayama). Taiwan: Emei -> the [Tourism Administration's Northern Taiwan region](https://eng.taiwan.net.tw/m1.aspx?sNo=0029001), comprising Taipei, New Taipei, Keelung, Yilan, Taoyuan, Hsinchu County and Hsinchu City. These explicit definitions remain archived. Nuwara Eliya -> Central Province; Hoang Su Phi -> source-era Ha Giang. Drinks have no associated polygons.

The audit table separately records each original origin, representative coordinate, origin source, flavor source, display region, boundary source, scope note, selection reason and omitted status. Full recipe and sensory paraphrases are in `data/tasting/tea_catalogue.csv` / `.json`; editable final additions are in `data/tasting/final_additions.json`.

### Rendering and spatial provenance

The confirmed Asian view, Mercator projection, 1600 x 1200 canvas, 300 dpi export, rice-paper background, pale tea-colored land, standard typography and in-map title / signature are retained. Template settings in `data/template.json` come from the established Day 19 / Day 22 design system: Georgia title 44.8 px, Segoe UI headings 17.6 px, notes 19.2 px, captions 16 px, source 14 px and author 17 px. The map fills the canvas without a frame or separate footer. Line wrapping and positioning preserve those sizes.

Pastel tea-class fills use actual administrative shapes, inward feathering (1.1 px), no hard outlines, and a Natural Earth land mask. No point buffers or country-wide drink fills are used. Fourteen unions in `data/tasting/final_regions.geojson` preserve the documented display choices. Independent base, region, class-label, per-item label and drink layers remain in `outputs/layers/`. The per-item layers preserve exactly the approved label positions and support synchronized tasting-theme animation. The static overview PNG remains byte-identical to the approved candidate.

geoBoundaries inputs: China ADM1 (2019), India ADM1 (2011), Japan ADM1 (2017), Taiwan ADM1 (2017), Sri Lanka ADM1 (2017), Vietnam ADM1 (2008). The Vietnam layer deliberately retains the source-era Ha Giang boundary. Per-dataset metadata records licenses and original sources. Pinned URLs, full-download hashes, selected feature IDs and subset hashes are in `data/tasting/boundary_selection.json`. The broader subsets retain 39 required features, plus 20 earlier smaller features as original scope evidence. The China source's `Guangzhou Province` field is explicitly normalized to Guangdong and checked against Yingde's coordinate. All fills are clipped to the unchanged Natural Earth 1:50m coastline. Current source checksums are in `data/sources_manifest.json`.

### Reproduce and review

From the repository root using the existing environment (NumPy, Matplotlib, Pillow, pyproj, Shapely and Windows Georgia / Segoe UI fonts):

```powershell
./20/.venv/Scripts/python.exe -X utf8 23/scripts/build_tea_table.py
./20/.venv/Scripts/python.exe -X utf8 23/scripts/prepare_final_regions.py
./20/.venv/Scripts/python.exe -X utf8 23/scripts/render_final.py
./20/.venv/Scripts/python.exe -X utf8 23/scripts/encode_gif.py
./20/.venv/Scripts/python.exe -X utf8 23/scripts/validate_final.py --check-rebuild
./20/.venv/Scripts/python.exe -X utf8 23/scripts/validate_gif.py --check-rebuild
```

Rendering uses local retained data without network access. `acquire_boundaries.py` can restore exact boundary subsets from pinned downloads; `acquire_additions.py` documents new acquisition and named-place disambiguation. Source refreshes are separate from deterministic rendering.

Review uses the gallery's actual maximum media width, about 862 px, and 350 px for a 390 px phone viewport. At desktop gallery width, check six leader-free labels, Assam / Darjeeling attribution, north-to-south Fujian labels, neighboring text and leaf / cup distinction. At phone width fine annotations require the full PNG. Add `--review` to the renderer to recreate temporary inspection images. The validator checks all 17 displayed records, six leader removals, regional adjacency, shared Fujian geometry, distinct drink layer without shading, no sea spill, text / leader collisions, unchanged base pixels, layer composition and identical repeated PNG export.

[Gallery copy](GALLERY_BLURB.md) supplies the title, alt text and exactly two description sentences. `gallery-entry.json` matches the existing `scripts/gallery_entries.json` object schema and points at the final GIF, with the static overview PNG as a download. Gallery asset paths are `assets/23/day23_a_tasting_map_of_tea.gif` and `assets/23/day23_a_tasting_map_of_tea.png`; both approved assets are now copied byte for byte into `docs/assets/23/`.

Superseded exports and temporary review files are removed after reference checks and deterministic validation, with history in [CLEANUP.md](CLEANUP.md). The approved D23 entry is now included in the personal gallery, with changes limited to D23 and its collection integration. Commit, push and remote deployment remain with the owner.

### Tasting-theme animation

[Final GIF](outputs/day23_a_tasting_map_of_tea.gif) has five fixed-layout frames at 1600 x 1200: **Umami & brisk**, **Floral & fruity**, **Malty, mellow & sweet**, **Milk & spice** (2 seconds each), then **All teas & drinks** (3 seconds), looping every 11 seconds. The title, basemap, labels, legend, author, canvas and regional boundaries stay fixed. A theme label appears at the same position (84, 230) in the standard 19.2 px note style. See [theme membership and source descriptions](ANIMATION.md) and `data/tasting/animation_themes.json`.

These are editorial reading themes, not processing classes or exclusive sensory categories. Each of 16 items has exactly one theme. Original specific tasting words stay unchanged, including Darjeeling's grape aroma, Assam's malty aroma and Oriental Beauty's Honeyed. Shan Tuyet has no verified same-product sensory note in the retained source and therefore has no themed assignment: it stays faintly locatable during themes and is fully visible in the overview.

Each theme highlights its leaves or cups, complete text and applicable regional fills together. Inactive labels retain 30% alpha and inactive region fills 22%. Shared neutral Fujian stays neutral and at its static strength in every frame; its names and leaves follow the active theme. The Milk & spice frame highlights both dark cup symbols, names and ingredient labels together, while retaining static regional fill colors and adding no drink coverage polygons. All items return to full visibility in the overview. The standalone PNG has no extra animation heading and retains the approved static artwork exactly.

GIF encoding uses one shared 256-color palette with no dithering to keep unchanged pixels stable. No temporary frame PNGs are required for encoding. Run `encode_gif.py --review` to generate disposable 862 px and 350 px contact sheets. At 862 px active labels and symbols are clear and dim items remain locatable; phone-size detailed text still benefits from opening the full image. `review/animation_validation.json` verifies actual decoded timing, exact expected frame content, fixed title / legend / base pixels, shared-region behavior, single theme membership, unchanged static PNG and deterministic GIF reproduction.

### Personal gallery integration

D23 is included after Day 22 in [the personal gallery](../docs/index.html#day-23). Its approved GIF is the main display and the unchanged PNG is a static download. The exact owner-supplied English description and alt text are stored in [GALLERY_BLURB.md](GALLERY_BLURB.md), [gallery-entry.json](gallery-entry.json), the shared registry and the actual HTML. No artwork or playback timing has changed.

```powershell
node 23/scripts/update_gallery.cjs
node 23/scripts/check_gallery.cjs
node scripts/serve_gallery.cjs
```

The final command serves `http://127.0.0.1:8026/30DayMapChallenge/#day-23`. The scoped updater follows Day 22 and preserves every other row and the existing CSS; a whole-gallery rebuild is unnecessary. Both relative asset URLs work under the GitHub Pages project prefix. Files are staged in the deployment directory without a commit, push or remote deployment.

Browser review covers 1440, 390 and 320 px viewports, correct ordering, exact description / alt, natural aspect ratio, HTTP 200 image paths, full-size GIF clicks and all five animation frames recurring across more than two 11-second loops. Results: `review/gallery_validation.json` and `review/gallery_scope.json`. This final cleanup audit found no remaining superseded exports, duplicate previews or temporary frames; the earlier deletion history remains in [CLEANUP.md](CLEANUP.md). Updated files and the empty current deletion list are recorded in `review/gallery_changes.json`.
