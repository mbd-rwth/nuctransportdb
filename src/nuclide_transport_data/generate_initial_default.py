from pathlib import Path
from nuclide_transport_data.merge_method import merge_property_value
from nuclide_transport_data.dataframe2yaml import export2yaml
from nuclide_transport_data.property2dataframe import load_nuclide_property
from nuclide_transport_data.load_path import get_path_in_dir

def generate_initial_default(property_dir, output_dir):
    """
    Generate the initial default data for nuclide properties

    Args:
        property_dir (str): The path to the property directory.
        output_dir (str): The path to the output directory for saving YAML files.   
    """

    property_file_paths = get_path_in_dir(property_dir)
    yaml_property_paths = [
        fpath for fpath in property_file_paths if fpath.endswith(".yaml") and Path(fpath).parent.name != "default"
    ]

    merged_df = load_nuclide_property(yaml_property_paths)
    # Get a unqiue rock type list
    rock_unqiue_lithologies = (
        merged_df["simplified_lithology"].explode().unique().tolist()
    )

    for rock in rock_unqiue_lithologies:
        # get the data for the current rock type
        rock_mask = merged_df["simplified_lithology"].apply(lambda x: rock in x)
        rock_df = merged_df[rock_mask].copy()


        input_df_for_merging = rock_df.drop_duplicates(subset=["ID"])

        merged_property_df = merge_property_value(
            input_df_for_merging, source_type="default"
        )
        # Only maintainers can save the generated data to YAML files.
        save_to_file = True

        if save_to_file:
            export2yaml(
                merged_property_df,
                output_file_path=f"{output_dir}/{rock}.yaml",
            )
