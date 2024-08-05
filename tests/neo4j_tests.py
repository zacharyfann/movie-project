import os
from langchain_community.graphs import Neo4jGraph
def test_neo4J_connection():
    result = {"message":"Starting test"}
    try:
        print(os.getenv("NEO4J_URI"))
        print(os.getenv("NEO4J_USERNAME"))
        print(os.getenv("NEO4J_PASSWORD"))
        client = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD")
        )

        result = client.query("MATCH (n) RETURN n LIMIT 100")
        # Check if the result is a list and has a length of 100 or less
        print(f"Successfully retrieved {len(result)} nodes.")
        
    except Exception as e:
        print(f"Failed to connect or query the database: {e}")
        result = {"message":f"Failed test {e}"}

    return result