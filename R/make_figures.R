# Render ready-made current maps to figure_files/.
#
# Modern replacement for the historical `Ready-made figure files.R`. Builds the
# three basemap examples defined in R/plot_currents.R and writes:
#   * one publication-ready PDF + PNG per map example, and
#   * r_preview.png -- the three panels side by side with a shared legend,
#     mirroring the Python python_preview.png.
#
#   install.packages("cowplot")   # for the combined preview only
#   source("R/make_figures.R")

source("R/plot_currents.R")  # provides p_barents, p_north_atlantic, p_arctic_ocean

dir.create("figure_files", showWarnings = FALSE)

save_fig <- function(plot, name, width = 18, height = 18) {
  ggplot2::ggsave(file.path("figure_files", paste0(name, ".pdf")),
                  plot, width = width, height = height, units = "cm", bg = "white")
  ggplot2::ggsave(file.path("figure_files", paste0(name, ".png")),
                  plot, width = width, height = height, units = "cm", dpi = 300,
                  bg = "white")
  message("wrote figure_files/", name, ".{pdf,png}")
}

save_fig(p_barents,        "barents_currents")
save_fig(p_north_atlantic, "north_atlantic_currents", width = 20, height = 20)
save_fig(p_arctic_ocean,   "arctic_ocean_currents",   width = 22, height = 20)

# ---------------------------------------------------------------------------
# Combined README preview: three panels in a row with one shared legend, the
# R counterpart of figure_files/python_preview.png.
# ---------------------------------------------------------------------------
library(cowplot)

# Drop the per-panel legends and give each a short, centred title.
panel <- function(p, title) {
  p + labs(title = title, caption = NULL) +
    theme(legend.position = "none",
          plot.title  = element_text(hjust = 0.5, size = 11),
          plot.margin = margin(6, 4, 2, 4))
}

# Shared current-type legend (the relative-strength scale is dropped here, as in
# the Python preview; it survives on the individual figures above).
legend <- cowplot::get_legend(
  p_barents +
    guides(linewidth = "none") +
    theme(legend.position = "bottom", legend.direction = "horizontal")
)

row <- cowplot::plot_grid(
  panel(p_barents,        "Barents Sea (UTM 33N)"),
  panel(p_north_atlantic, "North Atlantic (Polar Stereographic)"),
  panel(p_arctic_ocean,   "Arctic Ocean (Polar Stereographic)"),
  nrow = 1, rel_widths = c(0.9, 1.15, 0.9)
)

title <- cowplot::ggdraw() +
  cowplot::draw_label("Barents Sea, North Atlantic & Arctic Ocean ocean-current arrows",
                      fontface = "bold", size = 13)

preview <- cowplot::plot_grid(title, row, legend, ncol = 1,
                              rel_heights = c(0.09, 1, 0.07))

ggplot2::ggsave("figure_files/r_preview.png", preview,
                width = 30, height = 13, units = "cm", dpi = 200, bg = "white")
message("wrote figure_files/r_preview.png")
