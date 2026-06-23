# ----------------------------------------------------------------------------
# Project : EPOS x ECMWF - Climate-context seismic workflow (EPOS Summer School)
# Module  : epos_school_function.py
# Purpose : Shared plotting helpers for the teaching notebook. All figures use a
#           single house style (set_epos_style) so the Map, seismograms and the
#           climatology time series look consistent and presentation-ready.
#
#           Public helpers
#           --------------
#           set_epos_style()           : apply the notebook-wide Matplotlib theme
#           plot_epicentre_map(...)     : geographic map of candidate / monsoon
#                                         events on a real land basemap (Cartopy),
#                                         with the NEAREST CITY labelled for every
#                                         monsoon-linked event and a declutter pass
#                                         that prevents any label overlap
#           plot_monsoon_timeseries(...): 30-yr ERA5 monsoon history with mean,
#                                         +/-2 sigma envelope and the event year
#           plot_seismogram(...)        : single-station waveform with P / end picks
#           nearest_city(lat, lon)      : (name, distance_km) of the closest place
#
# Author  : Heriniaina Juliano Dani Ramanantsoa (University of Bergen)
# Licence : CC BY 4.0 (content) + MIT (code) - see the notebook header cell.
# ----------------------------------------------------------------------------

from __future__ import annotations

import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.patheffects import withStroke

__all__ = ["set_epos_style", "plot_epicentre_map", "plot_monsoon_timeseries",
           "plot_seismogram", "nearest_city", "find_lon_lat_columns",
           "REGION_CITIES"]

# Optional Cartopy: gives a real land/ocean basemap. If it is missing we fall
# back to a plain Matplotlib map (no land) and print a one-line hint.
try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
    _HAS_CARTOPY = True
    _CARTOPY_IMPORT_ERROR = None
except Exception as _e:                 # remember WHY it failed so we can show it
    _HAS_CARTOPY = False
    _CARTOPY_IMPORT_ERROR = repr(_e)

# ----------------------------------------------------------------------------
# House style + palette
# ----------------------------------------------------------------------------
INK   = "#16263A"   # near-black slate (titles / ink)
SOFT  = "#33414F"   # softer ink for labels
MUTED = "#6B7B8C"   # grey for ticks / captions
SEIS  = "#C0432B"   # seismic accent (brick red)  -> monsoon-linked events
CLIM  = "#1C7293"   # climate accent (teal)       -> climatology / precipitation
GOLD  = "#E0A21A"   # highlight accent
GREEN = "#2C7A39"   # "ok" accent                 -> waveform-validated rings
LAND  = "#F1EBDD"   # warm land fill
OCEAN = "#DCEBF1"   # light teal ocean fill
GRID  = "#C7D0D9"   # gridlines / rules


def set_epos_style():
    """Apply the notebook-wide Matplotlib theme. Call once near the top."""
    mpl.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 150, "savefig.bbox": "tight",
        "figure.facecolor": "white", "axes.facecolor": "white",
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.titlesize": 14, "axes.titleweight": "bold", "axes.titlecolor": INK,
        "axes.titlepad": 12,
        "axes.labelsize": 11, "axes.labelcolor": SOFT,
        "axes.edgecolor": MUTED, "axes.linewidth": 0.9,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "grid.alpha": 0.55,
        "xtick.color": MUTED, "ytick.color": MUTED,
        "xtick.labelsize": 9.5, "ytick.labelsize": 9.5,
        "legend.frameon": True, "legend.framealpha": 0.92, "legend.edgecolor": GRID,
        "legend.fontsize": 9.5, "legend.borderpad": 0.6,
        "axes.spines.top": False, "axes.spines.right": False,
    })


