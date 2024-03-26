from stringdb.protein_parser import protein_database as pdb
import pytest
import os

DATA_FOLDER = "data"
links = [
    "protein.info.v12.0/3750.protein.info.v12.0.txt.gz",
    "protein.aliases.v12.0/3750.protein.aliases.v12.0.txt.gz",
]
column_names = ["string_protein_id", "uniprot_AC"]
files = ["3750.protein.info.v12.0.txt.gz", "3750.protein.aliases.v12.0.txt.gz"]


class TestProteinDatabase:
    def setup_method(self):
        """Setup method to provide a pdb instane as self.db"""
        self.db = pdb(DATA_FOLDER)

    def test_download_data(self):
        data = "../data"
        db = pdb(data)
        db.download_data()
        # check if each file is created accurately
        for file in files:
            save_path: str = os.path.join(data, file)
            assert os.path.exists(save_path)

    def test_load_data(self):
        df: DataFrame = self.db.load_data()

        # check if data table created with proper column names
        assert list(df.columns) == column_names

        # check if test table contains data
        assert len(df) == 10
        assert df.duplicated().sum() == 0
