from fastapi import FastAPI, Request
from pydantic import BaseModel
import numpy as np

app = FastAPI()

class KinematicsRequest(BaseModel):
    a: float
    b: float
    c: float
    theta1: float

@app.post("/compute_kinematics/")
async def compute_kinematics(request: Request):
    """Converts input to float and computes kinematics."""
    try:
        # Read JSON request
        data = await request.json()

        # Convert values to float (handles string inputs)
        a = float(data.get("a", 0))
        b = float(data.get("b", 0))
        c = float(data.get("c", 0))
        theta1 = float(data.get("theta1", 0))

        # Compute kinematics
        theta1_rad = np.radians(theta1)
        x_b = a * np.cos(theta1_rad)
        y_b = a * np.sin(theta1_rad)
        x_c = x_b + b
        y_c = y_b

        return {"message": "Kinematics computed successfully!", "B": [x_b, y_b], "C": [x_c, y_c]}
    
    except ValueError:
        return {"error": "Invalid input. Ensure all values are numbers."}
