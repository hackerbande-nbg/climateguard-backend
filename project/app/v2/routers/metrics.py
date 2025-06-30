from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from datetime import datetime
from typing import Optional
import re

from app.db import get_session
from app.models import SensorMetric

router = APIRouter()


def parse_date_parameter(date_str: str) -> int:
    """Parse date parameter from Unix timestamp or ISO string to Unix timestamp"""
    if not date_str:
        return None

    # Try Unix timestamp first
    if date_str.isdigit():
        return int(date_str)

    # Try ISO format
    iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$'
    if re.match(iso_pattern, date_str):
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return int(dt.timestamp())
        except ValueError:
            pass

    raise HTTPException(
        status_code=400, detail=f"Invalid date format: {date_str}")


@router.get("/metrics", response_model=list[SensorMetric])
async def get_metrics(
    min_date: Optional[str] = Query(
        None, description="Minimum date filter (Unix timestamp or ISO string)"),
    max_date: Optional[str] = Query(
        None, description="Maximum date filter (Unix timestamp or ISO string)"),
    limit: Optional[int] = Query(
        100, ge=1, description="Number of records to return"),
    session: AsyncSession = Depends(get_session)
):
    """Get sensor metrics with optional date filtering"""

    # Build the base query
    query = select(SensorMetric).order_by(SensorMetric.timestamp_server.desc())

    # Apply date filters if provided
    if min_date:
        min_timestamp = parse_date_parameter(min_date)
        query = query.where(SensorMetric.timestamp_server >= min_timestamp)

    if max_date:
        max_timestamp = parse_date_parameter(max_date)
        query = query.where(SensorMetric.timestamp_server <= max_timestamp)

    # Apply limit
    if limit and limit > 0:
        query = query.limit(limit)

    # Execute query
    result = await session.execute(query)
    metrics = result.scalars().all()

    return metrics


@router.get("/sensormetrics", response_model=list[SensorMetric])
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
