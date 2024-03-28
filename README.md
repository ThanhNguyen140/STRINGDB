# STRINGDB

Table of content:
- [STRINGDB](#stringdb)
    - [1. Goal](#1-goal)
    - [2. Objective](#2-objective)
    - [3. Cleaning data](#3-cleaning-data)
    - [4. Manage database](#4-manage-database)
    - [5. Import data to Neo4j](#5-import-data-to-neo4j)
    - [6. Data](#6-data)
    - [7. Test](#7-test)
    - [8. Results](#8-results)

### 1. Goal
This project is created to deal with StringDB database, creating a database to work with Malus Domestica. The information of the created database was retrieved from StringDB interaction table. 

### 2. Objective
- Clean data
- Filter for UniProt_AC of each protein
- Get interaction table with homology, cooccurence, coexpression, neighborhood, combined_score columns
- Create SQL database with sqlalchemy package
- Create turtle file and import data into Neo4j
### 3. Cleaning data
- Protein table: processed by [protein_parser.py](src/stringdb/protein_parser.py). 
    1. The script helps download the data.
    2.  The protein table is merged with alias table from StringDB. The alias table provides the entry to other databases. In this project, link to Uniprot database is interesting to keep. The protein table is merged with alias with only UniProt_AC. 
    3.  The protein table is then saved in SQL database with name "protein" by [manager.py](src/stringdb/manager.py)
- Interaction table: processed by [interaction_parser.py](src/stringdb/interaction_parser.py)
    1. The script downloads data
    2. The interaction table is filtered for certain columns including string_protein_id of 2 proteins, homology, cooccurence, coexpression, neighborhood, combined_score columns
    3. The interaction table is also filtered for any duplicates if the pair of proteins is repeated
    4. The table is imported to database by [manager.py](src/stringdb/manager.py)
- There are no NaN values in the StringDB tables

### 4. Manage database
- Done by [manage.py](src/stringdb/manager.py)
- Load data in the folder where StringDB files are downloaded
- Clean data by using interaction_parser and protein_parser scripts
- Load data into SQL database
- Allow the filtering of interaction table in SQL database by threshold values

### 5. Import data to Neo4j
- Done by [import_Neo4j.py](src/stringdb/import_Neo4j.py)
- Create ttl file from .sqlite or .db databases containing protein and interaction tables
- Import ttl file to Neo4j

### 6. [Data](data)

### 7. [Test](tests)
- Including interaction_parser_test.py, manager_test.py, import_neo4j_test.py and protein_parser_test.py
- [data](tests/data/): containing data for the test scripts

### 8. Results
- .sqlite file can be created by sqlalchemy
- Allow the filter of interaction table for certain value threshold
- Graph is successfully created in Neo4j
- The graph is ready to be integrated with Uniprot database via the URI of Uniprot_AC  