# ----------------------------------------------------------------------------
# Regional city / reference-place database (lat, lon) for the monsoon belt
# (~68-104 E, 16-40 N). Used to label the closest place to each monsoon event.
# ----------------------------------------------------------------------------
REGION_CITIES = {
    "Kabul": (34.53, 69.17), "Gilgit": (35.92, 74.31), "Srinagar": (34.08, 74.80),
    "Islamabad": (33.69, 73.06), "Lahore": (31.55, 74.34), "Leh": (34.16, 77.58),
    "Dushanbe": (38.56, 68.79), "Kashgar": (39.47, 75.99), "Hotan": (37.11, 79.93),
    "Delhi": (28.61, 77.21), "Lucknow": (26.85, 80.95), "Patna": (25.59, 85.14),
    "Kathmandu": (27.72, 85.32), "Pokhara": (28.21, 83.99), "Gangtok": (27.33, 88.61),
    "Thimphu": (27.47, 89.64), "Shigatse": (29.27, 88.88), "Lhasa": (29.65, 91.14),
    "Dhaka": (23.81, 90.41), "Chittagong": (22.36, 91.78), "Imphal": (24.82, 93.94),
    "Kohima": (25.67, 94.11), "Aizawl": (23.73, 92.72), "Mandalay": (21.97, 96.08),
    "Naypyidaw": (19.75, 96.10), "Yangon": (16.84, 96.17), "Xining": (36.62, 101.78),
    "Golmud": (36.40, 94.90), "Chengdu": (30.57, 104.07), "Kunming": (25.04, 102.71),
}


def _haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in kilometres between two lat/lon points."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def nearest_city(lat, lon, cities=None):
    """Return (city_name, distance_km) for the closest entry in REGION_CITIES."""
    cities = REGION_CITIES if cities is None else cities
    best, best_d = None, float("inf")
    for name, (clat, clon) in cities.items():
        d = _haversine_km(lat, lon, clat, clon)
        if d < best_d:
            best, best_d = name, d
    return best, best_d


# ----------------------------------------------------------------------------
# Robust coordinate-column resolution
# ----------------------------------------------------------------------------
def _resolve(df, candidates):
    """First column matching any candidate (exact -> case-insensitive -> substring)."""
    cols = list(df.columns)
    for c in candidates:
        if c in cols:
            return c
    norm = {str(c).strip().lower(): c for c in cols}
    for c in candidates:
        if c.strip().lower() in norm:
            return norm[c.strip().lower()]
    for c in sorted(candidates, key=len):
        k = c.strip().lower()
        for col in cols:
            if k in str(col).strip().lower():
                return col
    return None


def find_lon_lat_columns(df):
    """Return (lon_col, lat_col) resolved from a DataFrame, or raise ValueError."""
    lat = _resolve(df, ["Epicentre latitude", "Epicentre lat", "Latitude", "latitude", "lat"])
    lon = _resolve(df, ["Epicentre longitude", "Epicentre lon", "Longitude", "longitude", "lon"])
    if lat is None or lon is None:
        raise ValueError("Could not find latitude/longitude columns "
                         "(expected e.g. 'Epicentre latitude' / 'Epicentre longitude'). "
                         f"Columns present: {list(df.columns)}")
    return lon, lat


# ----------------------------------------------------------------------------
# Label declutter: nudge annotation text in screen space until no two overlap.
# Works for both plain Axes and Cartopy GeoAxes because the offset is in *points*.
# ----------------------------------------------------------------------------
def _declutter(fig, anns, max_iter=400, pad=2.5, step=1.6):
    """Iteratively push overlapping annotation labels apart (force-based)."""
    if len(anns) < 2:
        return
    fig.canvas.draw()                                  # need a renderer for extents
    rend = fig.canvas.get_renderer()
    for _ in range(max_iter):
        boxes = [a.get_window_extent(rend) for a in anns]
        moved = False
        for i in range(len(anns)):
            for j in range(i + 1, len(anns)):
                bi, bj = boxes[i], boxes[j]
                if (bi.x0 - pad < bj.x1 and bj.x0 - pad < bi.x1 and
                        bi.y0 - pad < bj.y1 and bj.y0 - pad < bi.y1):
                    cix, ciy = (bi.x0 + bi.x1) / 2, (bi.y0 + bi.y1) / 2
                    cjx, cjy = (bj.x0 + bj.x1) / 2, (bj.y0 + bj.y1) / 2
                    dx, dy = cix - cjx, ciy - cjy
                    if dx == 0 and dy == 0:
                        dx, dy = 1.0, 0.7
                    n = math.hypot(dx, dy); dx, dy = dx / n, dy / n
                    ox, oy = anns[i].get_position()
                    anns[i].set_position((ox + dx * step, oy + dy * step))
                    px, py = anns[j].get_position()
                    anns[j].set_position((px - dx * step, py - dy * step))
                    moved = True
        if not moved:
            break
        fig.canvas.draw()


