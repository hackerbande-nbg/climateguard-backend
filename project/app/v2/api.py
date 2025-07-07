from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from app.v2.routers import metrics as v2_metrics
from app.v2.routers import devices as v2_devices
from app.v2.routers import auth as v2_auth

app = FastAPI(
    title="climateguard-backend v2",
    description="3/4 production of climateguard backend",
    version="2.3.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add security scheme for OpenAPI documentation
security_scheme = HTTPBearer(
    scheme_name="API Key Authentication",
    description="Use your API key in the Authorization header: `Bearer <your-api-key>` or X-API-Key header"
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
app.include_router(v2_auth.router)


@app.get("/ping",
         summary="Health check",
         description="Public health check endpoint - no authentication required")
async def pong():
    return {"ping": "pong!"}
