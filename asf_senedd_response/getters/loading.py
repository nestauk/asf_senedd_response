# File: asf_senedd_response/getters/loading.py
"""
For loading of raw data.
"""

from asf_core_data.getters.epc import epc_data
import pandas as pd

LOCAL_DATA_DIR = "/Users/chris.williamson/Documents/ASF_data/"
wales_epc_path = "inputs/data/wales_epc.csv"


def load_wales_df(from_csv=True):
    """Load preprocessed and deduplicated EPC dataset for Wales.
    If data is loaded from all-GB file, the filtered version is saved to csv
    for easier future loading.

    Args:
        from_csv (bool, optional): Whether to load from saved CSV. Defaults to True.

    Returns:
        pd.DataFrame: EPC data.
    """
    if from_csv:
        wales_epc = pd.read_csv(wales_epc_path)
    else:
        wales_epc = epc_data.load_preprocessed_epc_data(
            data_path=LOCAL_DATA_DIR,
            subset="Wales",
            batch="newest",
            version="preprocessed_dedupl",
            usecols=[
                "LMK_KEY",
                "INSPECTION_DATE",
                "UPRN",
                "POSTCODE",
                "CURRENT_ENERGY_EFFICIENCY",
                "CURRENT_ENERGY_RATING",
                "WALLS_ENERGY_EFF",
                "FLOOR_ENERGY_EFF",
                "ROOF_ENERGY_EFF",
                "CONSTRUCTION_AGE_BAND",
                "TENURE",
                "TRANSACTION_TYPE",
                "HP_INSTALLED",
            ],
        )

        wales_epc.TENURE = wales_epc.TENURE.replace(
            {
                "owner-occupied": "Owner-occupied",
                "rental (social)": "Socially rented",
                "rental (private)": "Privately rented",
                "unknown": "Unknown",
            }
        )
        wales_epc["CONSTRUCTION_AGE_BAND"].loc[
            (wales_epc.CONSTRUCTION_AGE_BAND == "unknown")
            & (wales_epc.TRANSACTION_TYPE == "new dwelling")
        ] = "2007 onwards"

        wales_epc.to_csv(wales_epc_path)

    return wales_epc


def load_wales_hp(wales_epc):
    """Load Welsh EPC data filtered to properties with heat pumps.

    Args:
        wales_epc (pd.DataFrame): Wales EPC data.

    Returns:
        pd.DataFrame: EPC data filtered to properties with heat pumps.
    """
    wales_hp = wales_epc.loc[wales_epc.HP_INSTALLED].reset_index(drop=True)

    return wales_hp
