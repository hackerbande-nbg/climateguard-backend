from sqlmodel import SQLModel
from typing import Optional, List
from datetime import datetime
from pydantic import Field


class TagCreate(SQLModel):
    category: str
    tag: str


class TagRead(SQLModel):
    id: int
    category: str
    tag: str


class DeviceCreate(SQLModel):
    name: str
    hardware_id: Optional[int] = None
    software_id: Optional[int] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    appeui: Optional[str] = None
    deveui: Optional[str] = None
    appkey: Optional[str] = None
    ground_cover: Optional[str] = None
    height_above_ground: Optional[int] = Field(None, ge=0)
    shading: Optional[int] = None
    close_to_a_tree: Optional[bool] = None
    close_to_water: Optional[bool] = None
    orientation: Optional[str] = None
    distance_to_next_building_cm: Optional[int] = Field(None, ge=0)
    tags: List[str] = []


class DeviceRead(SQLModel):
    device_id: int
    name: str
    hardware_id: Optional[int] = None
    software_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[datetime] = None
    appeui: Optional[str] = None
    deveui: Optional[str] = None
    appkey: Optional[str] = None
    ground_cover: Optional[str] = None
    height_above_ground: Optional[int] = None
    shading: Optional[int] = None
    close_to_a_tree: Optional[bool] = None
    close_to_water: Optional[bool] = None
    orientation: Optional[str] = None
    distance_to_next_building_cm: Optional[int] = None
    tags: List[TagRead] = []


class DeviceUpdate(SQLModel):
    name: Optional[str] = None
    hardware_id: Optional[int] = None
    software_id: Optional[int] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    appeui: Optional[str] = None
    deveui: Optional[str] = None
    appkey: Optional[str] = None
    ground_cover: Optional[str] = None
    height_above_ground: Optional[int] = Field(None, ge=0)
    shading: Optional[int] = None
    close_to_a_tree: Optional[bool] = None
    close_to_water: Optional[bool] = None
    orientation: Optional[str] = None
    distance_to_next_building_cm: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None
