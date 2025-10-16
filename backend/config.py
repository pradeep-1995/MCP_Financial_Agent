import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE_TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LSTM_MODEL_DIR = os.getenv("LSTM_MODEL_DIR", "./data/models")
PERF_DB_PATH = os.getenv("PERF_DB_PATH", "./data/perf.db")