def _label_monsoon_cities(fig, ax, monsoon_df, lon_col, lat_col, transform=None):
    """Annotate each monsoon-linked event with its nearest city (deduplicated)."""
    if monsoon_df.empty:
        return []
    groups = {}
    for _, ev in monsoon_df.iterrows():
        city, _d = nearest_city(float(ev[lat_col]), float(ev[lon_col]))
        groups.setdefault(city, []).append((float(ev[lon_col]), float(ev[lat_col])))

    anns = []
    for city, pts in groups.items():
        lon_c = sum(p[0] for p in pts) / len(pts)
        lat_c = sum(p[1] for p in pts) / len(pts)
        kw = dict(xy=(lon_c, lat_c), xytext=(10, 10), textcoords="offset points",
                  fontsize=8.5, fontweight="bold", color=INK, zorder=12,
                  ha="left", va="bottom",
                  bbox=dict(boxstyle="round,pad=0.22", fc="white", ec=SEIS, lw=0.8, alpha=0.92),
                  arrowprops=dict(arrowstyle="-", color=SEIS, lw=0.7, shrinkA=0, shrinkB=2))
        if transform is not None:
            kw["xycoords"] = transform
        anns.append(ax.annotate(city, **kw))
    _declutter(fig, anns)
    return anns


# ----------------------------------------------------------------------------
# Epicentre map
# ----------------------------------------------------------------------------
def plot_epicentre_map(
    df,
    highlight_idx=None,
    exceptional_idx=None,
    extent=(60, 106, 5, 42),
    roi_halfwidth=1.5,
    title="Epicentre map",
    ref_cities=None,
    label_cities=True,
    figsize=(13, 8.5),
):
    """Geographic map of candidate / monsoon-linked epicentres on a land basemap.

    Layers: grey = climate-region events, red = monsoon-linked
    (probable_climate_interaction), green ring = highlight_idx,
    gold star = exceptional_idx, red square = 3x3 deg ROI. When ``label_cities``
    is True each monsoon-linked event is annotated with its nearest city/region
    and overlapping labels are pushed apart automatically.
    """
    highlight_idx   = set() if highlight_idx   is None else set(highlight_idx)
    exceptional_idx = set() if exceptional_idx is None else set(exceptional_idx)
    lon_col, lat_col = find_lon_lat_columns(df)

    climate_df = df[df["is_climate_region"].astype(bool)] if "is_climate_region" in df else df
    if "probable_climate_interaction" in climate_df:
        monsoon_df = climate_df[climate_df["probable_climate_interaction"].astype(bool)]
    else:
        monsoon_df = climate_df.iloc[0:0]

    # -------------------------------------------------------------- CARTOPY map
    if _HAS_CARTOPY:
        proj = ccrs.PlateCarree()
        fig = plt.figure(figsize=figsize)
        ax = plt.axes(projection=proj)
        ax.set_extent(extent, crs=proj)
        ax.add_feature(cfeature.OCEAN.with_scale("50m"), facecolor=OCEAN)
        ax.add_feature(cfeature.LAND.with_scale("50m"), facecolor=LAND)
        ax.add_feature(cfeature.LAKES.with_scale("50m"), facecolor=OCEAN, alpha=0.6)
        ax.add_feature(cfeature.RIVERS.with_scale("50m"), edgecolor=CLIM, linewidth=0.3, alpha=0.5)
        ax.add_feature(cfeature.BORDERS.with_scale("50m"), edgecolor="#9AA7B2", linewidth=0.5)
        ax.coastlines("50m", linewidth=0.6, color="#5A6B7B")
        # Grid LINES only -- NO Cartopy gridline *labels*. On some Cartopy
        # versions, labelled gridlines make the title/gridliner transform
        # non-invertible during drawing (LinAlgError: Singular matrix). We add
        # lon/lat tick labels the robust way instead, via Matplotlib ticks +
        # Cartopy formatters, which avoids that code path entirely.
        ax.gridlines(draw_labels=False, linestyle=(0, (3, 3)), linewidth=0.4,
                     color=GRID, alpha=0.7)
        ax.set_xticks(range(int(extent[0]), int(extent[1]) + 1, 10), crs=proj)
        ax.set_yticks(range(int(extent[2]), int(extent[3]) + 1, 10), crs=proj)
        ax.xaxis.set_major_formatter(LongitudeFormatter())
        ax.yaxis.set_major_formatter(LatitudeFormatter())
        ax.tick_params(labelsize=9, colors=MUTED)
        tkw = dict(transform=proj)
        txform = proj._as_mpl_transform(ax)
    # ------------------------------------------------- fallback: plain Matplotlib
    else:
        print("Cartopy not active -> drawing the map WITHOUT a land basemap.")
        print("   reason :", _CARTOPY_IMPORT_ERROR or "cartopy imported but disabled")
        print("   fix    : conda install -n epos_school -c conda-forge cartopy")
        print("            then RESTART THE KERNEL and re-run (the check happens at import).")
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_xlim(extent[0], extent[1]); ax.set_ylim(extent[2], extent[3])
        ax.set_xlabel("Longitude (deg E)"); ax.set_ylabel("Latitude (deg N)")
        ax.set_aspect("equal", adjustable="box")
        tkw = {}
        txform = None

    ax.scatter(climate_df[lon_col], climate_df[lat_col], s=16, c="#8A98A6",
               alpha=0.7, edgecolors="white", linewidths=0.3, zorder=4,
               label="Climate-region events", **tkw)
    ax.scatter(monsoon_df[lon_col], monsoon_df[lat_col], s=46, c=SEIS,
               alpha=0.95, edgecolors="white", linewidths=0.5, zorder=6,
               label="Monsoon-linked events", **tkw)
    for _, ev in monsoon_df.iterrows():
        ax.add_patch(mpatches.Rectangle(
            (ev[lon_col] - roi_halfwidth, ev[lat_col] - roi_halfwidth),
            2 * roi_halfwidth, 2 * roi_halfwidth, ec=SEIS, fc="none",
            lw=0.8, alpha=0.45, zorder=5, **tkw))
    for idx in highlight_idx & set(df.index):
        ev = df.loc[idx]
        ax.scatter(ev[lon_col], ev[lat_col], s=230, facecolors="none",
                   edgecolors=GREEN, linewidths=1.6, zorder=7, label="_nolegend_", **tkw)
    for idx in exceptional_idx & set(df.index):
        ev = df.loc[idx]
        ax.scatter(ev[lon_col], ev[lat_col], s=150, marker="*", color=GOLD,
                   edgecolors=INK, linewidths=0.5, zorder=8, label="_nolegend_", **tkw)

    if ref_cities is None:
        ref_cities = {"Kathmandu": (27.72, 85.32), "Delhi": (28.61, 77.21),
                      "Yangon": (16.84, 96.17), "Lhasa": (29.65, 91.14)}
    for name, (latc, lonc) in ref_cities.items():
        ax.plot(lonc, latc, marker="^", ms=5, color=INK, zorder=9, **tkw)

    if label_cities:
        _label_monsoon_cities(fig, ax, monsoon_df, lon_col, lat_col, transform=txform)

    handles, labels = ax.get_legend_handles_labels()
    handles += [Line2D([0], [0], marker="o", mfc="none", mec=GREEN, mew=1.6, ms=11,
                       ls="none", label="Waveform-validated"),
                Line2D([0], [0], marker="*", mfc=GOLD, mec=INK, ms=12, ls="none",
                       label="Exceptional rain (>=+2 sigma)"),
                Line2D([0], [0], marker="^", color=INK, ms=8, ls="none",
                       label="Reference city")]
    ax.legend(handles=handles, loc="lower left", framealpha=0.94)
    ax.set_title(title, fontsize=15, fontweight="bold", color=INK)
    if not _HAS_CARTOPY:
        plt.tight_layout()   # safe for plain axes; tight_layout collapses GeoAxes
    plt.show()
    return ax


