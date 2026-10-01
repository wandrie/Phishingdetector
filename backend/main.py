import sys
import datetime
import pandas as pd
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Impor Konfigurasi & Modul Terpisah
from config import settings
from db import init_db, save_phishing_log, fetch_all_logs, clear_all_phishing_logs, delete_phishing_log_by_id
from ml_loader import ml_assets

# Menambahkan root project ke sys.path agar impor utilitas frontend tetap berfungsi
if settings.PROJECT_ROOT not in sys.path:
    sys.path.insert(0, settings.PROJECT_ROOT)

from frontend.utils.feature_extractor import extract_features_from_url

# Inisialisasi FastAPI & Database
app = FastAPI(title=settings.APP_NAME)

@app.on_event("startup")
def startup_event():
    init_db()

# Schema Pydantic Request
class PredictRequest(BaseModel):
    url: str = ""
    features: Optional[Dict[str, Any]] = None

# Endpoint Prediksi URL
@app.post("/predict")
def predict(data: PredictRequest):
    if ml_assets.model is None:
        raise HTTPException(
            status_code=500, 
            detail="Model ML tidak dimuat di server."
        )
        
    if not data.url:
        raise HTTPException(status_code=400, detail="URL tidak boleh kosong.")

    try:
        # Ekstraksi Fitur dari URL
        extracted_dict = extract_features_from_url(data.url, ml_assets.feature_names)
        df_features = pd.DataFrame([extracted_dict])
        
        if ml_assets.feature_names:
            df_features = df_features.reindex(columns=ml_assets.feature_names, fill_value=0)
        
        # Prediksi Model ML (0: Legitimate, 1: Phishing)
        prediction = int(ml_assets.model.predict(df_features)[0])
        
        status_label = "Phishing" if prediction == 1 else "Legitimate"
        if ml_assets.label_encoder is not None:
            try:
                status_label = str(ml_assets.label_encoder.inverse_transform([prediction])[0])
            except Exception:
                pass
        
        # Probabilitas Prediksi
        if hasattr(ml_assets.model, "predict_proba"):
            probability = ml_assets.model.predict_proba(df_features)[0].tolist()
        else:
            probability = [0.0, 1.0] if prediction == 1 else [1.0, 0.0]

        # Simpan Log ke DB jika terindikasi Phishing
        if prediction == 1 and data.url:
            confidence = round(probability[1] * 100, 2) if len(probability) == 2 else 100.0
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_phishing_log(data.url, confidence, created_at)

        return {
            "prediction": prediction,
            "status_label": status_label,
            "probability": probability
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint Mengambil Log Phishing
@app.get("/phishing-logs")
def get_phishing_logs():
    logs = fetch_all_logs()
    return {"logs": logs}

@app.delete("/phishing-logs")
def clear_logs():
    clear_all_phishing_logs()
    return {"message": "Seluruh log phishing berhasil dihapus."}

# Endpoint untuk menghapus 1 log spesifik berdasarkan ID
@app.delete("/phishing-logs/{log_id}")
def delete_log(log_id: int):
    delete_phishing_log_by_id(log_id)
    return {"message": f"Log dengan ID {log_id} berhasil dihapus."}