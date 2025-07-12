from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from app.db import get_session
from app.models import Device, Tag, DeviceTagLink
from app.schemas import DeviceCreate, DeviceRead, DeviceUpdate, TagRead
from app.dependencies import require_auth

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Access forbidden"},
        404: {"description": "Device not found"},
        422: {"description": "Validation error"},
        409: {"description": "Conflict - duplicate device name"},
        400: {"description": "Bad request - invalid device ID"},
    }
)


class PaginatedDevicesResponse(BaseModel):
    """Response model for paginated devices"""
    data: List[DeviceRead]
    pagination: Dict[str, Any]


@router.get("",
            response_model=PaginatedDevicesResponse,
            summary="List devices with filtering and pagination",
            description="""
    Retrieve a paginated list of devices with optional filtering capabilities.
    
    **⚠️ Authentication Required:** Valid API key in X-API-Key header or Authorization Bearer token
    
    **Filtering Options:**
    - **name**: Partial match on device name (case-insensitive)
    - **ground_cover**: Filter by ground cover type (earth, grass, concrete, asphalt, cobblestone, water, sand, other)
    - **orientation**: Filter by device orientation (north, east, west, south)
    - **shading**: Filter by shading level (0 = full sun, 100 = full shade)
    - **tag_category**: Filter by tag category (e.g., "device", "location", "type")
    - **tag_name**: Filter by specific tag name
    
    **Pagination:**
    - **limit**: Number of records per page (1-200, default: 100)
    - **page**: Page number starting from 1 (default: 1)
    """,
            response_description="Paginated list of devices with metadata"
            )
