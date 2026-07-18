import os
from importlib.resources import files
import astropy.units as u
import numpy as np
import pandas as pd
import yaml
from nuclide_transport_data.add_default import add_default_df
from nuclide_transport_data.data_tagging import filter_tagged_data
from nuclide_transport_data.dataframe2yaml import convert_to_flow_sequence
from nuclide_transport_data.dataframe2yaml import export2yaml
from nuclide_transport_data.merge_method import merge_property_value
from nuclide_transport_data.property2dataframe import load_nuclide_sorption_data


def load_all_emitted_energy():
    data_path = files("nuclide_transport_data") / "dataset"
    path_to_yaml = os.path.join(data_path, "emitted_energy", "emitted_energy.yaml")
    with open(path_to_yaml, encoding="utf-8") as f:
        yaml_config = yaml.safe_load(f)

    return yaml_config

def load_all_species_type_data():
    data_path = files("nuclide_transport_data") / "dataset"
    path_to_yaml = os.path.join(data_path,"species_type", "species_type.yaml")
    with open(path_to_yaml, encoding="utf-8") as f:
        yaml_config = yaml.safe_load(f)

    return yaml_config

def export_species_data(input_config):
    all_species_type_data = load_all_species_type_data()
    nuclides_list = input_config["nuclide_to_consider"]


    slow_categories = ["alkaline_earth_metal","transition_metal","lanthanide","actinide"]
    fast_element = ["Cl", "Br", "I", "K", "Cs", "Ag", "H"]

    species_type = {}
    diffusion_group = {}
    for nuclide in nuclides_list:
        info = all_species_type_data.get(nuclide)
        if info is None:
            species_type[nuclide] = {"value": None}
            diffusion_group[nuclide] = {"value": "fast"}
            continue

        species_type[nuclide] = {"value": info.get("species_type")}

        category = (info.get("element_category") or "").lower()

        element = nuclide.partition("-")[0]

        if category in slow_categories:
            diffusion_group[nuclide] = {"value": "slow"}
        elif element in fast_element:
            diffusion_group[nuclide] = {"value": "fast"}
        else: # Unclassified nuclided treated as fast per your rule
            diffusion_group[nuclide] = {"value": "fast"}

    path_to_save_nuclide_species_data = input_config["path_to_save_nuclide_species_data"]
    if not os.path.exists(path_to_save_nuclide_species_data):
        os.makedirs(path_to_save_nuclide_species_data)

    with open(os.path.join(path_to_save_nuclide_species_data, "species_type.yaml"), "w") as f:
        yaml.safe_dump(species_type, f, sort_keys=False)

    with open(os.path.join(path_to_save_nuclide_species_data, "diffusion_group.yaml"), "w") as f:
        yaml.safe_dump(diffusion_group, f, sort_keys=False)

def export_nuclide_emitted_energy(input_config):
    all_emitted_energy = load_all_emitted_energy()
    nuclides_list = input_config["nuclide_to_consider"]
    nuclide_emitted_energy = {}
    for nuclide in nuclides_list:
        info = all_emitted_energy.get(nuclide)
        if info is None:
            nuclide_emitted_energy[nuclide] = {"source": None,
                                                "alpha": 0.0,
                                                "electron": 0.0,
                                                "photon": 0.0,
                                                "total": 0.0,
                                                "unit_str": "kg*m^3/s^2",
                                                "unit_base": convert_to_flow_sequence([1, 2, -2, 0, 0, 0, 0])}
            continue

        nuclide_emitted_energy[nuclide] = {"source": info["source"],
                                            "alpha": float((info["alpha"] * u.MeV).to(u.J).value),
                                            "electron": float((info["electron"] * u.MeV).to(u.J).value),
                                            "photon": float((info["photon"] * u.MeV).to(u.J).value),
                                            "total": float((info["total"] * u.MeV).to(u.J).value),
                                            "unit_str": "kg*m^3/s^2",
                                            "unit_base": convert_to_flow_sequence([1, 2, -2, 0, 0, 0, 0])}


    path_to_save_nuclide_emitted_energy_data = input_config["path_to_save_nuclide_emitted_energy_data"]
    if not os.path.exists(path_to_save_nuclide_emitted_energy_data):
        os.makedirs(path_to_save_nuclide_emitted_energy_data)

    with open(os.path.join(path_to_save_nuclide_emitted_energy_data, "emitted_energy.yaml"), "w") as f:
        yaml.safe_dump(nuclide_emitted_energy, f, sort_keys=False)


def export_sorption_data_for_site(input_config):
    with open(input_config["input_site_yaml_path"], encoding="utf-8") as f:
        yaml_config = yaml.safe_load(f)
    yaml_config.pop("name", None)
    yaml_config.pop("description", None)

    nuclides_list = input_config["nuclide_to_consider"]

    for rock_unit, rock_infos in yaml_config.items():

        tag_dict = {"simplified_lithology": rock_infos["simplified_lithology"]}

        mdfnsds = []
        for nuclide in nuclides_list:
            element = nuclide.partition("-")[0]
            # load all sorption data for all nuclides
            nsd = load_nuclide_sorption_data()
            # filter data with simplified lithologies
            fnsd = filter_tagged_data(nsd, tag_dict)
            fnsd = fnsd[fnsd["nuclide"]==element]

            # add default data based on the litholgies for the merged rock unit
            dfnsd = add_default_df(fnsd, tag_dict["simplified_lithology"], nuclide=element)
            # Fill none simplified_lithology with rock_type
            dfnsd["simplified_lithology"] = dfnsd["simplified_lithology"].fillna(
                dfnsd["rock_type"],
            )
            # make sure all properties are sorption_coefficient
            dfnsd["nuclide_property"] = "sorption_coefficient"
            dfnsd["nuclide"] = nuclide

            mdfnsd = merge_property_value(dfnsd, source_type="merged")
            mdfnsds.append(mdfnsd)

        result = pd.concat(mdfnsds, ignore_index=True)

        # Replace np.nan with None
        result = result.replace({np.nan: None, "": None})

        # save the sorption data for the specific rock unit
        path_to_save_sorption_data = input_config["path_to_save_sorption_data"]
        if not os.path.exists(path_to_save_sorption_data):
            os.makedirs(path_to_save_sorption_data)
        export2yaml(result, f"{path_to_save_sorption_data}/{rock_unit}.yaml")
