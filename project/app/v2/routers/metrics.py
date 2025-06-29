from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.db import get_session
from app.models import SensorMetric

router = APIRouter()


@router.get("/sensormetrics", response_model=list[SensorMetric])
async def get_sensormetrics(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(SensorMetric)
        .order_by(SensorMetric.timestamp_server.desc())
        .limit(100)
    )
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


@router.post("/sensormetrics")
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
