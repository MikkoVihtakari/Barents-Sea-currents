# Changelog

## 0.2.0 (2026-05-29)

- **Added North Atlantic / Arctic Ocean currents** alongside the Barents Sea
  arrows (`shapefiles/North Atlantic/`, `shapefiles/Arctic Ocean/`).
- **Reorganized shapefiles** into per-region folders: `Barents Sea/`,
  `North Atlantic/`, `Arctic Ocean/`.
- **Modernized plotting to [ggOceanMaps](https://mikkovihtakari.github.io/ggOceanMaps/)**;
  removed the deprecated PlotSvalbard workflow and the retired `rgdal`/`sp`/
  `broom` dependencies. New scripts: `R/produce_csv.R`, `R/plot_currents.R`,
  `R/make_figures.R` (using `sf` + `smoothr`).
- **Added a Python pipeline**: `python/produce_csv.py` (geopandas) and
  `python/plot_currents.py` (matplotlib, Arctic Polar Stereographic preview),
  with `requirements.txt`.
- **New tidy CSV products**: `tabular/north_atlantic_currents.csv` and
  `tabular/all_currents.csv` (combined, harmonized schema with a `region`
  column). `tabular/barents_currents.csv` retained for backward compatibility.
- **AI-agent-friendly documentation**: `llms.txt`, `AGENTS.md`, `CLAUDE.md`,
  `DATA_DICTIONARY.md`, `CITATION.cff`, and a rewritten `README`.

## 0.1.1 (2022-03-04)

- Barents Sea ocean-current arrows; plotting via the PlotSvalbard package.
