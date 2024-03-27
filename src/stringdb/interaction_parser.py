import pandas as pd
from tqdm import tqdm
import os
import requests
from typing import Literal


class InteractionParser:
    """A class for downloading, loading, and saving data related to protein interactions."""

    BASE_URL: str = "https://stringdb-downloads.org/download/"

    def __init__(self, path):
        """
        Initializes the InteractionParser object.

        Creates the data folder if it doesn't exist and sets up data links and desired columns.
        """
        self.DATA_FOLDER = path
        if not os.path.exists(self.DATA_FOLDER):
            os.makedirs(self.DATA_FOLDER)

        self.data_links: dict[Literal["interaction", "accessory"], tuple[str, ...]] = {
            "interaction": (
                "protein.links.full.v12.0/3750.protein.links.full.v12.0.txt.gz",
            )
        }
        self.desired_columns = [
            "protein1",
            "protein2",
            "neighborhood",
            "cooccurence",
            "homology",
            "coexpression",
            "combined_score",
        ]

    def download_data(self):
        """
        Downloads specified data files from the provided links.

        Downloads data files based on the links specified in the data_links attribute.
        Saves the files to the DATA_FOLDER directory.
        """
        for _, links in self.data_links.items():
            for link in links:
                url: str = f"{self.BASE_URL}{link}"
                response: requests.Response = requests.get(url, stream=True)

                file_name: str = os.path.basename(link)
                file_path: str = os.path.join(self.DATA_FOLDER, file_name)

                with open(file_path, "wb") as file:
                    for chunk in tqdm(response.iter_content(chunk_size=1024)):
                        if chunk:
                            file.write(chunk)

    def interaction_vers2(self) -> pd.DataFrame:
        """
        Enhances interaction data with additional protein information.

        Merges the interaction data with protein information from the accessory data file.
        Returns the merged DataFrame.
        """

        file_name_interaction: str = os.path.basename(self.data_links["interaction"][0])
        path_interaction: str = os.path.join(self.DATA_FOLDER, file_name_interaction)
        interaction1: pd.DataFrame = pd.read_csv(
            path_interaction, sep=" ", usecols=self.desired_columns, low_memory=True
        )
        cols: list[str] = [
            "neighborhood",
            "cooccurence",
            "homology",
            "coexpression",
            "combined_score",
        ]
        interaction1: pd.DataFrame = interaction1.drop_duplicates(subset=cols)
        interaction1.index += 1
        interaction1.index.name = "id"
        return interaction1
