import os
import uuid
from importlib.resources import files
from pathlib import Path
import numpy as np
import pandas as pd
from nuclide_transport_data.generate_id import get_entry_str
from nuclide_transport_data.generate_id import ntd_namespace
from nuclide_transport_data.load_path import get_path_in_dir
from nuclide_transport_data.property2dataframe import load_nuclide_property


def get_all_default_rock_types():
    """Get all available default rock types.

    Returns:
        list: a list of default rock names.
    """
    data_path = files("nuclide_transport_data") / "dataset"
    default_property_path = os.path.join(data_path, "sorption_coefficient", "default")
    default_property_file_paths = get_path_in_dir(default_property_path)
    default_yaml_property_paths = [
        path for path in default_property_file_paths if path.endswith(".yaml")
    ]
    return [Path(p).stem for p in default_yaml_property_paths]

def load_default_sorption_df(lithologies):
    """Load default rock property DataFrame for the given lithologies.

    Args:
        lithologies (list): list of lithologies.

    Returns:
        pd.DataFrame: Default rock property DataFrame.
    """
    # load default rock property from yaml files

    data_path = files("nuclide_transport_data") / "dataset"
    add_default_yaml_list = [

        os.path.join(
            data_path,
            "sorption_coefficient",
            "default",
            f"{lithology}.yaml",
        )
        for lithology in lithologies
    ]
    default_df = load_nuclide_property(add_default_yaml_list)
    return default_df

def create_empty_sorption_pd():
    """Function for creating an empty sorption dataframe.

    Returns:
        pd.DataFrame: Empty dataframe with defined columns
    """
    columns = [
    "nuclide_property", "rock_type", "nuclide", "source", "type",
    "value", "value_min", "value_max", "value_std", "sample_size",
    "sampled_data", "unit_str", "unit_base", "variable_name",
    "variable_unit_str", "variable_unit_base", "description",
    "agency", "location", "simplified_lithology", "ID",
    ]
    return pd.DataFrame(columns=columns)

def get_matching_default_df(nuclide, missing_rock_names):
    """Get the matching default DataFrame for the given lithologies and missing properties.

    Args:
        nuclide (str): nuclide to search for.
        missing_rock_names (list): list of missing properties to find defaults for.

    Returns:
        pd.DataFrame: DataFrame containing the matching default properties
    """
    if missing_rock_names == []:
        return create_empty_sorption_pd()

    # load default rock property from yaml files
    matching_default_df = load_default_sorption_df(missing_rock_names)

    return matching_default_df[matching_default_df["nuclide"]==nuclide]


def find_missing_properties(property_df, lithologies):
    """Find missing properties in the property DataFrame.

    Args:
        property_df (pd.DataFrame): DataFrame containing the properties to check
        lithologies (list): list of lithologies to look for default properties

    Returns:
        list: List of missing property names.
    """
    required_rock_names = set(lithologies)

    if property_df.empty:
        return list(required_rock_names)
    no_id_props = list(property_df.loc[property_df["ID"].isna()]["simplified_lithology"])
    # drop the missing id properties from the original DataFrame
    removed_missing_id_property_df = property_df[
        ~property_df["simplified_lithology"].isin(no_id_props)
    ]

    # find the missing properties

    all_rocks = list(set(item for sublist in list(removed_missing_id_property_df["simplified_lithology"]) for item in sublist))

    missing_props = list(required_rock_names - set(all_rocks))
    return missing_props