# ----------------------------------------------------------------------------
# 30-year monsoon climatology time series
# ----------------------------------------------------------------------------
def plot_monsoon_timeseries(years, series, mu, sigma, obs_year, obs_total, z,
                            lat, lon, figsize=(9.5, 4.6)):
    """Plot the 30-yr ERA5 May-Sep total with mean, +/-1/2 sigma bands and the event."""
    fig, ax = plt.subplots(figsize=figsize)
    y0, y1 = min(years), max(years)

    ax.axhspan(mu - 2 * sigma, mu + 2 * sigma, color=CLIM, alpha=0.08, zorder=0)
    ax.axhspan(mu - 1 * sigma, mu + 1 * sigma, color=CLIM, alpha=0.12, zorder=0,
               label="+/-1 sigma")
    ax.axhline(mu, ls="--", color=MUTED, lw=1.1, zorder=2, label=f"Mean {mu:.0f} mm")
    ax.axhline(mu + 2 * sigma, ls=":", color=MUTED, lw=1.0, zorder=2,
               label=f"+2 sigma {mu + 2 * sigma:.0f} mm")

    ax.plot(years, series, "-o", color=CLIM, ms=4.5, lw=1.8, zorder=3,
            markerfacecolor="white", markeredgecolor=CLIM, markeredgewidth=1.2,
            label="ERA5 May-Sep total")

    ax.scatter([obs_year], [obs_total], s=150, marker="D", color=SEIS,
               edgecolors="white", linewidths=1.0, zorder=5,
               label=f"{obs_year} earthquake")
    ax.annotate(f"{obs_year}\n{obs_total:.0f} mm\nz = {z:+.2f}",
                xy=(obs_year, obs_total), xytext=(14, 16),
                textcoords="offset points", fontsize=9, color=INK,
                ha="left", va="bottom", zorder=6,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=SEIS, lw=0.9, alpha=0.95),
                arrowprops=dict(arrowstyle="->", color=SEIS, lw=1.1))

    ax.set_xlim(y0 - 0.5, y1 + 0.5)
    ax.set_xlabel("Year"); ax.set_ylabel("May-Sep precipitation (mm)")
    ax.set_title(f"Monsoon history - 3x3 deg box around {lat:.2f} N / {lon:.2f} E")
    ax.legend(loc="upper left", ncol=2, fontsize=8.5)
    plt.tight_layout()
    plt.show()
    return fig, ax


