[out:json][timeout:180][date:"2026-09-01T00:00:00Z"];
(
  way["highway"](34.9905,135.7655,35.0080,135.7865);
  nwr["railway"~"station|halt|tram_stop|subway_entrance|platform"](34.9905,135.7655,35.0080,135.7865);
  nwr["public_transport"](34.9905,135.7655,35.0080,135.7865);
  nwr["amenity"~"toilets|shelter|bus_station"](34.9905,135.7655,35.0080,135.7865);
  nwr["emergency"](34.9905,135.7655,35.0080,135.7865);
  nwr["entrance"](34.9905,135.7655,35.0080,135.7865);
  nwr["tourism"](34.9905,135.7655,35.0080,135.7865);
  nwr["wheelchair"](34.9905,135.7655,35.0080,135.7865);
);
out body geom;
