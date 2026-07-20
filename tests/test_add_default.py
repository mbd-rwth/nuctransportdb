import uuid
import numpy as np
import pandas as pd
import pytest
from nuctransportdb import add_default
from nuctransportdb.add_default import add_default_conservative_values
from nuctransportdb.add_default import add_default_df
from nuctransportdb.add_default import create_empty_sorption_pd
from nuctransportdb.add_default import find_missing_properties
from nuctransportdb.add_default import get_matching_default_df


# --------------------------------------------------------------------------- #
# Shared fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture
def empty_df():
    return create_empty_sorption_pd()


def make_default_row(rock_type, nuclide="I", value=1.0):
    # build a single-row DataFrame
    cols = create_empty_sorption_pd().columns
    row = dict.fromkeys(cols)
    row.update(
        {
            "nuclide_property": "sorption_coefficient",
            "rock_type": rock_type,
            "nuclide": nuclide,
            "source": "default",
            "type": "scalar",
            "value": value,
            "ID": str(uuid.uuid4()),
        },
    )
    return pd.DataFrame([row])

class TestFindMissingProperties:
    # find_missing_properties
    def test_empty_input_returns_all_lithologies(self, empty_df):
        missing = find_missing_properties(empty_df, ["Sandstone", "Mudstone"])
        assert set(missing) == {"Sandstone", "Mudstone"}

    def test_no_missing_when_all_present(self):
        df = pd.DataFrame(
            {
                "ID": ["id-1", "id-2"],
                "simplified_lithology": [["Sandstone"], ["Mudstone"]],
            },
        )
        missing = find_missing_properties(df, ["Sandstone", "Mudstone"])
        assert missing == []

    def test_partial_missing(self):
        df = pd.DataFrame(
            {"ID": ["id-1"], "simplified_lithology": [["Sandstone"]]},
        )
        missing = find_missing_properties(df, ["Sandstone", "Mudstone"])
        assert missing == ["Mudstone"]

    def test_rows_with_missing_id_are_ignored(self):
        df = pd.DataFrame(
            {
                "ID": [None, "id-2"],
                "simplified_lithology": [["Sandstone"], ["Mudstone"]],
            },
        )
        missing = find_missing_properties(df, ["Sandstone", "Mudstone"])
        assert missing == ["Sandstone"]


class TestAddDefaultConservativeValues:
    # add_default_conservative_values
    def test_creates_one_row_per_rock_type(self):
        result = add_default_conservative_values("I", ["Sandstone", "Mudstone"])
        assert len(result) == 2
        assert set(result["rock_type"]) == {"Sandstone", "Mudstone"}

    def test_conservative_values_are_zero(self):
        result = add_default_conservative_values("I", ["Sandstone"])
        row = result.iloc[0]
        assert row["value"] == 0.0
        assert row["value_std"] == 0.0
        assert row["source"] == "default"
        assert row["nuclide"] == "I"

    def test_ids_are_generated(self):
        result = add_default_conservative_values("I", ["Sandstone", "Mudstone"])
        assert result["ID"].notna().all()

    def test_empty_list_returns_empty_dataframe(self):
        result = add_default_conservative_values("I", [])
        assert result.empty


class TestGetMatchingDefaultDf:
    # get_matching_default_df
    def test_empty_missing_rock_names_returns_empty(self, empty_df):
        result = get_matching_default_df("I", [])
        assert result.empty

    def test_filters_by_nuclide(self, monkeypatch):
        fake_default = pd.concat(
            [make_default_row("Sandstone", nuclide="I"),
             make_default_row("Sandstone", nuclide="Cs")],
            ignore_index=True,
        )
        monkeypatch.setattr(add_default, "load_default_sorption_df", lambda liths: fake_default)
        result = get_matching_default_df("I", ["Sandstone"])
        assert (result["nuclide"] == "I").all()
        assert len(result) == 1


class TestAddDefaultDf:
    # add_default_df
    @pytest.fixture(autouse=True)
    def patch_defaults(self, monkeypatch):

        monkeypatch.setattr(add_default, "get_all_default_rock_types", lambda: ["Sandstone"])

        def fake_matching(nuclide, missing_rock_names):
            if not missing_rock_names:
                return create_empty_sorption_pd()
            rows = [make_default_row(r, nuclide=nuclide) for r in missing_rock_names]
            return pd.concat(rows, ignore_index=True)

        monkeypatch.setattr(add_default, "get_matching_default_df", fake_matching)

    def test_empty_property_df_all_defaults_available(self):
        result = add_default_df(create_empty_sorption_pd(), ["Sandstone"], "I")
        assert len(result) == 1
        assert result.iloc[0]["rock_type"] == "Sandstone"
        assert result.iloc[0]["source"] == "default"

    def test_empty_property_df_missing_default_uses_conservative(self):
        result = add_default_df(create_empty_sorption_pd(), ["Mudstone"], "I")
        assert len(result) == 1
        row = result.iloc[0]
        assert row["rock_type"] == "Mudstone"
        assert row["value"] == 0.0

    def test_mixed_available_and_missing_lithologies(self):
        result = add_default_df(create_empty_sorption_pd(), ["Sandstone", "Mudstone"], "I",
        )
        assert set(result["rock_type"]) == {"Sandstone", "Mudstone"}
        mudstone_row = result[result["rock_type"] == "Mudstone"].iloc[0]
        assert mudstone_row["value"] == 0.0

    def test_existing_data_with_missing_lithology_adds_default(self):
        existing = pd.DataFrame(
            [
                {
                    **dict.fromkeys(create_empty_sorption_pd().columns),
                    "rock_type": "Sandstone",
                    "nuclide": "I",
                    "simplified_lithology": ["Sandstone"],
                    "ID": "existing-id-1",
                    "value": 5.0,
                },
            ],
        )
        result = add_default_df(existing, ["Sandstone", "Mudstone"], "I")
        assert set(result["rock_type"]) == {"Sandstone", "Mudstone"}
        assert len(result) == 2


    def test_nan_replaced_with_none_in_output(self):
        existing = pd.DataFrame(
            [
                {
                    **dict.fromkeys(create_empty_sorption_pd().columns),
                    "rock_type": "Sandstone",
                    "nuclide": "I",
                    "simplified_lithology": ["Sandstone"],
                    "ID": "existing-id-1",
                    "value": np.nan,
                },
            ],
        )
        result = add_default_df(existing, ["Sandstone"], "I")
        assert result.iloc[0]["value"] is None
