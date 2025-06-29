from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.v1.routers import metrics

app = FastAPI(
    title="climateguard-backend v1",
    version="0.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://quantum.hackerban.de",
        "https://api.quantum.hackerban.de",
        "http://quantum.hackerban.de",
        "http://api.quantum.hackerban.de"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics.router)


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}
