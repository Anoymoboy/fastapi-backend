from fastapi import FastAPI, Request
from pydantic import BaseModel
import numpy as np
from functools import lru_cache
import logging
import uvicorn

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Health check route (to test if FastAPI is running)
@app.get("/")
def home():
    return {"message": "FastAPI is running on Railway!"}

# Define input model
class PositionRequest(BaseModel):
    a: float  # Crank length
    b: float  # Coupler length
    c: float  # Follower length
    d: float  # Ground link length
    theta2: float  # Input angle in degrees

# Caching function to avoid redundant calculations
@lru_cache(maxsize=100)
def compute_kinematics(a, b, c, d, theta2):
    """Computes θ4 first, then θ3 using Freudenstein’s equation for a four-bar linkage."""
    theta2_rad = np.radians(theta2)

    # Compute constants
    K1 = d / a
    K2 = d / c
    K3 = (a**2 - b**2 + c**2 + d**2) / (2 * a * c)
    K4 = d / b
    K5 = (c**2 - d**2 - a**2 - b**2) / (2 * a * b)

    # Compute A, B, C for θ4
    A = np.cos(theta2_rad) - K1 - K2 * np.cos(theta2_rad) + K3
    B = -2 * np.sin(theta2_rad)
    C = K1 - (K2 + 1) * np.cos(theta2_rad) + K3

    # Compute θ4 using Freudenstein’s equation
    discriminant = B**2 - 4 * A * C
    if discriminant < 0:
        return {"error": "No real solution for θ4"}

    theta4_rad_1 = 2 * np.arctan((-B - np.sqrt(discriminant)) / (2 * A))
    theta4_rad_2 = 2 * np.arctan((-B + np.sqrt(discriminant)) / (2 * A))

    theta4_1 = np.degrees(theta4_rad_1)
    theta4_2 = np.degrees(theta4_rad_2)

    # Compute D, E, F for θ3
    D = np.cos(theta2_rad) - K1 + K4 * np.cos(theta2_rad) + K5
    E = -2 * np.sin(theta2_rad)
    F = K1 + (K4 - 1) * np.cos(theta2_rad) + K5

    discriminant1 = E**2 - 4 * D * F
    if discriminant1 < 0:
        return {"error": "No real solution for θ3"}

    theta3_rad_1 = 2 * np.arctan((-E - np.sqrt(discriminant1)) / (2 * D))
    theta3_rad_2 = 2 * np.arctan((-E + np.sqrt(discriminant1)) / (2 * D))

    theta3_1 = np.degrees(theta3_rad_1)
    theta3_2 = np.degrees(theta3_rad_2)

    return {
        "theta4_options": [theta4_1, theta4_2],
        "theta3_options": [theta3_1, theta3_2]
    }

@app.post("/compute_position/")
async def compute_position(request: Request):
    """API Endpoint to compute four-bar linkage kinematics."""
    data = await request.json()
    
    def safe_float(value, default=0):
    try:
        return float(value) if value is not None else default
    except ValueError:
        return default

a = safe_float(data.get("a"), 0)
b = safe_float(data.get("b"), 0)
c = safe_float(data.get("c"), 0)
d = safe_float(data.get("d"), 0)
theta2 = safe_float(data.get("theta2"), 0)



        # Log received data for debugging
        logger.info(f"Received data: {data}")

        # Compute kinematics
        result = compute_kinematics(a, b, c, d, theta2)

        # Log response
        logger.info(f"Response: {result}")

        return {"message": "Kinematics computed successfully!", "result": result}

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"error": f"Invalid input: {str(e)}"}

# Run FastAPI on Railway's required settings
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

