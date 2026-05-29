# Render ready-made current maps to figure_files/.
#
# Modern replacement for the historical `Ready-made figure files.R`. Builds the
# basemaps and current overlays defined in R/plot_currents.R and writes
# publication-ready PDF and PNG versions.
#
#   source("R/make_figures.R")

source("R/plot_currents.R")  # provides p_barents and p_north_atlantic

dir.create("figure_files", showWarnings = FALSE)

save_fig <- function(plot, name, width = 18, height = 18) {
  ggplot2::ggsave(file.path("figure_files", paste0(name, ".pdf")),
                  plot, width = width, height = height, units = "cm")
  ggplot2::ggsave(file.path("figure_files", paste0(name, ".png")),
                  plot, width = width, height = height, units = "cm", dpi = 300)
  message("wrote figure_files/", name, ".{pdf,png}")
}

save_fig(p_barents,        "barents_currents")
save_fig(p_north_atlantic, "north_atlantic_currents", width = 20, height = 20)
