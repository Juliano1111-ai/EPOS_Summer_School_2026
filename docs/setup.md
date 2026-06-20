# Setup & credentials

This page gets you from a clean machine to running both notebooks. It takes ~15 minutes,
most of which is registering for two **free** data accounts.

## 1. Install the environment

Clone the repository and create the environment. `conda`/`mamba` is recommended because
two dependencies (`copernicusmarine`, `cartopy`) are far easier to install that way.

`````{tab-set}
````{tab-item} conda / mamba (recommended)
```bash
git clone https://github.com/Juliano1111-ai/EPOS_Summer_School_2026.git
cd EPOS_Summer_School_2026
mamba env create -f environment.yml      # or: conda env create -f environment.yml
conda activate epos-school
jupyter lab
```
````

````{tab-item} pip + venv
```bash
git clone https://github.com/Juliano1111-ai/EPOS_Summer_School_2026.git
cd EPOS_Summer_School_2026
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab
```
````
`````

## 2. Register the data credentials

Both services are free for research and education.

### Copernicus Marine (CMEMS) — needed for Application 1

1. Register at [data.marine.copernicus.eu/register](https://data.marine.copernicus.eu/register).
2. Store your credentials **once** with the toolbox (preferred — nothing ends up in the notebook):

   ```bash
   copernicusmarine login
   ```

   Then leave `USERNAME`/`PASSWORD` blank in the notebook; the toolbox uses the cached login.
   Alternatively, export them before launching Jupyter:

   ```bash
   export COPERNICUSMARINE_SERVICE_USERNAME="<your_username>"
   export COPERNICUSMARINE_SERVICE_PASSWORD="<your_password>"
   ```

### Copernicus Climate Data Store (CDS / ERA5) — needed for Application 2

```{warning}
The **legacy CDS** (`cds.climate.copernicus.eu/api/v2`) was retired on **26 Sep 2024**.
Use the new endpoint and a **Personal Access Token** (an old `UID:key` will not work).
```

1. Create an ECMWF account and log in to
   [cds.climate.copernicus.eu](https://cds.climate.copernicus.eu).
2. Copy your token from your [CDS profile](https://cds.climate.copernicus.eu/profile) into
   `~/.cdsapirc`:

   ```text
   url: https://cds.climate.copernicus.eu/api
   key: <YOUR-PERSONAL-ACCESS-TOKEN>
   ```

3. **Accept the licence** on each dataset page you intend to use (e.g.
   *ERA5 monthly means on single levels*) — downloads fail until you do.

```{tip}
With `~/.cdsapirc` in place you can delete the in-notebook credential lines entirely and
just call `cdsapi.Client()` with no arguments.
```

## 3. ARGO (BGC-Argo via IFREMER ERDDAP)

No account required — Application 1 queries the public
[IFREMER ERDDAP server](https://erddap.ifremer.fr/erddap/tabledap/ArgoFloats-synthetic-BGC.html)
over plain HTTP.

## 4. Run order

Work through **Application 1** then **Application 2** — each notebook is self-contained and
runs top to bottom. The small demo datasets (a CMEMS Sea-Level subset and the EPOS
earthquake catalogue) ship with the repository, so the offline parts of each notebook work
immediately even before your credentials are active.

```{admonition} Running in the cloud
:class: note
Use the **🚀 rocket icon** at the top-right of any notebook page to open it on **Colab** or
**Binder**. The credential-free cells run as-is; for the data-download cells, add your own
keys as described above.
```
