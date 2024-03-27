from typing import Sequence, Tuple

from sqlalchemy.engine.row import Row
from stringdb.manager import Database, Protein, Interaction
from sqlalchemy.orm import Session
from sqlalchemy import Inspector, Select, select, inspect
import pytest

DATA_FOLDER = "data/stringdb.sqlite"


class TestDatabase:
    def setup_method(self):
        """Setup method to provide a Database instane as self.db"""
        self.db = Database(DATA_FOLDER)

    def test_create_database(self):
        "Test create_database method"
        self.db.create_database()
        insp: Inspector = inspect(self.db.engine)
        assert set(insp.get_table_names()) == {"protein", "interaction"}

    def test_add_data(self):
        "Test add_data method"
        self.db.add_data("data")
        session = Session(self.db.engine)
        stmt1: Select[Tuple[Protein]] = select(Protein)
        stmt2: Select[Tuple[Interaction]] = select(Interaction)
        prot: Sequence[Row[Tuple[Protein]]] = session.execute(stmt1).all()
        inter: Sequence[Row[Tuple[Interaction]]] = session.execute(stmt2).all()
        assert len(prot) == 10
        assert len(inter) == 2

    def test_filter_data(self):
        "Test filter_data method"
        result: list[dict] = self.db.filter_data(combined_score_thre=200)
        assert len(result) == 1
        dct = result[0]
        assert dct["protein_AC_1"] == "A0A097IC86"
        assert dct["protein_AC_2"] == "A0A0M3R7K5"
        assert dct["combined_score"] == 213

    def test_recreate_data(self):
        "Test recreate_database method"
        self.db.recreate_database()
        self.db.add_data("data")
        session = Session(self.db.engine)
        stmt1: Select[Tuple[Protein]] = select(Protein)
        stmt2: Select[Tuple[Interaction]] = select(Interaction)
        prot: Sequence[Row[Tuple[Protein]]] = session.execute(stmt1).all()
        inter: Sequence[Row[Tuple[Interaction]]] = session.execute(stmt2).all()
        assert len(prot) == 10
        assert len(inter) == 2

    def test_delete_database(self):
        "Test delete_database method"
        self.db.delete_database()
        insp = inspect(self.db.engine)
        assert len(insp.get_table_names()) == 0
