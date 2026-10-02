# 🛡️ Wandrie Phishing URL Detector

![Python](https://img.shields.io/badge/Python-3.1%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-v0.100%2B-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-v1.30%2B-FF4B4B)
![Machine Learning](https://img.shields.io/badge/Model-Light%20GBM-success)

**Wandrie Phishing URL Detector** adalah sistem keamanan siber berbasis Machine Learning yang dirancang untuk menganalisis dan mendeteksi tautan (_URL_) phishing secara real-time. Sistem ini mengombinasikan _backend_ berbasis FastAPI untuk pemrosesan prediksi dan ekstraksi fitur, serta _frontend_ interaktif berbasis Streamlit.

---

## 🎨 Antarmuka Aplikasi

- **Single URL Scanner:** Analisis tingkat keamanan URL individu secara instan.
- **Mass URL Scan:** Fitur pemindaian tautan secara massal melalui unggahan file log/dokumen.
- **Phishing Log History:** Database pencatatan otomatis untuk URL terdeteksi berbahaya.

---

## 📂 Struktur Proyek

```text
Phishingdetector/
├── backend/                  # REST API Service (FastAPI)
│   ├── config.py             # Konfigurasi aplikasi & database
│   ├── db.py                 # Koneksi SQLite database
│   ├── main.py               # Entry point FastAPI & endpoint API
│   ├── ml_loader.py          # Script pemuat model Machine Learning
│   ├── phishing_logs.db      # Database log ancaman (lokal)
│   └── requirements.txt      # Dependensi khusus backend
├── frontend/                 # User Interface (Streamlit)
│   ├── app.py                # Main script Streamlit & UI layout
│   ├── utils/                # Modul pembantu UI & ekstraksi fitur
│   │   └── feature_extractor.py
│   └── requirements.txt      # Dependensi khusus frontend
├── models/                   # Model Machine Learning & Aset Ekstraksi
│   ├── feature_names.pkl
│   ├── label_encoder.pkl
│   ├── model_features.json
│   └── phishing_lgbm_model.pkl # Trained LightGBM
├── .gitignore                # File pengecualian Git
└── README.md                 # Dokumentasi proyek
```
