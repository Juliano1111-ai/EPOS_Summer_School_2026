```{image} _static/epos_logo.png
:alt: EPOS — European Plate Observing System
:width: 300px
:align: center
:target: https://www.epos-eu.org/
```

# Interlinking Research Infrastructures

### A hands-on summer-school module on Geoscience & Climate data

```{epigraph}
Changing Climate and Geoscience.

-- EPOS ON Summer School
```

Welcome! This is lecture materials **“Interlinking Research
Infrastructures in Earth System: A Focus on Geoscience and Climate”**, delivered at the
[EPOS ON](https://www.epos-eu.org/on) Summer School. The goal is
to show, with real code and real data, how the major European environmental
**Research Infrastructures (RIs)** can be combined to ask scientific questions that no
single archive could answer alone.

Each RI exposes its data through a *different* access protocol. Here we show how to access, collect, and combine data from atmospheric and ocean science as well as geoscience; and treat results into a single
analysis.

| Domain | Research Infrastructure | Access mechanism |
|---|---|---|
| Climate reanalysis | **ECMWF** (ERA5) | API-based retrieval (`cdsapi`) |
| Climate in-situ | **ARGO** (BGC-Argo) | ERDDAP tabledap (REST/JSON) |
| Climate observation | **CMEMS** (Copernicus Marine) | OpenDAP / `copernicusmarine` toolbox |
| Solid-earth | **GFZ / FDSN** | Seismic waveform web services (`obspy`) |

## What you will build

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} 🌊 Application 1 — ARGO & CMEMS
Investigate how a tsunami perturbs the physical and biogeochemical state of the sea.
You will pull **Sea Level Anomaly** fields from CMEMS to visualise the wave, and
**BGC-Argo float** profiles (chlorophyll, backscatter) from IFREMER's ERDDAP server to
look for a biogeochemical response — focused on the 2018 Ionian Sea (M6.8) event.
+++
{doc}`Open Application 1 → <application_1_argo_cmems/epos_argo_cmems>`
:::

:::{grid-item-card} 🏔️ Application 2 — ECMWF & Seismicity
Explore the hypothesis that **monsoon hydrological loading modulates seismicity** in
the Himalaya. You will flag climate-sensitive earthquakes from an EPOS catalogue, fetch
their waveforms (with an optional STA/LTA picker), and overlay **ERA5 precipitation** to
rank each event against a 30-year climatology.
+++
{doc}`Open Application 2 → <application_2_ecmwf/epos_ecmwf>`
:::
::::

## How this book works

```{admonition} Read this before you run anything
:class: important
The notebooks call **live data services that require free credentials**. The pages you
see here display outputs that were saved when the author last ran them — so you can read
the full analysis without an account. To *re-run* the code yourself, follow the
{doc}`setup` page first, then launch a notebook with the **🚀 rocket icon** (top-right of
each notebook page) on **Google Colab** or **Binder**, or run it locally.
```

- **{doc}`setup`** — install the environment and register the (free) data credentials.
- **Applications 1 & 2** — the two annotated, runnable notebooks.
- **{doc}`references`** — the full scientific bibliography.

## Prerequisites

A working knowledge of Python and the scientific stack (`numpy`, `pandas`, `xarray`,
`matplotlib`). No prior seismology or oceanography is assumed — the relevant background is
explained inline.

```{admonition} How to cite
:class: tip
Ramanantsoa, H. J. D. (2025). *Interlinking Research Infrastructures: A Focus on
Geoscience and Climate* — EPOS ON Summer School teaching materials.
```

---

*Author:* **Heriniaina Juliano Dani Ramanantsoa**, University of Bergen ·
✉️ [heriniaina.j.ramanantsoa@uib.no](mailto:heriniaina.j.ramanantsoa@uib.no)
