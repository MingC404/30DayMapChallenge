"""Real DSM analysis only. Historical 2-D preview rendering has been retired."""
import sys,pathlib,json,csv,math,hashlib
R=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'.deps'));sys.path.insert(0,str(R.parent/'research/.deps'))
import numpy as np, rasterio
from rasterio.transform import from_origin
from rasterio.warp import reproject,Resampling,transform as transform_coords
from scipy.ndimage import gaussian_filter,zoom,label
from skimage.measure import find_contours
from skimage.morphology import skeletonize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image,ImageDraw,ImageFont,ImageFilter
D=R/'data'
meta=json.loads((D/'dem_acquisition.json').read_text())
view=meta['view_bounds_epsg3826'];bounds=meta['processing_bounds_epsg3826'];res=30
w=int((bounds[2]-bounds[0])/res);h=int((bounds[3]-bounds[1])/res)
tr=from_origin(bounds[0],bounds[3],res,res)
z=np.full((h,w),-9999,dtype='float32')
with rasterio.open(D/'copernicus_glo30_native_aoi.tif') as src:
    reproject(rasterio.band(src,1),z,src_transform=src.transform,src_crs=src.crs,dst_transform=tr,dst_crs='EPSG:3826',resampling=Resampling.bilinear,dst_nodata=-9999)
assert np.isfinite(z).all() and np.all(z>-9999)
profile=dict(driver='GTiff',width=w,height=h,count=1,dtype='float32',crs='EPSG:3826',transform=tr,nodata=-9999,compress='deflate')
def tif(name,a,meaning):
    with rasterio.open(D/name,'w',**profile) as dst:
        dst.write(a.astype('float32'),1);dst.update_tags(source='Copernicus GLO-30 nominal 30m DSM',meaning=meaning,vertical_datum='EGM2008; no TWVD2001 conversion')
def fc(name,features):
    (D/name).write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,indent=2),encoding='utf8')
def native_xy(rc):
    r,c=np.asarray(rc).T;return np.column_stack([bounds[0]+(c+.5)*res,bounds[3]-(r+.5)*res])
def geographic(coords):
    x,y=np.asarray(coords).T;lon,lat=transform_coords('EPSG:3826','EPSG:4326',x,y);return np.column_stack([lon,lat]).tolist()
tif('dem_glo30_tm2_30m.tif',z,'Bilinear reprojected DSM; 30m output grid, not MOI DTM')
zs=gaussian_filter(z,.65)
dy,dx=np.gradient(zs,res,res);east=dx;north=-dy
slope=np.arctan(np.hypot(east,north))
def shade(az,alt=38):
    az,alt=np.deg2rad([az,alt]);return np.clip((-east*np.sin(az)*np.cos(alt)-north*np.cos(az)*np.cos(alt)+np.sin(alt))/np.sqrt(1+east**2+north**2),0,1)
hs=shade(315);multi=.5*hs+.25*shade(270)+.25*shade(45)
tif('hillshade_nw.tif',hs,'315deg azimuth, 38deg altitude; z factor 1; 0.65-cell Gaussian smoothing')
tif('hillshade_multidirectional.tif',multi,'weighted 315/270/45deg hillshade, 38deg altitude, z factor 1')
tif('slope_degrees.tif',np.rad2deg(slope),'slope of smoothed DSM, projected metric gradients')
tpi=zs-gaussian_filter(zs,5)
tif('tpi_150m.tif',tpi,'DSM minus Gaussian neighborhood sigma 150m; signed landform interpretation, not measured crest/channel')
contours=[];contour_xy=[]
for level in range(int(np.ceil(z.min()/20)*20),int(z.max())+1,20):
    for rc in find_contours(z,level):
        if len(rc)<4:continue
        coords=native_xy(rc);contour_xy.append((level,coords))
        contours.append({'type':'Feature','geometry':{'type':'LineString','coordinates':geographic(coords)},'properties':{'elevation_m':level,'interval_m':20,'vertical_datum':'EGM2008','source':'Copernicus GLO-30 DSM, 30m projected grid','major':level%100==0}})
