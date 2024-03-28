from neo4j import Driver, Record
from stringdb.import_Neo4j import import_data, GraphDatabase
from stringdb.manager import Database
from .const import DATA_FOLDER
import os

TEST_DB = os.path.join(DATA_FOLDER, "stringdb.sqlite")
TURTLE_PATH = os.path.join(DATA_FOLDER, "stringdb.ttl")


class TestImportNeo4j:
    def setup_method(self):
        """Initiate to create the database"""
        self.db = Database(TEST_DB)
        self.db.recreate_database()
        self.db.add_data(DATA_FOLDER)

    def test_create_ttl(self):
        """Test create_ttl function"""
        imp = import_data(TEST_DB, TURTLE_PATH)
        imp.create_ttl()
        assert os.path.exists(TURTLE_PATH) == True

    def test_to_neo4j(self):
        """Test to_neo4j function"""
        imp = import_data(TEST_DB, TURTLE_PATH)
        imp.to_neo4j(clear=True)
        URI = "neo4j://localhost:7687"
        USER = "neo4j"
        PWD = "neo4j_passwd"
        driver: Driver = GraphDatabase.driver(URI, auth=(USER, PWD))
        with driver.session() as session:
            cypher1 = "MATCH (n:interaction) RETURN count(n) AS nodeCount"
            cypher2 = "MATCH (n:Resource) RETURN count(n) AS nodeCount"
            result1: Record | None = session.run(cypher1).single()
            result2: Record | None = session.run(cypher2).single()
        total_nodes: int = result2["nodeCount"]  # type: ignore
        interaction_node: int = result1["nodeCount"]  # type: ignore
        assert total_nodes == 5
        assert interaction_node == 2

    def test_to_neo4j_filter(self):
        """Test create_ttl and to_neo4j function with filtered data"""
        imp = import_data(TEST_DB, TURTLE_PATH)
        imp.create_ttl(combined_score_thre=200)
        imp.to_neo4j(clear=True)
        URI = "neo4j://localhost:7687"
        USER = "neo4j"
        PWD = "neo4j_passwd"
        driver: Driver = GraphDatabase.driver(URI, auth=(USER, PWD))
        with driver.session() as session:
            cypher1 = "MATCH (n:interaction) RETURN count(n) AS nodeCount"
            cypher2 = "MATCH (n:Resource) RETURN count(n) AS nodeCount"
            result1: Record | None = session.run(cypher1).single()
            result2: Record | None = session.run(cypher2).single()
        total_nodes: int = result2["nodeCount"]  # type: ignore
        interaction_node: int = result1["nodeCount"]  # type: ignore
        assert total_nodes == 3
        assert interaction_node == 1
