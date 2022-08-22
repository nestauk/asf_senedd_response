from asf_core_data.pipeline.preprocessing import preprocess_epc_data
from asf_core_data.getters.data_getters import load_data

from pathlib import Path
import pandas as pd

data_path = "inputs/wales_epc.csv"


def load_wales_df():

    if not Path(data_path).is_file():

        print("Loading and preparing the data...")

        wales_epc = preprocess_epc_data.load_and_preprocess_epc_data(
            data_path="S3",
            subset="Wales",
            usecols=None,
            remove_duplicates=False,
            save_data=None,
        )

        wales_epc.to_csv(data_path, index=False)

        print("Done!")

    else:

        print("Loading the data...")
        wales_epc = pd.read_csv(data_path)
        print("Done!")

    wales_df_noindex = wales_epc.reset_index(drop=True)
    wales_df = wales_df_noindex.sort_values("INSPECTION_DATE").groupby("UPRN").tail(1).reset_index(drop=True)
    wales_df.TENURE = wales_df.TENURE.replace({
        "owner-occupied": "Owner-occupied",
        "rental (social)": "Socially rented",
        "rental (private)": "Privately rented",
        "unknown": "Unknown"
    })
    wales_df["CONSTRUCTION_AGE_BAND"].loc[(wales_df.CONSTRUCTION_AGE_BAND=='unknown') & (wales_df.TRANSACTION_TYPE=='new dwelling')] = "2007 onwards"
    
    return wales_df


def load_wales_hp(wales_df):

    wales_hp = wales_df.loc[wales_df.HP_INSTALLED].reset_index(drop=True)
    
    return wales_hp


def load_pc_df():
    
    pc_df = load_data("S3", "inputs/supplementary_data/geospatial/ukpostcodes_to_coordindates.csv")
    pc_df = pc_df.rename(
        columns={
            "postcode": "POSTCODE",
            "latitude": "LATITUDE",
            "longitude": "LONGITUDE",
        }
    )
    
    return pc_df