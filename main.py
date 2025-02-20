from fastapi import FastAPI, Request
from pydantic import BaseModel
import numpy as np

app = FastAPI()

class KinematicsRequest(BaseModel):
    a: float | None = 0
    b: float | None = 0
    c: float | None = 0
    theta1: float | None = 0

@app.post("/compute_kinematics/")
async def compute_kinematics(request: Request):
    """Converts input to float and computes kinematics."""
    try:
        # Read JSON request
        data = await request.json()

        # Ensure values are not None before converting to float
        a = float(data["a"]) if data.get("a") is not None else 0.0
        b = float(data["b"]) if data.get("b") is not None else 0.0
        c = float(data["c"]) if data.get("c") is not None else 0.0
        theta1 = float(data["theta1"]) if data.get("theta1") is not None else 0.0

        # Compute kinematics
        theta1_rad = np.radians(theta1)
        x_b = a * np.cos(theta1_rad)
        y_b = a * np.sin(theta1_rad)
        x_c = x_b + b
        y_c = y_b

        return {"message": "Kinematics computed successfully!", "B": [x_b, y_b], "C": [x_c, y_c]}
    
    except Exception as e:
        return {"error": f"Invalid input. Ensure all values are numbers. Details: {str(e)}"}
