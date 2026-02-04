from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SensorData(BaseModel):
    ir_value: float
    us_value: float
    acc_x: float
    acc_y: float
    acc_z: float
    gyr_x: float
    gyr_y: float
    gyr_z: float

class PredictionResponse(BaseModel):
    predicted_water_level: float
    detected_turbidity_status: str

class SensorRecord(BaseModel):
    id: int
    timestamp: datetime
    ir_value: float
    us_value: float
    acc_x: float
    acc_y: float
    acc_z: float
    gyr_x: float
    gyr_y: float
    gyr_z: float
    predicted_water_level: float
    detected_turbidity_status: str

class SensorRecordUpdate(BaseModel):
    ir_value: Optional[float] = None
    us_value: Optional[float] = None
    acc_x: Optional[float] = None
    acc_y: Optional[float] = None
    acc_z: Optional[float] = None
    gyr_x: Optional[float] = None
    gyr_y: Optional[float] = None
    gyr_z: Optional[float] = None
