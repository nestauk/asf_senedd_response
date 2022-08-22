from asf_core_data.utils.geospatial.data_agglomeration import add_hex_id
import pandas as pd


def generate_hex_counts(wales_df, pc_df):
    
    wales_df_coords = pd.merge(wales_df, pc_df, on=["POSTCODE"])
    wales_df_hex = add_hex_id(wales_df_coords, 6)
    hp_hex_counts = wales_df_hex.groupby(["hex_id", "HP_INSTALLED"]).size().unstack(fill_value=0)
    hp_hex_counts["total"] = hp_hex_counts[True] + hp_hex_counts[False]
    hp_hex_counts["perc_true"] = hp_hex_counts[True] / hp_hex_counts["total"] * 100
    hp_hex_counts = hp_hex_counts.reset_index()
    
    return hp_hex_counts


def generate_age_data(wales_df):
    
    age_props = wales_df.loc[wales_df.CONSTRUCTION_AGE_BAND != "unknown"].CONSTRUCTION_AGE_BAND.value_counts(normalize=True)*100
    age_props = age_props.reset_index()
    age_props = age_props.rename(columns={"index": "CONSTRUCTION_AGE_BAND", "CONSTRUCTION_AGE_BAND": "proportion"})
    ages_efficiencies = wales_df.groupby("CONSTRUCTION_AGE_BAND")["CURRENT_ENERGY_EFFICIENCY"].mean().reset_index()
    age_data = age_props.merge(ages_efficiencies, on="CONSTRUCTION_AGE_BAND")
    age_data["CONSTRUCTION_AGE_BAND"] = age_data["CONSTRUCTION_AGE_BAND"].replace({"England and Wales: before 1900": "Pre-1900"})
    age_data = age_data.set_index("CONSTRUCTION_AGE_BAND").loc[
        ["Pre-1900",
            "1900-1929",
            "1930-1949",
            "1950-1966",
            "1965-1975",
            "1976-1983",
            "1983-1991",
            "1991-1998",
            "1996-2002",
            "2003-2007",
            "2007 onwards"]
    ].reset_index()
    age_data["CURRENT_ENERGY_EFFICIENCY"] = age_data["CURRENT_ENERGY_EFFICIENCY"].round(1)
    age_data["cumul_prop"] = age_data["proportion"].cumsum()
    
    return age_data