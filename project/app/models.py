from sqlmodel import SQLModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class SensorMetric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp_device: Optional[int] = None
    timestamp_server: Optional[int] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    device_id: Optional[str] = None


class GroundCover(str, Enum):
    earth = "earth"
    grass = "grass"
    concrete = "concrete"
    asphalt = "asphalt"
    cobblestone = "cobblestone"
    water = "water"
    sand = "sand"
    other = "other"


class Orientation(str, Enum):
    north = "north"
    east = "east"
    west = "west"
    south = "south"


class Shading(int, Enum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5


class HardwareRevision(SQLModel, table=True):
    hardware_id: Optional[int] = Field(default=None, primary_key=True)
    version_name: Optional[str] = None
    specification_repo: Optional[str] = None
    specification_commit: Optional[str] = None
    specification_file_path: Optional[str] = None


class SoftwareVersion(SQLModel, table=True):
    software_id: Optional[int] = Field(default=None, primary_key=True)
    version_name: Optional[str] = None
    git_commit: Optional[str] = None


class Device(SQLModel, table=True):
    device_id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = None
    hardware_id: Optional[int] = None
    software_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[datetime] = None
    appeui: Optional[str] = None
    deveui: Optional[str] = None
    appkey: Optional[str] = None
    ground_cover: Optional[GroundCover] = None
    height_above_ground: Optional[int] = None
    shading: Optional[Shading] = None
    close_to_a_tree: Optional[bool] = None
    close_to_water: Optional[bool] = None
    orientation: Optional[Orientation] = None
    distance_to_next_building_cm: Optional[int] = None
