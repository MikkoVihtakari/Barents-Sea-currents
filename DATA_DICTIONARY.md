# Data dictionary

This repository stores **ocean-current arrows** — generalized, directional
spatial lines indicating the *influence* of Atlantic (warm) and Arctic (cold)
surface currents. They are *not* velocity fields and carry no mass balance or
seasonality. Arrows are expert-curated and meant for *"Figure 1"*-type maps in
scientific publications.

## Folder layout

```
shapefiles/                      Authoritative GIS source data (edit in QGIS)
  Barents Sea/                   atlantic_water, arctic_water     EPSG:32633
  North Atlantic/                warm_currents,  cold_currents    EPSG:4326  (v1)
                                 warm_currents_v2, cold_currents_v2 EPSG:3995 (v2, latest)
  Arctic Ocean/                  warm_currents_v2, cold_currents_v2 EPSG:3995
tabular/                         Derived, tidy CSV products (generated)
  barents_currents.csv           Barents Sea only (legacy schema)
  north_atlantic_currents.csv    North Atlantic only            (generated)
  all_currents.csv               Barents Sea + North Atlantic   (generated)
R/                               Modern R pipeline (sf + ggOceanMaps)
python/                          Modern Python pipeline (geopandas + matplotlib)
figure_files/                    Ready-made / preview maps
```

## Shapefiles (source of truth)

| Field      | Type    | Description                                              |
|------------|---------|---------------------------------------------------------|
| `id`       | integer | Feature id (Barents Sea files only).                    |
| `size`     | integer | Relative current strength, `1` (weak) … `5` (strong).   |
| geometry   | LINESTRING | Arrow path; last vertex is the arrow head.            |

Coordinate reference systems:

- **EPSG:32633** — WGS 84 / UTM zone 33N (Barents Sea files).
- **EPSG:4326** — WGS 84 decimal degrees (North Atlantic `v1`).
- **EPSG:3995** — WGS 84 / Arctic Polar Stereographic (`_v2` files). Preferred
  for pan-Arctic maps because some arrows cross the 180° meridian and would
  otherwise smear in decimal degrees.

The `_v2` North Atlantic files are the **latest and most complete** versions
(more features than `v1`); the generated CSVs are built from `_v2`.

> **Note on `Arctic Ocean/`:** these `_v2` files are currently byte-identical to
> `North Atlantic/*_v2`. The folder is kept as a separate map context. If the
> two ever diverge, update the source paths in `R/produce_csv.R` and
> `python/produce_csv.py` accordingly.

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
