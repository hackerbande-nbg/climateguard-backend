from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
import re

from app.db import get_session
from app.models import SensorMetric

router = APIRouter()


class PaginatedMetricsResponse(BaseModel):
    """Response model for paginated metrics"""
    data: list[SensorMetric]
    pagination: Dict[str, Any]


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


@router.get("/metrics")
async def get_metrics(
    min_date: Optional[str] = Query(
        None, description="Minimum date filter (Unix timestamp or ISO string)"),
    max_date: Optional[str] = Query(
        None, description="Maximum date filter (Unix timestamp or ISO string)"),
    limit: Optional[int] = Query(
        100, ge=1, le=200, description="Number of records to return per page"),
    page: Optional[int] = Query(
        1, ge=1, description="Page number for pagination (starts from 1)"),
    session: AsyncSession = Depends(get_session)
):
    """Get sensor metrics with optional date filtering and pagination"""

    # Build the base query for counting
    count_query = select(func.count(SensorMetric.id))
    data_query = select(SensorMetric).order_by(
        SensorMetric.timestamp_server.desc())

    # Apply date filters if provided
    if min_date:
        min_timestamp = parse_date_parameter(min_date)
        count_query = count_query.where(
            SensorMetric.timestamp_server >= min_timestamp)
        data_query = data_query.where(
            SensorMetric.timestamp_server >= min_timestamp)

    if max_date:
        max_timestamp = parse_date_parameter(max_date)
        count_query = count_query.where(
            SensorMetric.timestamp_server <= max_timestamp)
        data_query = data_query.where(
            SensorMetric.timestamp_server <= max_timestamp)

    # Get total count
    total_result = await session.execute(count_query)
    total_count = total_result.scalar()

    # Check if pagination is needed (more than 200 entries)
    if total_count > limit:
        # Calculate pagination
        offset = (page - 1) * limit
        total_pages = (total_count + limit - 1) // limit  # Ceiling division

        # Apply pagination
        data_query = data_query.offset(offset).limit(limit)

        # Execute query
        result = await session.execute(data_query)
        metrics = result.scalars().all()

        # Return paginated response
        return PaginatedMetricsResponse(
            data=metrics,
            pagination={
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        )
    else:
        # No pagination needed, but return same structure
        if limit and limit > 0:
            data_query = data_query.limit(limit)

        result = await session.execute(data_query)
        metrics = result.scalars().all()

        # Return consistent structure even without pagination
        return PaginatedMetricsResponse(
            data=metrics,
            pagination={
                "total_count": total_count,
                "page": 1,
                "limit": len(metrics),
                "total_pages": 1,
                "has_next": False,
                "has_prev": False
            }
        )
