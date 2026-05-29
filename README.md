
# Barents Sea & North Atlantic ocean-current arrows

**Data repository for updated Barents Sea and North Atlantic ocean-current
arrows (Institute of Marine Research and Norwegian Polar Institute). Version
0.2.0 (2026-05-29)**

This repository contains geospatial data for ocean-current arrows meant for
scientific publications as *“Figure 1”*-type arrows indicating the *influence*
of Atlantic (warm) and Arctic (cold) surface currents on different areas. The
arrows are **generalizations** and do not consider mass balance, seasonality, or
other variations. They are based on the current understanding of ocean currents
in the Barents Sea, Greenland Sea, North Atlantic, and Arctic Ocean.

Version 0.2 adds **North Atlantic / Arctic Ocean** currents alongside the
original Barents Sea arrows, modernizes the plotting to
[**ggOceanMaps**](https://mikkovihtakari.github.io/ggOceanMaps/) (replacing the
deprecated PlotSvalbard package and the retired `rgdal`/`sp` stack), and adds a
Python workflow.

The arrows are based on publications by Harald Gjøsæter (Institute of Marine
Research) and complemented by the knowledge of oceanographers/researchers at the
Norwegian Polar Institute (Arild Sundfjord, Laura de Steur, Mikko Vihtakari).
They are meant to stay updated; see *Contact information*.

![Barents Sea and North Atlantic ocean-current arrows in Arctic Polar
Stereographic projection](figure_files/python_preview.png)

*Barents Sea and North Atlantic ocean-current arrows (warm/Atlantic in red,
cold/Arctic in blue), produced by [`python/plot_currents.py`](python/plot_currents.py).*

## Repository layout

```
shapefiles/        Authoritative GIS source data (edit in QGIS)
  Barents Sea/       atlantic_water, arctic_water         (EPSG:32633)
  North Atlantic/    warm/cold currents (v1 EPSG:4326, v2 EPSG:3995, latest)
  Arctic Ocean/      warm/cold currents v2               (EPSG:3995)
tabular/           Tidy CSV products (generated)
  barents_currents.csv         Barents Sea (legacy schema)
  north_atlantic_currents.csv  North Atlantic
  all_currents.csv             Barents Sea + North Atlantic
R/                 R pipeline (sf + ggOceanMaps)
python/            Python pipeline (geopandas + matplotlib)
figure_files/      Ready-made / preview maps
```

See [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) for the full schema and CRS
reference, and [`AGENTS.md`](AGENTS.md) for contributor/agent conventions.

## Usage

### R (ggOceanMaps)

```r
# install.packages(c("ggOceanMaps", "sf", "smoothr", "ggplot2"))
library(ggOceanMaps)
library(sf)
library(smoothr)
library(ggplot2)

# Read, smooth and reproject an Atlantic-water arrow set to UTM 33N
cur <- sf::st_read("shapefiles/Barents Sea/atlantic_water.shp", quiet = TRUE) |>
  sf::st_transform(4326) |>
  smoothr::smooth(method = "spline") |>
  sf::st_transform(32633)

basemap(limits = c(-5, 60, 68, 83), crs = 32633, bathymetry = TRUE) +
  geom_sf(data = cur, aes(linewidth = size), color = "#d7301f",
          arrow = arrow(type = "open", angle = 15, length = unit(0.25, "lines"))) +
  scale_linewidth(range = c(0.3, 1.3))
```

Complete, ready-to-run examples for both the Barents Sea and the North Atlantic
are in [`R/plot_currents.R`](R/plot_currents.R); render publication figures with
[`R/make_figures.R`](R/make_figures.R).

### Python (geopandas + matplotlib)

```bash
pip install -r requirements.txt
python python/produce_csv.py     # shapefiles -> tidy CSVs
python python/plot_currents.py   # -> figure_files/python_preview.png
```

[`python/plot_currents.py`](python/plot_currents.py) reads
[`tabular/all_currents.csv`](tabular/all_currents.csv), smooths the arrows with a
Catmull-Rom spline, and plots them in Arctic Polar Stereographic projection.

## Smoothing

The arrows are stored as directed lines with relatively **few nodes** to make
editing easy. Run a spline through the nodes before plotting so the arrows appear
smooth (R: `smoothr::smooth(method = "spline")`; Python: Catmull-Rom in
`plot_currents.py`). The historical PlotSvalbard workflow used
`graphics::xspline(..., shape = -0.6)`; the modern approaches reproduce the same
look. Users of other software (GIS, Matlab, etc.) can apply any equivalent
spline.

## File types and coordinate systems

| Data            | Format    | CRS                                            |
|-----------------|-----------|------------------------------------------------|
| Barents Sea     | shapefile | EPSG:32633 (WGS 84 / UTM 33N)                  |
| North Atlantic v1 | shapefile | EPSG:4326 (WGS 84 decimal degrees)           |
| North Atlantic / Arctic Ocean v2 | shapefile | EPSG:3995 (Arctic Polar Stereographic) |
| `tabular/*.csv` | CSV       | EPSG:4326 (WGS 84 decimal degrees)             |

The `_v2` shapefiles are the latest, most complete North Atlantic data and are
recommended for pan-Arctic maps (some arrows cross the 180° meridian and smear in
decimal degrees). The tidy CSVs are generated from the `_v2` data.

## Regenerating the data

```bash
python python/produce_csv.py   # Python (geopandas)
Rscript R/produce_csv.R        # R (sf) — identical schema
```

## Citations

If you use the arrows in your publications, please cite them as:

Vihtakari M, Sundfjord A, de Steur L (2019). Barents Sea ocean-current arrows
modified from Eriksen et al. (2018). Norwegian Polar Institute and Institute of
Marine Research. Available at:
<https://github.com/MikkoVihtakari/Barents-Sea-currents>

When plotting with ggOceanMaps, please also cite that package and its underlying
data sources (`citation("ggOceanMaps")`).

## References

The Barents Sea arrows are modified from:

Eriksen E, Gjøsæter H, Prozorkevich D et al. (2018) From single species surveys
towards monitoring of the Barents Sea ecosystem. Progress in Oceanography, 166,
4–14. <https://doi.org/10.1016/j.pocean.2017.09.007>

## Contact information

Any corrections, suggestions, or other discussion can be directed to the site
maintainer (<mikko.vihtakari@gmail.com>).
