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


class UserTagLink(SQLModel, table=True):
    user_id: Optional[int] = Field(
        default=None, foreign_key="user.user_id", primary_key=True)
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True)


class SensorMessageTagLink(SQLModel, table=True):
    sensor_message_id: Optional[int] = Field(
        default=None, foreign_key="sensormessage.id", primary_key=True)
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True)


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str
    tag: str
    comment: Optional[str] = None

    # Relationships
    sensor_metrics: List["SensorMetric"] = Relationship(
        back_populates="tags", link_model=SensorMetricTagLink)
    sensor_messages: List["SensorMessage"] = Relationship(
        back_populates="tags", link_model=SensorMessageTagLink)
    hardware_revisions: List["HardwareRevision"] = Relationship(
        back_populates="tags", link_model=HardwareRevisionTagLink)
    software_versions: List["SoftwareVersion"] = Relationship(
        back_populates="tags", link_model=SoftwareVersionTagLink)
    devices: List["Device"] = Relationship(
        back_populates="tags", link_model=DeviceTagLink)
    users: List["User"] = Relationship(
        back_populates="tags", link_model=UserTagLink)


class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: Optional[str] = None
    api_key_hash: Optional[str] = None  # null until registration
    api_key_salt: Optional[str] = None  # null until registration
    is_active: bool = Field(default=False)
    is_registered: bool = Field(default=False)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    registered_at: Optional[datetime] = None  # set during registration
    last_login: Optional[datetime] = None

    # Relationships - following vibe code instructions
    tags: List[Tag] = Relationship(
        back_populates="users", link_model=UserTagLink)


class SensorMetric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp_device: Optional[int] = None
    timestamp_server: Optional[int] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    air_pressure: Optional[float] = None
    battery_voltage: Optional[float] = None
    device_id: Optional[int] = Field(
        default=None, foreign_key="device.device_id")
    confirmed: Optional[bool] = None
    consumed_airtime: Optional[float] = None
    f_cnt: Optional[int] = None
    frequency: Optional[int] = None

    device: Optional["Device"] = Relationship(back_populates="sensor_metrics")
    sensor_messages: List["SensorMessage"] = Relationship(
        back_populates="sensor_metric")
    tags: List[Tag] = Relationship(
        back_populates="sensor_metrics", link_model=SensorMetricTagLink)


class SensorMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    gateway_id: Optional[str] = None
    rssi: Optional[float] = None
    snr: Optional[float] = None
    channel_rssi: Optional[float] = None
    lora_bandwidth: Optional[int] = None
    lora_spreading_factor: Optional[int] = None
    lora_coding_rate: Optional[str] = None

    device_id: Optional[int] = Field(
        default=None, foreign_key="device.device_id")
    sensor_metric_id: Optional[int] = Field(
        default=None, foreign_key="sensormetric.id")

    # Relationships
    device: Optional["Device"] = Relationship(back_populates="sensor_messages")
    sensor_metric: Optional["SensorMetric"] = Relationship(
        back_populates="sensor_messages")
    tags: List[Tag] = Relationship(
        back_populates="sensor_messages", link_model=SensorMessageTagLink)


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
    sensor_messages: List["SensorMessage"] = Relationship(
        back_populates="device")
    tags: List[Tag] = Relationship(
        back_populates="devices", link_model=DeviceTagLink)
    comment: Optional[str] = None


###############################################
# SQL Only Models Below
###############################################

class HardwareRevision(SQLModel, table=True):
    hardware_id: Optional[int] = Field(default=None, primary_key=True)
    version_name: Optional[str] = None
    specification_repo: Optional[str] = None
    specification_commit: Optional[str] = None
    specification_file_path: Optional[str] = None
    comment: Optional[str] = None

    tags: List[Tag] = Relationship(
        back_populates="hardware_revisions", link_model=HardwareRevisionTagLink)


class SoftwareVersion(SQLModel, table=True):
    software_id: Optional[int] = Field(default=None, primary_key=True)
    version_name: Optional[str] = None
    git_commit: Optional[str] = None
    comment: Optional[str] = None

    tags: List[Tag] = Relationship(
        back_populates="software_versions", link_model=SoftwareVersionTagLink)


class DbMetrics(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    snapshot_timestamp: datetime
    db_name: str = Field(default="current_database()")
    db_size_bytes: int
    active_connections: int
    xact_commit: int
    xact_rollback: int
    blks_read: int
    blks_hit: int
    temp_files: int
    temp_bytes: int
    deadlocks: int


class TableStorageMetrics(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    snapshot_timestamp: datetime
    schemaname: str
    tablename: str
    relid: Optional[int] = None
    total_bytes: int
    table_bytes: int
    index_bytes: int
    toast_bytes: int


class TableActivityMetrics(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    snapshot_timestamp: datetime
    schemaname: str
    tablename: str
    relid: Optional[int] = None
    seq_scan: int
    idx_scan: int
    n_tup_ins: int
    n_tup_upd: int
    n_tup_del: int
    n_tup_hot_upd: int
    n_dead_tup: int
    last_vacuum: Optional[datetime] = None
    last_autovacuum: Optional[datetime] = None
    last_analyze: Optional[datetime] = None
    last_autoanalyze: Optional[datetime] = None


class IndexActivityMetrics(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    snapshot_timestamp: datetime
    schemaname: str
    tablename: str
    indexname: str
    indexrelid: Optional[int] = None
    relid: Optional[int] = None
    idx_scan: int
    idx_tup_read: int
    idx_tup_fetch: int
