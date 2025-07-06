from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.v2.routers import metrics as v2_metrics
from app.v2.routers import devices as v2_devices
app = FastAPI(
    title="climateguard-backend v2",
    description="semiproduction of climateguard backend",
    version="2.3.0",
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

# first wins
app.include_router(v2_metrics.router)
app.include_router(v2_devices.router)


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}
