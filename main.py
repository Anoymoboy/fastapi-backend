from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from functools import lru_cache
import logging
from fastapi.middleware.cors import CORSMiddleware

# Setup logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS to allow requests from Bubble.io
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your Bubble.io domain for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check route
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

# Caching function for efficiency (but avoids unhashable issues)
def compute_kinematics(a: float, b: float, c: float, d: float, theta2: float):
    """Computes θ4 first, then θ3 using Freudenstein’s equation for a four-bar linkage."""
    try:
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

        # Check for real solutions
        discriminant = B**2 - 4 * A * C
        if discriminant < 0:
            raise ValueError("No real solution for θ4")

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
            raise ValueError("No real solution for θ3")

        theta3_rad_1 = 2 * np.arctan((-E - np.sqrt(discriminant1)) / (2 * D))
        theta3_rad_2 = 2 * np.arctan((-E + np.sqrt(discriminant1)) / (2 * D))

        theta3_1 = np.degrees(theta3_rad_1)
        theta3_2 = np.degrees(theta3_rad_2)

        return {
            "theta4_options": [theta4_1, theta4_2],
            "theta3_options": [theta3_1, theta3_2]
        }
    except Exception as e:
        logger.error(f"Error in computation: {e}")
        raise ValueError("Math error in kinematic calculations.")

@app.post("/compute_position/")
async def compute_position(request_data: PositionRequest):
    """API Endpoint to compute four-bar linkage kinematics."""
    try:
        # Extract values from request
        a = request_data.a
        b = request_data.b
        c = request_data.c
        d = request_data.d
        theta2 = request_data.theta2

        # Log received data for debugging
        logger.info(f"Received data: {request_data}")

        # Compute kinematics
        result = compute_kinematics(a, b, c, d, theta2)

        # Log response
        logger.info(f"Response: {result}")

        return {"message": "Kinematics computed successfully!", "result": result}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Server error")

# Run FastAPI on Railway's required settings
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
