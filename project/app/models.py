from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

# vibe code instructions
# make sure that all entities have tags associated with them from model point of view.


class SensorMetricTagLink(SQLModel, table=True):
    sensor_metric_id: Optional[int] = Field(
        default=None, foreign_key="sensormetric.id", primary_key=True)
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True)


class HardwareRevisionTagLink(SQLModel, table=True):
    hardware_id: Optional[int] = Field(
        default=None, foreign_key="hardwarerevision.hardware_id", primary_key=True)
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True)


class SoftwareVersionTagLink(SQLModel, table=True):
    software_id: Optional[int] = Field(
        default=None, foreign_key="softwareversion.software_id", primary_key=True)
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True)


class DeviceTagLink(SQLModel, table=True):
    device_id: Optional[int] = Field(
        default=None, foreign_key="device.device_id", primary_key=True)
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True)


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str
    tag: str

    # Relationships
    sensor_metrics: List["SensorMetric"] = Relationship(
        back_populates="tags", link_model=SensorMetricTagLink)
    hardware_revisions: List["HardwareRevision"] = Relationship(
        back_populates="tags", link_model=HardwareRevisionTagLink)
    software_versions: List["SoftwareVersion"] = Relationship(
        back_populates="tags", link_model=SoftwareVersionTagLink)
    devices: List["Device"] = Relationship(
        back_populates="tags", link_model=DeviceTagLink)


class SensorMetric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp_device: Optional[int] = None
    timestamp_server: Optional[int] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    device_id: Optional[int] = Field(
        default=None, foreign_key="device.device_id")

    device: Optional["Device"] = Relationship(back_populates="sensor_metrics")
    tags: List[Tag] = Relationship(
        back_populates="sensor_metrics", link_model=SensorMetricTagLink)


class HardwareRevision(SQLModel, table=True):
    hardware_id: Optional[int] = Field(default=None, primary_key=True)
    version_name: Optional[str] = None
    specification_repo: Optional[str] = None
    specification_commit: Optional[str] = None
    specification_file_path: Optional[str] = None

    tags: List[Tag] = Relationship(
        back_populates="hardware_revisions", link_model=HardwareRevisionTagLink)


class SoftwareVersion(SQLModel, table=True):
    software_id: Optional[int] = Field(default=None, primary_key=True)
    version_name: Optional[str] = None
    git_commit: Optional[str] = None

    tags: List[Tag] = Relationship(
        back_populates="software_versions", link_model=SoftwareVersionTagLink)


class Device(SQLModel, table=True):
    device_id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None, unique=True)
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
    shading: Optional[int] = None  # 0 - full sun, 100 - full shade
    close_to_a_tree: Optional[bool] = None
    close_to_water: Optional[bool] = None
    orientation: Optional[str] = None
    distance_to_next_building_cm: Optional[int] = None
    # 0 - full sun, 100 - full shade
    shading_of_surrounding_area: Optional[int] = None

    sensor_metrics: List["SensorMetric"] = Relationship(
        back_populates="device")
    tags: List[Tag] = Relationship(
        back_populates="devices", link_model=DeviceTagLink)
