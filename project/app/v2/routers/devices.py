from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from app.db import get_session
from app.models import Device, Tag, DeviceTagLink
from app.schemas import DeviceCreate, DeviceRead, DeviceUpdate, TagRead

router = APIRouter()


class PaginatedDevicesResponse(BaseModel):
    """Response model for paginated devices"""
    data: List[DeviceRead]
    pagination: Dict[str, Any]


@router.get("/devices", response_model=PaginatedDevicesResponse)
async def get_devices(
    limit: Optional[int] = Query(
        100, ge=1, le=200, description="Number of records to return per page"),
    page: Optional[int] = Query(
        1, ge=1, description="Page number for pagination (starts from 1)"),
    name: Optional[str] = Query(None, description="Filter by device name"),
    ground_cover: Optional[str] = Query(
        None, description="Filter by ground cover"),
    orientation: Optional[str] = Query(
        None, description="Filter by orientation"),
    shading: Optional[int] = Query(
        None, description="Filter by shading level"),
    tag_category: Optional[str] = Query(
        None, description="Filter by tag category"),
    tag_name: Optional[str] = Query(None, description="Filter by tag name"),
    session: AsyncSession = Depends(get_session)
):
    """Get devices with optional filtering and pagination"""

    # Build base queries
    count_query = select(func.count(Device.device_id))
    data_query = select(Device).order_by(Device.created_at.desc())

    # Apply filters
    if name:
        count_query = count_query.where(Device.name.ilike(f"%{name}%"))
        data_query = data_query.where(Device.name.ilike(f"%{name}%"))

    if ground_cover:
        count_query = count_query.where(Device.ground_cover == ground_cover)
        data_query = data_query.where(Device.ground_cover == ground_cover)

    if orientation:
        count_query = count_query.where(Device.orientation == orientation)
        data_query = data_query.where(Device.orientation == orientation)

    if shading:
        count_query = count_query.where(Device.shading == shading)
        data_query = data_query.where(Device.shading == shading)

    # Tag filtering
    if tag_category or tag_name:
        tag_subquery = select(DeviceTagLink.device_id).join(Tag)
        if tag_category:
            tag_subquery = tag_subquery.where(Tag.category == tag_category)
        if tag_name:
            tag_subquery = tag_subquery.where(Tag.tag == tag_name)

        count_query = count_query.where(Device.device_id.in_(tag_subquery))
        data_query = data_query.where(Device.device_id.in_(tag_subquery))

    # Get total count
    total_result = await session.execute(count_query)
    total_count = total_result.scalar()

    # Calculate pagination
    offset = (page - 1) * limit
    total_pages = (total_count + limit - 1) // limit

    # Apply pagination
    data_query = data_query.offset(offset).limit(limit)

    # Execute query and load tags
    result = await session.execute(data_query)
    devices = result.scalars().all()

    # Load tags for each device
    device_reads = []
    for device in devices:
        # Load tags for this device
        tags_query = select(Tag).join(DeviceTagLink).where(
            DeviceTagLink.device_id == device.device_id)
        tags_result = await session.execute(tags_query)
        tags = tags_result.scalars().all()

        # Convert to DeviceRead
        device_read = DeviceRead(
            device_id=device.device_id,
            name=device.name,
            hardware_id=device.hardware_id,
            software_id=device.software_id,
            latitude=device.latitude,
            longitude=device.longitude,
            created_at=device.created_at,
            appeui=device.appeui,
            deveui=device.deveui,
            appkey=device.appkey,
            ground_cover=device.ground_cover,
            height_above_ground=device.height_above_ground,
            shading=device.shading,
            close_to_a_tree=device.close_to_a_tree,
            close_to_water=device.close_to_water,
            orientation=device.orientation,
            distance_to_next_building_cm=device.distance_to_next_building_cm,
            tags=[TagRead(id=tag.id, category=tag.category, tag=tag.tag)
                  for tag in tags]
        )
        device_reads.append(device_read)

    return PaginatedDevicesResponse(
        data=device_reads,
        pagination={
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    )


@router.get("/devices/{device_id}", response_model=DeviceRead)
async def get_device(
    device_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get a specific device with tags"""
    # Check for out of bounds device ID
    if device_id < 1 or device_id > 1000000:
        raise HTTPException(
            status_code=400, detail="Device ID out of bounds")

    # Get device
    device_query = select(Device).where(Device.device_id == device_id)
    device_result = await session.execute(device_query)
    device = device_result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=404, detail=f"Device with ID {device_id} not found")

    # Get tags
    tags_query = select(Tag).join(DeviceTagLink).where(
        DeviceTagLink.device_id == device_id)
    tags_result = await session.execute(tags_query)
    tags = tags_result.scalars().all()

    return DeviceRead(
        device_id=device.device_id,
        name=device.name,
        hardware_id=device.hardware_id,
        software_id=device.software_id,
        latitude=device.latitude,
        longitude=device.longitude,
        created_at=device.created_at,
        appeui=device.appeui,
        deveui=device.deveui,
        appkey=device.appkey,
        ground_cover=device.ground_cover,
        height_above_ground=device.height_above_ground,
        shading=device.shading,
        close_to_a_tree=device.close_to_a_tree,
        close_to_water=device.close_to_water,
        orientation=device.orientation,
        distance_to_next_building_cm=device.distance_to_next_building_cm,
        tags=[TagRead(id=tag.id, category=tag.category, tag=tag.tag)
              for tag in tags]
    )


@router.post("/devices", response_model=DeviceRead, status_code=201)
async def create_device(
    device_data: DeviceCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new device with tags"""

    # Check if device name already exists
    if device_data.name:
        existing_query = select(Device).where(Device.name == device_data.name)
        existing_result = await session.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=409, detail=f"Device with name '{device_data.name}' already exists")

    # Create device
    new_device = Device(
        name=device_data.name,
        hardware_id=device_data.hardware_id,
        software_id=device_data.software_id,
        latitude=device_data.latitude,
        longitude=device_data.longitude,
        created_at=datetime.utcnow(),
        appeui=device_data.appeui,
        deveui=device_data.deveui,
        appkey=device_data.appkey,
        ground_cover=device_data.ground_cover,
        height_above_ground=device_data.height_above_ground,
        shading=device_data.shading,
        close_to_a_tree=device_data.close_to_a_tree,
        close_to_water=device_data.close_to_water,
        orientation=device_data.orientation,
        distance_to_next_building_cm=device_data.distance_to_next_building_cm
    )

    session.add(new_device)
    await session.commit()
    await session.refresh(new_device)

    # Handle tags - simple list of strings with hardcoded "device" category
    created_tags = []
    for tag_name in device_data.tags:
        # Check if tag already exists with category "device"
        tag_query = select(Tag).where(
            Tag.category == "device", Tag.tag == tag_name)
        tag_result = await session.execute(tag_query)
        tag = tag_result.scalar_one_or_none()

        if not tag:
            # Create new tag with hardcoded "device" category
            tag = Tag(category="device", tag=tag_name)
            session.add(tag)
            await session.commit()
            await session.refresh(tag)

        # Link tag to device
        device_tag_link = DeviceTagLink(
            device_id=new_device.device_id, tag_id=tag.id)
        session.add(device_tag_link)
        created_tags.append(
            TagRead(id=tag.id, category=tag.category, tag=tag.tag))

    await session.commit()

    return DeviceRead(
        device_id=new_device.device_id,
        name=new_device.name,
        hardware_id=new_device.hardware_id,
        software_id=new_device.software_id,
        latitude=new_device.latitude,
        longitude=new_device.longitude,
        created_at=new_device.created_at,
        appeui=new_device.appeui,
        deveui=new_device.deveui,
        appkey=new_device.appkey,
        ground_cover=new_device.ground_cover,
        height_above_ground=new_device.height_above_ground,
        shading=new_device.shading,
        close_to_a_tree=new_device.close_to_a_tree,
        close_to_water=new_device.close_to_water,
        orientation=new_device.orientation,
        distance_to_next_building_cm=new_device.distance_to_next_building_cm,
        tags=created_tags
    )


@router.put("/devices/{device_id}", response_model=DeviceRead)
async def update_device(
    device_id: int,
    device_data: DeviceUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update a device"""

    # Check for out of bounds device ID
    if device_id < 1 or device_id > 1000000:
        raise HTTPException(
            status_code=400, detail="Device ID out of bounds")

    # Get existing device
    device_query = select(Device).where(Device.device_id == device_id)
    device_result = await session.execute(device_query)
    device = device_result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=404, detail=f"Device with ID {device_id} not found")

    # Check name uniqueness if name is being updated
    if device_data.name and device_data.name != device.name:
        existing_query = select(Device).where(Device.name == device_data.name)
        existing_result = await session.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=409, detail=f"Device with name '{device_data.name}' already exists")

    # Update device fields
    update_data = device_data.model_dump(exclude_unset=True, exclude={'tags'})
    for field, value in update_data.items():
        setattr(device, field, value)

    # Handle tags if provided - simple list of strings with hardcoded "device" category
    if device_data.tags is not None:
        # Remove existing tag associations
        delete_links_query = select(DeviceTagLink).where(
            DeviceTagLink.device_id == device_id)
        delete_links_result = await session.execute(delete_links_query)
        for link in delete_links_result.scalars().all():
            await session.delete(link)

        # Add new tag associations
        updated_tags = []
        for tag_name in device_data.tags:
            # Check if tag already exists with category "device"
            tag_query = select(Tag).where(
                Tag.category == "device", Tag.tag == tag_name)
            tag_result = await session.execute(tag_query)
            tag = tag_result.scalar_one_or_none()

            if not tag:
                # Create new tag with hardcoded "device" category
                tag = Tag(category="device", tag=tag_name)
                session.add(tag)
                await session.commit()
                await session.refresh(tag)

            # Link tag to device
            device_tag_link = DeviceTagLink(device_id=device_id, tag_id=tag.id)
            session.add(device_tag_link)
            updated_tags.append(
                TagRead(id=tag.id, category=tag.category, tag=tag.tag))
    else:
        # Keep existing tags
        tags_query = select(Tag).join(DeviceTagLink).where(
            DeviceTagLink.device_id == device_id)
        tags_result = await session.execute(tags_query)
        tags = tags_result.scalars().all()
        updated_tags = [
            TagRead(id=tag.id, category=tag.category, tag=tag.tag) for tag in tags]

    await session.commit()
    await session.refresh(device)

    return DeviceRead(
        device_id=device.device_id,
        name=device.name,
        hardware_id=device.hardware_id,
        software_id=device.software_id,
        latitude=device.latitude,
        longitude=device.longitude,
        created_at=device.created_at,
        appeui=device.appeui,
        deveui=device.deveui,
        appkey=device.appkey,
        ground_cover=device.ground_cover,
        height_above_ground=device.height_above_ground,
        shading=device.shading,
        close_to_a_tree=device.close_to_a_tree,
        close_to_water=device.close_to_water,
        orientation=device.orientation,
        distance_to_next_building_cm=device.distance_to_next_building_cm,
        tags=updated_tags
    )


@router.delete("/devices/{device_id}")
async def delete_device(
    device_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete a device"""
    # Check for out of bounds device ID
    if device_id < 1 or device_id > 1000000:
        raise HTTPException(
            status_code=400, detail="Device ID out of bounds")

    # Get device
    device_query = select(Device).where(Device.device_id == device_id)
    device_result = await session.execute(device_query)
    device = device_result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=404, detail=f"Device with ID {device_id} not found")

    # Delete tag associations
    delete_links_query = select(DeviceTagLink).where(
        DeviceTagLink.device_id == device_id)
    delete_links_result = await session.execute(delete_links_query)
    for link in delete_links_result.scalars().all():
        await session.delete(link)

    # Delete device
    await session.delete(device)
    await session.commit()

    return {"message": f"Device {device_id} deleted successfully"}