def add_default_conservative_values(nuclide, props_to_load):
    """Function to add conservative estimates when no default data is available.

    Args:
        nuclide (str): nuclide to search for.
        props_to_load (list): list of rock types.

    Returns:
        pd.DataFrame: DataFrame containing the conservative estimates.
    """
    NTD_NAMESPACE = ntd_namespace()

    add_missing_default_nuclide_df = create_empty_sorption_pd()


    for rock_type in props_to_load:
        row = dict.fromkeys(add_missing_default_nuclide_df.columns)
        overwrite_row = {
        "nuclide_property": "default",
        "rock_type": rock_type,
        "nuclide": nuclide,
        "source": "default",
        "type": "scalar",
        "value": 0.0,
        "value_std": 0.0,
        "unit_str": "m^3/kg",
        "unit_base": [-1, 3, 0, 0, 0, 0, 0],
        "description": f"No default value was found for {nuclide} in {rock_type}. To avoid over-crediting retardation in the simulation, we assume this value to be zero.",
        }
        overwrite_row["ID"] = str(
                uuid.uuid5(
                    NTD_NAMESPACE, get_entry_str(row, nuclide),
                ),
            )
        row.update(overwrite_row)
        add_missing_default_nuclide_df.loc[len(add_missing_default_nuclide_df)] = row

    return add_missing_default_nuclide_df

def add_default_df(property_df, lithologies, nuclide):
    """Add default properties to the property DataFrame.

    Args:
        property_df (pd.DataFrame): DataFrame containing the properties to check.
        lithologies (list): list of lithologies to look for default properties.
        nuclide (str): nuclide to search for.

    Returns:
        pd.DataFrame: DataFrame with default properties added
    """
    all_default_rocks = get_all_default_rock_types()
    if property_df.empty:
        missing_rock_in_default = [rock for rock in lithologies if rock in all_default_rocks]
        matching_default_nuclide_df = get_matching_default_df(nuclide, missing_rock_in_default)
        missing_prop_after_matching_default = list(set(lithologies)  - set(list(matching_default_nuclide_df["rock_type"].unique())))
        add_missing_default_nuclide_df = create_empty_sorption_pd()
        if len(missing_prop_after_matching_default)>0:
            add_missing_default_nuclide_df = add_default_conservative_values(nuclide, missing_prop_after_matching_default)

        return pd.concat(
        [
            df
            for df in [matching_default_nuclide_df, add_missing_default_nuclide_df]
            if not df.empty
        ],
        ignore_index=True,
    )

    no_id_props = list(property_df.loc[property_df["ID"].isna()]["rock_type"])
    # drop the missing id properties from the original DataFrame
    removed_missing_id_property_df = property_df[
        ~property_df["rock_type"].isin(no_id_props)
    ]

    missing_prop_names = find_missing_properties(property_df, lithologies).copy()

    # check if we have the available default data

    missing_rock_in_default = [rock for rock in missing_prop_names if rock in all_default_rocks]

    if len(missing_rock_in_default)==0: # no default can be loaded
        matching_default_nuclide_df = create_empty_sorption_pd()
        missing_prop_after_matching_default = missing_prop_names.copy()
    else: # load defaults for missing_rock_in_default
        matching_default_nuclide_df = get_matching_default_df(nuclide, missing_rock_in_default)
        missing_prop_after_matching_default = list(set(missing_prop_names)  - set(list(matching_default_nuclide_df["rock_type"].unique())))

    add_missing_default_nuclide_df = create_empty_sorption_pd()


    # default dataframe is empty: 1. there is no missing data, missing_prop_names is an empty list or 2. we cannot find the data
    # default dataframe is not empty, but we still have some data missing for some rocks.
    if ((matching_default_nuclide_df.empty) and (len(missing_prop_names)>0)) or (len(missing_prop_after_matching_default)>0):

        # only load the missing props after adding available defaults
        props_to_load = missing_prop_after_matching_default.copy() if len(missing_prop_after_matching_default) > 0 else missing_prop_names.copy()
        add_missing_default_nuclide_df = add_default_conservative_values(nuclide, props_to_load)

    add_default_property_df = pd.concat(
        [
            df
            for df in [removed_missing_id_property_df, matching_default_nuclide_df, add_missing_default_nuclide_df]
            if not df.empty
        ],
        ignore_index=True,
    )
    # Replace np.nan with None
    add_default_property_df = add_default_property_df.replace({np.nan: None, "": None})

    return add_default_property_df
