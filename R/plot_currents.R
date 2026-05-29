# Plot the ocean-current arrows with ggOceanMaps.
#
# Modern replacement for the historical `Smooth csv and plot.R`, which relied on
# the deprecated PlotSvalbard package. ggOceanMaps (>= 2.0) draws projected
# bathymetric basemaps with ggplot2; here we overlay the curated current arrows,
# smoothed with smoothr (an X-spline-like effect) and drawn with arrow heads.
#
# Two curated datasets drive three map examples:
#   * Barents Sea  -> shapefiles/Barents Sea/        (detailed, EPSG:32633)
#   * North Atlantic -> shapefiles/North Atlantic/   (pan-Atlantic to Arctic,
#                                                      EPSG:3995). The same set
#                                                      drives the North Atlantic
#                                                      and Arctic Ocean maps,
#                                                      cropped to different extents.
#
#   install.packages(c("ggOceanMaps", "sf", "smoothr", "ggplot2"))
#   source("R/plot_currents.R")
#
# Tip: bathymetry/land are downloaded on first use. Set a persistent data path
# in your .Rprofile (see the ggOceanMaps README) to avoid re-downloading.

library(ggOceanMaps)
library(sf)
library(smoothr)
library(ggplot2)

cur_cols <- c(Atlantic = "#d7301f", Arctic = "#2166ac")  # warm = red, cold = blue
cur_arrow <- arrow(type = "open", angle = 15, ends = "last",
                   length = unit(0.25, "lines"))

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

current_layers <- function(df) {
  list(
    geom_path(data = df, aes(X, Y, group = group, color = type, linewidth = size),
              arrow = cur_arrow),
    scale_color_manual("Current type", values = cur_cols,
                       labels = c(Atlantic = "Atlantic (warm)", Arctic = "Arctic (cold)")),
    scale_linewidth("Relative strength", range = c(0.3, 1.3))
  )
}

# ---------------------------------------------------------------------------
# 1. Barents Sea (UTM 33N, EPSG:32633) -- the classic "Figure 1" map
# ---------------------------------------------------------------------------
barents <- rbind(
  load_currents("shapefiles/Barents Sea/atlantic_water.shp", "Atlantic", 32633),
  load_currents("shapefiles/Barents Sea/arctic_water.shp",   "Arctic",   32633)
)

p_barents <-
  basemap(limits = c(-5, 60, 68, 83), crs = 32633, bathymetry = TRUE,
          legends = c(FALSE, TRUE)) +
  current_layers(barents) +
  labs(title = "Barents Sea",
       caption = "Vihtakari et al. (2019), modified from Eriksen et al. (2018)")

# ---------------------------------------------------------------------------
# North Atlantic currents in Arctic Polar Stereographic (EPSG:3995). The same
# projected arrows drive examples 2 and 3 below, cropped to different extents.
# ---------------------------------------------------------------------------
north_atlantic <- rbind(
  load_currents("shapefiles/North Atlantic/warm_currents.shp", "Atlantic", 3995),
  load_currents("shapefiles/North Atlantic/cold_currents.shp", "Arctic",   3995)
)

# 2. North Atlantic extent
p_north_atlantic <-
  basemap(limits = c(-80, 30, 40, 82), crs = 3995, bathymetry = TRUE,
          legends = c(FALSE, TRUE)) +
  current_layers(north_atlantic) +
  labs(title = "North Atlantic",
       caption = "Current arrows: see README citation (ICES J. Mar. Sci. 79(6):1902, 2022)")

# 3. Arctic Ocean (pan-Arctic) extent -- same data, polar view
p_arctic_ocean <-
  basemap(limits = 45, crs = 3995, bathymetry = TRUE, legends = c(FALSE, TRUE)) +
  current_layers(north_atlantic) +
  labs(title = "Arctic Ocean",
       caption = "Current arrows: see README citation (ICES J. Mar. Sci. 79(6):1902, 2022)")

# Display when run interactively
if (interactive()) {
  print(p_barents)
  print(p_north_atlantic)
  print(p_arctic_ocean)
}
