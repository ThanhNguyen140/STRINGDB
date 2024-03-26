import os
import pandas as pd
import pytest
from stringdb.interaction_parser import InteractionParser

BASE_URL: str = "https://stringdb-downloads.org/download/"
DATA_FOLDER = "data"

expected_columns: list[str] = [
    "protein1",
    "protein2",
    "neighborhood",
    "cooccurence",
    "homology",
    "coexpression",
    "combined_score",
]

files = ["3750.protein.links.full.v12.0.txt.gz"]


class TestInteractionParser:

    @pytest.fixture
    def interaction_parser(self):
        return InteractionParser(DATA_FOLDER)

    def test_download_data(self, interaction_parser: InteractionParser):
        """Test download_data method."""
        inter = InteractionParser("../data")
        inter.download_data()
        # Check if files are created
        for file in files:
            file_path = os.path.join("../data", file)
            assert os.path.exists(file_path)

    def test_interaction_vers2(self, interaction_parser: InteractionParser):
        """Test interaction_vers2 method."""
        df = interaction_parser.interaction_vers2()
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == expected_columns
        assert len(df) == 2
