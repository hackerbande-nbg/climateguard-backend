from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import SensorMetric

app = FastAPI(
    title="climateguard-backend",
    description="hackerban.de's climateguard backend API",
    version="0.0.1",  # 👈 critical: OpenAPI version
    # 👈 expose OpenAPI schema at versioned endpoint
    openapi_url="/docs/openapi.json",
    docs_url="/docs/docs",             # 👈 Swagger UI for v1
    redoc_url="/docs/redoc"            # 👈 ReDoc UI (optional)
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


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}


@app.get("/sensormetrics", response_model=list[SensorMetric])
async def get_sensormetrics(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(SensorMetric))
    metrics = result.scalars().all()
    return [
        SensorMetric(
            id=metric.id,
            device_id=metric.device_id,
            timestamp_device=metric.timestamp_device,
            timestamp_server=metric.timestamp_server,
            temperature=metric.temperature,
            humidity=metric.humidity,
        )
        for metric in metrics
    ]


@app.post("/sensormetrics")
async def add_sensormetric(
    metric: SensorMetric, session: AsyncSession = Depends(get_session)
):
    metric = SensorMetric(
        device_id=metric.device_id,
        timestamp_device=metric.timestamp_device,
        timestamp_server=metric.timestamp_server,
        temperature=metric.temperature,
        humidity=metric.humidity,
    )
    session.add(metric)
    await session.commit()
    await session.refresh(metric)
    return metric
