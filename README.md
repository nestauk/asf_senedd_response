# asf_senedd_response

This repo contains code for producing charts for ASF's August 2022 response to the Welsh Government call for evidence on home heating, and the updated versions of these plots for ASF's April 2023 response to the Welsh Government's consultation on Wales' renewable energy targets. The remainder of the charts for the April 2023 reponse can be produced from code in the repo `asf_welsh_energy_consultation`, as these charts are brand new for the response and this repo contains reworkings of older charts.

## Setup

- Meet the data science cookiecutter [requirements](http://nestauk.github.io/ds-cookiecutter/quickstart), in brief:
  - Install: `direnv` and `conda`
- Clone the repo: `git clone git@github.com:nestauk/asf_senedd_response.git`
- Navigate to the repo folder
- Checkout the correct branch if not working on dev
- Run `make install` to configure the development environment:
  - Setup the conda environment
  - Configure `pre-commit`
- Run `direnv allow`
- Activate conda environment: `conda activate asf_senedd_response`
- Install requirements: `pip install -r requirements.txt`
- Perform additional setup in order to save plots:

  - Follow the instructions here - you may just need to run `conda install -c conda-forge vega-cli vega-lite-cli`

- Change `LOCAL_DATA_DIR` in `getters/loading.py` to your local EPC data directory.

Note: no syncing of data from S3 is required as only EPC data is used here.

## Contributor guidelines

[Technical and working style guidelines](https://github.com/nestauk/ds-cookiecutter/blob/master/GUIDELINES.md)

---

<small><p>Project based on <a target="_blank" href="https://github.com/nestauk/ds-cookiecutter">Nesta's data science project template</a>
(<a href="http://nestauk.github.io/ds-cookiecutter">Read the docs here</a>).
</small>
