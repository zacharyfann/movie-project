
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, Response
from neo4j import exceptions
import logging

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