async def get_devices(
    limit: Optional[int] = Query(
        100, ge=1, le=200,
        description="Number of records to return per page",
        example=10
    ),
    page: Optional[int] = Query(
        1, ge=1,
        description="Page number for pagination (starts from 1)",
        example=1
    ),
    name: Optional[str] = Query(
        None,
        description="Filter by device name (partial match, case-insensitive)",
        example="Sensor"
    ),
    ground_cover: Optional[str] = Query(
        None,
        description="Filter by ground cover type",
        example="grass"
    ),
    orientation: Optional[str] = Query(
        None,
        description="Filter by device orientation",
        example="north"
    ),
    shading: Optional[int] = Query(
        None,
        description="Filter by shading level (0-100)",
        example=50
    ),
    tag_category: Optional[str] = Query(
        None,
        description="Filter by tag category",
        example="device"
    ),
    tag_name: Optional[str] = Query(
        None,
        description="Filter by specific tag name",
        example="outdoor"
    ),
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


@router.get("/{device_id}",
            response_model=DeviceRead,
            summary="Get device by ID",
            description="""
    Retrieve a specific device by its unique ID along with associated tags.
    
    **⚠️ Authentication Required:** Valid API key in X-API-Key header or Authorization Bearer token
    
    **Device ID Constraints:**
    - Must be between 1 and 1,000,000
    - Returns 404 if device does not exist
    - Returns 400 if ID is out of bounds
    """,
            response_description="Device details with associated tags",
            responses={
                200: {
                    "description": "Device found",
                    "content": {
                        "application/json": {
                            "example": {
                                "device_id": 1,
                                "name": "Weather Station Alpha",
                                "latitude": 40.7128,
                                "longitude": -74.0060,
                                "ground_cover": "grass",
                                "orientation": "north",
                                "shading": 25,
                                "created_at": "2024-01-15T10:30:00Z",
                                "tags": [
                                    {"id": 1, "category": "device",
                                        "tag": "outdoor"},
                                    {"id": 2, "category": "device", "tag": "weather"}
                                ]
                            }
                        }
                    }
                }
            }
            )
async def get_device(
    device_id: int = Path(
        ...,
        description="Unique device identifier",
        example=1,
        ge=1,
        le=1000000
    ),
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


@router.post("",
             response_model=DeviceRead,
             status_code=201,
             summary="Create a new device",
             description="""
    Create a new device with optional tags and configuration.
    
    **⚠️ Authentication Required:** Valid API key in X-API-Key header or Authorization Bearer token
    
    **Required Fields:**
    - **name**: Unique device name
    
    **Optional Configuration:**
    - **ground_cover**: Type of ground surface (earth, grass, concrete, asphalt, cobblestone, water, sand, other)
    - **orientation**: Device facing direction (north, east, west, south)
    - **shading**: Shading level from 0 (full sun) to 100 (full shade)
    - **tags**: List of tag strings (automatically assigned to "device" category)
    
    **Location Data:**
    - **latitude**: GPS latitude (-90 to 90)
    - **longitude**: GPS longitude (-180 to 180)
    
    **LoRaWAN Configuration:**
    - **appeui**: Application EUI
    - **deveui**: Device EUI
    - **appkey**: Application Key
    """,
             response_description="Created device with generated ID and tags",
             responses={
                 201: {
                     "description": "Device created successfully",
                     "content": {
                         "application/json": {
                             "example": {
                                 "device_id": 123,
                                 "name": "New Weather Station",
                                 "latitude": 40.7128,
                                 "longitude": -74.0060,
                                 "ground_cover": "grass",
                                 "orientation": "north",
                                 "shading": 25,
                                 "created_at": "2024-01-15T10:30:00Z",
                                 "tags": [
                                     {"id": 15, "category": "device",
                                         "tag": "outdoor"}
                                 ]
                             }
                         }
                     }
                 },
                 409: {
                     "description": "Device name already exists",
                     "content": {
                         "application/json": {
                             "example": {
                                 "detail": "Device with name 'Weather Station Alpha' already exists"
                             }
                         }
                     }
                 }
             }
             )
async def create_device(
    device_data: DeviceCreate = Body(
        ...,
        description="Device creation data",
        example={
            "name": "Weather Station Beta",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "ground_cover": "grass",
            "orientation": "north",
            "shading": 25,
            "close_to_a_tree": True,
            "close_to_water": False,
            "height_above_ground": 200,
            "tags": ["outdoor", "weather", "research"]
        }
    ),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_auth)
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


@router.put("/{device_id}",
            response_model=DeviceRead,
            summary="Update device",
            description="""
    Update an existing device. Only provided fields will be updated.
    
    **⚠️ Authentication Required:** Valid API key in X-API-Key header or Authorization Bearer token
    
    **Updateable Fields:**
    - All device configuration fields
    - Device name (must remain unique)
    - Location coordinates
    - Tags (replaces all existing tags)
    
    **Tag Handling:**
    - If tags are provided, all existing tags are replaced
    - If tags are not provided (null), existing tags are preserved
    - All tags are automatically assigned to "device" category
    """,
            response_description="Updated device with current tag associations"
            )
async def update_device(
    device_id: int = Path(
        ...,
        description="Unique device identifier to update",
        example=1,
        ge=1,
        le=1000000
    ),
    device_data: DeviceUpdate = Body(
        ...,
        description="Device update data (only provided fields will be updated)",
        example={
            "name": "Updated Weather Station",
            "shading": 30,
            "tags": ["outdoor", "updated", "monitoring"]
        }
    ),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_auth)
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


@router.delete("/{device_id}",
               summary="Delete device",
               description="""
    Permanently delete a device and all its associated data.
    
    **⚠️ Authentication Required:** Valid API key in X-API-Key header or Authorization Bearer token
    
    **Warning:** This action cannot be undone and will:
    - Remove the device record
    - Remove all tag associations
    - Orphan any sensor metrics (metrics will remain but lose device reference)
    
    **Returns:** Confirmation message with deleted device ID
    """,
               response_description="Deletion confirmation message",
               responses={
                   200: {
                       "description": "Device deleted successfully",
                       "content": {
                           "application/json": {
                               "example": {
                                   "message": "Device 123 deleted successfully"
                               }
                           }
                       }
                   }
               }
               )
async def delete_device(
    device_id: int = Path(
        ...,
        description="Unique device identifier to delete",
        example=1,
        ge=1,
        le=1000000
    ),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_auth)
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
