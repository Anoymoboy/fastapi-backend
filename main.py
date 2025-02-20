from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Define a request model to properly receive JSON data
class KinematicsRequest(BaseModel):
    a: float
    b: float
    c: float
    theta1: float
    x_b: float
    y_b: float
    x_c: float
    y_c: float

kinematics_results = {}

@app.post("/receive_kinematics/")
def receive_kinematics(data: KinematicsRequest):
    """Receives kinematics results from MATLAB."""
    global kinematics_results
    kinematics_results = data.dict()  # Convert to dictionary
    return {"message": "Kinematics data received successfully!"}

@app.get("/kinematics/")
def get_kinematics():
    """Returns the last stored kinematics result."""
    if not kinematics_results:
        return {"error": "No kinematics data available"}
    return kinematics_results
