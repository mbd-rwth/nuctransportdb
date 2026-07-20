import pytest
from nuctransportdb.merge_method import value_empty_mask
from nuctransportdb.merge_method import value_invalid_mask
from nuctransportdb.property2dataframe import load_nuclide_sorption_data


@pytest.fixture(scope="module")
def merged_df():
    # Load the all properties into a DataFrame
    return load_nuclide_sorption_data()

@pytest.fixture(scope="module")
def sourced_property_df(merged_df):
    # drop empty data entry
    return merged_df.dropna(subset=["source"]).copy()


def test_sourced_properties_do_not_have_empty_values(sourced_property_df):
    # --- Check if there are empty data with a valid source ---#
    empty_mask = value_empty_mask(sourced_property_df)
    assert sourced_property_df[
        empty_mask
    ].empty, f"Rows with missing data:\n{sourced_property_df[empty_mask]}"


def test_sourced_properties_do_not_have_invalid_values(sourced_property_df):
    # --- check if the value entry is valid ---#
    is_invalid_mask = value_invalid_mask(sourced_property_df)
    assert sourced_property_df[
        is_invalid_mask
    ].empty, f"Rows with invalid entries:\n{sourced_property_df[is_invalid_mask]}"
