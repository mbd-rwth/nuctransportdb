We compiled the emitted energy data for a selected set of 47 nuclides, identified in [Behrens et al., 2023](https://doi.org/10.5194/adgeo-58-109-2023) as the most relevant inventory of nuclear waste. The energy emitted per nuclear transformation were extracted from the [ICRP (2008)]( https://doi.org/10.1016/j.icrp.2008.10.004) nuclear decay database. 

The YAML file follows this structure:

```
nuclide:
  source: STR                       # String with BibTeX key of data source.
  alpha: VAL                        # Energy emitted per transformation via alpha decay.
  electron: VAL                     # Energy emitted per transformation via electron emission.
  photon: VAL                       # Energy emitted per transformation via photon emission.
  total: VAL                        # Total energy emitted per transformation including the contribution of ﬁssion fragments and neutrons associated with spontaneous ﬁssion.
  unit_str: STR                     # Human-readable string indicating the unit.
  unit_base: LIST(INT)              # An array of the form [ kg m s K A mol cd ] that gives the unit as the exponent of the SI basis units, e.g., m/s^2 is [0, 1, -2, 0, 0, 0, 0].
``` 