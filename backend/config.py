import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Nama & Informasi Aplikasi
    APP_NAME: str = "Wandrie Phishing Detector API"
    DEBUG: bool = True
    
    # Resolusi Path Direktori Utama
    BACKEND_DIR: str = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT: str = os.path.dirname(BACKEND_DIR)
    
    # Path Database SQLite
    DB_PATH: str = os.path.join(BACKEND_DIR, "phishing_logs.db")
    
    # Path Aset Machine Learning
    MODEL_DIR: str = os.path.join(PROJECT_ROOT, "models")
    MODEL_PATH: str = os.path.join(MODEL_DIR, "phishing_rf_model.pkl")
    ENCODER_PATH: str = os.path.join(MODEL_DIR, "label_encoder.pkl")
    FEATURES_JSON_PATH: str = os.path.join(MODEL_DIR, "model_features.json")

    class Config:
        env_file = ".env"
        extra = "ignore"

# Single Instance Konfigurasi
settings = Settings()