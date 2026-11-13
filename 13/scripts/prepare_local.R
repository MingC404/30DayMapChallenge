# Restricted outputs are confined to 13/.local, excluded by 13/.gitignore.
suppressPackageStartupMessages({library(sf); library(arrow); library(dplyr); library(jsonlite)})
sf_use_s2(FALSE)
source_root <- 'E:/MUSA/6890 city at night/city at night'
out <- '13/.local'
ctx <- file.path(out,'context')
dir.create(file.path(out,'data'),recursive=TRUE,showWarnings=FALSE)
dir.create(file.path(out,'metadata'),recursive=TRUE,showWarnings=FALSE)
write_geo <- function(x,name,tolerance=0) {
  if(all(st_geometry_type(x) %in% c('POLYGON','MULTIPOLYGON'))) {
    xy <- st_coordinates(st_transform(suppressWarnings(st_point_on_surface(x)),4326))
    x$anchor_lon <- xy[,1]; x$anchor_lat <- xy[,2]
  }
  if(tolerance>0) x <- st_simplify(x,dTolerance=tolerance,preserveTopology=TRUE)
  st_write(st_transform(x,4326),file.path(out,'data',paste0(name,'.geojson')),delete_dsn=TRUE,quiet=TRUE)
}
streets <- st_transform(st_read(file.path(ctx,'streets_complete.geojson'),quiet=TRUE),26918)
edge <- streets[streets$st_name %in% c('MARKET','SPRUCE','38TH','45TH'),]
print(table(edge$st_name))
polys <- st_cast(st_collection_extract(st_polygonize(st_union(st_geometry(edge))),'POLYGON'),'POLYGON')
print(st_area(polys))
stopifnot(length(polys)>0)
# The four complete road chains form one enclosed area; no rectangle approximation.
target <- st_sf(name='Market–Spruce / 38th–45th',geometry=polys[which.max(st_area(polys))])
stopifnot(as.numeric(st_area(target))>5e5,as.numeric(st_area(target))<3e6)
write_geo(target,'target')
write_geo(edge[c('seg_id','st_name','streetlabe')],'boundary_roads')
g <- readRDS(file.path(source_root,'output/philadelphia_cbgs_2024_geometry.rds'))
g <- st_transform(st_make_valid(g['GEOID']),26918)
g$GEOID <- as.character(g$GEOID)
stopifnot(!anyDuplicated(g$GEOID),all(st_is_valid(g)))
candidates <- st_filter(g,target,.predicate=st_intersects)
candidates$cbg_m2 <- as.numeric(st_area(candidates))
ix <- suppressWarnings(st_intersection(candidates,target))
area <- tapply(as.numeric(st_area(ix)),ix$GEOID,sum)
candidates$overlap_m2 <- as.numeric(area[candidates$GEOID])
candidates$overlap_m2[is.na(candidates$overlap_m2)] <- 0
candidates$overlap_pct <- 100*candidates$overlap_m2/candidates$cbg_m2
# Report all contact candidates. Exclude boundary-only/slivers <1% AND <1000m2.
candidates$small_overlap <- candidates$overlap_pct<1 & candidates$overlap_m2<1000
candidates$included <- !candidates$small_overlap
selection <- st_drop_geometry(candidates)
write.csv(selection,file.path(out,'data/destination_selection.csv'),row.names=FALSE)
print(selection)
dest <- candidates[candidates$included,]
write_geo(candidates,'destination_candidates')
write_geo(dest,'destinations')
write_geo(g,'philadelphia',10)
write_geo(streets[c('streetlabe','st_name','class')],'streets',1)
major <- st_read(file.path(ctx,'major_streets.geojson'),quiet=TRUE)
write_geo(st_transform(major[c('streetlabe','class')],26918),'major_streets',8)
w <- st_read(file.path(ctx,'tl_2024_42101_areawater/tl_2024_42101_areawater.shp'),quiet=TRUE)
w <- st_transform(w,26918)
w <- w[as.numeric(st_area(w))>200000,]
write_geo(w[intersect('FULLNAME',names(w))],'water',10)

