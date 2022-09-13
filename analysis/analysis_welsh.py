from pipeline.augmenting import generate_hex_counts, generate_age_data
from getters.loading import load_wales_df, load_wales_hp, load_pc_df
from pipeline.plotting_welsh import generic_plot, age_prop_chart, plot_kepler_graph


wales_df = load_wales_df()
wales_hp = load_wales_hp(wales_df)
pc_df = load_pc_df()

hp_hex_counts = generate_hex_counts(wales_df, pc_df)
age_data = generate_age_data(wales_df)

welsh_replacements = {
    "TENURE": {
        "Owner-occupied": "Perchen-feddiannaeth",
        "Socially rented": "Rhentu cymdeithasol",
        "Privately rented": "Rhentu preifat",
        "Unknown": "Anhysbys",
    },
    "CONSTRUCTION_AGE_BAND": {
        "England and Wales: before 1900": "Cyn 1900",
        "Pre-1900": "Cyn 1900",
        "2007 onwards": "2007 ymlaen",
        "unknown": "Anhysbys"
    }
}

for df in [wales_df, wales_hp, pc_df, hp_hex_counts, age_data]:
    for col in ["TENURE", "CONSTRUCTION_AGE_BAND"]:
        if col in df.columns:
            df[col] = df[col].replace(welsh_replacements[col])

# Key statistics
# print("Number of heat pumps:", len(wales_hp))
# print("Number of properties in EPC:", len(wales_df))
# print("Estimated proportion of properties with a heat pump:", "{:.2%}".format(len(wales_hp)/len(wales_df)))
# print(wales_hp.TENURE.value_counts(normalize=True))

# good_props = wales_df.loc[
#     wales_df.CURRENT_ENERGY_RATING.isin(["A", "B", "C"])
#     & wales_df.WALLS_ENERGY_EFF.isin(["Good", "Very Good"])
#     & wales_df.FLOOR_ENERGY_EFF.isin(["Good", "Very Good"])
# ]
# print("Number of EPC C+ properties with good or very good wall and floor insulation:", len(good_props))
# print("As a proportion of properties in EPC:", len(good_props)/len(wales_df))

# Tenure of Welsh HPs
generic_plot(
    wales_hp,
    "TENURE",
    "Ffig. 4: Deiliadaeth eiddo â phympiau gwres yng Nghymru",
    'Deiliadaeth',
    'Canran yr eiddo',
    filename="hp_tenure_welsh",
    x_type="tenure",
    expand_y=True
)

## Kepler graph goes here in the flow of the doc

# EPC, all
generic_plot(
    wales_df.loc[wales_df.CURRENT_ENERGY_RATING != "unknown"],
    "CURRENT_ENERGY_RATING",
    "Ffig. 6: Sgoriau EPC holl eiddo Cymru",
    'Sgôr effeithlonrwydd ynni',
    'Canran yr eiddo',
    filename="epc_all_welsh",
    x_type="other"
)

# EPC, private sector with HPs
generic_plot(
    wales_hp.loc[wales_hp.TENURE.isin(["Perchen-feddiannaeth", "Rhentu preifat"])],
    "CURRENT_ENERGY_RATING",
    ["Ffig. 7: Sgoriau EPC eiddo perchen-feddiannaeth a", "rhentu preifat Cymru sydd â phympiau gwres"],
    'Sgôr effeithlonrwydd ynni',
    'Canran yr eiddo',
    filename="epc_hp_private_welsh",
    x_type="other"
)

# EPCs, private sector with retrofitted HPs
generic_plot(
    wales_hp.loc[wales_hp.TENURE.isin(["Perchen-feddiannaeth", "Rhentu preifat"]) & (wales_hp.CONSTRUCTION_AGE_BAND != "2007 ymlaen")],
    "CURRENT_ENERGY_RATING",
    ["Ffig. 8: Sgoriau EPC eiddo perchen-feddiannaeth a rhentu prifat", "Cymru sydd â phympiau gwres, a adeiladwyd cyn 2007"],
    'Sgôr effeithlonrwydd ynni',
    'Canran yr eiddo',
    filename="epc_hp_private_retrofit_welsh",
    x_type="other"
)

# Ages and EPC ratings
age_prop_chart(age_data, "Ffig. 9: Bandiau oedran adeiladu ac effeithlonrwydd ynni", "age_prop_welsh")

# Map of Welsh HPs
plot_kepler_graph(hp_hex_counts, "hp_map_welsh")