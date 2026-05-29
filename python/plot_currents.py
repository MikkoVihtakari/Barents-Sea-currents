"""Plot the ocean-current arrows in Python (matplotlib).

A self-contained example that reads the tidy CSV produced by
``produce_csv.py`` and draws smoothed, directional current arrows coloured by
water-mass type. It mirrors what ``R/plot_currents.R`` does with ggOceanMaps,
for users who prefer Python.

Because the arrows span the whole Arctic (some cross the 180° meridian), the
data are reprojected to the **WGS 84 / Arctic Polar Stereographic** projection
(EPSG:3995) before plotting. Plotting in decimal degrees would smear the
trans-polar arrows into horizontal streaks - the same reason the curated
``*_v2`` shapefiles are stored in EPSG:3995.

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

# Arctic Polar Stereographic; coordinates handled in km for readable axes.
TO_POLAR = Transformer.from_crs("EPSG:4326", "EPSG:3995", always_xy=True)


def to_polar_km(lon, lat):
    x, y = TO_POLAR.transform(np.asarray(lon), np.asarray(lat))
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


def latitude_circle(ax, lat, color="0.8"):
    """Draw a reference parallel (line of constant latitude)."""
    ring = to_polar_km(np.linspace(-180, 180, 361), np.full(361, lat))
    ax.plot(ring[:, 0], ring[:, 1], color=color, lw=0.6, zorder=0)
    top = to_polar_km([0], [lat])[0]
    ax.text(top[0], top[1], f"{lat}°N", color="0.5", fontsize=7,
            ha="center", va="center", zorder=0)


def main():
    if not os.path.exists(CSV):
        raise SystemExit("Run python/produce_csv.py first to build the CSVs.")
    df = pd.read_csv(CSV)

    fig, ax = plt.subplots(figsize=(10, 10))
    for lat in (40, 50, 60, 70, 80):
        latitude_circle(ax, lat)

    for _, g in df.sort_values("order").groupby("group"):
        xy = catmull_rom(to_polar_km(g["long"], g["lat"]))
        color = COLORS.get(g["type"].iloc[0], "grey")
        lw = 0.4 + 0.35 * float(g["size"].iloc[0])
        ax.plot(xy[:, 0], xy[:, 1], color=color, lw=lw, solid_capstyle="round")
        ax.annotate(
            "", xy=xy[-1], xytext=xy[-3],
            arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                            mutation_scale=8 + 2 * lw),
        )

    handles = [plt.Line2D([], [], color=c, lw=2, label=LABELS[t]) for t, c in COLORS.items()]
    ax.legend(handles=handles, title="Current type", loc="lower left", frameon=False)

    ax.set_title("Barents Sea & North Atlantic ocean-current arrows\n"
                 "(WGS 84 / Arctic Polar Stereographic, EPSG:3995)")
    ax.set_xlabel("Easting (km)")
    ax.set_ylabel("Northing (km)")
    ax.set_aspect("equal")
    ax.grid(False)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"wrote {os.path.relpath(OUT, HERE)}")


if __name__ == "__main__":
    main()
