import time
from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session

from api.logger import logger
from api.schemas import MachineData
from api.predictor import predict_failure
from database.connection import get_db
from database.models import Base, PredictionLog
from database.connection import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Predictive Maintenance API",
    version="1.0"
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log incoming request path
    logger.info("Incoming request: %s %s", request.method, request.url.path)
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(
            "Completed request: %s %s - Status: %d - Latency: %.2fms",
            request.method, request.url.path, response.status_code, process_time
        )
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(
            "Failed request: %s %s - Error: %s - Latency: %.2fms",
            request.method, request.url.path, str(e), process_time, exc_info=True
        )
        raise e


@app.get("/")
def health_check():
    logger.info("Health check endpoint accessed")
    return {
        "message": "Predictive Maintenance API Running"
    }


@app.post("/predict")
def predict(
    payload: MachineData,
    db: Session = Depends(get_db)
):
    logger.info(
        "Predicting maintenance risk for machine type: %s, rotational_speed: %d rpm, torque: %.2f Nm",
        payload.Type, payload.Rotational_speed_rpm, payload.Torque_Nm
    )

    result = predict_failure(payload)
    
    logger.info(
        "Prediction result - Status: %s, Failure Prob: %.4f, Risk Category: %s",
        "FAILURE" if result["prediction"] == 1 else "NORMAL",
        result["failure_probability"],
        result["risk_category"]
    )

    log = PredictionLog(
        machine_type=payload.Type,
        air_temperature=payload.Air_temperature_K,
        process_temperature=payload.Process_temperature_K,
        rotational_speed=payload.Rotational_speed_rpm,
        torque=payload.Torque_Nm,
        tool_wear=payload.Tool_wear_min,
        prediction=result["prediction"],
        failure_probability=result["failure_probability"],
        risk_category=result["risk_category"]
    )

    try:
        db.add(log)
        db.commit()
        db.refresh(log)
        logger.info("Successfully saved prediction log to database with ID: %d", log.id)
    except Exception as db_err:
        logger.error("Failed to write prediction log to database: %s", str(db_err), exc_info=True)
        # We still return the prediction even if logging fails
        db.rollback()

    return result


@app.get("/logs")
def get_logs(db: Session = Depends(get_db)):
    """Retrieve all prediction logs in JSON format."""
    logs = db.query(PredictionLog).all()
    return logs


@app.get("/logs/csv")
def get_logs_csv(db: Session = Depends(get_db)):
    """Export prediction logs in CSV format, ideal for Power BI."""
    import csv
    import io
    from fastapi.responses import StreamingResponse

    logs = db.query(PredictionLog).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "id", "machine_type", "air_temperature", "process_temperature", 
        "rotational_speed", "torque", "tool_wear", "prediction", 
        "failure_probability", "risk_category", "created_at"
    ])
    
    # Write data rows
    for log in logs:
        writer.writerow([
            log.id, log.machine_type, log.air_temperature, log.process_temperature,
            log.rotational_speed, log.torque, log.tool_wear, log.prediction,
            log.failure_probability, log.risk_category, log.created_at
        ])
        
    output.seek(0)
    return StreamingResponse(
        output, 
        media_type="text/csv", 
        headers={"Content-Disposition": "attachment; filename=prediction_logs.csv"}
    )