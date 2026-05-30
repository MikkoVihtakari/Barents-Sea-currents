# Changelog

## 0.2.1 (2026-05-30)

- **Current arrows now sit under the coastline** in the R maps via
  `ggOceanMaps::reorder_layers()`, matching a published "Figure 1" look.
- **Fixed the Arctic Ocean R map**: dropped the redundant `crs = 3995` argument
  (the circular `limits = 45` basemap already fixes the CRS to EPSG:3995) and
  rendered the ready-made figures on a white background, so the Arctic legend is
  no longer lost against the transparent margin.
- **README lead figure** is now a single side-by-side `figure_files/r_preview.png`
  (three panels + shared legend, the R counterpart of `python_preview.png`),
  replacing the three vertically stacked maps. Each panel is still saved on its
  own in `figure_files/`.
- **Removed the legacy PlotSvalbard renders** (`blue_bathy*`, `grey_bathy*`),
  superseded by the ggOceanMaps figures.

## 0.2.0 (2026-05-29)

- **Added North Atlantic currents** alongside the Barents Sea arrows. The North
  Atlantic set spans the subtropical Atlantic through the Arctic Ocean and drives
  both the North Atlantic and Arctic Ocean map examples.
- **Reorganized shapefiles** into per-dataset folders: `Barents Sea/` and
  `North Atlantic/`. Removed a redundant `Arctic Ocean/` folder (byte-identical
  duplicate of the North Atlantic data) and superseded older lower-resolution
  North Atlantic files, keeping the latest EPSG:3995 versions.
- **Three map examples** (Barents Sea, North Atlantic, Arctic Ocean) in both the
  R and Python plotting scripts.
- **Modernized plotting to [ggOceanMaps](https://mikkovihtakari.github.io/ggOceanMaps/)**;
  removed the deprecated PlotSvalbard workflow and the retired `rgdal`/`sp`/
  `broom` dependencies. New scripts: `R/produce_csv.R`, `R/plot_currents.R`,
  `R/make_figures.R` (using `sf` + `smoothr`).
- **Added a Python pipeline**: `python/produce_csv.py` (geopandas) and
  `python/plot_currents.py` (cartopy, three-panel preview on a bathymetric
  basemap), with `requirements.txt`.
- **README lead figures** use the ggOceanMaps maps from `R/make_figures.R`; the
  cartopy bathymetry preview is shown under the Python section.
- **Completed the North Atlantic source citation**: Vihtakari et al. (2022),
  *ICES Journal of Marine Science* 79(6):1902–1917,
  [doi:10.1093/icesjms/fsac127](https://doi.org/10.1093/icesjms/fsac127).
- **New tidy CSV products**: `tabular/north_atlantic_currents.csv` and
  `tabular/all_currents.csv` (combined, harmonized schema with a `region`
  column). `tabular/barents_currents.csv` retained for backward compatibility.
- **AI-agent-friendly documentation**: `llms.txt`, `AGENTS.md`, `CLAUDE.md`,
  `DATA_DICTIONARY.md`, `CITATION.cff`, and a rewritten `README`.

## 0.1.1 (2022-03-04)

- Barents Sea ocean-current arrows; plotting via the PlotSvalbard package.
