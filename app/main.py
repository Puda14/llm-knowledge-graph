from neo4j import GraphDatabase
import os

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

def test_neo4j_connection():
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful' AS message")
            for record in result:
                print(record["message"])
    except Exception as e:
        print("Connection failed:", e)
    finally:
        driver.close()

if __name__ == "__main__":
    test_neo4j_connection()