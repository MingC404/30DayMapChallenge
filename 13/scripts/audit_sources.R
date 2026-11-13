# Stage A only. Read external sources; print summaries, never export origin cells.
suppressPackageStartupMessages({library(arrow); library(sf); library(jsonlite)})
root <- 'E:/MUSA/6890 city at night/city at night'
cat('\nWEEKLY RAW FILES\n')
for (f in list.files(file.path(root,'data'), '\\.parquet$', full.names=TRUE)) {
  d <- as.data.frame(read_parquet(f))
  names(d) <- tolower(names(d))
  cat(basename(f), 'rows', nrow(d), '\n')
  print(unique(d[intersect(c('date_range_start','date_range_end'),names(d))]))
  cat('Origin/time/coordinate fields:', paste(grep('home|night|hour|latitude|longitude|id_store',names(d),value=TRUE),collapse=', '),'\n')
}
cat('\nLOCAL DERIVED POI COVERAGE\n')
d <- as.data.frame(read_parquet(file.path(root,'output/visits_U_City_West_200m.parquet')))
print(names(d))
print(unique(d[intersect(c('date_range_start','date_range_end'),names(d))]))
pois <- unique(d[intersect(c('id_store','location_name','street_address','latitude','longitude'),names(d))])
cat('unique POI/location records',nrow(pois),'unique IDs',length(unique(d$id_store)),'\n')
print(pois[grepl('Drink|Cinem|Terakawa|Rotunda',pois$location_name,ignore.case=TRUE),], row.names=FALSE)
cat('rows',nrow(d),'duplicate store/week',sum(duplicated(d[c('id_store','date_range_start')])),'\n')
cat('Missing/empty origin rows',sum(is.na(d$visitor_home_cbgs) | d$visitor_home_cbgs %in% c('','{}','null')),'\n')
cat('\nNIGHTTIME DERIVED COVERAGE\n')
n <- read.csv(file.path(root,'output/neighborhood_night_site_2025_AugSep.csv'),colClasses='character')
print(unique(n[c('date_range_start','date_range_end')]))
print(table(n$destination_cbg,n$date_range_start))
cat('duplicate destination/month',sum(duplicated(n[c('destination_cbg','date_range_start')])),'\n')
for (dest in unique(n$destination_cbg)) {
  z <- n[n$destination_cbg==dest,]
  a <- lapply(z$nightlife_home_origins, fromJSON)
  vals <- unlist(a); ids <- unlist(lapply(a,names))
  cat(dest,'months',nrow(z),'empty',sum(lengths(a)==0),'origin cells',length(vals),'unique origins',length(unique(ids)),'sum scaled values',sum(vals),'non-US cells',sum(!grepl('^[0-9]{12}$',ids)),'\n')
}
cat('\nCBG GEOMETRY\n')
g <- readRDS(file.path(root,'output/philadelphia_cbgs_2024_geometry.rds'))
cat('features',nrow(g),'crs',st_crs(g)$input,'fields',names(g),'\n')
site <- st_read(file.path(root,'output/U_City_West_boundary.geojson'),quiet=TRUE)
print(st_bbox(site))
target <- st_filter(g,st_transform(site,st_crs(g)))
cat('CBGs intersecting unbuffered site:',target$GEOID,'\n')
origins <- unlist(lapply(n$nightlife_home_origins,fromJSON))
keys <- names(origins)
cat('Origin cells',length(origins),'unique origin IDs',length(unique(keys)),
    'mapped Philly cells',sum(keys %in% g$GEOID),
    'Philly GEOIDs not matched',length(setdiff(unique(keys[grepl('^42101',keys)]),g$GEOID)),'\n')
cat('Hourly array lengths:'); print(table(vapply(d$visits_by_each_hour,function(x) if(is.na(x)) 0L else length(fromJSON(x)),integer(1))))
for (f in list.files(file.path(root,'data/neighborhood-patterns'),'\\.parquet$',full.names=TRUE)) {
  ds <- open_dataset(f)
  if (grepl('2025-08|2025-09',basename(f))) {
    cat('\nRAW NEIGHBORHOOD',basename(f),'\n')
    # Arrow predicate limits collection to destination CBGs in the prior extract.
    ids <- unique(n$destination_cbg)
    z <- dplyr::collect(dplyr::filter(ds, AREA %in% ids))
    cat('matching rows',nrow(z),'\n')
    print(unique(as.data.frame(z)[intersect(c('DATE_RANGE_START','DATE_RANGE_END','AREA_TYPE','ORIGIN_AREA_TYPE','YEAR','MONTH'),names(z))]))
    cat('Raw/extract exact JSON matches:',sum(z$NIGHTLIFE_DEVICE_HOME_AREAS %in% n$nightlife_home_origins),'\n')
  }
}
