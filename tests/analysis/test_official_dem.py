"""Regression tests for source-bound native-cell DEM sampling."""

import pytest

from src.analysis.official_dem import parse_gsi_dem_gml


def _fixture(tuple_list: str, *, start: str = "0 0") -> bytes:
    return f'''<Dataset xmlns:gml="http://www.opengis.net/gml/3.2" xmlns="http://fgd.gsi.go.jp/spec/2008/FGD_GMLSchema"><DEM><mesh>00000000</mesh><coverage><gml:boundedBy><gml:Envelope srsName="fguuid:jgd2024.bl"><gml:lowerCorner>35 135</gml:lowerCorner><gml:upperCorner>37 137</gml:upperCorner></gml:Envelope></gml:boundedBy><gml:gridDomain><gml:Grid><gml:limits><gml:GridEnvelope><gml:low>0 0</gml:low><gml:high>1 1</gml:high></gml:GridEnvelope></gml:limits><gml:axisLabels>x y</gml:axisLabels></gml:Grid></gml:gridDomain><gml:rangeSet><gml:DataBlock><gml:tupleList>{tuple_list}</gml:tupleList></gml:DataBlock></gml:rangeSet><gml:coverageFunction><gml:GridFunction><gml:sequenceRule order="+x-y">Linear</gml:sequenceRule><gml:startPoint>{start}</gml:startPoint></gml:GridFunction></gml:coverageFunction></coverage></DEM></Dataset>'''.encode()


def test_native_cell_sampling_keeps_zero_negative_and_surface_type():
    """[source_conformance] Four 1x1-degree cells map NW→E then S, without interpolation."""
    grid = parse_gsi_dem_gml(_fixture("地表面,0\n地表面,-2.5\n内水底面,3\n地表面,4"), dem_class="DEM5A", revision="2025-01-01")
    assert grid.sample(135.25, 36.75) == {
        "grid_x": 0, "grid_y": 0, "cell_center_longitude": 135.5,
        "cell_center_latitude": 36.5, "status": "SAMPLED_NATIVE_CELL",
        "elevation_m": 0.0, "raw_value": 0.0, "surface_type": "地表面",
        "reason": "Exact containing native cell; no interpolation, smoothing, or slope inference.",
    }
    assert grid.sample(136.25, 36.75)["elevation_m"] == -2.5
    assert grid.sample(135.25, 35.25)["surface_type"] == "内水底面"


def test_nonzero_start_and_omitted_sequence_fail_closed():
    """[source_conformance] startPoint 1 0 places two tuples at indices 1,2; indices 0,3 are omitted."""
    grid = parse_gsi_dem_gml(_fixture("データなし,-9999\n海水面,-9999", start="1 0"), dem_class="DEM5A", revision="2025-01-01")
    assert grid.sample(135.25, 36.75)["status"] == "OMITTED_SEQUENCE_VALUE"
    assert grid.sample(136.25, 36.75)["status"] == "NODATA"
    assert grid.sample(135.25, 35.25)["status"] == "SURFACE_VALUE_UNRESOLVED"
    assert grid.sample(136.25, 35.25)["status"] == "OMITTED_SEQUENCE_VALUE"


@pytest.mark.parametrize("start", ["-1 0", "0 -1", "2 0", "0 2"])
def test_start_point_outside_grid_is_rejected(start):
    """[software_correctness] A 2×2 grid accepts startPoint coordinates only in 0..1."""
    with pytest.raises(ValueError, match="startPoint"):
        parse_gsi_dem_gml(_fixture("地表面,1", start=start), dem_class="DEM5A", revision="fixture")
