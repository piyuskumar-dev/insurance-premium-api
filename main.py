from turtle import lt

from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json


class Patient(BaseModel):

    id: Annotated[str, Field(..., description="Unique identifier for the patient", example="P001")]
    name: Annotated[str, Field(..., description="Name of the patient", example="John Doe")]
    city: Annotated[str, Field(..., description="City of residence", example="New York")]
    age: Annotated[int, Field(..., gt=0, lt=150, description="Age of the patient", example=30)]
    gender: Annotated[Literal["Male", "Female", "Other"]    , Field(..., description="Gender of the patient", example="Male")]
    height: Annotated[float, Field(..., gt=0, description="Height of the patient in m", example=175.5)]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the patient in kg", example=70.5)]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 25:
            return "Normal weight"
        elif 25 <= self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"


class Update_Patient(BaseModel):

    name: Annotated[Optional[str], Field( description="Name of the patient", example="John Doe")]
    city: Annotated[Optional[str], Field( description="City of residence", example="New York")]
    age: Annotated[Optional[int], Field( gt=0, lt=150, description="Age of the patient", example=30)]
    gender: Annotated[Optional[Literal["Male", "Female", "Other"]], Field( description="Gender of the patient", example="Male")]
    height: Annotated[Optional[float], Field( gt=0, description="Height of the patient in m", example=175.5)]
    weight: Annotated[Optional[float], Field( gt=0, description="Weight of the patient in kg", example=70.5)]




app = FastAPI()

def load_data():
    json_file = 'patients.json'
    with open(json_file, 'r') as f:
        data = json.load(f)

    return data

def save_data(data):
    json_file = 'patients.json'
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)


@app.get("/")
def hello():
    return {'message': 'Patient record management system API'}

@app.get("/about")
def about():
    return {'message':'This is a patience record management system to keep the record of patient in one place where the doctor can view the records update, delete and create new patient ID'}

@app.get("/view")
def view():
    data = load_data()
    return data

@app.get("/view/{patient_id}")
def view_patient(patient_id: str = Path(..., description='ID of patient in database', example="P001")):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description='Field to sort by', example="height"), order: str = Query("asc", description="Sort order", example="asc")):
    data = load_data()
    if sort_by not in ['bmi', 'height', 'weight']:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid sort order")
    
    sort_order = True if order == 'desc' else False

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient ID already exists")
    
    data[patient.id] = patient.model_dump(exclude=['id'])

    save_data(data)

    return JSONResponse(status_code=201, content={"message": "Patient created successfully"})


@app.put("/update/{patient_id}")
def update_patient(patient_id: str, updated_patient: Update_Patient):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=400, detail="Patient doesn't exist")
    
    for key, value in updated_patient.model_dump(exclude_unset=True).items():
        data[patient_id][key] = value
    
    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient updated successfully"})