records <- list(); links <- list(); checks <- list()
for(month in c('2025-08','2025-09')) {
  f <- list.files(file.path(source_root,'data/neighborhood-patterns'),paste0('^',month),full.names=TRUE)
  stopifnot(length(f)==1)
  ids <- candidates$GEOID
  z <- collect(filter(open_dataset(f), AREA %in% ids))
  stopifnot(!anyDuplicated(z$AREA),all(z$AREA_TYPE=='Census Block Group'),all(z$ORIGIN_AREA_TYPE=='Census Block Group'))
  stopifnot(all(format(z$DATE_RANGE_START,'%Y-%m')==month))
  expected_end <- if(month=='2025-08') '2025-09-01' else '2025-10-01'
  stopifnot(all(as.character(as.Date(z$DATE_RANGE_END))==expected_end))
  for(id in ids) {
    row <- z[z$AREA==id,]
    status <- if(!nrow(row)) 'missing record' else if(is.na(row$NIGHTLIFE_DEVICE_HOME_AREAS) || trimws(row$NIGHTLIFE_DEVICE_HOME_AREAS) %in% c('','{}','null')) 'unreported origins' else 'reported'
    checks[[length(checks)+1]] <- data.frame(month=month,GEOID=id,status=status)
    if(!id %in% dest$GEOID) next
    if(status!='reported') next
    a <- unlist(fromJSON(row$NIGHTLIFE_DEVICE_HOME_AREAS),use.names=TRUE)
    stopifnot(is.numeric(a),!is.null(names(a)),all(is.finite(a)),all(a>=0),!anyDuplicated(names(a)))
    links[[length(links)+1]] <- data.frame(month=month,destination=id,origin=names(a),value=as.numeric(a))
  }
}
links <- bind_rows(links); checks <- bind_rows(checks)
write.csv(checks,file.path(out,'data/destination_month_coverage.csv'),row.names=FALSE)
write.csv(links,file.path(out,'data/restricted_associations.csv'),row.names=FALSE)

# Regional cartographic CBG geometry. Full destination units retain detailed cache geometry.
regional <- bind_rows(lapply(c('42','34','10'),function(state) {
  n <- paste0('cb_2024_',state,'_bg_500k')
  b <- st_read(file.path(ctx,n,paste0(n,'.shp')),quiet=TRUE)
  st_transform(b['GEOID'],26918)
}))
regional$GEOID <- as.character(regional$GEOID)
stopifnot(!anyDuplicated(regional$GEOID))
regional <- st_make_valid(regional)
center <- st_centroid(st_geometry(target))
nearby <- st_filter(regional,st_buffer(center,80000))
# Philadelphia cache replaces generalized versions and preserves small CBGs.
regional <- rbind(nearby[!nearby$GEOID %in% g$GEOID,],g)
write_geo(st_sf(geometry=st_union(st_geometry(regional))),'regional_context',25)
origin_ids <- unique(links$origin)
origins <- regional[regional$GEOID %in% origin_ids,]
stopifnot(!anyDuplicated(origins$GEOID),all(st_is_valid(origins)))
write_geo(origins,'origins',8)
print(paste('Destination count',nrow(dest),'origin geometries',nrow(origins)))
print(checks)
summaries <- list(); data <- list()
for(month in unique(links$month)) {
  data[[month]] <- list()
  for(id in c('all',dest$GEOID)) {
    x <- links[links$month==month & (id=='all' | links$destination==id),]
    a <- aggregate(value~origin,x,sum)
    total <- sum(a$value)
    mapped <- a$origin %in% origins$GEOID
    philly <- substr(a$origin,1,5)=='42101'
    nearby_mask <- mapped & !philly
    invalid <- !grepl('^[0-9]{12}$',a$origin)
    s <- data.frame(month=month,destination=id,represented_value_sum=total,
      origin_ids=nrow(a),mapped_pct=100*sum(a$value[mapped])/total,
      philadelphia_pct=100*sum(a$value[philly])/total,
      nearby_mapped_pct=100*sum(a$value[nearby_mask])/total,
      outside_geometry_pct=100*sum(a$value[!mapped])/total,
      non_us_pct=100*sum(a$value[invalid])/total,
      reported_destinations=sum(checks$month==month & checks$status=='reported' & checks$GEOID %in% dest$GEOID & (id=='all' | checks$GEOID==id)))
    stopifnot(abs(s$mapped_pct+s$outside_geometry_pct-100)<1e-8)
    data[[month]][[id]] <- list(total=total,values=setNames(as.list(a$value),a$origin),coverage=as.list(s))
    summaries[[length(summaries)+1]] <- s
  }
}
summaries <- bind_rows(summaries)
write.csv(summaries,file.path(out,'data/coverage_summary.csv'),row.names=FALSE)
write_json(list(months=data,checks=checks,destinations=dest$GEOID,
  selection=selection,geometry_ids=origins$GEOID),file.path(out,'data/restricted.json'),auto_unbox=TRUE,digits=12)
print(summaries[summaries$destination=='all',])
cat('Local preparation complete. Restricted outputs must remain ignored.\n')
