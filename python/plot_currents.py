"""Plot the ocean-current arrows in Python (matplotlib).

A self-contained example that reads the tidy CSV produced by ``produce_csv.py``
and draws smoothed, directional current arrows coloured by water-mass type. It
mirrors the three map examples in ``R/plot_currents.R`` (Barents Sea, North
Atlantic, Arctic Ocean) for users who prefer Python.

Two curated datasets drive the three panels:
  * Barents Sea    -> regional arrows, drawn in UTM 33N (EPSG:32633).
  * North Atlantic -> pan-Atlantic-to-Arctic arrows in Arctic Polar
    Stereographic (EPSG:3995); the same set is shown cropped to a North
    Atlantic extent and to a full pan-Arctic extent.

Plotting in a projected CRS (not raw decimal degrees) keeps the trans-polar
arrows from smearing across the 180 meridian.

The node-to-curve smoothing uses a Catmull-Rom spline, reproducing the look of
the X-spline (``graphics::xspline(..., shape = -0.6)``) used by the historical
PlotSvalbard/R workflow without heavy dependencies.

Usage
-----
    python python/produce_csv.py        # (re)build the CSVs first
    python python/plot_currents.py      # writes figure_files/python_preview.png

Dependencies: pandas, numpy, matplotlib, pyproj (see requirements.txt).
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")  # headless / reproducible rendering
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyproj import Transformer

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(HERE, "tabular", "all_currents.csv")
OUT = os.path.join(HERE, "figure_files", "python_preview.png")

COLORS = {"Atlantic": "#d7301f", "Arctic": "#2166ac"}  # warm = red, cold = blue
LABELS = {"Atlantic": "Atlantic (warm)", "Arctic": "Arctic (cold)"}

TO_POLAR = Transformer.from_crs("EPSG:4326", "EPSG:3995", always_xy=True)   # pan-Arctic
TO_UTM33 = Transformer.from_crs("EPSG:4326", "EPSG:32633", always_xy=True)  # Barents


def project_km(lon, lat, transformer):
    x, y = transformer.transform(np.asarray(lon), np.asarray(lat))
    return np.column_stack([x, y]) / 1000.0


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


def draw_currents(ax, df, transformer):
    for _, g in df.sort_values("order").groupby("group"):
        xy = catmull_rom(project_km(g["long"], g["lat"], transformer))
        color = COLORS.get(g["type"].iloc[0], "grey")
        lw = 0.4 + 0.3 * float(g["size"].iloc[0])
        ax.plot(xy[:, 0], xy[:, 1], color=color, lw=lw, solid_capstyle="round")
        ax.annotate("", xy=xy[-1], xytext=xy[-3],
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                    mutation_scale=7 + 2 * lw))


def latitude_circles(ax, lats):
    for lat in lats:
        ring = project_km(np.linspace(-180, 180, 361), np.full(361, lat), TO_POLAR)
        ax.plot(ring[:, 0], ring[:, 1], color="0.85", lw=0.6, zorder=0)
        top = project_km([0], [lat], TO_POLAR)[0]
        ax.text(top[0], top[1], f"{lat}N", color="0.6", fontsize=7,
                ha="center", va="center", zorder=0)


def main():
    if not os.path.exists(CSV):
        raise SystemExit("Run python/produce_csv.py first to build the CSVs.")
    df = pd.read_csv(CSV)
    barents = df[df.region == "Barents Sea"]
    natl = df[df.region == "North Atlantic"]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6.5))

    # Panel 1: Barents Sea (UTM 33N)
    draw_currents(axes[0], barents, TO_UTM33)
    axes[0].set_title("Barents Sea\n(UTM 33N, EPSG:32633)")

    # Panel 2: North Atlantic extent (polar stereographic, cropped to Atlantic)
    draw_currents(axes[1], natl, TO_POLAR)
    box = project_km([-80, 40, -80, 40], [40, 40, 82, 82], TO_POLAR)
    axes[1].set_xlim(box[:, 0].min(), box[:, 0].max())
    axes[1].set_ylim(box[:, 1].min(), box[:, 1].max())
    axes[1].set_title("North Atlantic\n(Arctic Polar Stereographic, EPSG:3995)")

    # Panel 3: Arctic Ocean / pan-Arctic (polar stereographic, full extent)
    latitude_circles(axes[2], (40, 60, 80))
    draw_currents(axes[2], natl, TO_POLAR)
    axes[2].set_title("Arctic Ocean\n(Arctic Polar Stereographic, EPSG:3995)")

    for ax in axes:
        ax.set_aspect("equal")
        ax.set_xlabel("Easting (km)")
        ax.set_ylabel("Northing (km)")

    handles = [plt.Line2D([], [], color=c, lw=2, label=LABELS[t]) for t, c in COLORS.items()]
    fig.legend(handles=handles, title="Current type", loc="lower center",
               ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Barents Sea, North Atlantic & Arctic Ocean ocean-current arrows",
                 fontsize=14)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    fig.savefig(OUT, dpi=140, bbox_inches="tight")
    print(f"wrote {os.path.relpath(OUT, HERE)}")


if __name__ == "__main__":
    main()
