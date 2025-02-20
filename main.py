from fastapi import FastAPI, Request
from pydantic import BaseModel
import numpy as np

app = FastAPI()

class PositionRequest(BaseModel):
    a: float | None = 0
    b: float | None = 0
    c: float | None = 0
    d: float | None = 0
    theta2: float | None = 0

@app.post("/compute_position/")
async def compute_position(request: Request):
    """Logs and processes the incoming request for debugging."""
    data = await request.json()
    print("Received request:", data)  # Log the incoming JSON data

    try:
        # Ensure all values are numbers, replacing None with 0
        a = float(data.get("a", 0) or 0)
        b = float(data.get("b", 0) or 0)
        c = float(data.get("c", 0) or 0)
        d = float(data.get("d", 0) or 0)
        theta2 = float(data.get("theta2", 0) or 0)

        return {
            "message": "Received data successfully",
            "a": a, "b": b, "c": c, "d": d, "theta2": theta2
        }

    except Exception as e:
        return {"error": f"Invalid input: {str(e)}"}
