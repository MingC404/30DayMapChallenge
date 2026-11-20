"""One metric 3-D scene, three orthographic cameras, software depth-buffer renderer.

Run with the existing Day18 Python interpreter. Requires the existing ../terrain/.deps.
All elevations are interpolated on the same triangulated 30m DSM surface.
No 2-D hillshade is transformed into a mock 3-D image.
"""
from pathlib import Path
import sys,json,csv,hashlib,math
R=Path(__file__).resolve().parent;DAY=R.parent
sys.path.insert(0,str(DAY/'terrain/.deps'))
import numpy as np,rasterio
from rasterio.warp import transform as transform_xy
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
W,H=1600,1800
FRAME=(70,270,1530,1510)
VE=1.20
PAPER=np.array([243,239,225],dtype=np.uint8)
ELEVATIONS=[45.,30.,18.]
NAMES=['A_gentle_oblique','B_landscape_depth','C_monumental_mountain']
TITLES=['Gentle Oblique','Landscape Depth','Monumental Mountain']
sources=[DAY/'terrain/data/dem_glo30_tm2_30m.tif',DAY/'research/data/tree_inventory_1_24.csv',DAY/'research/data/public_track_20240802.geojson']
preserved={str(p.relative_to(DAY)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['research','terrain/data','preview'] for p in (DAY/folder).rglob('*') if p.is_file() and '.deps' not in p.parts and '__pycache__' not in p.parts}
with rasterio.open(sources[0]) as src:
    dem=src.read(1);tf=src.transform
    # Contiguous native-grid vertices, around the chosen A / Forest Setting area.
    cols=np.arange(23,67);rows=np.arange(38,79)
    east=tf.c+(cols+.5)*tf.a;north=tf.f+(rows+.5)*tf.e
    zz=dem[np.ix_(rows,cols)].astype(float)
    assert src.crs.to_epsg()==3826 and src.res==(30.,30.)
west,eastedge=float(east[0]),float(east[-1]);south,northedge=float(north[-1]),float(north[0])
BOUNDS=[west,south,eastedge,northedge]
NY,NX=zz.shape
xx,yy=np.meshgrid(east,north)
vertices=np.column_stack([xx.ravel(),yy.ravel(),zz.ravel()])
faces=[]
for r in range(NY-1):
    for c in range(NX-1):
        a=r*NX+c;b=a+1;d=a+NX;e=d+1
        faces.extend([[a,b,e],[a,e,d]])
faces=np.array(faces,dtype=np.int32)
def ground(xy):
    """Exact piecewise planar barycentric interpolation on the rendered mesh."""
    xy=np.asarray(xy);u=(xy[...,0]-west)/30;v=(northedge-xy[...,1])/30
    c=np.clip(np.floor(u).astype(int),0,NX-2);r=np.clip(np.floor(v).astype(int),0,NY-2)
    u=np.clip(u-c,0,1);v=np.clip(v-r,0,1)
    z00=zz[r,c];z10=zz[r,c+1];z01=zz[r+1,c];z11=zz[r+1,c+1]
    return np.where(u>=v,(1-u)*z00+(u-v)*z10+v*z11,(1-v)*z00+u*z11+(v-u)*z01)
def project_geo(points):
    lon,lat=np.asarray(points).T;x,y=transform_xy('EPSG:4326','EPSG:3826',lon,lat)
    return np.column_stack([x,y])
inventory=list(csv.DictReader(sources[1].open(encoding='utf-8-sig')))
treerows=[r for r in inventory if r['best_available_category']=='B']
tree_xy=project_geo([[float(r['longitude']),float(r['latitude'])] for r in treerows])
tree_numbers=[int(r['tree_number']) for r in treerows]
tree_z=ground(tree_xy);tree_xyz=np.column_stack([tree_xy,tree_z])
assert len(tree_xyz)==15 and 13 not in tree_numbers
gpx=json.loads(sources[2].read_text())
segments=[];segment_ids=[];track_parts=[]
for partid,f in enumerate(gpx['features']):
    pts=project_geo(f['geometry']['coordinates']);track_parts.append(pts)
    for a,b in zip(pts,pts[1:]):
        if np.linalg.norm(b-a)<1e-7:continue
        # Preserve every original track edge and repeats, densify without smoothing.
        count=max(1,math.ceil(np.linalg.norm(b-a)/3.))
        sub=a+np.linspace(0,1,count+1)[:,None]*(b-a)
        for aa,bb in zip(sub,sub[1:]):segments.append([aa,bb]);segment_ids.append(partid)
segments=np.array(segments);mid=segments.mean(axis=1)
weights=np.linalg.norm(segments[:,1]-segments[:,0],axis=1)
assert np.all(tree_xy>=[west,south]) and np.all(tree_xy<=[eastedge,northedge])
assert np.all(segments>=[west,south]) and np.all(segments<=[eastedge,northedge])
track_xyz=np.dstack([segments,ground(segments)])
mid_xyz=np.column_stack([mid,ground(mid)])
center=np.array([(west+eastedge)/2,(south+northedge)/2,np.median(zz)])

def visible_rays(points,azimuth,elevation):
    """Independent terrain LOS test, not marker-label visibility.

    March toward camera horizontally at 1.5m, first check 1.5m from sample;
    compare rendered exaggerated terrain against the camera ray with 0.25m
    vertical tolerance. No terrain beyond this explicitly clipped scene is assumed.
    """
    angle=np.deg2rad(azimuth);direction=np.array([np.sin(angle),np.cos(angle)])
    distances=np.arange(1.5,2200,1.5)
    results=[]
    for start in range(0,len(points),96):
        p=points[start:start+96]
        q=p[:,None,:2]+distances[None,:,None]*direction
        inside=(q[...,0]>=west)&(q[...,0]<=eastedge)&(q[...,1]>=south)&(q[...,1]<=northedge)
        rayz=p[:,2,None]*VE+distances[None,:]*np.tan(np.deg2rad(elevation))
        terrain=ground(q)*VE
        blocked=inside&(terrain>rayz+.25)
        results.extend(~blocked.any(axis=1))
    return np.array(results)

# Data-based azimuth screen at B elevation; same chosen azimuth for all final cameras.
screen=[]
for az in [135.,180.,225.,270.,315.]:
    tv=visible_rays(tree_xyz,az,30)
    pv=visible_rays(mid_xyz[::4],az,30)
    right=np.array([-np.cos(np.deg2rad(az)),np.sin(np.deg2rad(az))])
    spread=float(np.ptp(tree_xy@right))
    score=float(tv.mean()*.48+pv.mean()*.40+min(spread/650,1)*.12)
    screen.append({'azimuth_deg':az,'tree_roots_visible':int(tv.sum()),'track_sample_visibility':float(pv.mean()),'horizontal_grove_spread_m':spread,'score':score})
AZ=max(screen,key=lambda s:s['score'])['azimuth_deg']
print('Azimuth screen:',json.dumps(screen),flush=True)

def camera_basis(az,el):
    az,el=np.deg2rad([az,el]);toward=np.array([np.sin(az)*np.cos(el),np.cos(az)*np.cos(el),np.sin(el)])
    right=np.array([-np.cos(az),np.sin(az),0.]);up=np.cross(toward,right)
    return np.array([right,up,toward])
world=vertices-center;world[:,2]*=VE
matrices=[camera_basis(AZ,e) for e in ELEVATIONS]
camera_coords=[world@m.T for m in matrices]
aspect=(FRAME[2]-FRAME[0])/(FRAME[3]-FRAME[1])
# Identical orthographic scale and world target make camera effects comparable.
ortho_height=max(max(np.max(np.abs(p[:,1]))*2,np.max(np.abs(p[:,0]))*2/aspect) for p in camera_coords)*1.13
scale=(FRAME[3]-FRAME[1])/ortho_height
def to_screen(xyz,matrix):
    p=np.asarray(xyz)-center;p=p.copy();p[...,2]*=VE
    cam=p@matrix.T
    out=cam.copy();out[...,0]=(FRAME[0]+FRAME[2])/2+cam[...,0]*scale
    out[...,1]=(FRAME[1]+FRAME[3])/2-cam[...,1]*scale
    return out
def raster_triangle(points,color,depth,rgb):
    x0=max(0,int(np.floor(points[:,0].min())));x1=min(W-1,int(np.ceil(points[:,0].max())))
    y0=max(0,int(np.floor(points[:,1].min())));y1=min(H-1,int(np.ceil(points[:,1].max())))
    if x1<x0 or y1<y0:return
    a,b,c=points;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(den)<1e-10:return
    py,px=np.mgrid[y0:y1+1,x0:x1+1];px=px+.5;py=py+.5
    wa=((b[1]-c[1])*(px-c[0])+(c[0]-b[0])*(py-c[1]))/den
    wb=((c[1]-a[1])*(px-c[0])+(a[0]-c[0])*(py-c[1]))/den;wc=1-wa-wb
    z=wa*a[2]+wb*b[2]+wc*c[2]
    target=depth[y0:y1+1,x0:x1+1];keep=(wa>=-1e-7)&(wb>=-1e-7)&(wc>=-1e-7)&(z>target)
    target[keep]=z[keep];rgb[y0:y1+1,x0:x1+1][keep]=color
def raster_line(a,b,color,width,depth,rgb,epsilon=.7):
    n=max(2,int(np.ceil(np.max(np.abs(b[:2]-a[:2]))*2))+1)
    pts=a+np.linspace(0,1,n)[:,None]*(b-a)
    for dx in range(-width,width+1):
        for dy in range(-width,width+1):
            if dx*dx+dy*dy>width*width:continue
            x=np.floor(pts[:,0]+dx).astype(int);y=np.floor(pts[:,1]+dy).astype(int)
            ok=(x>=0)&(x<W)&(y>=0)&(y<H);x,y,z=x[ok],y[ok],pts[ok,2]
            keep=z>=depth[y,x]-epsilon;x,y,z=x[keep],y[keep],z[keep]
            rgb[y,x]=color;depth[y,x]=np.maximum(depth[y,x],z)

np.savez_compressed(R/'scene_mesh_epsg3826.npz',vertices_epsg3826_egm2008=vertices,faces=faces,tree_xyz=tree_xyz,tree_numbers=tree_numbers,track_segments_xyz=track_xyz,track_segment_part=segment_ids)
scene={'crs':'EPSG:3826','vertical_datum':'EGM2008','source_product':'Copernicus GLO-30 DSM, nominal 30m; includes canopy, not bare earth','mesh_bounds_epsg3826':BOUNDS,'mesh_vertices':len(vertices),'mesh_triangles':len(faces),'native_grid_m':30,'interpolation':'piecewise planar barycentric on the same terrain triangles','target_world_epsg3826_egm2008':center.tolist(),'azimuth_convention':'camera position bearing clockwise from EPSG:3826 grid north; looks toward target','vertical_exaggeration':VE,'marker_height_m_before_exaggeration':22,'marker_ground_clearance_m':0,'track_render_offset_m':.12,'root_visibility':'terrain LOS, 1.5m horizontal marching, 0.25m vertical tolerance after exaggeration','trail_visibility':'length-weighted horizontal GPX edge midpoint LOS; repeats retained; not unique trail-network completeness','root_records':[{'number':n,'easting':float(p[0]),'northing':float(p[1]),'surface_elevation_m_egm2008':float(p[2]),'status':'unverified OSM tree candidate; DSM surface not measured trunk base'} for n,p in zip(tree_numbers,tree_xyz)],'azimuth_screen':screen,'sources':[{'file':str(p.relative_to(DAY)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]}
(R/'scene.json').write_text(json.dumps(scene,indent=2),encoding='utf8')
results=[]
fontdir=Path('C:/Windows/Fonts')
def font(n,f='body'):return ImageFont.truetype(str(fontdir/('georgia.ttf' if f=='title' else 'segoeui.ttf')),n)
for title,name,elevation,matrix in zip(TITLES,NAMES,ELEVATIONS,matrices):
    rgb=np.empty((H,W,3),dtype=np.uint8);rgb[:]=PAPER;depth=np.full((H,W),-np.inf)
    projected=to_screen(vertices,matrix)
    # Face normals on actual 3-D exaggerated mesh; constant sun for all cameras.
    sun=np.array([-.50,-.32,.805]);sun/=np.linalg.norm(sun)
    for face in faces:
        a,b,c=world[face];normal=np.cross(b-a,c-a)
        if normal[2]<0:normal=-normal
        normal/=np.linalg.norm(normal);illum=max(0,float(normal@sun))
        color=np.array([112,147,128])*(.66+.42*illum)+np.array([37,34,24])*.12
        raster_triangle(projected[face],np.uint8(np.clip(color,0,255)),depth,rgb)
    terrain_depth=depth.copy()
    # Exercise the actual raster depth test, separately from the LOS visibility model.
    probe_rgb=rgb.copy();probe_depth=terrain_depth.copy()
    buried_probe=tree_xyz.copy();buried_probe[:,2]-=60
    buried_top=buried_probe.copy();buried_top[:,2]+=8
    for a,b in zip(to_screen(buried_probe,matrix),to_screen(buried_top,matrix)):
        raster_line(a,b,[255,0,255],2,probe_depth,probe_rgb)
    assert np.array_equal(probe_rgb,rgb),'Buried geometry leaked through terrain depth buffer'
    route=track_xyz.copy();route[:,:,2]+=.12
    for seg in to_screen(route,matrix):raster_line(seg[0],seg[1],[159,104,61],1,depth,rgb)
    root_vis=visible_rays(tree_xyz,AZ,elevation)
    top_xyz=tree_xyz.copy();top_xyz[:,2]+=22
    top_vis=visible_rays(top_xyz,AZ,elevation)
    projected_roots=to_screen(tree_xyz,matrix);projected_tops=to_screen(top_xyz,matrix)
    for a,b in zip(projected_roots,projected_tops):raster_line(a,b,[28,62,44],2,depth,rgb)
    # Root crosses are true 3-D ground-clamped segments, not floating 2-D markers.
    for p in tree_xyz:
        for delta in [[5,0],[0,5]]:
            pp=np.array([p[:2]-delta,p[:2]+delta]);zzp=ground(pp)
            co=to_screen(np.column_stack([pp,zzp+.10]),matrix);raster_line(co[0],co[1],[36,73,51],1,depth,rgb)
    trail_vis=visible_rays(mid_xyz,AZ,elevation)
    fraction=float(np.sum(weights[trail_vis])/weights.sum())
    # A buried-probe test catches see-through-terrain regressions in the LOS model.
    buried=tree_xyz.copy();buried[:,2]-=60
    assert not visible_rays(buried,AZ,elevation).any()
    result={'name':title,'file':name+'.png','camera_azimuth_deg':AZ,'camera_elevation_deg':elevation,'orthographic_scale_vertical_m':ortho_height,'orthographic_scale_horizontal_m':ortho_height*aspect,'vertical_exaggeration':VE,'visible_tree_root_count':int(root_vis.sum()),'visible_tree_root_numbers':[n for n,v in zip(tree_numbers,root_vis) if v],'visible_marker_any_part_count':int(top_vis.sum()),'visible_trail_fraction':fraction,'total_reference_track_planar_m':float(weights.sum()),'visible_reference_track_planar_m':float(weights[trail_vis].sum()),'terrain_depth_test_enabled':True,'buried_60m_test_all_hidden':True,'world_to_camera_matrix':matrix.tolist(),'root_screen_coordinates':[{'number':n,'x':float(p[0]),'y':float(p[1]),'camera_depth':float(p[2]),'root_los_visible':bool(v)} for n,p,v in zip(tree_numbers,projected_roots,root_vis)]}
    im=Image.fromarray(rgb);draw=ImageDraw.Draw(im)
    def text(pos,s,n=24,face='body',fill=(44,65,51),anchor=None):draw.text(pos,s,font=font(n,face),fill=fill,anchor=anchor)
    text((85,60),'DAY 18 / NULL   ·   OBLIQUE CAMERA STUDY',22)
    text((80,103),'Among the Ancient Trees',55,'title')
    text((85,184),title+f'  /  camera elevation {elevation:.0f}°',28)
    # Annotation labels only for a terrain-visible marker top. Labels are not spatial objects.
    for n,p,v in zip(tree_numbers,projected_tops,top_vis):
        if v:text((p[0]+5,p[1]-4),str(n),17,anchor='ls')
    text((85,1525),f'Azimuth {AZ:.0f}°   /   Elevation {elevation:.0f}°   /   Vertical exaggeration {VE:.2f}×',23)
    text((85,1567),f'Orthographic height {ortho_height:,.0f} m   /   Visible roots {int(root_vis.sum())}/15   /   GPX visible {fraction:.1%}',23)
    text((85,1620),'Green: 3-D root / upright test marker     Ochre: terrain-draped reference GPX',21)
    text((85,1661),'Tree locations are approximate and unverified. Markers are not measured tree heights.',19)
    text((85,1702),'Copernicus GLO-30 DSM · 30 m · EGM2008 / EPSG:3826 · Sources and licence: 18/NOTICE.md',18)
    text((85,1736),'Orthographic terrain mesh + depth buffer; the same world coordinates and target in every view.',18)
    im.save(R/(name+'.png'),dpi=(220,220));results.append(result)
    print(title,root_vis.sum(),fraction,flush=True)
    np.savez_compressed(R/(name+'_depth.npz'),terrain_camera_depth=terrain_depth.astype('float32'))
(R/'camera_comparison.json').write_text(json.dumps(results,indent=2),encoding='utf8')
with (R/'camera_comparison.csv').open('w',newline='',encoding='utf-8-sig') as f:
    fields=['name','camera_azimuth_deg','camera_elevation_deg','orthographic_scale_vertical_m','orthographic_scale_horizontal_m','vertical_exaggeration','visible_tree_root_count','visible_marker_any_part_count','visible_trail_fraction']
    writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(results)
assert all(hashlib.sha256((DAY/p).read_bytes()).hexdigest()==sha for p,sha in preserved.items())
checks={'protected_files_unchanged':len(preserved),'root_surface_residual_max_m':float(np.max(abs(tree_xyz[:,2]-ground(tree_xyz[:,:2])))),'route_surface_residual_max_m':float(np.max(abs(track_xyz[:,:,2]-ground(track_xyz[:,:,:2])))),'all_roots_inside_scene':True,'all_gpx_edges_inside_scene':True,'tree_candidate_count':15,'candidate_13_excluded':True,'same_projection_for_terrain_track_markers':True,'same_camera_azimuth_and_ortho_scale':True,'real_terrain_mesh_not_warped_hillshade':True,'source_files':scene['sources']}
(R/'validation.json').write_text(json.dumps(checks,indent=2),encoding='utf8')
print('Validation',checks,flush=True)
