import os
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field
from neo4j import exceptions
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# testing
# Print all environment variables
# for key, value in os.environ.items():
#    print(f"{key}: {value}")


# Ensure that you have imported your chains correctly
from app.graph_chain import graph_chain, CYPHER_GENERATION_PROMPT
from app.vector_chain import vector_graph_chain, VECTOR_GRAPH_PROMPT
from app.simple_agent import simple_agent_chain

app = FastAPI()


class ApiChatPostRequest(BaseModel):
    message: str = Field(..., description="The chat message to send")
    mode: str = Field(
        "agent",
        description='The mode of the chat message. Current options are: "vector", "graph", "agent". Default is "agent"',
    )


class ApiChatPostResponse(BaseModel):
    response: str


class Neo4jExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except exceptions.AuthError as e:
            msg = f"Neo4j Authentication Error: {e}"
            logging.warning(msg)
            return Response(content=msg, status_code=400, media_type="text/plain")
        except exceptions.ServiceUnavailable as e:
            msg = f"Neo4j Database Unavailable Error: {e}"
            logging.warning(msg)
            return Response(content=msg, status_code=400, media_type="text/plain")
        except Exception as e:
            msg = f"Neo4j Uncaught Exception: {e}"
            logging.error(msg)
            return Response(content=msg, status_code=400, media_type="text/plain")


# Read the API key from the environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')


# Allowed CORS origins
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(Neo4jExceptionMiddleware)


@app.post(
    "/api/chat",
    response_model=None,
    responses={"201": {"model": ApiChatPostResponse}},
    tags=["chat"],
)
async def send_chat_message(body: ApiChatPostRequest):
    question = body.message

    if body.mode == "vector":
        v_response = vector_graph_chain().invoke(
            {"query": question}, prompt=VECTOR_GRAPH_PROMPT, return_only_outputs=True, openai_api_key=OPENAI_API_KEY
        )
        response = v_response
    elif body.mode == "graph":
        g_response = graph_chain().invoke(
            {"query": question},
            prompt=CYPHER_GENERATION_PROMPT,
            return_only_outputs=True,
            openai_api_key=OPENAI_API_KEY
        )
        response = g_response["result"]
    else:
        v_response = vector_graph_chain().invoke(
            {"query": question}, prompt=VECTOR_GRAPH_PROMPT, return_only_outputs=True, openai_api_key=OPENAI_API_KEY
        )
        g_response = graph_chain().invoke(
            {"query": question},
            prompt=CYPHER_GENERATION_PROMPT,
            return_only_outputs=True,
            openai_api_key=OPENAI_API_KEY
        )["result"]

        response = simple_agent_chain().invoke(
            {
                "question": question,
                "vector_result": v_response,
                "graph_result": g_response,
            },
            openai_api_key=OPENAI_API_KEY
        )

    return response, 200

# To run the server, use the command: uvicorn main:app --reload
# Link to interactive docs: http://localhost:8000/docs
