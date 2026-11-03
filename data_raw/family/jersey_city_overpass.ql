[out:json][timeout:180];
(
 way["highway"](40.693,-74.055,40.735,-74.023);
 nwr["leisure"~"^(park|garden|playground)$"](40.693,-74.055,40.735,-74.023);
 nwr["natural"="water"](40.693,-74.055,40.735,-74.023);
 nwr["waterway"="riverbank"](40.693,-74.055,40.735,-74.023);
 way["natural"="coastline"](40.693,-74.055,40.735,-74.023);
);
out body geom;
