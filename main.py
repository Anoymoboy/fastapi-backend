from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np

app = FastAPI()

# Request model for position analysis
class PositionRequest(BaseModel):
    a: float  # Crank length
    b: float  # Coupler length
    c: float  # Follower length
    d: float  # Ground link length
    theta2: float  # Input angle (degrees) for θ2

@app.post("/compute_position/")
def compute_position(data: PositionRequest):
    """Computes θ3 and θ4 for a four-bar linkage using Freudenstein’s equation."""
    
    # Convert theta2 to radians
    theta2_rad = np.radians(data.theta2)

    # Compute constants
    K1 = (data.d**2 - data.a**2 - data.b**2 - data.c**2) / (2 * data.a * data.c)
    K2 = data.d / data.a
    K3 = data.d / data.c
    K4 = data.b / data.a
    K5 = data.b / data.c

    # Compute A, B, C for θ3
    A = np.cos(theta2_rad) - K1 - K2 * np.cos(theta2_rad) + K3
    B = -2 * np.sin(theta2_rad)
    C = K1 + (K2 - K3) * np.cos(theta2_rad) + 1

    # Compute θ3 using Freudenstein’s equation
    discriminant = B**2 - 4 * A * C
    if discriminant < 0:
        return {"error": "No real solution for θ3 (linkage configuration invalid)"}

    theta3_rad_1 = 2 * np.arctan((-B + np.sqrt(discriminant)) / (2 * A))
    theta3_rad_2 = 2 * np.arctan((-B - np.sqrt(discriminant)) / (2 * A))

    # Convert θ3 solutions to degrees
    theta3_1 = np.degrees(theta3_rad_1)
    theta3_2 = np.degrees(theta3_rad_2)

    # Compute D, E, F for θ4
    D1 = np.cos(theta2_rad) - K4 + K5 * np.cos(theta3_rad_1) + K2
    D2 = np.cos(theta2_rad) - K4 + K5 * np.cos(theta3_rad_2) + K2
    E = -2 * np.sin(theta2_rad)
    F1 = K4 + (K5 - K2) * np.cos(theta3_rad_1) + 1
    F2 = K4 + (K5 - K2) * np.cos(theta3_rad_2) + 1

    # Compute θ4 using Freudenstein’s equation
    discriminant1 = E**2 - 4 * D1 * F1
    discriminant2 = E**2 - 4 * D2 * F2

    if discriminant1 < 0 or discriminant2 < 0:
        return {"error": "No real solution for θ4 (linkage configuration invalid)"}

    theta4_rad_1 = 2 * np.arctan((-E + np.sqrt(discriminant1)) / (2 * D1))
    theta4_rad_2 = 2 * np.arctan((-E + np.sqrt(discriminant2)) / (2 * D2))

    # Convert θ4 solutions to degrees
    theta4_1 = np.degrees(theta4_rad_1)
    theta4_2 = np.degrees(theta4_rad_2)

    # Return both possible solutions
    return {
        "message": "Kinematics computed successfully!",
        "theta3_options": [theta3_1, theta3_2],
        "theta4_options": [theta4_1, theta4_2]
    }
