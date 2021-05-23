"""Utilisation functions."""
import json
from math import cos, pi
from pathlib import Path
from typing import Any, List, Tuple

import ee
import geopandas


def to_geojson(path: Path) -> Any:
    """Transform a given shapefile - defined under path - to geojson."""
    temp = Path.cwd() / "temp.geojson"

    # Transform shapefile to GeoJSON
    shp_file = geopandas.read_file(path)
    shp_file.to_file(temp, driver="GeoJSON")

    # Open the GeoJSON file
    with open(temp, "r") as f:
        geojson = json.load(f)

    temp.unlink(missing_ok=True)
    return geojson


def to_polygon(geojson: Any) -> ee.Geometry:
    """Transform a given geojson to an Earth Engine Polygon."""
    return ee.Geometry(geojson["features"][0]["geometry"])


def create_polygon(coordinates: List[List[Tuple[float, float]]]) -> ee.Geometry:
    """Transform a given geometry to an Earth Engine Polygon."""
    return ee.Geometry(
        {
            "type": "Polygon",
            "coordinates": coordinates,
        }
    )


def create_bounding_box(
    lng: float,
    lat: float,
    offset: int = 512,
) -> Any:
    """
    Create a bounding box around the (lon,lat) center with an offset expressed in meters.

    :param lng: Longitude in degrees
    :param lat: Latitude in degrees
    :param offset: Offset in meters, which creates a bounding box of 2*offset by 2*offset
    :return: GeoJSON of a polygon
    """
    dlat, dlng = get_dlat_dlng(
        lat=lat,
        dx=offset,
        dy=offset,
    )
    return {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": [
            {
                "type": "Feature",
                "properties": {"FID": 0},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [lng - dlng, lat - dlat],
                            [lng + dlng, lat - dlat],
                            [lng + dlng, lat + dlat],
                            [lng - dlng, lat + dlat],
                            [lng - dlng, lat - dlat],
                        ]
                    ],
                },
            }
        ],
    }


def get_dlat_dlng(
    lat: float,
    dx: int,
    dy: int,
) -> Tuple[float, float]:
    """
    Get the latitude and longitude relative to the provided coordinates under the offset in meters.

    For more information, visit:
    https://gis.stackexchange.com/a/2980

    :param lat: Latitude in degrees
    :param dx: Longitude offset in meters
    :param dy: Latitude offset in meters
    """
    r = 6378137  # Earth radius
    dlat = dy / r * 180 / pi
    dlng = dx / (r * cos(pi * lat / 180)) * 180 / pi
    return dlat, dlng