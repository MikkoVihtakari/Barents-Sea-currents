# AGENTS.md — guidance for AI coding agents (and humans)

This file orients automated coding agents working in this repository. It follows
the same spirit as the [`llms.txt`](llms.txt) summary and is intentionally short.

## What this repository is

A **data repository** of expert-curated ocean-current arrows for the Barents
Sea and the wider North Atlantic / Arctic Ocean. It is **not** an installable R
package. The deliverables are: GIS source data (`shapefiles/`), tidy derived
tables (`tabular/`), reproducible R + Python pipelines (`R/`, `python/`), and
ready-made figures (`figure_files/`).

## Golden rules

1. **Shapefiles are the source of truth.** They are edited by hand in QGIS.
   Never machine-rewrite them. The CSVs in `tabular/` are *generated* — change
   the pipeline, then regenerate, never hand-edit generated CSVs.
2. **Keep R and Python pipelines in lock-step.** `R/produce_csv.R` and
   `python/produce_csv.py` must emit the same schema (see
   [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md)). If you change one, change both.
3. **No absolute / local paths, no secrets.** All paths are relative to the repo
   root. Do not reintroduce machine-specific paths (e.g. `/Users/...`).
4. **Plotting uses [ggOceanMaps](https://mikkovihtakari.github.io/ggOceanMaps/)
   in R** (the deprecated PlotSvalbard package and the retired `rgdal`/`sp`/
   `broom` stack have been removed). Use `sf` for vector I/O.
5. **Don't fabricate current data.** The arrows encode oceanographic expertise.
   New arrows come from the maintainer via QGIS edits, not from code.

## Conventions

- **CRS:** decimal degrees = EPSG:4326; Barents UTM = EPSG:32633; North Atlantic
  / pan-Arctic = EPSG:3995.
- **Datasets:** two curated sets — Barents Sea, and North Atlantic (spans the
  subtropical Atlantic through the Arctic Ocean). The North Atlantic set drives
  both the North Atlantic and Arctic Ocean map examples (different extents, same
  data).
- **Current types:** `Atlantic` (warm, red `#d7301f`) and `Arctic`
  (cold, blue `#2166ac`). `warm`/`cold` shapefile labels map to these.
- **Strength:** integer `size` 1–5, mapped to line width.
- **Smoothing:** nodes are sparse for easy editing; smooth before plotting
  (R: `smoothr::smooth(method = "spline")`; Python: Catmull-Rom in
  `python/plot_currents.py`). Historically this was `graphics::xspline(shape = -0.6)`.

## Common tasks

| Task                         | Command                                  |
|------------------------------|------------------------------------------|
| Rebuild CSVs (Python)        | `python python/produce_csv.py`           |
| Rebuild CSVs (R)             | `Rscript R/produce_csv.R`                |
| Preview map (Python)         | `python python/plot_currents.py`         |
| Build figures (R)            | `Rscript R/make_figures.R`               |
| Install Python deps          | `pip install -r requirements.txt`        |

## Verify before committing

- Run `python python/produce_csv.py && python python/plot_currents.py` and
  confirm both succeed (these are CI-checkable without R).
- Check `git grep -nE "/Users/|/home/|secret|password|token"` returns nothing.
- Bump the version + date in `README.Rmd`/`README.md` for data changes.