# ----------------------------------------------------------------------------
# Single-station seismogram with P / end picks
# ----------------------------------------------------------------------------
def plot_seismogram(tr, p_time, t_time, net, sta, cha, figsize=(14, 4.6)):
    """Plot one ObsPy trace with the STA/LTA onset (P) and end-of-shaking markers."""
    fig, ax = plt.subplots(figsize=figsize)
    times = tr.times("matplotlib")
    ax.plot(times, tr.data, color="#1B2A3A", lw=0.7, zorder=3, label="Ground motion")

    if p_time and t_time:
        ax.axvspan(p_time.matplotlib_date, t_time.matplotlib_date,
                   color=SEIS, alpha=0.10, zorder=1, label="Detected shaking")
    if p_time:
        ax.axvline(p_time.matplotlib_date, color=CLIM, ls="--", lw=1.6,
                   zorder=4, label="P onset")
    if t_time:
        ax.axvline(t_time.matplotlib_date, color=GREEN, ls="--", lw=1.6,
                   zorder=4, label="End of shaking")

    ax.xaxis_date()
    ax.set_title(f"Seismogram  {net}.{sta}  ({cha})", fontsize=13, fontweight="bold")
    ax.set_xlabel("Time (UTC)"); ax.set_ylabel("Amplitude (counts)")
    ax.margins(x=0.01)
    ax.legend(loc="upper right", ncol=4, fontsize=8.5)
    plt.tight_layout()
    plt.show()
    return fig, ax
