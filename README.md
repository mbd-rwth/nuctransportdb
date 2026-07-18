## Nuclide Transport Data
[![github repo badge](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue)](https://github.com/CQ-QianChen/nuclide_transport_data) [![github license badge](https://img.shields.io/github/license/CQ-QianChen/nuclide_transport_data)](https://github.com/CQ-QianChen/nuclide_transport_data) [![Documentation Status](https://readthedocs.org/projects/nuclide_transport_data/badge/?version=latest)](https://nuclide_transport_data.readthedocs.io/en/latest/?badge=latest) [![build](https://github.com/CQ-QianChen/nuclide_transport_data/actions/workflows/build.yml/badge.svg)](https://github.com/CQ-QianChen/nuclide_transport_data/actions/workflows/build.yml) [![cffconvert](https://github.com/CQ-QianChen/nuclide_transport_data/actions/workflows/cffconvert.yml/badge.svg)](https://github.com/CQ-QianChen/nuclide_transport_data/actions/workflows/cffconvert.yml) [![link-check](https://github.com/CQ-QianChen/nuclide_transport_data/actions/workflows/link-check.yml/badge.svg)](https://github.com/CQ-QianChen/nuclide_transport_data/actions/workflows/link-check.yml)




A simulation-ready database for radionuclide transport simulations, providing emitted energy data for a selected set of nuclides, sorption coefficient cross rock types, and chemical-species data.

## Installation

To install nuclide_transport_data from GitHub repository, do:

```console
git clone git@github.com:CQ-QianChen/nuclide_transport_data.git
cd nuclide_transport_data
python -m pip install .
```

## Exporting Nuclide Data

Use [export_data.py](./src/nuclide_transport_data/export_data.py) to extract nuclide data for a specific candidate site and defined model setup. The script reads a YAML configuration file that specifies which nuclides to extract, along with optional output paths for the different data types.

### Configuration file format 

| Field | Description |
|---|---|
| `nuclide_to_consider` | List of nuclides to extract (e.g., `I-129`). |
| `site_name` | Name of the disposal site. |
| `site_scenario_name` | Name of the specific site scenario. |
| `input_site_yaml_path` | Path to a custom site YAML file. | 
| `path_to_save_sorption_data` | Output directory for sorption coefficient data. | 
| `path_to_save_nuclide_species_data` | Output directory for nuclide species data. | 
| `path_to_save_nuclide_emitted_energy_data` | Output directory for emitted energy data. |

#### example:
```yaml
nuclide_to_consider:
  - I-129

site_name: DE_South_Claystone
site_scenario_name: DE_South_Claystone_Germany


Path to a site-specific YAML file defining site properties.
If omitted, defaults to the built-in site data.
input_site_yaml_path: input/site_data/DE_South_Claystone_Germany/DE_South_Claystone.yaml

Directory to save the exported sorption coefficient data.
path_to_save_sorption_data: output/DE_South_Claystone_Germany/sorption_data

Directory to save the exported nuclide species data.
path_to_save_nuclide_species_data: output/DE_South_Claystone_Germany/nuclide_data

Directory to save the exported nuclide emitted energy data.
path_to_save_nuclide_emitted_energy_data: output/DE_South_Claystone_Germany/nuclide_data
```

### Running the script

```bash
python export_data.py --config path/to/your_config.yaml
```

## Documentation

[see our readthedocs](https://nuclide-transport-data.readthedocs.io/en/latest/)

## Contributing

If you want to contribute to the development of nuclide_transport_data,
have a look at the [contribution guidelines](CONTRIBUTING.md).

## Credits
The code in `src/` is developed based on and heavily relies on source code from
[mbd-rwth/smart_data_hub](https://github.com/mbd-rwth/smart_data_hub).
The authors of this project is [@CQ-QianChen](https://github.com/CQ-QianChen).
