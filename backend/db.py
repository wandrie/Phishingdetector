import sqlite3
from config import settings

def get_db_connection():
    """Membuat koneksi ke database SQLite."""
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inisialisasi tabel database saat aplikasi startup."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS phishing_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            confidence REAL,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_phishing_log(url: str, confidence: float, created_at: str):
    """Menyimpan tautan yang terindikasi Phishing ke log."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO phishing_logs (url, confidence, created_at)
        VALUES (?, ?, ?)
    """, (url, confidence, created_at))
    conn.commit()
    conn.close()

def fetch_all_logs():
    """Mengambil seluruh daftar log ancaman phishing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, url, confidence, created_at FROM phishing_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_all_phishing_logs():
    """Menghapus seluruh isi log phishing dari tabel."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM phishing_logs")
    conn.commit()
    conn.close()

def delete_phishing_log_by_id(log_id: int):
    """Menghapus satu log berdasarkan ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM phishing_logs WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()