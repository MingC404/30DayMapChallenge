"""Recolour only the existing Day 02 light-map recipe; never edits Day 01."""
import json
from build_waterfront_preview import prepare_basemap,WORK

prepare_basemap()
style=json.loads((WORK/'day01_light_style.json').read_text(encoding='utf-8'))
for layer in style['layers']:
 paint=layer.setdefault('paint',{})
 if layer['type']=='background':paint['background-color']='#fffaf1'
 elif layer['type']=='fill':paint['fill-color']='#deedf5' if layer['id']=='water' else '#fffaf1'
 elif layer['type']=='line':
  if layer['id']=='waterway':paint['line-color']='#c6dfeb'
  elif layer['id'].startswith(('highway','road','tunnel')):
   paint['line-color']='#e9e4db' if 'casing' in layer['id'] else '#fffaf1'
 elif layer['type']=='raster':layer.setdefault('layout',{})['visibility']='none'
(WORK/'day01_light_style.json').write_text(json.dumps(style),encoding='utf-8')
print('Prepared cream-land / baby-blue-water detail style from existing light-map recipe.')
