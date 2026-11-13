# Display metadata only: derive nearby real junctions from City street nodes.
# No mobility data, selection rules, or statistics are read or changed.
suppressPackageStartupMessages({library(sf);library(jsonlite)})
roads <- st_transform(st_read('13/.local/context/streets_complete.geojson',quiet=TRUE),26918)
dest <- st_transform(st_read('13/.local/data/destinations.geojson',quiet=TRUE),26918)
road_names <- c('MARKET','CHESTNUT','WALNUT','LOCUST','SPRUCE','38TH','39TH','40TH','41ST','42ND','43RD','44TH','45TH')
roads <- roads[roads$st_name %in% road_names,]
ends <- do.call(rbind,lapply(seq_len(nrow(roads)),function(i){
  xy <- st_coordinates(st_geometry(roads)[i])[,1:2,drop=FALSE]
  data.frame(node=as.character(c(roads$fnode_[i],roads$tnode_[i])),street=roads$st_name[i],
    segment=roads$seg_id[i],x=c(xy[1,1],xy[nrow(xy),1]),y=c(xy[1,2],xy[nrow(xy),2]))
}))
nodes <- list()
for(id in unique(ends$node)) {
  e <- ends[ends$node==id,];names <- unique(e$street)
  numbered <- names[grepl('^[0-9]',names)];cross <- names[!grepl('^[0-9]',names)]
  if(length(numbered)!=1 || length(cross)!=1) next
  nodes[[length(nodes)+1]] <- data.frame(node=id,numbered=numbered,cross=cross,
    segments=paste(unique(e$segment),collapse=','),x=mean(e$x),y=mean(e$y))
}
nodes <- st_as_sf(do.call(rbind,nodes),coords=c('x','y'),crs=26918)
pretty <- function(x) if(grepl('^[0-9]',x)) paste0(tolower(x),' St') else paste0(substr(x,1,1),tolower(substr(x,2,nchar(x))),' St')
labels <- list(); evidence <- list()
for(i in seq_len(nrow(dest))) {
  d <- dest[i,]; p <- suppressWarnings(st_point_on_surface(d))
  # Only genuine junction nodes within/along this CBG (15 m source-line tolerance).
  candidates <- nodes[lengths(st_intersects(nodes,st_buffer(d,15)))>0,]
  stopifnot(nrow(candidates)>0)
  distance <- as.numeric(st_distance(p,candidates))
  chosen <- candidates[which.min(distance),]
  id <- as.character(d$GEOID)
  title <- paste(pretty(chosen$numbered),'&',pretty(chosen$cross))
  labels[[id]] <- list(title=title,qualifier='Junction area',GEOID=id)
  xy <- st_coordinates(st_transform(chosen,4326))
  evidence[[i]] <- data.frame(GEOID=id,label=title,node=chosen$node,segments=chosen$segments,
    distance_from_interior_point_m=min(distance),longitude=xy[1],latitude=xy[2],
    within_cbg_or_15m_tolerance=TRUE)
}
write_json(labels,'13/.local/metadata/destination_labels.json',auto_unbox=TRUE,pretty=TRUE)
write.csv(do.call(rbind,evidence),'13/.local/metadata/destination_label_evidence.csv',row.names=FALSE)
print(do.call(rbind,evidence),row.names=FALSE)
