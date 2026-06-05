from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime
)

from sqlalchemy.orm import declarative_base

from datetime import datetime

Base = declarative_base()


class PredictionLog(Base):

    __tablename__ = "prediction_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    machine_type = Column(String(10))

    air_temperature = Column(Float)

    process_temperature = Column(Float)

    rotational_speed = Column(Integer)

    torque = Column(Float)

    tool_wear = Column(Integer)

    prediction = Column(Integer)

    failure_probability = Column(Float)

    risk_category = Column(String(20))

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )