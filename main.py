from __future__ import annotations
# import streamlit as st
import logging

# st.write("Movie Recommendations App!")
# question = st.text_input("Input Your Question Here:")
# st.write(f"Your question is: {question}")

from app.graph_chain import graph_chain, CYPHER_GENERATION_PROMPT
from app.vector_chain import vector_chain, VECTOR_GRAPH_PROMPT
from app.simple_agent import simple_agent_chain
from fastapi import FastAPI, Request, Response

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from neo4j import exceptions
import os
import uvicorn
from dotenv import load_dotenv
from utils.neo4j_utils import Neo4jExceptionMiddleware
from tests.neo4j_tests import test_neo4J_connection
from tests.openai_tests import test_openai_connection

# Load environment variables from .env file
load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Allowed CORS origins
origins = [
    "http://127.0.0.1:8000",  # Alternative localhost address
    "http://localhost:8000",
]

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Neo4j exception handling middleware
app.add_middleware(Neo4jExceptionMiddleware)
# What does this do?

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/tests/neo4j_connection")
async def neo4j_connection():
    return test_neo4J_connection()
# Testing connection
# print(test_neo4J_connection())
@app.get("/tests/openai_connection")
async def openai_connection():
    return test_openai_connection()
# Testing connection
# print(test_openai_connection())

class ApiChatPostRequest(BaseModel):
    message: str = Field(..., description="The chat message to send")
    mode: str = Field(
        "agent",
        description='The mode of the chat message. Current options are: "vector", "graph", "agent". Default is "agent"',
    )


class ApiChatPostResponse(BaseModel):
    response: str


@app.post(
    "/api/chat",
    response_model=None,
    responses={"201": {"model": ApiChatPostResponse}},
    tags=["chat"],
)
async def send_chat_message(body: ApiChatPostRequest):
    # pass
    """
    Send a chat message
    """

    question = body.message

    # Simple exception check. See https://neo4j.com/docs/api/python-driver/current/api.html#errors for full set of driver exceptions

    if body.mode == "vector":
        # Return only the Vector answer
        v_response = vector_chain().invoke(
            {"query": question}, prompt=VECTOR_GRAPH_PROMPT, return_only_outputs=True
        )
        response = v_response
    elif body.mode == "graph":
        # Return only the Graph (text2Cypher) answer
        g_response = graph_chain().invoke(
            {"query": question},
            prompt=CYPHER_GENERATION_PROMPT,
            return_only_outputs=True,
        )
        response = g_response["result"]
    else:
        # Return both vector + graph answers
        v_chain = vector_chain()
        v_response = v_chain.invoke(
            {"query": question}, prompt=VECTOR_GRAPH_PROMPT, return_only_outputs=True
        )
        g_response = graph_chain().invoke(
            {"query": question},
            prompt=CYPHER_GENERATION_PROMPT,
            return_only_outputs=True,
        )["result"]

        # Synthesize a composite of both the Vector and Graph responses
        response = simple_agent_chain().invoke(
            {
                "question": question,
                "vector_result": v_response,
                "graph_result": g_response,
            }
        )

    return response, 200
