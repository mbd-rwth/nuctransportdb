import pandas as pd
import pytest
from nuctransportdb.data_tagging import filter_tagged_data


class TestFilterTaggedData:
    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame(
            {
                "nuclide": ["I", "I", "Cs", "I"],
                "simplified_lithology": [
                    ["Mudstone"],
                    ["Sandstone"],
                    ["Limestone"],
                    ["Shale"],
                ],
                "agency": [["NAGRA"], ["ANDRA"], ["NAGRA"], ["ANDRA"]],
            },
        )

    def test_single_tag_type_filters_correctly(self, sample_df):
        result = filter_tagged_data(
            sample_df, {"simplified_lithology": ["Mudstone", "Sandstone"]},
        )
        assert set(result.index) == {0, 1}

    def test_multiple_tag_types_are_and_combined(self, sample_df):
        result = filter_tagged_data(
            sample_df,
            {
                "simplified_lithology": ["Mudstone", "Sandstone", "Limestone"],
                "agency": ["NAGRA"],
            },
        )
        # Only rows matching lithology AND agency should remain
        assert set(result.index) == {0, 2}

    def test_empty_tag_dict_returns_all_rows(self, sample_df):
        result = filter_tagged_data(sample_df, {})
        pd.testing.assert_frame_equal(result, sample_df)

    def test_no_match_returns_empty_dataframe(self, sample_df):
        result = filter_tagged_data(sample_df, {"simplified_lithology": ["Granite"]})
        assert result.empty

    def test_preserves_columns(self, sample_df):
        result = filter_tagged_data(sample_df, {"agency": ["NAGRA"]})
        assert list(result.columns) == list(sample_df.columns)

    def test_result_is_subset_of_original(self, sample_df):
        result = filter_tagged_data(sample_df, {"agency": ["ANDRA"]})
        assert result.index.isin(sample_df.index).all()
