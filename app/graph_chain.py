from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain.prompts.prompt import PromptTemplate
from langchain.schema.runnable import Runnable
from langchain_openai import ChatOpenAI
import os

CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Examples: Here are a few examples of generated Cypher statements for particular questions:

Example Questions 1: "What movie would you recommend when I liked Top Gun?"
 [
    {
        "step": 1,
        "description": "Find actors in the movie 'Top Gun'",
        "query": "MATCH (m:Movie {title: 'Top Gun'})<-[:ACTED_IN]-(a:Actor) RETURN a.name"
    },
    {
        "step": 2,
        "description": "Find other movies those actors have acted in",
        "query": "MATCH (a:Actor)-[:ACTED_IN]->(m:Movie) WHERE a.name IN [\"Tom Cruise\", \"Kelly McGillis\"] AND m.title <> 'Top Gun' RETURN DISTINCT m.title AS RecommendedMovies"
    },
    {
        "step": "combined",
        "description": "Find other movies those actors have acted in (Combined Query)",
        "query": "MATCH (m:Movie {title: 'Top Gun'})<-[:ACTED_IN]-(a:Actor)-[:ACTED_IN]->(rec:Movie) WHERE rec.title <> 'Top Gun' RETURN DISTINCT rec.title AS RecommendedMovies"
    }
]
The question is:
{question}"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)


def graph_chain() -> Runnable:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LLM = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)

    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=os.getenv("NEO4J_DATABASE"),
        sanitize=True,
    )

    graph.refresh_schema()

    # Official API doc for GraphCypherQAChain at: https://api.python.langchain.com/en/latest/chains/langchain.chains.graph_qa.base.GraphQAChain.html#
    graph_chain = GraphCypherQAChain.from_llm(
        cypher_llm=LLM,
        qa_llm=LLM,
        validate_cypher=True,
        graph=graph,
        verbose=True,
        return_intermediate_steps=True,
        # return_direct = True,
    )

    return graph_chain
