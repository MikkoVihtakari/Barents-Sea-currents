# Data dictionary

This repository stores **ocean-current arrows** — generalized, directional
spatial lines indicating the *influence* of Atlantic (warm) and Arctic (cold)
surface currents. They are *not* velocity fields and carry no mass balance or
seasonality. Arrows are expert-curated and meant for *"Figure 1"*-type maps in
scientific publications.

There are **two curated datasets**, which drive **three map examples**:

| Dataset        | Extent                                   | Drives map example(s)             |
|----------------|------------------------------------------|-----------------------------------|
| Barents Sea    | Barents & Greenland seas (regional)      | Barents Sea                       |
| North Atlantic | Subtropical Atlantic → Arctic Ocean (30–89°N) | North Atlantic, Arctic Ocean |

The North Atlantic dataset spans both the North Atlantic and the Arctic Ocean,
so it is shown twice (cropped to a North Atlantic extent, and as a full
pan-Arctic view) rather than duplicated as separate files.

## Folder layout

```
shapefiles/                      Authoritative GIS source data (edit in QGIS)
  Barents Sea/                   atlantic_water, arctic_water     EPSG:32633
  North Atlantic/                warm_currents,  cold_currents    EPSG:3995
tabular/                         Derived, tidy CSV products (generated)
  barents_currents.csv           Barents Sea only (legacy schema)
  north_atlantic_currents.csv    North Atlantic only            (generated)
  all_currents.csv               Barents Sea + North Atlantic   (generated)
R/                               Modern R pipeline (sf + ggOceanMaps)
python/                          Modern Python pipeline (geopandas + cartopy)
figure_files/                    Ready-made / preview maps
```

## Shapefiles (source of truth)

| Field      | Type       | Description                                           |
|------------|------------|-------------------------------------------------------|
| `id`       | integer    | Feature id (Barents Sea files only).                  |
| `size`     | integer    | Relative current strength, `1` (weak) … `5` (strong). |
| geometry   | LINESTRING | Arrow path; last vertex is the arrow head.            |

Coordinate reference systems:

- **EPSG:32633** — WGS 84 / UTM zone 33N (Barents Sea files).
- **EPSG:3995** — WGS 84 / Arctic Polar Stereographic (North Atlantic files).
  Preferred for pan-Arctic maps because some arrows cross the 180° meridian and
  would otherwise smear in decimal degrees.

The North Atlantic files are the latest, most complete versions of the
warm/cold currents.

## Tidy CSVs (generated — do not hand-edit)

`north_atlantic_currents.csv` and `all_currents.csv` share one long-format
schema, **one row per vertex**, in WGS 84 decimal degrees:

| Column   | Type    | Description                                                        |
|----------|---------|-------------------------------------------------------------------|
| `long`   | numeric | Longitude in decimal degrees (EPSG:4326).                         |
| `lat`    | numeric | Latitude in decimal degrees (EPSG:4326).                          |
| `order`  | integer | Vertex order within an arrow (`1` = start, `n` = arrow head).     |
| `group`  | string  | Unique arrow id, `<type>_<region>_<n>`.                           |
| `size`   | integer | Relative current strength, `1` … `5`.                             |
| `type`   | string  | Water-mass origin: `Atlantic` (warm) or `Arctic` (cold).         |
| `region` | string  | `Barents Sea` or `North Atlantic`.                               |

`barents_currents.csv` is the **legacy** Barents-only table (kept for backward
compatibility). It has no `region` column and uses the original `id`/`group`
naming.

### `warm`/`cold` → `Atlantic`/`Arctic` mapping

The North Atlantic shapefiles label currents `warm`/`cold`. These are harmonized
to the established Barents Sea convention so a single colour scale works
everywhere: **`warm` → `Atlantic`** (red), **`cold` → `Arctic`** (blue).

## Regenerating the CSVs

```bash
python python/produce_csv.py      # Python (geopandas)
# or
Rscript R/produce_csv.R           # R (sf)
```

Both read the shapefiles, reproject to EPSG:4326, and write identical schemas.
