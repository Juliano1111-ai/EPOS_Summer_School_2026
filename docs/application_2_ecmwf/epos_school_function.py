# ----------------------------------------------------------------------------
# Project: Seismic Event Analysis and Waveform Picking with Climate Context
# Description: This script processes earthquake event data, flags events
#              potentially influenced by climate interactions, fetches seismic
#              waveforms for these flagged events, performs P/T phase
#              picking using the STA/LTA algorithm. It then integrates
#              ECMWF (ERA5) cumulative precipitation data for the identified events
#              to assess potential correlation with monsoon conditions.
#              Finally, it saves all relevant outputs into a single
#              multimodal pickle file for comprehensive data archiving.
# Target Audience: Students of seismology, geophysics, environmental science.
# ----------------------------------------------------------------------------

import os
import pandas as pd
import matplotlib.pyplot as plt
from obspy.clients.fdsn import Client
from obspy import UTCDateTime, Trace # Removed 'Stats' from import, as it's not directly importable from obspy top-level
from obspy.signal.trigger import classic_sta_lta, trigger_onset
import numpy as np # For handling numeric data, especially for tolist() conversion



# ──────────────────────────────────────────────────────────────────────────────
# 📍  Generic epicentre plotting helper
# 📍  MAP OF CLIMATE-SENSITIVE EPICENTRES AND MONSOON-LINKED EVENTS
# ──────────────────────────────────────────────────────────────────────────────

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    _HAS_CARTOPY = True
except ModuleNotFoundError:               # falls back to plain scatter if Cartopy missing
    _HAS_CARTOPY = False


