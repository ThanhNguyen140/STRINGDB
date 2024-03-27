from rdflib import Graph, URIRef, Literal, Namespace, RDF, XSD
from rdflib_neo4j import Neo4jStore, HANDLE_VOCAB_URI_STRATEGY, Neo4jStoreConfig
from neo4j import GraphDatabase
import os
from stringdb.manager import Database


class Graph_for_ttl:
    """Create graph and name space for turtle file"""

    def __init__(self):
        """Create name space for the graph"""
        self.stringdb_ns = Namespace("https://plab2.bit.uni-bonn.de/stringdb#")
        self.node = Namespace("https://plab2.bit.uni-bonn.de/stringdb/node#")
        self.uniprot_ns = Namespace("http://purl.uniprot.org/uniprot/")
        self.relation = Namespace("https://plab2.bit.uni-bonn.de/stringdb/relation#")

    def get_empty_graph(self):
        """Return an empty RDFlib.Graph with all needed namespaces"""
        self.graph = Graph()
        self.graph.bind("stringdb", self.stringdb_ns)
        self.graph.bind("node", self.node)
        self.graph.bind("relation", self.relation)
        self.graph.bind("xs", XSD)
        self.graph.bind("uniprot", self.uniprot_ns)
        return self.graph


class import_data:
    """Import data into SQL database"""

    def __init__(self, path_to_db: str, path_to_ttl: str):
        """

        Args:
            path_to_db (str): path to SQL database
            path_to_ttl (str): path to turtle file. It ends with ttl

        Raises:
            FileNotFoundError: raise error if path to SQL database is not found
        """
        self.path_to_db: str = path_to_db
        self.path_to_ttl: str = path_to_ttl
        if not os.path.exists(self.path_to_db):
            raise FileNotFoundError

    def create_ttl(
        self,
        homology_thre: int = 0,
        cooccurence_thre: int = 0,
        coexpression_thre: int = 0,
        neighborhood_thre: int = 0,
        combined_score_thre: int = 0,
    ):
        """Create tuttle file based on threshold values in interaction table

        Args:
            homology_thre (int, optional): Homology score. Defaults to 0.
            cooccurence_thre (int, optional): Cooccurence score. Defaults to 0.
            coexpression_thre (int, optional): Coexpression score. Defaults to 0.
            neighborhood_thre (int, optional): Neighborhood score. Defaults to 0.
            combined_score_thre (int, optional): Combined score. Defaults to 0.
        """
        g = Graph_for_ttl()
        graph = g.get_empty_graph()
        database = Database(self.path_to_db)
        data_list = database.filter_data(
            homology_thre,
            cooccurence_thre,
            coexpression_thre,
            neighborhood_thre,
            combined_score_thre,
        )

        for dct in data_list:

            protein_1 = URIRef(g.uniprot_ns[dct["protein_AC_1"]])
            protein_2 = URIRef(g.uniprot_ns[dct["protein_AC_2"]])

            idx = dct["interaction_id"]
            interaction_node = URIRef(g.relation[f"id_{idx}"])

            graph.add((interaction_node, RDF.type, g.node["interaction"]))
            graph.add(
                (
                    interaction_node,
                    g.relation["identifier"],
                    Literal(idx, datatype=XSD.integer),
                )
            )
            graph.add((protein_1, g.relation["interact"], interaction_node))
            graph.add((interaction_node, g.relation["interact"], protein_2))
            for column in [
                "homology",
                "coexpression",
                "neighborhood",
                "cooccurence",
                "combined_score",
            ]:
                value: int = dct[column]
                graph.add(
                    (
                        interaction_node,
                        g.relation[column],
                        Literal(value, datatype=XSD.integer),
                    )
                )

        graph.serialize(self.path_to_ttl, format="turtle")
        del graph
        print("Finished creating ttl files")

    def to_neo4j(self, clear=False):
        """Create graphs in Neo4j

        Args:
            clear (bool, optional): Clear previous data in Neo4j. Defaults to False.
        """
        URI = "neo4j://localhost:7687"
        USER = "neo4j"
        PWD = "neo4j_passwd"
        driver = GraphDatabase.driver(URI, auth=(USER, PWD))

        if clear:
            with driver.session() as session:
                cypher = "DROP CONSTRAINT n10s_unique_uri IF EXISTS"
                session.run(cypher)
                cypher = "MATCH (n) CALL { WITH n DETACH DELETE n} IN TRANSACTIONS OF 50000 ROWS"
                session.run(cypher)
                cypher = "MATCH (n) DELETE n"
                session.run(cypher)
        with driver.session() as session:
            cypher = "CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS  FOR (r:Resource) REQUIRE r.uri IS UNIQUE"
            session.run(cypher)

        auth_data = {"uri": URI, "database": "neo4j", "user": USER, "pwd": PWD}

        config = Neo4jStoreConfig(
            auth_data=auth_data,
            custom_prefixes={},
            handle_vocab_uri_strategy=HANDLE_VOCAB_URI_STRATEGY.IGNORE,
            batching=True,
        )

        neo4j_db = Graph(store=Neo4jStore(config=config))
        # Calling the parse method will implictly open the store
        neo4j_db.parse(self.path_to_ttl, format="ttl")
        neo4j_db.close(True)
