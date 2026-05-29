# Produce tidy CSV files of ocean-current arrows from the source shapefiles.
#
# Modern, reproducible replacement for the historical `Produce csv.R`. Uses sf
# (rgdal, sp and broom are retired) to read the curated current-arrow
# shapefiles, reproject everything to WGS84 decimal degrees (EPSG:4326), and
# write long-format CSV tables for plotting in R, Python or any GIS/Matlab
# workflow. Mirrors python/produce_csv.py.
#
# Run from the repository root:  Rscript R/produce_csv.R
#
# Schema (one row per vertex): long, lat, order, group, size, type, region
#   type   = water-mass origin, "Atlantic" (warm) or "Arctic" (cold)
#   region = "Barents Sea" or "North Atlantic"

library(sf)

# Source shapefiles -> (type, region). "warm" = Atlantic water, "cold" =
# Arctic water; harmonised to the Barents Atlantic/Arctic convention. The
# North Atlantic "_v2" files are the latest, most complete versions (EPSG:3995)
# and are reprojected to decimal degrees here.
sources <- list(
  list(file = "shapefiles/Barents Sea/atlantic_water.shp",    type = "Atlantic", region = "Barents Sea"),
  list(file = "shapefiles/Barents Sea/arctic_water.shp",      type = "Arctic",   region = "Barents Sea"),
  list(file = "shapefiles/North Atlantic/warm_currents_v2.shp", type = "Atlantic", region = "North Atlantic"),
  list(file = "shapefiles/North Atlantic/cold_currents_v2.shp", type = "Arctic",   region = "North Atlantic")
)

read_source <- function(file, type, region) {
  x <- sf::st_transform(sf::st_read(file, quiet = TRUE), 4326)
  co <- as.data.frame(sf::st_coordinates(x))      # X, Y, L1 (feature index)
  tag <- substr(region, 1, regexpr(" ", paste0(region, " ")) - 1)
  data.frame(
    long   = round(co$X, 6),
    lat    = round(co$Y, 6),
    order  = ave(co$L1, co$L1, FUN = seq_along),
    group  = paste(type, tag, co$L1, sep = "_"),
    size   = as.integer(x$size[co$L1]),
    type   = type,
    region = region,
    stringsAsFactors = FALSE
  )
}

all_parts <- lapply(sources, function(s) read_source(s$file, s$type, s$region))
all_currents <- do.call(rbind, all_parts)

dir.create("tabular", showWarnings = FALSE)

na <- all_currents[all_currents$region == "North Atlantic", ]
write.csv(na, "tabular/north_atlantic_currents.csv", row.names = FALSE)
write.csv(all_currents, "tabular/all_currents.csv", row.names = FALSE)

message(sprintf("north_atlantic_currents.csv: %d arrows, %d vertices",
                length(unique(na$group)), nrow(na)))
message(sprintf("all_currents.csv: %d arrows, %d vertices",
                length(unique(all_currents$group)), nrow(all_currents)))
