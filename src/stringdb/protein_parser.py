import pandas as pd
from tqdm import tqdm
import os
import requests


class ProteinDatabase:
    """Provide functions to download,clean and load protein tables from StringDB"""

    def __init__(self, path):
        """Initiation of protein_database

        Args:
            path (str): Path where the data and and DB should be store
        """
        self.base_url: str = "https://stringdb-downloads.org/download/"
        self.path = path
        self.links: list[str] = [
            "protein.info.v12.0/3750.protein.info.v12.0.txt.gz",
            "protein.aliases.v12.0/3750.protein.aliases.v12.0.txt.gz",
        ]
        self.data: list[str] = [
            "3750.protein.info.v12.0.txt.gz",
            "3750.protein.aliases.v12.0.txt.gz",
        ]

    def download_data(self):
        for link in tqdm(self.links):
            url: str = self.base_url + link
            file_name: str = os.path.basename(p=url)
            save_path: str = os.path.join(self.path, file_name)
            if not os.path.exists(path=save_path):
                resp = requests.get(url=url)
                with open(file=save_path, mode="wb") as f:
                    f.write(resp.content)

    def load_data(self) -> pd.DataFrame:
        """Load data and process the data

        Args:
            test (bool, optional): If True, only 100 rows of each data file is used. Defaults to False.

        Returns:
            DataFrame: Final protein data frame
        """
        df_list: list[pd.DataFrame] = []
        for file in tqdm(self.data):
            f: str = os.path.join(self.path, file)
            df: pd.DataFrame = pd.read_csv(f, sep="\t").rename(
                columns={"#string_protein_id": "string_protein_id"}
            )
            df_list.append(df)
        uniprot_alias: pd.DataFrame = df_list[1][
            df_list[1].source.str.contains("UniProt_AC")
        ].reset_index()
        uniprot_alias = uniprot_alias.drop(["source"], axis=1)

        protein = df_list[0]
        protein_merge: pd.DataFrame = pd.merge(
            protein, uniprot_alias, how="inner", on="string_protein_id"
        )
        protein_merge = protein_merge.rename(columns={"alias": "uniprot_AC"})
        protein_merge = protein_merge.drop(["index"], axis=1)
        protein_merge.index.name = "id"
        protein_merge.index += 1

        return protein_merge[["string_protein_id", "uniprot_AC"]]
