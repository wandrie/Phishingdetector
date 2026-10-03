# 🛡️ Wandrie Phishing URL Detector

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-v0.100%2B-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-v1.30%2B-FF4B4B)
![Machine Learning](https://img.shields.io/badge/Model-LightGBM-success)
![Accuracy](https://img.shields.io/badge/Accuracy-96.94%25-brightgreen)

**Wandrie Phishing URL Detector** adalah sistem keamanan siber berbasis _Machine Learning_ yang dirancang untuk menganalisis dan mendeteksi tautan (_URL_) _phishing_ secara _real-time_. Sistem ini menerapkan arsitektur _decoupled_ yang mengombinasikan _backend_ REST API berbasis **FastAPI** untuk analisis dan inferensi model, serta _frontend_ interaktif berbasis **Streamlit**.

---

## 🚀 Fitur Utama

- **Single URL Scanner:** Analisis instan tingkat risiko URL individu beserta persentase probabilitas bahaya.
- **Mass URL Scan:** Fitur pemindaian banyak tautan sekaligus melalui unggahan file (CSV/TXT).
- **Threat Logging & Management:** Pencatatan otomatis URL terindikasi _phishing_ ke basis data SQLite beserta fitur pengelolaan log (_get/delete_).
- **Interactive REST API:** API publik dengan dokumentasi Swagger UI interaktif bawaan FastAPI.

---

## 📊 Performa Model Machine Learning

Model utama menggunakan algoritma **LightGBM** yang dilatih pada dataset fitur eksklusif berbasis URL, dengan metrik performa hasil pengujian sebagai berikut:

- **Accuracy:** 96.94%
- **Precision (Phishing):** 0.97
- **Recall (Phishing):** 0.97
- **F1-Score:** 0.97

---

## 📂 Struktur Proyek

```text
Phishingdetector/
├── backend/                  # REST API Service (FastAPI)
│   ├── config.py             # Konfigurasi aplikasi & pydantic settings
│   ├── db.py                 # Manajemen SQLite database & log
│   ├── main.py               # Entry point FastAPI & endpoint REST API
│   ├── ml_loader.py          # Script pemuat aset model Machine Learning
│   ├── phishing_logs.db      # Database log ancaman (lokal)
│   └── requirements.txt      # Dependensi Python khusus backend
├── frontend/                 # User Interface (Streamlit)
│   ├── app.py                # Script antarmuka utama Streamlit
│   ├── utils/                # Modul ekstraksi fitur URL
│   │   └── feature_extractor.py
│   └── requirements.txt      # Dependensi Python khusus frontend
├── models/                   # Model ML Terlatih & Asset Pickle
│   ├── feature_names.pkl
│   ├── label_encoder.pkl
│   ├── model_features.json
│   └── phishing_lgbm_model.pkl # Model LightGBM terlatih
├── .env.example              # Contoh konfigurasi environment
├── .gitignore                # Pengecualian berkas Git
└── README.md                 # Dokumentasi proyek
```
