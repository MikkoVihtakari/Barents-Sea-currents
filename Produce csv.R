library(PlotSvalbard)
library(rgdal)
library(cowplot)
library(broom)

## Atlantic currents

atl <- rgdal::readOGR("shapefiles/atlantic_water.shp")
atl <- sp::spTransform(atl, sp::CRS("+proj=longlat +datum=WGS84"))
tmp <- suppressWarnings(broom::tidy(atl))

meta <- data.frame(id = rownames(atl@data), size = atl@data$size)
atl <- merge(tmp, meta, by = "id", all.x = TRUE)
atl$type <- "Atlantic"

## Arctic currents

arc <- readOGR("shapefiles/arctic_water.shp")
arc <- sp::spTransform(arc, sp::CRS("+proj=longlat +datum=WGS84"))
tmp <- suppressWarnings(broom::tidy(arc))

meta <- data.frame(id = rownames(arc@data), size = arc@data$size)
arc <- merge(tmp, meta, by = "id", all.x = TRUE)
arc$type <- "Arctic"

## Compile and clean up

cur <- rbind(atl,arc)

cur$group <- paste(cur$type, cur$group, sep = "_")

cur <- cur[names(cur) != "piece"]

write.csv(cur, file = "tabular/barents_currents.csv", row.names = FALSE)
