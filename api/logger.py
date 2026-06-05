import logging
from pathlib import Path

# Place logs in the database directory so they are persisted on mounted volumes (Render/Docker)
LOG_DIR = Path(__file__).resolve().parent.parent / "database" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler(LOG_FILE, encoding="utf-8")  # File output
    ]
)

logger = logging.getLogger("predictive_maintenance")
logger.info("Logging initialized. Output file: %s", LOG_FILE)
