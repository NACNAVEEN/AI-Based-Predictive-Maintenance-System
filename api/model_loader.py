import joblib
from pathlib import Path

MODEL_PATH = (
    Path(__file__).parent.parent
    / "models"
    / "predictive_maintenance_model.pkl"
)

model = joblib.load(MODEL_PATH)