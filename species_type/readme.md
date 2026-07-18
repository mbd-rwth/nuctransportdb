
The YAML file describes aqueous chemical speciation of 47 radionuclides (identified in [Behrens et al., 2023](https://doi.org/10.5194/adgeo-58-109-2023)) and sorted those nuclides into alkaline earth metals, transition metals and so on using [periodic‑table chemistry](https://pubchem.ncbi.nlm.nih.gov/periodic-table/) for mapping the nuclides to the two diffusivity groups defined by [Van Loon (2014)](https://doi.org/10.13140/RG.2.1.3244.9762), which follows analogue-ion diffusion data published by [Li & Gregory (1974)](https://doi.org/10.1016/0016-7037(74)90145-8).


The YAML file follows this structure:

```
nuclide:
  source: STR                       # String with BibTeX key of data source.
  species_type: STR                 # cation, anion, or mixed (redox- or pH-dependent, spanning multiple forms).
  element_category: STR             # E.g., alkaline_earth_metal, transition_metal, or lanthanide.
  description:                      # Free-text explanation of the chemical behavior and rationale for the classification.
``` 