import os
from importlib.resources import files
import numpy as np
import pandas as pd
import yaml
from nuclide_transport_data.load_path import get_path_in_dir


def preserve_value_type(value):
    """Preserve the original type of the value.

    Args:
        value (float, str, None): The input value to preserve.

    Returns:
        float, str, None: The preserved value.
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return value


def load_nuclide_property(yaml_property_paths):
    """Load nuclide properties from YAML files to a DataFrame.

    Args:
        yaml_property_paths (list): a list of paths to YAML files containing nuclide properties.

    Returns:
        pd.DataFrame: a DataFrame containing the loaded nuclide properties.
    """
    # load property files to DataFrame
    records = []
    for filepath in yaml_property_paths:
        # save nuclide property name
        nuclide_property = os.path.dirname(filepath).split("/")[-1]
        # save rock type name
        rock_type = os.path.splitext(os.path.basename(filepath))[0]

        # Load YAML file
        with open(filepath, encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)

        # Iterate over each top-level property
        for nuclide, entries in yaml_data.items():
            for entry in entries:
                property_entry = {"nuclide_property": nuclide_property}
                property_entry["rock_type"] = rock_type
                property_entry["nuclide"] = nuclide

                for key, value in entry.items():
                    if key == "probability_distribution":
                        pdf_data = value or {}
                        property_entry["sample_size"] = pdf_data.get("sample_size")
                        property_entry["sampled_data"] = pdf_data.get("sampled_data")
                    elif key == "tag":
                        tag_data = value or {}
                        if rock_type != "default":
                            property_entry["agency"] = tag_data.get("agency")

                            property_entry["location"] = tag_data.get("location")

                            property_entry["simplified_lithology"] = tag_data.get(
                                "simplified_lithology",
                            )
                        property_entry["ID"] = tag_data.get("ID")
                    else:
                        property_entry[key] = value

                records.append(property_entry)

    # Create the DataFrame for properties
    property_df = pd.DataFrame(records)
    # Preserve float for scalar and string for expression and dictionary
    property_df[["value", "value_min", "value_max", "value_std"]] = property_df[
        ["value", "value_min", "value_max", "value_std"]
    ].map(preserve_value_type)
    # Keep the sample_size as integer
    property_df["sample_size"] = pd.to_numeric(
        property_df["sample_size"], errors="coerce",
    ).astype("Int64")
    # Convert list to numpy array
    property_df["sampled_data"] = property_df["sampled_data"].map(
        lambda sampled_data: (
            np.array(sampled_data, dtype=np.float64)
            if isinstance(sampled_data, list)
            else sampled_data
        ),
    )
    # Replace np.nan with None
    property_df = property_df.replace({np.nan: None})
    return property_df

def load_nuclide_sorption_data():
    """Load collected sorption data.

    Returns:
        pd.dataframe: panda dataframe contains all collected sorption data.
    """
    # load YAML file paths from the rock_property directory
    data_path = files("nuclide_transport_data") / "dataset"
    property_path = os.path.join(data_path, "sorption_coefficient")
    property_file_paths = get_path_in_dir(property_path)
    yaml_property_paths = [
        path for path in property_file_paths if path.endswith(".yaml")
    ]

    # remove the YAML file paths in default directory
    real_path = os.path.realpath(os.path.dirname(__file__))
    default_path = os.path.realpath(
        os.path.join(
            real_path,
            os.path.join(os.path.join(data_path, "sorption_coefficient", "default")),
        ),
    )
    yaml_rock_property_paths = [
        path for path in yaml_property_paths if default_path not in path
    ]
    rock_sorption_coefficient = load_nuclide_property(yaml_rock_property_paths)
    return rock_sorption_coefficient
