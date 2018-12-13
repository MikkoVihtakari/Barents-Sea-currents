library(PlotSvalbard)

bb <- basemap("barentssea", bathymetry = TRUE, currents = TRUE, current.size = "scaled", legends = c(FALSE, TRUE), legend.position = "bottom", base_size = 10) + labs(caption = "Vihtakari et al. (2018), modified from Eriksen et al. (2018)")

bb_png <- basemap("barentssea", bathymetry = TRUE, currents = TRUE, current.size = "scaled", legends = c(FALSE, TRUE), base_size = 14) + labs(caption = "Vihtakari et al. (2018), modified from Eriksen et al. (2018)")

gb <- basemap("barentssea", bathymetry = TRUE, currents = TRUE, current.size = "scaled", legends = c(FALSE, TRUE), bathy.style = "poly_greys", legend.position = "bottom", base_size = 10) + labs(caption = "Vihtakari et al. (2018), modified from Eriksen et al. (2018)")

gb_png <- basemap("barentssea", bathymetry = TRUE, currents = TRUE, current.size = "scaled", legends = c(FALSE, TRUE), bathy.style = "poly_greys", base_size = 14) + labs(caption = "Vihtakari et al. (2018), modified from Eriksen et al. (2018)")

pdf("figure_files/blue_bathy.pdf", width = 6.85, height = 6.85, useDingbats = FALSE)
bb
dev.off()

png("figure_files/blue_bathy.png", width = 24.9, height = 18.7, res = 300, units = "cm")
bb_png
dev.off()

pdf("figure_files/grey_bathy.pdf", width = 6.85, height = 6.85, useDingbats = FALSE)
gb
dev.off()

png("figure_files/grey_bathy.png", width = 24.9, height = 18.7, res = 300, units = "cm")
gb_png
dev.off()
