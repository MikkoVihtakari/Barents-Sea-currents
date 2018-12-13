library(PlotSvalbard)

## Read the file

cur <- read.csv("tabular/barents_currents.csv")
cur <- PlotSvalbard::transform_coord(x = cur, map.type = "barentssea", bind = TRUE)

## Plot the limits (required for the xspline function)

lims <- PlotSvalbard::basemap_limits(c(0,50,70,83), type = "barents")$bound_utm
plot(lims)

## Run xspline through the nodes

tp <- lapply(unique(cur$group), function(j) {
  tmp <- cur[cur$group == j,]
  bla <- xspline(x = tmp$lon.utm, y = tmp$lat.utm, shape = -0.6, draw = FALSE)
  data.frame(long = bla$x, lat = bla$y, group = j, size = unique(tmp$size), type = unique(tmp$type))
})

cur <- do.call(rbind, tp)

## Plot 

basemap("barentssea") + geom_path(data = cur, aes(x = long, y = lat, group = group, color = type), size = 0.5, arrow = arrow(type = "open", angle = 15, ends = "last", length = unit(0.3, "lines"))) + scale_color_manual(name = "Current\ntype", values = c("Arctic" = "blue", "Atlantic" = "red"), guide = guide_legend(order = 2, override.aes = list(fill = NA)))

## Note that PlotSvalbard already have the ocean currents and more incorporated

basemap("barentssea", bathymetry = TRUE, currents = TRUE, current.size = "scaled")

