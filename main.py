from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np

app = FastAPI()

# Define a request model for kinematics calculations
class KinematicsRequest(BaseModel):
    a: float
    b: float
    c: float
    theta1: float

@app.post("/compute_kinematics/")
def compute_kinematics(data: KinematicsRequest):
    """Computes four-bar linkage kinematics given user input."""
    
    # Convert theta1 from degrees to radians
    theta1_rad = np.radians(data.theta1)

    # Compute joint positions
    x_b = data.a * np.cos(theta1_rad)
    y_b = data.a * np.sin(theta1_rad)
    x_c = x_b + data.b
    y_c = y_b

    return {
        "message": "Kinematics computed successfully!",
        "B": [x_b, y_b],
        "C": [x_c, y_c]
    }

