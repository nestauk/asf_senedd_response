from pipeline.augmenting import generate_hex_counts, generate_age_data
from getters.loading import load_wales_df, load_wales_hp, load_pc_df
from pipeline.plotting import generic_plot, age_prop_chart, plot_kepler_graph


wales_df = load_wales_df()
wales_hp = load_wales_hp(wales_df)
pc_df = load_pc_df()

hp_hex_counts = generate_hex_counts(wales_df, pc_df)
age_data = generate_age_data(wales_df)

# Key statistics
print("Number of heat pumps:", len(wales_hp))
print("Number of properties in EPC:", len(wales_df))
print("Estimated proportion of properties with a heat pump:", "{:.2%}".format(len(wales_hp)/len(wales_df)))
print(wales_hp.TENURE.value_counts(normalize=True))

good_props = wales_df.loc[
    wales_df.CURRENT_ENERGY_RATING.isin(["A", "B", "C"])
    & wales_df.WALLS_ENERGY_EFF.isin(["Good", "Very Good"])
    & wales_df.FLOOR_ENERGY_EFF.isin(["Good", "Very Good"])
]
print("Number of EPC C+ properties with good or very good wall and floor insulation:", len(good_props))
print("As a proportion of properties in EPC:", len(good_props)/len(wales_df))

# Tenure of Welsh HPs
generic_plot(
    wales_hp,
    "TENURE",
    "Fig. 4: Tenure of Welsh properties with heat pumps",
    'Tenure',
    'Percentage of properties',
    filename="hp_tenure",
    x_type="tenure",
    expand_y=True
)

## Kepler graph goes here in the flow of the doc

# EPC, all
generic_plot(
    wales_df.loc[wales_df.CURRENT_ENERGY_RATING != "unknown"],
    "CURRENT_ENERGY_RATING",
    "Fig. 6: EPC ratings of all Welsh properties",
    'Energy efficiency rating',
    'Percentage of properties',
    filename="epc_all",
    x_type="other"
)

# EPC, private sector with HPs
generic_plot(
    wales_hp.loc[wales_hp.TENURE.isin(["Owner-occupied", "Privately rented"])],
    "CURRENT_ENERGY_RATING",
    ["Fig. 7: EPC ratings of owner-occupied and privately rented", "Welsh properties with heat pumps"],
    'Energy efficiency rating',
    'Percentage of properties',
    filename="epc_hp_private",
    x_type="other"
)

# EPCs, private sector with retrofitted HPs
generic_plot(
    wales_hp.loc[wales_hp.TENURE.isin(["Owner-occupied", "Privately rented"]) & (wales_hp.CONSTRUCTION_AGE_BAND != "2007 onwards")],
    "CURRENT_ENERGY_RATING",
    ["Fig. 8: EPC ratings of owner-occupied and privately rented", "Welsh properties with heat pumps, built pre-2007"],
    'Energy efficiency rating',
    'Percentage of properties',
    filename="epc_hp_private_retrofit",
    x_type="other"
)

# Ages and EPC ratings
age_prop_chart(age_data, "Fig. 9: Construction age bands and energy efficiencies", "age_prop")

# Map of Welsh HPs
plot_kepler_graph(hp_hex_counts, "hp_map")