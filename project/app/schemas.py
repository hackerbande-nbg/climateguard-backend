from sqlmodel import SQLModel
from typing import Optional, List
from datetime import datetime
from pydantic import Field


class TagCreate(SQLModel):
    category: str
    tag: str
    comment: Optional[str] = None


class TagRead(SQLModel):
    id: int
    category: str
    tag: str
    comment: Optional[str] = None


# Authentication Schemas
class UserRegistrationRequest(SQLModel):
    """Schema for user self-registration"""
    username: str = Field(...,
                          description="Username (must match existing database entry)")
    email: Optional[str] = Field(None, description="Optional email address")


class UserRead(SQLModel):
    """Schema for user information (excludes sensitive data)"""
    user_id: int
    username: str
    email: Optional[str] = None
    is_active: bool
    is_registered: bool
    created_at: Optional[datetime] = None
    registered_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    tags: List[TagRead] = []


class ApiKeyResponse(SQLModel):
    """Schema for API key generation response"""
    user_id: int
    username: str
    api_key: str = Field(...,
                         description="32-character API key (shown only once)")
    message: str = Field(
        default="Registration complete. Save your API key - it won't be shown again.")


class AuthenticationError(SQLModel):
    """Schema for authentication error responses"""
    detail: str
    error_code: str
    status_code: int


# Device Schemas
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
    comment: Optional[str] = None


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
    comment: Optional[str] = None


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
    comment: Optional[str] = None


# Sensor Message Schemas
class SensorMessageCreate(SQLModel):
    """Schema for creating sensor messages"""
    gateway_id: Optional[str] = None
    rssi: Optional[float] = None
    snr: Optional[float] = None
    channel_rssi: Optional[float] = None
    lora_bandwidth: Optional[int] = Field(None, ge=0)
    lora_spreading_factor: Optional[int] = Field(None, ge=7, le=12)
    lora_coding_rate: Optional[str] = None
    device_id: Optional[int] = None
    sensor_metric_id: Optional[int] = None
    tags: List[str] = []


class SensorMessageRead(SQLModel):
    """Schema for reading sensor messages"""
    id: int
    gateway_id: Optional[str] = None
    rssi: Optional[float] = None
    snr: Optional[float] = None
    channel_rssi: Optional[float] = None
    lora_bandwidth: Optional[int] = None
    lora_spreading_factor: Optional[int] = None
    lora_coding_rate: Optional[str] = None
    device_id: Optional[int] = None
    sensor_metric_id: Optional[int] = None
    tags: List[TagRead] = []


class SensorMessageUpdate(SQLModel):
    """Schema for updating sensor messages"""
    gateway_id: Optional[str] = None
    rssi: Optional[float] = None
    snr: Optional[float] = None
    channel_rssi: Optional[float] = None
    lora_bandwidth: Optional[int] = Field(None, ge=0)
    lora_spreading_factor: Optional[int] = Field(None, ge=7, le=12)
    lora_coding_rate: Optional[str] = None
    device_id: Optional[int] = None
    sensor_metric_id: Optional[int] = None
    tags: Optional[List[str]] = None


# Metric Schemas
class CreateMetricRequest(SQLModel):
    """Request model for creating a new metric with optional sensor message data"""
    device_name: str
    timestamp_device: Optional[int] = None
    timestamp_server: Optional[int] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    air_pressure: Optional[float] = None
    battery_voltage: Optional[float] = None
    # New SensorMetric fields
    confirmed: Optional[bool] = None
    consumed_airtime: Optional[float] = Field(None, ge=0)
    f_cnt: Optional[int] = Field(None, ge=0)
    frequency: Optional[int] = Field(None, ge=0)
    # Optional multiple sensor messages
    sensor_messages: Optional[List[SensorMessageCreate]] = None


class SensorMetricRead(SQLModel):
    """Schema for reading sensor metrics with nested sensor messages"""
    id: int
    timestamp_device: Optional[int] = None
    timestamp_server: Optional[int] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    air_pressure: Optional[float] = None
    battery_voltage: Optional[float] = None
    device_id: Optional[int] = None
    confirmed: Optional[bool] = None
    consumed_airtime: Optional[float] = None
    f_cnt: Optional[int] = None
    frequency: Optional[int] = None
    tags: List[TagRead] = []
    sensor_messages: List[SensorMessageRead] = []
