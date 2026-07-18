import scipy.stats as stats
import numpy as np
import pandas as pd
import os
from pathlib import Path
from nuclide_transport_data.property2dataframe import load_nuclide_property
from nuclide_transport_data.load_path import get_path_in_dir


def s_CV(df):
    """Calculate the coefficient of variation (CV) for the specific rock types.

    Args:
        df (pd.DataFrame): The dataframe containing nuclide property data.

    Returns:
        float: The coefficient of variation for the specified rock type.
    """
    
    # stacks all values into one long Series
    combined_df = pd.concat([df[c] for c in ("value", "value_min", "value_max") if c in df.columns], ignore_index=True)
    # dropping any missing values and convert are values to float type.
    combined_df= combined_df.dropna().astype(float)
    # take data within one standard deviation of the mean
    filtered_df = combined_df[np.abs(stats.zscore(combined_df)) < 1].copy()

    mean_values = filtered_df.mean()
    std_values = filtered_df.std(ddof=0)
    return std_values / mean_values


def rock_CV():
    """Calculate the coefficient of variation (CV) for each rock type.

    Returns:
        dict: A dictionary containing the CV for each rock type.
    """
    
    # Get the coefficient of variation (CV) for each property
    property_path = os.path.join(Path(__file__).resolve().parent.parent.parent, "sorption_coefficient")
    property_file_paths = get_path_in_dir(property_path)
    yaml_property_paths = [
        fpath for fpath in property_file_paths if fpath.endswith(".yaml") and Path(fpath).parent.name != "default"
    ]

    merged_df = load_nuclide_property(yaml_property_paths)

    # take only the scalar type values
    merged_df = merged_df.loc[merged_df["type"] == "scalar"]

    rock_unqiue_lithologies = (merged_df["simplified_lithology"].explode().unique().tolist())
    dict_rock_cv = {}

    # calculate the CV for simplified lithology 
    for rock in rock_unqiue_lithologies:
        rock_mask = merged_df["simplified_lithology"].apply(lambda x: rock in x)
        rock_df = merged_df[rock_mask].copy()

        dict_rock_cv.update({rock: s_CV(rock_df)})

    # extend the CV for boarder rock types, including Marlstone and Carbonate rock.
    boarder_rock_types = list(set(merged_df["rock_type"].explode().unique().tolist()) - set(rock_unqiue_lithologies))
    for boarder_rock in boarder_rock_types:
        boarder_rock_mask = merged_df["rock_type"].apply(lambda x: boarder_rock in x)
        boarder_rock_df = merged_df[boarder_rock_mask].copy()

        dict_rock_cv.update({boarder_rock: s_CV(boarder_rock_df)})

    return dict_rock_cv
