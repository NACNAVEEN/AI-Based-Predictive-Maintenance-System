from pydantic import BaseModel


class MachineData(BaseModel):

    Type: str

    Air_temperature_K: float

    Process_temperature_K: float

    Rotational_speed_rpm: int

    Torque_Nm: float

    Tool_wear_min: int