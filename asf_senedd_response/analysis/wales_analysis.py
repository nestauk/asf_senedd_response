from asf_senedd_response.getters.loading import load_wales_df, load_wales_hp
from asf_senedd_response.pipeline.augmenting import generate_age_data
from asf_senedd_response.pipeline.plotting import generic_plot, age_prop_chart

wales_df = load_wales_df(from_csv=False)
wales_hp = load_wales_hp(wales_df)


## English plots

# Key statistics
print("Number of heat pumps:", len(wales_hp))
print("Number of properties in EPC:", len(wales_df))
print(
    "Estimated proportion of properties with a heat pump:",
    "{:.2%}".format(len(wales_hp) / len(wales_df)),
)
print(wales_hp.TENURE.value_counts(normalize=True))

epc_c_or_above_and_good_walls = wales_df.loc[
    wales_df["CURRENT_ENERGY_RATING"].isin(["A", "B", "C"])
    & wales_df["WALLS_ENERGY_EFF"].isin(["Good", "Very Good"])
]

epc_c_or_above_and_good_walls_and_roof = epc_c_or_above_and_good_walls.loc[
    epc_c_or_above_and_good_walls["ROOF_ENERGY_EFF"].isin(["Good", "Very Good"])
]

print(
    "Number of EPC C+ properties with good or very good wall insulation:",
    len(epc_c_or_above_and_good_walls),
)
print(
    "As a proportion of properties in EPC:",
    len(epc_c_or_above_and_good_walls) / len(wales_df),
)

print(
    "\nNumber of EPC C+ properties with good or very good wall and roof insulation:",
    len(epc_c_or_above_and_good_walls_and_roof),
)
print(
    "As a proportion of properties in EPC:",
    len(epc_c_or_above_and_good_walls_and_roof) / len(wales_df),
)

new_good = epc_c_or_above_and_good_walls.loc[
    epc_c_or_above_and_good_walls.INSPECTION_DATE > "2022-04-01"
]

# Tenure of Welsh HPs
generic_plot(
    wales_hp,
    "TENURE",
    "Fig. 4: Tenure of Welsh properties with heat pumps",
    "Tenure",
    "Percentage of properties",
    filename="hp_tenure",
    x_type="tenure",
    expand_y=True,
)

# EPC, all
generic_plot(
    wales_df.loc[wales_df.CURRENT_ENERGY_RATING != "unknown"],
    "CURRENT_ENERGY_RATING",
    "Fig. 6: EPC ratings of all Welsh properties",
    "Energy efficiency rating",
    "Percentage of properties",
    filename="epc_all",
    x_type="other",
)

# EPC, private sector with HPs
generic_plot(
    wales_hp.loc[wales_hp.TENURE.isin(["Owner-occupied", "Privately rented"])],
    "CURRENT_ENERGY_RATING",
    [
        "Fig. 7: EPC ratings of owner-occupied and privately rented",
        "Welsh properties with heat pumps",
    ],
    "Energy efficiency rating",
    "Percentage of properties",
    filename="epc_hp_private",
    x_type="other",
)

# EPCs, private sector with retrofitted HPs
generic_plot(
    wales_hp.loc[
        wales_hp.TENURE.isin(["Owner-occupied", "Privately rented"])
        & (wales_hp.CONSTRUCTION_AGE_BAND != "2007 onwards")
    ],
    "CURRENT_ENERGY_RATING",
    [
        "Fig. 8: EPC ratings of owner-occupied and privately rented",
        "Welsh properties with heat pumps, built pre-2007",
    ],
    "Energy efficiency rating",
    "Percentage of properties",
    filename="epc_hp_private_retrofit",
    x_type="other",
)

age_data = generate_age_data(wales_df)
age_prop_chart(
    age_data, "Fig. 9: Construction age bands and energy efficiencies", "age_prop"
)


## Welsh plots

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
        "unknown": "Anhysbys",
    },
}

for df in [wales_df, wales_hp]:
    for col in ["TENURE", "CONSTRUCTION_AGE_BAND"]:
        if col in df.columns:
            df[col] = df[col].replace(welsh_replacements[col])

# Tenure of Welsh HPs
generic_plot(
    wales_hp,
    "TENURE",
    "Ffig. 4: Deiliadaeth eiddo â phympiau gwres yng Nghymru",
    "Deiliadaeth",
    "Canran yr eiddo",
    filename="hp_tenure_welsh",
    x_type="tenure",
    expand_y=True,
    language="welsh",
)

# EPC, all
generic_plot(
    wales_df.loc[wales_df.CURRENT_ENERGY_RATING != "unknown"],
    "CURRENT_ENERGY_RATING",
    "Ffig. 6: Sgoriau EPC holl eiddo Cymru",
    "Sgôr effeithlonrwydd ynni",
    "Canran yr eiddo",
    filename="epc_all_welsh",
    x_type="other",
    language="welsh",
)

# EPC, private sector with HPs
generic_plot(
    wales_hp.loc[wales_hp.TENURE.isin(["Perchen-feddiannaeth", "Rhentu preifat"])],
    "CURRENT_ENERGY_RATING",
    [
        "Ffig. 7: Sgoriau EPC eiddo perchen-feddiannaeth a",
        "rhentu preifat Cymru sydd â phympiau gwres",
    ],
    "Sgôr effeithlonrwydd ynni",
    "Canran yr eiddo",
    filename="epc_hp_private_welsh",
    x_type="other",
    language="welsh",
)

# EPCs, private sector with retrofitted HPs
generic_plot(
    wales_hp.loc[
        wales_hp.TENURE.isin(["Perchen-feddiannaeth", "Rhentu preifat"])
        & (wales_hp.CONSTRUCTION_AGE_BAND != "2007 ymlaen")
    ],
    "CURRENT_ENERGY_RATING",
    [
        "Ffig. 8: Sgoriau EPC eiddo perchen-feddiannaeth a rhentu prifat",
        "Cymru sydd â phympiau gwres, a adeiladwyd cyn 2007",
    ],
    "Sgôr effeithlonrwydd ynni",
    "Canran yr eiddo",
    filename="epc_hp_private_retrofit_welsh",
    x_type="other",
    language="welsh",
)

# Ages and EPC ratings
age_prop_chart(
    age_data,
    "Ffig. 9: Bandiau oedran adeiladu ac effeithlonrwydd ynni",
    "age_prop_welsh",
)
