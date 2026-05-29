"""Produce tidy CSV files of ocean-current arrows from the source shapefiles.

This is the modern, reproducible replacement for the historical
``Produce csv.R`` script. It reads the curated current-arrow shapefiles,
reprojects everything to WGS84 decimal degrees (EPSG:4326), and writes long-
format CSV tables that are easy to plot in R (ggOceanMaps), Python
(matplotlib/geopandas), or any GIS/Matlab workflow.

Usage
-----
    python python/produce_csv.py

Outputs (written to ``tabular/``)
---------------------------------
- ``north_atlantic_currents.csv`` : North Atlantic / Arctic Ocean arrows.
- ``all_currents.csv``            : Barents Sea + North Atlantic combined.

Schema (long format, one row per vertex)
----------------------------------------
- ``long``, ``lat`` : vertex coordinates in decimal degrees (EPSG:4326).
- ``order``         : vertex order within an arrow (1 = start, n = arrow head).
- ``group``         : unique arrow id (``<type>_<region>_<n>``).
- ``size``          : relative current strength (1 = weak ... 5 = strong).
- ``type``          : water-mass origin, ``"Atlantic"`` (warm) or ``"Arctic"`` (cold).
- ``region``        : ``"Barents Sea"`` or ``"North Atlantic"``.

Dependencies: geopandas, pandas (see requirements.txt).
"""

from __future__ import annotations

import os
import sys

import geopandas as gpd
import pandas as pd

WGS84 = "EPSG:4326"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHP = os.path.join(HERE, "shapefiles")
OUT = os.path.join(HERE, "tabular")

# Source shapefiles -> (type, region). "warm" currents carry Atlantic water,
# "cold" currents carry Arctic water; we harmonise to the Barents Sea
# Atlantic/Arctic convention so a single colour scale works across regions.
# The North Atlantic files (EPSG:3995, Arctic Polar Stereographic) span the
# subtropical Atlantic through the Arctic Ocean; we reproject them to decimal
# degrees for the tidy tables.
SOURCES = {
    "Barents Sea": [
        (os.path.join(SHP, "Barents Sea", "atlantic_water.shp"), "Atlantic"),
        (os.path.join(SHP, "Barents Sea", "arctic_water.shp"), "Arctic"),
    ],
    "North Atlantic": [
        (os.path.join(SHP, "North Atlantic", "warm_currents.shp"), "Atlantic"),
        (os.path.join(SHP, "North Atlantic", "cold_currents.shp"), "Arctic"),
    ],
}


def line_to_rows(geom, group, size, type_, region):
    """Explode a (multi)line geometry into ordered vertex rows."""
    if geom.geom_type == "MultiLineString":
        coords = [pt for part in geom.geoms for pt in part.coords]
    else:
        coords = list(geom.coords)
    return [
        {
            "long": round(x, 6),
            "lat": round(y, 6),
            "order": i + 1,
            "group": group,
            "size": int(size),
            "type": type_,
            "region": region,
        }
        for i, (x, y, *_) in enumerate(coords)
    ]


def build_region(region, sources):
    rows = []
    for path, type_ in sources:
        if not os.path.exists(path):
            sys.exit(f"Missing source shapefile: {path}")
        gdf = gpd.read_file(path).to_crs(WGS84)
        for n, (_, feature) in enumerate(gdf.iterrows(), start=1):
            size = feature.get("size", 3)
            group = f"{type_}_{region.split()[0]}_{n}"
            rows.extend(line_to_rows(feature.geometry, group, size, type_, region))
    return pd.DataFrame(rows)


def main():
    os.makedirs(OUT, exist_ok=True)

    na = build_region("North Atlantic", SOURCES["North Atlantic"])
    na.to_csv(os.path.join(OUT, "north_atlantic_currents.csv"), index=False)
    print(f"north_atlantic_currents.csv: {na.group.nunique()} arrows, {len(na)} vertices")

    parts = [build_region(r, s) for r, s in SOURCES.items()]
    allc = pd.concat(parts, ignore_index=True)
    allc.to_csv(os.path.join(OUT, "all_currents.csv"), index=False)
    print(
        f"all_currents.csv: {allc.group.nunique()} arrows, {len(allc)} vertices "
        f"({', '.join(sorted(allc.region.unique()))})"
    )


if __name__ == "__main__":
    main()