fc('contours_20m.geojson',contours)
# Candidate crest and concavity axes from local relative height. No hydrological claim.
interpret=[];skels={}
for kind,mask in [('ridge',tpi>12),('valley',tpi<-12)]:
    sk=skeletonize(mask & (np.rad2deg(slope)>4))
    lab,n=label(sk,structure=np.ones((3,3)))
    sizes=np.bincount(lab.ravel());sk &= sizes[lab]>=5;skels[kind]=sk
    coords=set(map(tuple,np.argwhere(sk)));neighbors={p:[q for q in coords if max(abs(q[0]-p[0]),abs(q[1]-p[1]))==1] for p in []}
    neighbors={p:[(p[0]+dr,p[1]+dc) for dr in [-1,0,1] for dc in [-1,0,1] if (dr or dc) and (p[0]+dr,p[1]+dc) in coords] for p in coords}
    used=set()
    for start in sorted(coords,key=lambda p:len(neighbors[p])==2):
        for nextp in neighbors[start]:
            edge=frozenset([start,nextp])
            if edge in used:continue
            path=[start,nextp];used.add(edge)
            while len(neighbors[path[-1]])==2:
                nxt=next(q for q in neighbors[path[-1]] if q!=path[-2]);edge=frozenset([path[-1],nxt])
                if edge in used:break
                path.append(nxt);used.add(edge)
            if len(path)<4:continue
            pts=native_xy(path)
            interpret.append({'type':'Feature','geometry':{'type':'LineString','coordinates':geographic(pts)},'properties':{'interpretation':kind,'method':'skeleton of signed TPI threshold +/-12m, Gaussian sigma150m','status':'model-derived candidate; not surveyed; not a stream inventory'}})
fc('ridge_valley_candidates.geojson',interpret)
for kind,sk in skels.items():tif(kind+'_candidate_mask.tif',sk,kind+' TPI skeleton candidate; not measured network')
hist,edges=np.histogram(z,bins=np.arange(math.floor(z.min()/50)*50,math.ceil(z.max()/50)*50+1,50))
with (D/'elevation_distribution.csv').open('w',newline='',encoding='utf-8') as f:
    cw=csv.writer(f);cw.writerow(['lower_m','upper_m','cells','area_km2','percent'])
    for n,lo,hi in zip(hist,edges,edges[1:]):cw.writerow([lo,hi,int(n),n*res**2/1e6,100*n/z.size])
row0=int((bounds[3]-view[3])/res);col0=int((view[0]-bounds[0])/res)
vh=int((view[3]-view[1])/res);vw=int((view[2]-view[0])/res)
v=z[row0:row0+vh,col0:col0+vw]
stats={'analysis_crs':'EPSG:3826','vertical_datum':'EGM2008','source_nominal_resolution_m':30,'analysis_grid_m':30,'analysis_shape':[h,w],'view_bounds_epsg3826':view,'processing_bounds_epsg3826':bounds,'analysis_area_km2':z.size*res**2/1e6,'nodata_cells':0,'analysis_min_m':float(z.min()),'analysis_max_m':float(z.max()),'analysis_mean_m':float(z.mean()),'analysis_percentiles_m':{str(q):float(np.percentile(z,q)) for q in [5,25,50,75,95]},'view_min_m':float(v.min()),'view_max_m':float(v.max()),'contour_features':len(contours),'ridge_valley_candidate_features':len(interpret),'display_contour_interval_m':40,'vertical_exaggeration':1,'gpx_geometry_modified':False}
(D/'analysis_summary.json').write_text(json.dumps(stats,indent=2),encoding='utf8')
with PdfPages(D/'terrain_diagnostics.pdf') as pdf:
    fig,axs=plt.subplots(2,2,figsize=(10,11),layout='constrained')
    extent=[bounds[0],bounds[2],bounds[1],bounds[3]]
    axs[0,0].imshow(z,extent=extent,cmap='terrain');axs[0,0].set_title('GLO-30 DSM / 30 m grid / EGM2008 metres')
    axs[0,1].imshow(multi,extent=extent,cmap='gray',vmin=0,vmax=1);axs[0,1].set_title('Multi-direction hillshade / z factor 1')
    axs[1,0].imshow(tpi,extent=extent,cmap='BrBG',vmin=-35,vmax=35)
    for level,co in contour_xy:
        if level%100==0:axs[1,0].plot(co[:,0],co[:,1],color='k',lw=.3)
    for kind,color in [('ridge','#9b5a38'),('valley','#225a73')]:
        r,c=np.where(skels[kind]);axs[1,0].scatter(bounds[0]+(c+.5)*res,bounds[3]-(r+.5)*res,s=1,c=color,label=kind+' candidate')
    axs[1,0].legend(fontsize=7);axs[1,0].set_title('TPI + model-derived ridge / valley candidates')
    axs[1,1].hist(z.ravel(),bins=edges,color='#3b786b',edgecolor='white');axs[1,1].set(xlabel='Surface elevation (m, EGM2008)',ylabel='30 m grid cells',title='Elevation distribution / buffered analysis AOI')
    for ax in axs.flat[:3]:ax.tick_params(labelsize=6);ax.set_aspect('equal')
    pdf.savefig(fig);plt.close(fig)

