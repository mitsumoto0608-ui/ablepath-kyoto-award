[out:json][timeout:180][date:"2026-09-01T00:00:00Z"];
(
  way["highway"](35.2950,139.4720,35.3140,139.4935);
  nwr["railway"~"station|halt|tram_stop|subway_entrance|platform"](35.2950,139.4720,35.3140,139.4935);
  nwr["public_transport"](35.2950,139.4720,35.3140,139.4935);
  nwr["amenity"~"toilets|shelter|bus_station"](35.2950,139.4720,35.3140,139.4935);
  nwr["emergency"](35.2950,139.4720,35.3140,139.4935);
  nwr["entrance"](35.2950,139.4720,35.3140,139.4935);
  nwr["tourism"](35.2950,139.4720,35.3140,139.4935);
  nwr["wheelchair"](35.2950,139.4720,35.3140,139.4935);
);
out body geom;
