from fastapi import FastAPI
from app.v2.api import app as v2_app

app = FastAPI(
    title="Climateguard Root",
    docs_url=None,
    openapi_url=None,
)

app.mount("/v2", v2_app)
