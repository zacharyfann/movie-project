from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from typing import Tuple, List, Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.messages import HumanMessage
#graph = Neo4jGraph("neo4j+s://2a09654f.databases.neo4j.io","neo4j","9CoPsNYCDYzE3ePBpSnS1iyM_Y5NqZcS1QC54j4c9tE")
llm = Ollama(model="llama3")
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are an un-helpful assistant"),
    ("user", "Answer this question: {question}")
])
question = input("Input Your Question Here: ")

response1 = prompt_template.invoke({"question": question})
print(llm.invoke(response1))
