"""Plot the ocean-current arrows in Python on a bathymetric basemap (cartopy).

A self-contained example that reads the tidy CSV produced by ``produce_csv.py``
and draws smoothed, directional current arrows coloured by water-mass type over
a shaded bathymetry + land basemap. It mirrors the three ggOceanMaps map
examples in ``R/plot_currents.R`` (Barents Sea, North Atlantic, Arctic Ocean)
for users who prefer Python.

Two curated datasets drive the three panels:
  * Barents Sea    -> regional arrows, drawn in UTM 33N.
  * North Atlantic -> pan-Atlantic-to-Arctic arrows in North Polar
    Stereographic; the same set is shown cropped to a North Atlantic extent and
    to a full pan-Arctic extent (vertices south of 45N dropped on the latter so
    the Atlantic inflow does not dangle outside the circular map).

Plotting in a projected CRS (not raw decimal degrees) keeps the trans-polar
arrows from smearing across the 180 meridian.

The basemap uses Natural Earth land and bathymetry (shaded depth bands), so the
look is comparable to the ggOceanMaps figures. The vector layers are downloaded
and cached by cartopy on first use.

The node-to-curve smoothing uses a Catmull-Rom spline, reproducing the look of
the X-spline (``graphics::xspline(..., shape = -0.6)``) used by the historical
PlotSvalbard/R workflow without heavy dependencies.

Usage
-----
    python python/produce_csv.py        # (re)build the CSVs first
    python python/plot_currents.py      # writes figure_files/python_preview.png

Dependencies: pandas, numpy, matplotlib, cartopy (see requirements.txt).
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")  # headless / reproducible rendering
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(HERE, "tabular", "all_currents.csv")
OUT = os.path.join(HERE, "figure_files", "python_preview.png")

COLORS = {"Atlantic": "#d7301f", "Arctic": "#2166ac"}  # warm = red, cold = blue
LABELS = {"Atlantic": "Atlantic (warm)", "Arctic": "Arctic (cold)"}

# Map projections for the three panels (mirroring the ggOceanMaps CRSs).
PROJ_BARENTS = ccrs.UTM(zone=33)                                   # ~ EPSG:32633
PROJ_POLAR = ccrs.NorthPolarStereo(central_longitude=0, true_scale_latitude=71)  # ~ EPSG:3995

LAND = "#d9d9d9"
COAST = "#7f7f7f"

# Natural Earth bathymetry layers, shallow -> deep. Each polygon covers all
# water deeper than its threshold, so painting shallow (light) first and deeper
# (dark) on top yields graduated depth bands.
BATHY_LEVELS = [
    "bathymetry_K_200", "bathymetry_J_1000", "bathymetry_I_2000",
    "bathymetry_H_3000", "bathymetry_G_4000", "bathymetry_F_5000",
    "bathymetry_E_6000", "bathymetry_D_7000", "bathymetry_C_8000",
    "bathymetry_B_9000", "bathymetry_A_10000",
]


def catmull_rom(points: np.ndarray, n_per_seg: int = 20) -> np.ndarray:
    """Smooth a polyline through its nodes with a Catmull-Rom spline."""
    if len(points) < 3:
        return points
    pts = np.vstack([points[0], points, points[-1]])  # pad ends
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        t = np.linspace(0, 1, n_per_seg)[:, None]
        out.append(
            0.5
            * (
                (2 * p1)
                + (-p0 + p2) * t
                + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2
                + (-p0 + 3 * p1 - 3 * p2 + p3) * t**3
            )
        )
    return np.vstack(out)


def add_basemap(ax):
    """Shaded bathymetry + land for a cartopy GeoAxes."""
    ax.add_feature(cfeature.OCEAN.with_scale("50m"), facecolor="#eaf3fb", zorder=0)
    blues = plt.cm.Blues(np.linspace(0.18, 0.95, len(BATHY_LEVELS)))
    for name, color in zip(BATHY_LEVELS, blues):
        feat = cfeature.NaturalEarthFeature("physical", name, "10m")
        ax.add_feature(feat, facecolor=color, edgecolor="none", zorder=1)
    ax.add_feature(cfeature.LAND.with_scale("50m"), facecolor=LAND, zorder=2)
    ax.add_feature(cfeature.COASTLINE.with_scale("50m"), edgecolor=COAST,
                   linewidth=0.4, zorder=3)
    ax.gridlines(color="0.7", linewidth=0.4, alpha=0.7, zorder=4)


def draw_currents(ax, df, proj):
    """Project lon/lat arrows to ``proj``, smooth and draw them on ``ax``."""
    for _, g in df.sort_values("order").groupby("group"):
        xyz = proj.transform_points(ccrs.PlateCarree(),
                                     g["long"].to_numpy(), g["lat"].to_numpy())
        xy = catmull_rom(xyz[:, :2])
        color = COLORS.get(g["type"].iloc[0], "grey")
        lw = 0.4 + 0.3 * float(g["size"].iloc[0])
        ax.plot(xy[:, 0], xy[:, 1], color=color, lw=lw, solid_capstyle="round",
                transform=proj, zorder=5)
        ax.annotate("", xy=xy[-1], xytext=xy[-3], xycoords="data", zorder=6,
                    annotation_clip=True,  # drop arrowheads whose tip falls outside the map
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                    mutation_scale=7 + 2 * lw))


def circular_boundary(ax):
    """Clip a polar GeoAxes to a circle (for the pan-Arctic view)."""
    theta = np.linspace(0, 2 * np.pi, 200)
    verts = np.column_stack([np.sin(theta), np.cos(theta)]) * 0.5 + 0.5
    ax.set_boundary(mpath.Path(verts), transform=ax.transAxes)


def main():
    if not os.path.exists(CSV):
        raise SystemExit("Run python/produce_csv.py first to build the CSVs.")
    df = pd.read_csv(CSV)
    barents = df[df.region == "Barents Sea"]
    natl = df[df.region == "North Atlantic"]

    fig = plt.figure(figsize=(18, 7))

    # Panel 1: Barents Sea (UTM 33N)
    ax1 = fig.add_subplot(1, 3, 1, projection=PROJ_BARENTS)
    ax1.set_extent([-5, 60, 68, 83], crs=ccrs.PlateCarree())
    add_basemap(ax1)
    draw_currents(ax1, barents, PROJ_BARENTS)
    ax1.set_title("Barents Sea\n(UTM 33N)")

    # Panel 2: North Atlantic extent (polar stereographic, cropped to Atlantic)
    ax2 = fig.add_subplot(1, 3, 2, projection=PROJ_POLAR)
    ax2.set_extent([-80, 30, 40, 82], crs=ccrs.PlateCarree())
    add_basemap(ax2)
    draw_currents(ax2, natl, PROJ_POLAR)
    ax2.set_title("North Atlantic\n(North Polar Stereographic)")

    # Panel 3: Arctic Ocean / pan-Arctic (polar stereographic, circular extent)
    ax3 = fig.add_subplot(1, 3, 3, projection=PROJ_POLAR)
    ax3.set_extent([-180, 180, 45, 90], crs=ccrs.PlateCarree())
    circular_boundary(ax3)
    add_basemap(ax3)
    draw_currents(ax3, natl[natl.lat >= 45], PROJ_POLAR)  # drop arrows south of view
    ax3.set_title("Arctic Ocean\n(North Polar Stereographic)")

    handles = [plt.Line2D([], [], color=c, lw=2, label=LABELS[t]) for t, c in COLORS.items()]
    fig.legend(handles=handles, title="Current type", loc="lower center",
               ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Barents Sea, North Atlantic & Arctic Ocean ocean-current arrows",
                 fontsize=14)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    fig.savefig(OUT, dpi=140, bbox_inches="tight")
    print(f"wrote {os.path.relpath(OUT, HERE)}")


if __name__ == "__main__":
    main()
