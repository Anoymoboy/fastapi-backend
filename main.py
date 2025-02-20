from fastapi import FastAPI, Request
from pydantic import BaseModel
import numpy as np

app = FastAPI()

# Define input model for position analysis
class PositionRequest(BaseModel):
    a: float  # Crank length
    b: float  # Coupler length
    c: float  # Follower length
    d: float  # Ground link length
    theta2: float  # Input angle in degrees

@app.post("/compute_position/")
async def compute_position(request: Request):
    """Computes θ4 first, then θ3 using Freudenstein’s equation for a four-bar linkage."""
    data = await request.json()

    try:
        # Extract values and ensure they are float
        a = float(data.get("a", 0) or 0)
        b = float(data.get("b", 0) or 0)
        c = float(data.get("c", 0) or 0)
        d = float(data.get("d", 0) or 0)
        theta2 = float(data.get("theta2", 0) or 0)

        # Convert theta2 to radians
        theta2_rad = np.radians(theta2)

        # Compute constants
        K1 = (d**2 - a**2 - b**2 - c**2) / (2 * a * c)
        K2 = d / a
        K3 = d / c
        K4 = b / a
        K5 = b / c

        # Compute A, B, C for θ4
        A = np.cos(theta2_rad) - K1 - K2 * np.cos(theta2_rad) + K3
        B = -2 * np.sin(theta2_rad)
        C = K1 + (K2 - K3) * np.cos(theta2_rad) + 1

        # Compute θ4 using Freudenstein’s equation
        discriminant = B**2 - 4 * A * C
        if discriminant < 0:
            return {"error": "No real solution for θ4"}

        theta4_rad_1 = 2 * np.arctan((-B + np.sqrt(discriminant)) / (2 * A))
        theta4_rad_2 = 2 * np.arctan((-B - np.sqrt(discriminant)) / (2 * A))

        theta4_1 = np.degrees(theta4_rad_1)
        theta4_2 = np.degrees(theta4_rad_2)

        # Compute D, E, F for θ3
        D1 = np.cos(theta2_rad) - K4 + K5 * np.cos(theta4_rad_1) + K2
        D2 = np.cos(theta2_rad) - K4 + K5 * np.cos(theta4_rad_2) + K2
        E = -2 * np.sin(theta2_rad)
        F1 = K4 + (K5 - K2) * np.cos(theta4_rad_1) + 1
        F2 = K4 + (K5 - K2) * np.cos(theta4_rad_2) + 1

        discriminant1 = E**2 - 4 * D1 * F1
        discriminant2 = E**2 - 4 * D2 * F2

        if discriminant1 < 0 or discriminant2 < 0:
            return {"error": "No real solution for θ3"}

        theta3_rad_1 = 2 * np.arctan((-E + np.sqrt(discriminant1)) / (2 * D1))
        theta3_rad_2 = 2 * np.arctan((-E + np.sqrt(discriminant2)) / (2 * D2))

        theta3_1 = np.degrees(theta3_rad_1)
        theta3_2 = np.degrees(theta3_rad_2)

        # Return both possible solutions
        return {
            "message": "Kinematics computed successfully!",
            "theta4_options": [theta4_1, theta4_2],  # θ4 first (Corrected)
            "theta3_options": [theta3_1, theta3_2]   # Then θ3 (Corrected)
        }

    except Exception as e:
        return {"error": f"Invalid input: {str(e)}"}
