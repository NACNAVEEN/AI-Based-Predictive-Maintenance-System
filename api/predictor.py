import pandas as pd

from api.model_loader import model


def classify_risk(probability):

    if probability < 0.25:
        return "Low"

    elif probability < 0.50:
        return "Medium"

    elif probability < 0.75:
        return "High"

    else:
        return "Critical"


def predict_failure(payload):

    temperature_difference = (
        payload.Process_temperature_K
        - payload.Air_temperature_K
    )

    mechanical_stress = (
        payload.Rotational_speed_rpm
        * payload.Torque_Nm
    )

    wear_stress_index = (
        payload.Tool_wear_min
        * payload.Torque_Nm
    )

    type_l = 1 if payload.Type == "L" else 0
    type_m = 1 if payload.Type == "M" else 0

    data = pd.DataFrame([{

        "Air temperature [K]":
            payload.Air_temperature_K,

        "Process temperature [K]":
            payload.Process_temperature_K,

        "Rotational speed [rpm]":
            payload.Rotational_speed_rpm,

        "Torque [Nm]":
            payload.Torque_Nm,

        "Tool wear [min]":
            payload.Tool_wear_min,

        "Temperature_Difference":
            temperature_difference,

        "Mechanical_Stress":
            mechanical_stress,

        "Wear_Stress_Index":
            wear_stress_index,

        "Type_L":
            type_l,

        "Type_M":
            type_m
    }])

    prediction = int(
        model.predict(data)[0]
    )

    probability = float(
        model.predict_proba(data)[0][1]
    )

    risk = classify_risk(probability)

    return {
        "prediction": prediction,
        "failure_probability": round(probability, 4),
        "risk_category": risk
    }