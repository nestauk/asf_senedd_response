# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: senedd_response
#     language: python
#     name: senedd_response
# ---

# +
from keplergl import KeplerGl

from getters.loading import load_wales_df, load_pc_df
from pipeline.augmenting import generate_hex_counts

# +
wales_df = load_wales_df()
pc_df = load_pc_df()

hex_counts = generate_hex_counts(wales_df, pc_df)

# +
hex_map = KeplerGl(height=500)

hex_map.save_to_html(
    file_name="outputs/hp_map.html",
    data={'data': hex_counts[["perc_true", "hex_id"]]},
    config=hex_map.config
)
