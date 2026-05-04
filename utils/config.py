import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class Config:
    # APIs
    OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
    GITHUB_TOKEN    = os.getenv("GITHUB_TOKEN")
    WAPPALYZER_KEY  = os.getenv("WAPPALYZER_API_KEY")
    BUILTWITH_KEY   = os.getenv("BUILTWITH_API_KEY")
    EMAIL_SENDER    = os.getenv("EMAIL_SENDER")
    EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
    EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD")


    # Chemins
    DB_PATH         = os.getenv("DB_PATH", "data/db/techstack.db")
    RAW_DATA_PATH   = "data/raw/"
    PROCESSED_PATH  = "data/processed/"

    # Paramètres scraping
    REQUEST_DELAY   = 1.5
    MAX_RETRIES     = 3
    TIMEOUT         = 10

config = Config()

# Setup logger
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    level=os.getenv("LOG_LEVEL", "INFO")
)

print("✅ Config chargée avec succès !")
