"""Inspect closed OSM street-centerline faces; retain reproducible evidence."""
import json
from pathlib import Path
import matplotlib.pyplot as plt
from shapely.geometry import LineString, mapping, Point
from shapely.ops import transform, unary_union, polygonize
import render_study as study

REVIEW=study.ROOT/'review'; REVIEW.mkdir(exist_ok=True)
CLASSES={'primary','secondary','tertiary','residential','unclassified','living_street','pedestrian'}

def blocks(panel):
    c,window,buildings,roads,meta=panel
    elements=study.fetch(c)['elements']; lines=[]; named=[]
    for el in elements:
        t=el.get('tags',{})
        if el['type']=='way' and t.get('highway') in CLASSES and t.get('area')!='yes':
            g=transform(study.TX.transform,LineString([(p['lon'],p['lat']) for p in el['geometry']]))
            lines.append(g); named.append((t.get('name','unnamed'),g))
    faces=[p for p in polygonize(unary_union(lines)) if window.buffer(-3).covers(p) and p.area>3500]
    faces.sort(key=lambda p:(-round(p.centroid.y/50),p.centroid.x))
    result=[]
    union=unary_union(buildings)
    for i,p in enumerate(faces):
        core=p.buffer(-15); void=core.difference(union)
        gaps=sorted(study.poly_parts(void),key=lambda p:p.area,reverse=True)
        names=sorted({name for name,g in named if p.boundary.intersection(g.buffer(.15)).length>20})
        result.append({'id':i,'geometry':mapping(p),'streets':names,'centerline_area_m2':p.area,
                       'core_area_m2':core.area,'core_unbuilt_m2':void.area,
                       'core_unbuilt_fraction':void.area/core.area,'largest_core_gap_m2':gaps[0].area if gaps else 0})
    return faces,result

def main():
    panels=[study.prepare(c) for c in study.C['candidates']]
    report={}
    fig,axs=plt.subplots(1,3,figsize=(18,6),facecolor=study.BG)
    for ax,panel in zip(axs,panels):
        study.draw(ax,panel); faces,records=blocks(panel)
        for i,p in enumerate(faces):
            ax.plot(*p.exterior.xy,color='#bd6b42',lw=1)
            ax.text(p.centroid.x,p.centroid.y,str(i),ha='center',va='center',fontsize=11,color='#75371c',bbox={'facecolor':study.BG,'edgecolor':'none','pad':2})
        ax.set_title(panel[0]['name']); report[panel[0]['slug']]=records
    fig.tight_layout(); fig.savefig(REVIEW/'block_candidates.png',dpi=160); plt.close(fig)
    (REVIEW/'block_candidates.json').write_text(json.dumps(report,indent=2))
    selected=[]
    for panel,index in zip(panels,[16,10,2]):
        faces,rs=blocks(panel); p=faces[index]; union=unary_union(panel[2]).intersection(p)
        gaps=list(study.poly_parts(p.buffer(-15).difference(union)))
        gap=max(gaps,key=lambda g:g.area)
        edges=[]
        for building in study.poly_parts(union):
            coords=list(building.exterior.coords)
            for a,b in zip(coords,coords[1:]):
                line=LineString([a,b])
                if line.length>8 and line.interpolate(.5,normalized=True).distance(p.boundary)<25:
                    edges.append(line)
        edge=max(edges,key=lambda g:g.length)
        record={**rs[index],'slug':panel[0]['slug'],'gap_geometry':mapping(gap),
                'gap_target':list(gap.representative_point().coords)[0],
                'longest_raw_facade_m':edge.length,'facade_geometry':mapping(edge),
                'facade_target':list(edge.interpolate(.5,normalized=True).coords)[0]}
        selected.append(record)
    (REVIEW/'selected_evidence.json').write_text(json.dumps(selected,indent=2))
    print('SELECTED',[(r['slug'],r['id'],round(r['longest_raw_facade_m'],1),round(r['largest_core_gap_m2'])) for r in selected])
    for name,rs in report.items():
        print(name)
        for r in rs: print(r['id'],','.join(r['streets']),round(r['centerline_area_m2']),round(r['core_unbuilt_fraction'],3),round(r['largest_core_gap_m2']))

if __name__=='__main__': main()
