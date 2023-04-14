# asf_senedd_response

This repo contains code for producing charts for ASF's August 2022 response to the Welsh Government call for evidence on home heating, and the updated versions of these plots for ASF's April 2023 response to the Welsh Government's consultation on Wales' renewable energy targets. The remainder of the charts for the April 2023 reponse can be produced from code in the repo `asf_welsh_energy_consultation`, as these charts are brand new for the response and this repo contains reworkings of older charts.

## Setup

- Meet the data science cookiecutter [requirements](http://nestauk.github.io/ds-cookiecutter/quickstart), in brief:
  - Install: `direnv` and `conda`
- Clone the repo: `git clone git@github.com:nestauk/asf_senedd_response.git`
- Navigate to the repo folder
- Run `direnv allow`
- Checkout the correct branch if not working on dev
- Try `make install`, but this old repo predates some cookiecutter functionality so it might not work. If it doesn't then just create the conda environment manually: `conda create --name asf_senedd_response python=3.8`, `conda activate asf_senedd_response`, `pip install -r requirements.txt requirements_dev.txt`
- Perform additional setup in order to save plots:

  - Follow the instructions here - you may just need to run `conda install -c conda-forge vega-cli vega-lite-cli`

- Change `LOCAL_DATA_DIR` in `getters/loading.py` to your local EPC data directory.

- Run `python asf_senedd_response/analysis/wales_analysis.py`. This should generate 10 plots, five in each of `outputs/figures/english/` and `outputs/figures/welsh/`:
  - `age_prop.png`
  - `epc_all.html`
  - `epc_hp_private_retrofit.html`
  - `epc_hp_private.html`
  - `hp_tenure.html`

Note: no syncing of data from S3 is required as only EPC data is used here.

## Skeleton folder structure

```
asf_senedd_response/
├─ analysis/
│  ├─ wales_analysis.py - produces plots and stats
├─ getters/
│  ├─ loading.py - getters for raw data
├─ pipeline/
│  ├─ augmenting.py - functions to process and enhance raw data
│  ├─ plotting.py - generic plotting functions
├─ utils/
│  ├─ formatting.py - formatting numbers for plots
outputs/
├─ figures/
│  ├─ english/ - English-language charts
│  ├─ welsh/ - Welsh-language charts
```

## Contributor guidelines

[Technical and working style guidelines](https://github.com/nestauk/ds-cookiecutter/blob/master/GUIDELINES.md)

---

<small><p>Project based on <a target="_blank" href="https://github.com/nestauk/ds-cookiecutter">Nesta's data science project template</a>
(<a href="http://nestauk.github.io/ds-cookiecutter">Read the docs here</a>).
</small>
