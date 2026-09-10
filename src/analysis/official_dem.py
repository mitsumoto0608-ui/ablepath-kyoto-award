"""Parse and sample source-bound GSI DEM grid cells without interpolation."""

from __future__ import annotations

from dataclasses import dataclass
import math
import xml.etree.ElementTree as ET

from pyproj import Transformer


GML = "{http://www.opengis.net/gml/3.2}"


@dataclass(frozen=True)
class DemGrid:
    """A single GSI DEM member retaining its explicit grid and sequence contract."""

    mesh_id: str
    dem_class: str
    revision: str
    srs_name: str
    lower_lat: float
    lower_lon: float
    upper_lat: float
    upper_lon: float
    width: int
    height: int
    start_x: int
    start_y: int
    tuples: tuple[tuple[str, float], ...]

    def sample(self, longitude: float, latitude: float) -> dict:
        """Return the native containing cell; never interpolate or fill omitted data."""
        if not all(math.isfinite(value) for value in (longitude, latitude)):
            raise ValueError("DEM query coordinate must be finite")
        if not (self.lower_lon <= longitude <= self.upper_lon and self.lower_lat <= latitude <= self.upper_lat):
            return {"status": "OUTSIDE_MEMBER_COVERAGE", "elevation_m": None, "raw_value": None, "surface_type": None, "reason": "Query coordinate is outside this member envelope."}
        lon_step = (self.upper_lon - self.lower_lon) / self.width
        lat_step = (self.upper_lat - self.lower_lat) / self.height
        longitude_position = (longitude - self.lower_lon) / lon_step
        latitude_position = (self.upper_lat - latitude) / lat_step
        tolerance = 1e-10
        if (
            0 < longitude_position < self.width
            and abs(longitude_position - round(longitude_position)) < tolerance
        ) or (
            0 < latitude_position < self.height
            and abs(latitude_position - round(latitude_position)) < tolerance
        ):
            return {"status": "AMBIGUOUS_CELL_BOUNDARY", "elevation_m": None, "raw_value": None, "surface_type": None, "reason": "The query lies on an exact native-cell boundary; no tie-break is inferred."}
        x = min(self.width - 1, max(0, int((longitude - self.lower_lon) / lon_step)))
        y = min(self.height - 1, max(0, int((self.upper_lat - latitude) / lat_step)))
        target = y * self.width + x
        first = self.start_y * self.width + self.start_x
        offset = target - first
        common = {
            "grid_x": x,
            "grid_y": y,
            "cell_center_longitude": self.lower_lon + (x + 0.5) * lon_step,
            "cell_center_latitude": self.upper_lat - (y + 0.5) * lat_step,
        }
        if offset < 0 or offset >= len(self.tuples):
            return {**common, "status": "OMITTED_SEQUENCE_VALUE", "elevation_m": None, "raw_value": None, "surface_type": None, "reason": "The native cell lies in an omitted leading or trailing sequence region."}
        surface_type, raw_value = self.tuples[offset]
        if surface_type == "データなし" and raw_value == -9999:
            return {**common, "status": "NODATA", "elevation_m": None, "raw_value": raw_value, "surface_type": surface_type, "reason": "The official GSI no-data tuple is retained as null."}
        if raw_value == -9999:
            return {**common, "status": "SURFACE_VALUE_UNRESOLVED", "elevation_m": None, "raw_value": raw_value, "surface_type": surface_type, "reason": "A -9999 value with a non-no-data surface label is not promoted to elevation."}
        return {**common, "status": "SAMPLED_NATIVE_CELL", "elevation_m": raw_value, "raw_value": raw_value, "surface_type": surface_type, "reason": "Exact containing native cell; no interpolation, smoothing, or slope inference."}

    def sample_from_epsg4326(self, longitude: float, latitude: float) -> dict:
        """Transform OSM/WGS84 coordinates through the officially unchanged JGD horizontal CRS."""
        if self.srs_name not in {"fguuid:jgd2024.bl", "fguuid:jgd2011.bl"}:
            raise ValueError("unsupported GSI horizontal CRS identifier")
        # GSI defines JGD2024 horizontal coordinates as the renamed, unchanged JGD2011
        # horizontal CRS. EPSG:6668 is therefore the bound implementation CRS here;
        # this does not equate or transform the vertical reference.
        convert = Transformer.from_crs("EPSG:4326", "EPSG:6668", always_xy=True, allow_ballpark=False)
        source_lon, source_lat = convert.transform(longitude, latitude)
        return self.sample(source_lon, source_lat)


def parse_gsi_dem_gml(payload: bytes, *, dem_class: str, revision: str) -> DemGrid:
    """Parse the exact GML fields required by the native-cell sampling contract."""
    root = ET.fromstring(payload)
    envelope = root.find(f".//{GML}Envelope")
    low = root.find(f".//{GML}low")
    high = root.find(f".//{GML}high")
    axis = root.find(f".//{GML}axisLabels")
    sequence = root.find(f".//{GML}sequenceRule")
    start = root.find(f".//{GML}startPoint")
    tuples = root.find(f".//{GML}tupleList")
    mesh = root.find(".//{*}mesh")
    if None in (envelope, low, high, axis, sequence, start, tuples, mesh):
        raise ValueError("GSI DEM GML contract is incomplete")
    if axis.text.strip() != "x y" or sequence.get("order") != "+x-y" or sequence.text.strip() != "Linear":
        raise ValueError("unsupported GSI DEM sequence contract")
    lower_lat, lower_lon = map(float, envelope.find(f"{GML}lowerCorner").text.split())
    upper_lat, upper_lon = map(float, envelope.find(f"{GML}upperCorner").text.split())
    low_x, low_y = map(int, low.text.split())
    high_x, high_y = map(int, high.text.split())
    start_x, start_y = map(int, start.text.split())
    if (low_x, low_y) != (0, 0) or high_x < 0 or high_y < 0:
        raise ValueError("unsupported GSI DEM grid envelope")
    if not all(math.isfinite(value) for value in (lower_lat, lower_lon, upper_lat, upper_lon)) or lower_lat >= upper_lat or lower_lon >= upper_lon:
        raise ValueError("invalid GSI DEM coordinate envelope")
    if not (0 <= start_x <= high_x and 0 <= start_y <= high_y):
        raise ValueError("GSI DEM startPoint is outside the grid envelope")
    values = []
    for line in tuples.text.strip().splitlines():
        surface_type, raw = line.strip().rsplit(",", 1)
        value = float(raw)
        if not math.isfinite(value):
            raise ValueError("DEM tuple value must be finite")
        values.append((surface_type, value))
    if not values:
        raise ValueError("GSI DEM tupleList is empty")
    first = start_y * (high_x + 1) + start_x
    if first + len(values) > (high_x + 1) * (high_y + 1):
        raise ValueError("DEM sequence exceeds grid envelope")
    return DemGrid(
        mesh_id=mesh.text.strip(), dem_class=dem_class, revision=revision,
        srs_name=envelope.get("srsName", ""), lower_lat=lower_lat, lower_lon=lower_lon,
        upper_lat=upper_lat, upper_lon=upper_lon, width=high_x + 1, height=high_y + 1,
        start_x=start_x, start_y=start_y, tuples=tuple(values),
    )
