from pandas import DataFrame
from stringdb.protein_parser import ProteinDatabase
import os
from .const import DATA_FOLDER, DOWNLOAD_FOLDER


links = [
    "protein.info.v12.0/3750.protein.info.v12.0.txt.gz",
    "protein.aliases.v12.0/3750.protein.aliases.v12.0.txt.gz",
]
column_names = ["string_protein_id", "uniprot_AC"]
files = ["3750.protein.info.v12.0.txt.gz", "3750.protein.aliases.v12.0.txt.gz"]


class TestProteinDatabase:

    def setup_method(self):
        """Setup method to provide a ProteinDatabase instance as self.db."""
        self.db = ProteinDatabase(DATA_FOLDER)

    def test_download_data(self):
        "Test download_data method."
        if not os.path.exists(DOWNLOAD_FOLDER):
            os.mkdir(DOWNLOAD_FOLDER)
        db = ProteinDatabase(DOWNLOAD_FOLDER)
        db.download_data()
        # check if each file is created accurately
        for file in files:
            save_path: str = os.path.join(DOWNLOAD_FOLDER, file)
            assert os.path.exists(save_path)

    def test_load_data(self):
        "Test load_data method."
        df: DataFrame = self.db.load_data()

        # check if data table created with proper column names
        assert list(df.columns) == column_names

        # check if test table contains data
        assert len(df) == 10
        assert df.duplicated().sum() == 0