def plot_epicentre_map(
    df,
    highlight_idx=None,              # green rings  (e.g., waveform_ok)
    exceptional_idx=None,            # blue stars   (e.g., very-wet seasons)
    extent=(50, 110, -5, 45),        # (W, E, S, N)
    roi_halfwidth=1.5,               # half-side of red ROI square (deg)
    title="Epicentre map",
    ref_cities=None,
    figsize=(12, 8),
):
    """
    Plot climate-sensitive epicentres and extra markers.
    Draw a regional map with:
      • grey  : all events in climate-sensitive regions  (df['is_climate_region'])
      • red   : subset flagged as probable monsoon interaction
      • green ring : optional ‘highlight_idx’ events (e.g., waveform found)
      • red box: 3×3° ROI around monsoon-linked events

    Parameters
    ----------
    df : DataFrame with epicentre columns and climate flags.
    highlight_idx : iterable[int] or None
        Event indices to encircle in green.
    exceptional_idx : iterable[int] or None
        Event indices to mark with blue stars.
    extent : tuple
        (west, east, south, north) map bounds in degrees.
    """
    highlight_idx   = set() if highlight_idx   is None else set(highlight_idx)
    exceptional_idx = set() if exceptional_idx is None else set(exceptional_idx)

    climate_df  = df[df["is_climate_region"]]
    monsoon_df  = climate_df[climate_df["probable_climate_interaction"]]

    # ──────────────────────────────  CARTOPY  ───────────────────────────────
    if _HAS_CARTOPY:
        proj = ccrs.PlateCarree()
        fig  = plt.figure(figsize=figsize)
        ax   = plt.axes(projection=proj)

        ax.set_extent(extent, crs=proj)
        ax.add_feature(cfeature.LAND,   facecolor="#f7f7f7")
        ax.add_feature(cfeature.OCEAN,  facecolor="#e0f2ff")
        ax.add_feature(cfeature.BORDERS, linewidth=0.4)
        ax.coastlines("110m", linewidth=0.4)

        # base layers
        ax.scatter(climate_df["Epicentre longitude"], climate_df["Epicentre latitude"],
                   s=12, c="grey", alpha=0.6, transform=proj,
                   label="Climate-region quakes")
        ax.scatter(monsoon_df["Epicentre longitude"], monsoon_df["Epicentre latitude"],
                   s=22, c="red", alpha=0.9, transform=proj,
                   label="Monsoon-linked quakes")

        # ROI squares
        for _, ev in monsoon_df.iterrows():
            ax.add_patch(mpatches.Rectangle(
                (ev["Epicentre longitude"]-roi_halfwidth,
                 ev["Epicentre latitude"] -roi_halfwidth),
                2*roi_halfwidth, 2*roi_halfwidth,
                ec="red", fc="none", lw=0.6, alpha=0.5, transform=proj))

        # green rings
        for idx in highlight_idx & set(df.index):
            ev = df.loc[idx]
            ax.scatter(ev["Epicentre longitude"], ev["Epicentre latitude"],
                       s=200, facecolors="none", edgecolors="green",
                       linewidths=1.3, transform=proj, label="_nolegend_")

        # blue stars
        for idx in exceptional_idx & set(df.index):
            ev = df.loc[idx]
            ax.scatter(ev["Epicentre longitude"], ev["Epicentre latitude"],
                       s=90, marker="*", color="blue", edgecolors="white",
                       linewidths=0.4, transform=proj, label="_nolegend_")

        # labelled graticule
        gl = ax.gridlines(draw_labels=True, linestyle="--",
                          linewidth=0.3, alpha=0.5)
        gl.top_labels = gl.right_labels = False
        gl.xlabel_style = gl.ylabel_style = {"size": 9}


        # ── reference cities ─────────────────────────────────────────────
        if ref_cities is None:
            ref_cities = {
                "Kathmandu": (27.7172, 85.3240),
                "Delhi":     (28.7041, 77.1025),
                "Yangon":    (16.8409, 96.1735),
            }
        for name, (latc, lonc) in ref_cities.items():
            ax.plot(lonc, latc, marker="^", markersize=6, color="black", transform=proj)
            ax.text(lonc, latc - 0.5, name, fontsize=8,
                    ha="center", va="top", transform=proj)

    # ─────────────────────── fallback: plain Matplotlib ─────────────────────
    else:
        fig, ax = plt.subplots(figsize=figsize)
        ax.scatter(climate_df["Epicentre longitude"], climate_df["Epicentre latitude"],
                   s=12, c="grey", alpha=0.6, label="Climate-region quakes")
        ax.scatter(monsoon_df["Epicentre longitude"], monsoon_df["Epicentre latitude"],
                   s=22, c="red", alpha=0.9, label="Monsoon-linked quakes")

        for _, ev in monsoon_df.iterrows():
            rect = mpatches.Rectangle(
                (ev["Epicentre longitude"]-roi_halfwidth,
                 ev["Epicentre latitude"] -roi_halfwidth),
                2*roi_halfwidth, 2*roi_halfwidth,
                ec="red", fc="none", lw=0.6, alpha=0.5)
            ax.add_patch(rect)

        for idx in highlight_idx & set(df.index):
            ev = df.loc[idx]
            ax.scatter(ev["Epicentre longitude"], ev["Epicentre latitude"],
                       s=200, facecolors="none", edgecolors="green",
                       linewidths=1.3)

        for idx in exceptional_idx & set(df.index):
            ev = df.loc[idx]
            ax.scatter(ev["Epicentre longitude"], ev["Epicentre latitude"],
                       s=90, marker="*", color="blue", edgecolors="white",
                       linewidths=0.4)

        ax.set_xlim(extent[0], extent[1]); ax.set_ylim(extent[2], extent[3])
        ax.set_xticks(range(int(extent[0]), int(extent[1])+1, 10))
        ax.set_yticks(range(int(extent[2]), int(extent[3])+1, 10))
        ax.set_xlabel("Longitude (°)"); ax.set_ylabel("Latitude (°)")
        ax.grid(True, ls="--", lw=0.25, alpha=0.5)

    ax.legend(loc="lower left")
    ax.set_title(title)
    plt.show()
    return ax


# plot_epicentre_map(df, title="Map 1 – Candidate & monsoon-linked epicentres")




# --------------------------------------------------------------------------
# Plot_seismograms with this improved version
# --------------------------------------------------------------------------












