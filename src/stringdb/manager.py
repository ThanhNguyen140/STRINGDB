from typing import Tuple
from pandas import DataFrame
from sqlalchemy import Engine, Result, Row, Select, select
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from stringdb.protein_parser import ProteinDatabase as pdb
from stringdb.interaction_parser import InteractionParser
from stringdb.model import Base, Interaction, Protein


class Database:
    def __init__(self, path_to_files: str):
        """

        Args:
            path_to_files (str): Path to .sqlite or .db file
        """
        self.engine: Engine = create_engine(f"sqlite:///{path_to_files}", echo=True)

    def create_database(self):
        """Create an empty database"""
        Base.metadata.create_all(self.engine)

    def delete_database(self):
        """Delete available database"""
        Base.metadata.drop_all(self.engine)

    def recreate_database(self):
        """Recreate database if it is already available"""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def add_data(self, path: str):
        """Add data to database

        Args:
            path (str):Path to the data folder where interactions and protein data of stringdb
            are available
        """
        p = pdb(path)
        protein_df: DataFrame = p.load_data()
        inter = InteractionParser(path)
        int_df: DataFrame = inter.interaction_vers2()
        with Session(bind=self.engine) as session:
            for _, data in protein_df.iterrows():
                data_dict = dict(data)
                session.add(Protein(**data_dict))
            for _, data in int_df.iterrows():
                protein_1: Protein | None = (
                    session.query(Protein)
                    .filter_by(string_protein_id=data.protein1)
                    .first()
                )
                protein_2: Protein | None = (
                    session.query(Protein)
                    .filter_by(string_protein_id=data.protein2)
                    .first()
                )
                if protein_1 and protein_2:
                    interaction = Interaction(
                        neighborhood=data.neighborhood,
                        cooccurence=data.cooccurence,
                        homology=data.homology,
                        coexpression=data.coexpression,
                        combined_score=data.combined_score,
                        protein1=protein_1.id,
                        protein2=protein_2.id,
                    )
                    session.add(interaction)
            session.commit()

    def filter_data(
        self,
        homology_thre: int = 0,
        cooccurence_thre: int = 0,
        coexpression_thre: int = 0,
        neighborhood_thre: int = 0,
        combined_score_thre: int = 0,
    ) -> list[dict]:
        """Filter interaction table in SQL database based on certain thresholds

        Args:
            homology_thre (int, optional): _description_. Defaults to 0.
            cooccurence_thre (int, optional): _description_. Defaults to 0.
            coexpression_thre (int, optional): _description_. Defaults to 0.
            neighborhood_thre (int, optional): _description_. Defaults to 0.
            combined_score_thre (int, optional): _description_. Defaults to 0.

        Returns:
            list[dict]: _description_
        """
        results: list[dict] = []
        session = Session(self.engine)
        stmt1: Select[Tuple[Interaction]] = (
            select(Interaction)
            .where(Interaction.combined_score >= combined_score_thre)
            .where(Interaction.homology >= homology_thre)
            .where(Interaction.coexpression >= coexpression_thre)
            .where(Interaction.cooccurence >= cooccurence_thre)
            .where(Interaction.neighborhood >= neighborhood_thre)
        )
        interaction: Result[Tuple[Interaction]] = session.execute(stmt1).all()
        for row in interaction:

            dct = {}
            dct["interaction_id"] = row.Interaction.id
            dct["coexpression"] = row.Interaction.coexpression
            dct["neighborhood"] = row.Interaction.neighborhood
            dct["cooccurence"] = row.Interaction.cooccurence
            dct["homology"] = row.Interaction.homology
            dct["combined_score"] = row.Interaction.combined_score
            stmt2: Select[Tuple[str]] = select(Protein.uniprot_AC).where(
                Protein.id == row.Interaction.protein1
            )
            protein_AC_1: Row[Tuple[str]] = session.execute(stmt2).one()
            stmt3: Select[Tuple[str]] = select(Protein.uniprot_AC).where(
                Protein.id == row.Interaction.protein2
            )
            protein_AC_2: Row[Tuple[str]] = session.execute(stmt3).one()
            dct["protein_AC_1"] = protein_AC_1[0]
            dct["protein_AC_2"] = protein_AC_2[0]

            results.append(dct)

        return results
