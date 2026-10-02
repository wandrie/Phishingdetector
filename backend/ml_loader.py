import os
import json
import joblib

try:
    from config import settings
except ImportError:
    class settings:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, "models", "model.joblib"))
        ENCODER_PATH = os.getenv("ENCODER_PATH", os.path.join(BASE_DIR, "models", "label_encoder.joblib"))
        FEATURES_JSON_PATH = os.getenv("FEATURES_JSON_PATH", os.path.join(BASE_DIR, "models", "features.json"))

        @classmethod
        def get(cls, key, default=None):
            return getattr(cls, key, default)

class MLModelContainer:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.feature_names = []
        self.load_artifacts()

    def load_artifacts(self):
        try:
            if os.path.exists(settings.MODEL_PATH):
                self.model = joblib.load(settings.MODEL_PATH)
                print(f"✅ Model ML dimuat: {settings.MODEL_PATH}")
            else:
                print(f"❌ Model tidak ditemukan: {settings.MODEL_PATH}")

            if os.path.exists(settings.ENCODER_PATH):
                self.label_encoder = joblib.load(settings.ENCODER_PATH)
                print(f"✅ Label Encoder dimuat: {settings.ENCODER_PATH}")

            if os.path.exists(settings.FEATURES_JSON_PATH):
                with open(settings.FEATURES_JSON_PATH, "r") as f:
                    features_config = json.load(f)
                    self.feature_names = features_config.get("features", [])
                print(f"✅ Fitur dimuat ({len(self.feature_names)} fitur)")
        except Exception as e:
            print(f"❌ Error saat memuat aset ML: {e}")

# Inisialisasi Instance Tunggal Model
ml_assets = MLModelContainer()