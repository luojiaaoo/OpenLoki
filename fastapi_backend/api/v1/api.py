from fastapi import FastAPI
from .endpoints.llm_endpoint import llm_router


def handle_router(app: FastAPI):
    app.include_router(llm_router)
