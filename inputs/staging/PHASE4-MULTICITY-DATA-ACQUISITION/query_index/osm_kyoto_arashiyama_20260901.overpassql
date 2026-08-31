[out:json][timeout:180][date:"2026-09-01T00:00:00Z"];
(
  way["highway"](35.0000,135.6710,35.0220,135.6890);
  nwr["railway"~"station|halt|tram_stop|subway_entrance|platform"](35.0000,135.6710,35.0220,135.6890);
  nwr["public_transport"](35.0000,135.6710,35.0220,135.6890);
  nwr["amenity"~"toilets|shelter|bus_station"](35.0000,135.6710,35.0220,135.6890);
  nwr["emergency"](35.0000,135.6710,35.0220,135.6890);
  nwr["entrance"](35.0000,135.6710,35.0220,135.6890);
  nwr["tourism"](35.0000,135.6710,35.0220,135.6890);
  nwr["wheelchair"](35.0000,135.6710,35.0220,135.6890);
);
out body geom;
