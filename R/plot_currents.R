# Plot the ocean-current arrows with ggOceanMaps.
#
# Modern replacement for the historical `Smooth csv and plot.R`, which relied on
# the deprecated PlotSvalbard package. ggOceanMaps (>= 2.0) draws projected
# bathymetric basemaps with ggplot2; here we overlay the curated current arrows,
# smoothed with smoothr (an X-spline-like effect) and drawn with arrow heads.
#
#   install.packages(c("ggOceanMaps", "sf", "smoothr", "ggplot2"))
#   source("R/plot_currents.R")
#
# Tip: bathymetry/land for these maps is downloaded on first use. Set a
# persistent data path in your .Rprofile (see the ggOceanMaps README) to avoid
# re-downloading every session.

library(ggOceanMaps)
library(sf)
library(smoothr)
library(ggplot2)

cur_cols <- c(Atlantic = "#d7301f", Arctic = "#2166ac")  # warm = red, cold = blue

# Read a current shapefile, smooth the nodes into curves, reproject to the
# basemap CRS and return a tidy data frame ready for geom_path().
load_currents <- function(file, type, crs.out) {
  x <- sf::st_transform(sf::st_read(file, quiet = TRUE), 4326)
  x <- smoothr::smooth(x, method = "spline")          # node -> curve smoothing
  x <- sf::st_transform(x, crs.out)
  co <- as.data.frame(sf::st_coordinates(x))          # X, Y, L1 (feature index)
  data.frame(
    X = co$X, Y = co$Y,
    group = paste0(type, "_", co$L1),
    size  = x$size[co$L1],
    type  = type
  )
}

cur_arrow <- arrow(type = "open", angle = 15, ends = "last",
                   length = unit(0.25, "lines"))

# ---------------------------------------------------------------------------
# 1. Barents Sea (UTM 33N, EPSG:32633) -- the classic "Figure 1" map
# ---------------------------------------------------------------------------
barents_crs <- 32633
barents <- rbind(
  load_currents("shapefiles/Barents Sea/atlantic_water.shp", "Atlantic", barents_crs),
  load_currents("shapefiles/Barents Sea/arctic_water.shp",   "Arctic",   barents_crs)
)

p_barents <-
  basemap(limits = c(-5, 60, 68, 83), crs = barents_crs, bathymetry = TRUE,
          legends = c(FALSE, TRUE)) +
  geom_path(data = barents,
            aes(X, Y, group = group, color = type, linewidth = size),
            arrow = cur_arrow) +
  scale_color_manual("Current type", values = cur_cols) +
  scale_linewidth("Relative strength", range = c(0.3, 1.3)) +
  labs(caption = "Vihtakari et al. (2019), modified from Eriksen et al. (2018)")

# ---------------------------------------------------------------------------
# 2. North Atlantic / pan-Arctic (Arctic Polar Stereographic, EPSG:3995)
# ---------------------------------------------------------------------------
arctic_crs <- 3995
north_atlantic <- rbind(
  load_currents("shapefiles/North Atlantic/warm_currents_v2.shp", "Atlantic", arctic_crs),
  load_currents("shapefiles/North Atlantic/cold_currents_v2.shp", "Arctic",   arctic_crs)
)

p_north_atlantic <-
  basemap(limits = 45, bathymetry = TRUE, legends = c(FALSE, TRUE)) +
  geom_path(data = north_atlantic,
            aes(X, Y, group = group, color = type, linewidth = size),
            arrow = cur_arrow) +
  scale_color_manual("Current type", values = cur_cols) +
  scale_linewidth("Relative strength", range = c(0.3, 1.3)) +
  labs(caption = "Barents-Sea-currents (2026)")

# Display when run interactively
if (interactive()) {
  print(p_barents)
  print(p_north_atlantic)
}
