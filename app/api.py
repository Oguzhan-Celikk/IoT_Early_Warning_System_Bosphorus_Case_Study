from fastapi import APIRouter, HTTPException
from app.schemas import SensorData, PredictionResponse, SensorRecord, SensorRecordUpdate
from ml_core.inference import Predictor
from ml_core.preprocessing import load_data
import pandas as pd
from typing import List
from datetime import datetime

router = APIRouter()

# Global instances
predictor_instance = None
df_high = None
df_medium = None
df_low = None

# In-memory storage for sensor records (simulating a database)
sensor_records = {}
record_counter = 0

def get_predictor():
    global predictor_instance
    if predictor_instance is None:
        predictor_instance = Predictor()
    return predictor_instance

def load_datasets_global(): #
    global df_high, df_medium, df_low
    df_high, df_medium, df_low = load_data(data_dir='data')

@router.post("/predict", response_model=PredictionResponse)
def predict(data: SensorData):
    pred = get_predictor()
    features = [
        data.ir_value, data.us_value, 
        data.acc_x, data.acc_y, data.acc_z, 
        data.gyr_x, data.gyr_y, data.gyr_z
    ]
    try:
        result = pred.predict(features)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/datasets/high")
def get_high_turbidity_data(limit: int = 100):
    if df_high is None: load_datasets_global()
    if df_high is None: raise HTTPException(status_code=500, detail="Datasets not loaded.")
    return df_high.head(limit).to_dict(orient='records')

@router.get("/datasets/medium")
def get_medium_turbidity_data(limit: int = 100):
    if df_medium is None: load_datasets_global()
    if df_medium is None: raise HTTPException(status_code=500, detail="Datasets not loaded.")
    return df_medium.head(limit).to_dict(orient='records')

@router.get("/datasets/low")
def get_low_turbidity_data(limit: int = 100):
    if df_low is None: load_datasets_global()
    if df_low is None: raise HTTPException(status_code=500, detail="Datasets not loaded.")
    return df_low.head(limit).to_dict(orient='records')

# CRUD Operations for Sensor Records

@router.get("/records", response_model=List[SensorRecord])
def get_all_records():
    """Get all sensor records"""
    return list(sensor_records.values())

@router.get("/records/{record_id}", response_model=SensorRecord)
def get_record(record_id: int):
    """Get a specific sensor record by ID"""
    if record_id not in sensor_records:
        raise HTTPException(status_code=404, detail="Record not found")
    return sensor_records[record_id]

@router.post("/records", response_model=SensorRecord)
def create_record(data: SensorData):
    """Create a new sensor record"""
    global record_counter
    record_counter += 1
    
    # Optionally predict on creation
    pred = get_predictor()
    features = [
        data.ir_value, data.us_value, 
        data.acc_x, data.acc_y, data.acc_z, 
        data.gyr_x, data.gyr_y, data.gyr_z
    ]
    prediction = pred.predict(features)
    
    record = SensorRecord(
        id=record_counter,
        timestamp=datetime.now(),
        ir_value=data.ir_value,
        us_value=data.us_value,
        acc_x=data.acc_x,
        acc_y=data.acc_y,
        acc_z=data.acc_z,
        gyr_x=data.gyr_x,
        gyr_y=data.gyr_y,
        gyr_z=data.gyr_z,
        predicted_water_level=prediction["predicted_water_level"],
        detected_turbidity_status=prediction["detected_turbidity_status"]
    )
    
    sensor_records[record_counter] = record
    return record

@router.put("/records/{record_id}", response_model=SensorRecord)
def update_record(record_id: int, data: SensorRecordUpdate):
    """Update an existing sensor record"""
    if record_id not in sensor_records:
        raise HTTPException(status_code=404, detail="Record not found")
    
    record = sensor_records[record_id]
    update_data = data.dict(exclude_unset=True)
    
    # Update fields
    for field, value in update_data.items():
        if hasattr(record, field) and value is not None:
            setattr(record, field, value)
    
    # Re-predict if sensor values changed
    if any(field in update_data for field in ['ir_value', 'us_value', 'acc_x', 'acc_y', 'acc_z', 'gyr_x', 'gyr_y', 'gyr_z']):
        pred = get_predictor()
        features = [
            record.ir_value, record.us_value,
            record.acc_x, record.acc_y, record.acc_z,
            record.gyr_x, record.gyr_y, record.gyr_z
        ]
        prediction = pred.predict(features)
        record.predicted_water_level = prediction["predicted_water_level"]
        record.detected_turbidity_status = prediction["detected_turbidity_status"]
    
    sensor_records[record_id] = record
    return record

@router.delete("/records/{record_id}")
def delete_record(record_id: int):
    """Delete a sensor record"""
    if record_id not in sensor_records:
        raise HTTPException(status_code=404, detail="Record not found")
    
    deleted_record = sensor_records.pop(record_id)
    return {"message": "Record deleted successfully", "deleted_record": deleted_record}

@router.delete("/records")
def delete_all_records():
    """Delete all sensor records"""
    global sensor_records
    count = len(sensor_records)
    sensor_records.clear()
    return {"message": f"All {count} records deleted successfully"}
