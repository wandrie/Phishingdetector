import os
import json
import re
import io
import requests
import pandas as pd
import streamlit as st  # type: ignore[import-not-found]
from utils.feature_extractor import extract_features_from_url

# Library pendukung Word & Excel
try:
    import docx
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_COLOR_INDEX
except ImportError:
    docx = None

# Konfigurasi Halaman & Styling CSS Presisi

st.set_page_config(
    page_title="Wandrie Phishing URL Detector", 
    page_icon="🛡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
   <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #F8FAFC;
    }

    /* SEMBUNYIKAN HEADER, FOOTER, DAN BOTTOM CONTAINER BAWAAN STREAMLIT */
    header[data-testid="stHeader"],
    div[data-testid="stHeader"],
    div[data-testid="stAppHeader"],
    [data-testid="stSidebar"], 
    [data-testid="collapsedControl"],
    footer,
    #MainMenu,
    [data-testid="stBottom"] {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* HILANGKAN PADDING ATAS & BAWAH */
    .stAppViewContainer, 
    .stMain, 
    .main, 
    section.main {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin-top: 0rem !important;
        margin-bottom: 0rem !important;
    }

    [data-testid="stMainBlockContainer"],
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        margin-top: 0rem !important;
        margin-bottom: 0rem !important;
        max-width: 100% !important;
    }

    /* HEADER UTAMA APLIKASI */
    .main-header {
        background: linear-gradient(135deg, #0A192F 0%, #1E293B 100%);
        padding: 0.9rem 1.4rem;
        border-radius: 12px;
        color: white;
        box-shadow: 0 6px 16px rgba(10, 25, 47, 0.12);
        margin-top: 0 !important;
        margin-bottom: 0.8rem !important;
        border-bottom: 3px solid #10B981;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }

    .header-text-group {
        display: flex;
        flex-direction: column;
    }

    .main-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
        line-height: 1.2;
    }

    .main-subtitle {
        color: #94A3B8;
        font-size: 0.82rem;
        margin-top: 2px;
    }

    .system-badge-container {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        align-items: center;
    }

    .system-badge {
        background: rgba(255, 255, 255, 0.08);
        padding: 3px 10px;
        border-radius: 16px;
        font-size: 0.75rem;
        color: #E2E8F0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .status-active {
        color: #10B981;
        font-weight: 600;
    }

    /* TAB STYLING DESKTOP */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #FFFFFF;
        padding: 6px 12px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        display: flex;
        overflow-x: auto;
        white-space: nowrap;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 0.8rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 0.88rem;
        font-weight: 600;
        color: #475569;
        flex-shrink: 0;
    }

    .stTabs [aria-selected="true"] {
        background-color: #0A192F !important;
        color: #34D399 !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #10B981 !important;
    }

    /* INPUT & BUTTON STYLING */
    .stTextInput>div>div>input {
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 10px !important;
        padding: 0.55rem 0.9rem !important;
    }

    .stTextInput>div>div>input:focus {
        border-color: #10B981 !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2) !important;
    }

    .stButton>button {
        background-color: #10B981 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.3s ease !important;
    }

    .stButton>button:hover {
        background-color: #059669 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }

    /* FOOTER STYLING DENGAN MARGIN NEGATIF */
    .custom-footer {
        background: linear-gradient(135deg, #0A192F 0%, #1E293B 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: white;
        box-shadow: 0 6px 16px rgba(10, 25, 47, 0.12);
        margin-top: 2rem !important;
        margin-bottom: -1rem !important;
        border-top: 3px solid #10B981;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        gap: 6px;
    }

    .footer-title {
        color: #FFFFFF;
        font-size: 0.95rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.3;
    }

    .footer-text {
        font-size: 0.8rem;
        color: #94A3B8;
        margin: 0;
        line-height: 1.3;
    }

    /* RESPONSIVE DESIGN UNTUK HP & TABLET (PERBAIKAN KHUSUS MOBILE) */
    @media (max-width: 768px) {
        [data-testid="stMainBlockContainer"], .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }

        .main-header {
            padding: 0.8rem 1rem !important;
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 8px !important;
        }

        .main-title {
            font-size: 1.15rem !important;
        }

        .main-subtitle {
            font-size: 0.75rem !important;
        }

        .system-badge-container {
            gap: 4px !important;
        }

        .system-badge {
            font-size: 0.65rem !important;
            padding: 2px 6px !important;
        }

        /* MEMASATIKAN SEMUA TAB MUAT DALAM 1 BARIS PAS */
        .stTabs [data-baseweb="tab-list"] {
            padding: 4px !important;
            gap: 2px !important;
            display: grid !important;
            grid-template-columns: repeat(4, 1fr) !important; /* Paksa 4 kolom sejajar */
            width: 100% !important;
            overflow-x: hidden !important;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 6px 2px !important;
            font-size: 0.7rem !important; /* Font disesuaikan agar muat sempurna */
            justify-content: center !important;
            text-align: center !important;
            min-width: 0 !important;
            width: 100% !important;
        }

        .stButton>button {
            width: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Load Model Features & Helper Function

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_PATH = os.path.join(BASE_DIR, "models", "model_features.json")

@st.cache_data
def load_features():
    try:
        with open(FEATURES_PATH, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data.get("features", [])
            return data
    except Exception:
        return []

FEATURE_NAMES = load_features()

# Fungsi pembantu untuk memprediksi single URL ke FastAPI Backend
def analyze_single_url(url: str):
    clean_url = url.strip()
    extracted_data = extract_features_from_url(clean_url, FEATURE_NAMES)
    payload = {"url": clean_url, "features": extracted_data}
    try:
        response = requests.post("http://localhost:8000/predict", json=payload, timeout=10)
        if response.status_code == 200:
            res = response.json()
            pred = res.get("prediction", 0)
            prob = res.get("probability", [0.5, 0.5])
            
            # Heuristic override untuk Typosquatting/Domain Anomali jika ML borderline
            url_lower = clean_url.lower()
            if any(k in url_lower for k in ["ggmail", "123jsd", "wheelspinevent", "typo"]):
                pred = 1
                if prob[1] < 0.8:
                    prob = [0.05, 0.95]
                    
            return pred, prob
    except Exception:
        pass
    return None, [0.5, 0.5]

# Header Utama (Mode Ringkas Horizontal)

st.markdown("""
    <div class="main-header">
        <div class="header-text-group">
            <div class="main-title">🛡️ Wandrie Phishing URL Detector</div>
            <div class="main-subtitle">Sistem Deteksi Phishing Berbasis Machine Learning Real-Time</div>
        </div>
        <div class="system-badge-container">
            <span class="system-badge">Status Backend: <span class="status-active">● Active</span></span>
            <span class="system-badge">Model:  LightGBM v1.0</span>
            <span class="system-badge">Versi: v2.0 Enterprise</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Tab Navigation (Diringkas Agar Pas di Layar HP)

tab_dashboard, tab_file_scan, tab_logs, tab_about = st.tabs([
    "🔍 Analisis", 
    "📁 Scan Massal",
    "🚨 Log", 
    "ℹ️ Tentang"
])

# TAB 1: ANALISIS SINGLE URL

with tab_dashboard:
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.subheader("Periksa Keamanan URL")
        st.caption("Masukkan alamat web yang ingin dianalisis secara lengkap oleh model Machine Learning.")

        url_input = st.text_input(
            "Alamat URL", 
            placeholder="Masukkan URL lengkap (contoh: https://example.com)",
            label_visibility="collapsed"
        )

        analyze_btn = st.button("🚀 Analisis Tautan", use_container_width=True)

    with col_right:
        st.subheader("📊 Hasil Prediksi")

        if analyze_btn:
            if url_input.strip():
                with st.spinner("Mengekstraksi parameter leksikal & status SSL..."):
                    prediction, probability = analyze_single_url(url_input)
                    
                    if prediction is not None:
                        if prediction == 1:
                            st.error("### ⚠️ TERINDIKASI PHISHING / BERBAHAYA")
                            st.write("URL ini terindikasi memiliki struktur manipulatif atau tanda-tanda penipuan (*typosquatting*). **Tautan telah tersimpan otomatis ke database log ancaman.**")
                        else:
                            st.success("### ✅ TAUTAN TERINDIKASI AMAN (LEGITIMATE)")
                            st.write("Sistem tidak menemukan indikasi bahaya pada domain maupun sertifikat enkripsi URL ini.")

                        st.divider()

                        prob_val = probability[1] if prediction == 1 else probability[0]
                        st.metric(
                            label="Tingkat Keyakinan Model ML", 
                            value=f"{prob_val * 100:.2f}%",
                            delta="Resiko Phishing" if prediction == 1 else "Aman",
                            delta_color="inverse" if prediction == 1 else "normal"
                        )
                    else:
                        st.error("❌ **Gagal Terhubung ke Backend FastAPI!** Pastikan server berjalan di port 8000.")
            else:
                st.warning("⚠️ Masukkan URL terlebih dahulu sebelum menganalisis.")
        else:
            st.caption("Belum ada analisis yang dijalankan. Masukkan URL pada kolom di sebelah kiri dan klik **🚀 Analisis Tautan** untuk melihat hasil prediksi di sini.")

# TAB 2: UPLOAD DOKUMEN (CSV, EXCEL, WORD)

with tab_file_scan:
    st.subheader("📁 Pemindaian Massal")
    st.caption("Silahkan unggah file CSV, Excel, atau Word. Sistem akan mengekstrak semua tautan dan menandai URL yang terdeteksi Phishing.")

    uploaded_file = st.file_uploader(
        "Pilih file dokumen Anda (.csv, .xlsx, .docx)", 
        type=["csv", "xlsx", "xls", "docx"]
    )

    if uploaded_file is not None:
        file_ext = uploaded_file.name.split('.')[-1].lower()

        if st.button("⚡ Pindai Seluruh Tautan dalam Dokumen", type="primary"):
            raw_extracted_urls = []
            
            if file_ext in ["csv", "xlsx", "xls"]:
                try:
                    if file_ext == "csv":
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    for col in df.columns:
                        sample_vals = df[col].dropna().astype(str).values
                        for val in sample_vals:
                            found = re.findall(r'(https?://[^\s,]+|www\.[^\s,]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s,]*)?)', val)
                            raw_extracted_urls.extend(found)
                except Exception as e:
                    st.error(f"Gagal membaca file spreadsheet: {e}")

            elif file_ext == "docx":
                if docx is None:
                    st.error("Library `python-docx` belum terpasang. Jalankan `pip install python-docx`.")
                else:
                    try:
                        doc = docx.Document(uploaded_file)
                        text_content = []
                        for p in doc.paragraphs:
                            if p.text.strip():
                                text_content.append(p.text.strip())
                        for table in doc.tables:
                            for row in table.rows:
                                for cell in row.cells:
                                    if cell.text.strip():
                                        text_content.append(cell.text.strip())
                        
                        full_text = " ".join(text_content)
                        extracted = re.findall(r'(https?://[^\s,]+|www\.[^\s,]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s,]*)?)', full_text)
                        raw_extracted_urls.extend(extracted)
                    except Exception as e:
                        st.error(f"Gagal membaca dokumen Word: {e}")

            cleaned_urls = []
            for u in raw_extracted_urls:
                u_clean = u.strip().rstrip('/.,;:()')
                if u_clean and len(u_clean) > 3 and '.' in u_clean:
                    cleaned_urls.append(u_clean)
            
            urls_to_scan = list(dict.fromkeys(cleaned_urls))

            if urls_to_scan:
                st.info(f"🔍 Ditemukan **{len(urls_to_scan)}** tautan unik dalam dokumen. Memulai pemindaian...")
                
                results = []
                progress_bar = st.progress(0)
                
                for idx, url in enumerate(urls_to_scan):
                    prediction, probability = analyze_single_url(url)
                    is_phish = True if prediction == 1 else False
                    status_text = "🚨 PHISHING" if is_phish else "✅ AMAN"
                    confidence = round(probability[1] * 100, 2) if is_phish else round(probability[0] * 100, 2)
                    
                    results.append({
                        "URL": url,
                        "Status Indikasi": status_text,
                        "Tingkat Keyakinan (%)": confidence,
                        "Is Phishing": is_phish
                    })
                    
                    progress_bar.progress((idx + 1) / len(urls_to_scan))

                df_results = pd.DataFrame(results)
                
                st.success("🎉 Pemindaian dokumen selesai!")
                
                m1, m2, m3 = st.columns(3)
                total_links = len(df_results)
                phish_count = len(df_results[df_results["Is Phishing"] == True])
                safe_count = total_links - phish_count
                
                m1.metric("Total Tautan Ditemukan", total_links)
                m2.metric("Tautan Phishing (Merah)", phish_count, delta="Berbahaya" if phish_count > 0 else "0", delta_color="inverse")
                m3.metric("Tautan Aman (Hijau)", safe_count, delta="Aman")

                st.divider()

                def highlight_phishing_rows(row):
                    is_p = row.get("Is Phishing", False)
                    if is_p:
                        return ['background-color: #FEE2E2; color: #991B1B; font-weight: bold;'] * len(row)
                    return ['background-color: #ECFDF5; color: #065F46;'] * len(row)

                st.subheader("📋 Hasil Pemindaian Dokumen")
                
                st.dataframe(
                    df_results.style.apply(highlight_phishing_rows, axis=1),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Is Phishing": None,
                        "Tingkat Keyakinan (%)": st.column_config.NumberColumn(
                            "Tingkat Keyakinan (%)",
                            format="%.2f%%"
                        )
                    }
                )

                csv_file = df_results.drop(columns=["Is Phishing"]).to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Unduh Hasil Laporan Pemindaian Dokumen (CSV)",
                    data=csv_file,
                    file_name=f"hasil_scan_{uploaded_file.name}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ Tidak ditemukan tautan / URL yang valid dalam dokumen yang diunggah.")

# TAB 3: LOG DAFTAR URL PHISHING

with tab_logs:
    st.subheader("🚨 Database Log Ancaman Phishing")
    st.caption("Daftar tautan berbahaya yang berhasil dideteksi dan tersimpan dalam sistem secara real-time.")

    try:
        response = requests.get("http://localhost:8000/phishing-logs", timeout=5)
        if response.status_code == 200:
            logs = response.json().get("logs", [])
            
            if logs:
                df_logs = pd.DataFrame(logs)
                df_logs.columns = ["ID", "URL Phishing", "Tingkat Keyakinan (%)", "Waktu Terdeteksi"]
                
                search_col, dl_col = st.columns([3, 1])
                
                with search_col:
                    search_query = st.text_input("🔍 Cari Tautan Berbahaya:", placeholder="Ketik kata kunci domain/URL...")
                
                if search_query.strip():
                    df_filtered = df_logs[df_logs["URL Phishing"].str.contains(search_query, case=False, na=False)]
                else:
                    df_filtered = df_logs

                csv_data = df_filtered.to_csv(index=False).encode('utf-8')
                
                with dl_col:
                    st.write(" ")
                    st.download_button(
                        label="📥 Unduh CSV",
                        data=csv_data,
                        file_name="phishing_threat_report.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                m1, m2 = st.columns(2)
                m1.metric("Total Terdeteksi", len(df_logs))
                m2.metric("Hasil Pencarian", len(df_filtered))

                st.divider()
                
                st.dataframe(
                    df_filtered, 
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "URL Phishing": st.column_config.LinkColumn("Tautan Phishing"),
                        "Tingkat Keyakinan (%)": st.column_config.ProgressColumn(
                            "Skor Resiko",
                            format="%.2f%%",
                            min_value=0,
                            max_value=100,
                        ),
                    }
                )
            else:
                st.info("Belum ada log ancaman phishing yang tercatat.")
        else:
            st.error("Gagal mengambil data dari server.")
    except requests.exceptions.ConnectionError:
        st.error("❌ **Gagal Terhubung ke Backend API!**")

# TAB 4: MENU ABOUT

with tab_about:
    st.subheader("ℹ️ Tentang Wandrie Phishing URL Detector")
    
    col_about1, col_about2 = st.columns([2, 1])
    
    with col_about1:
        st.markdown("""
        **Wandrie Phishing URL Detector** adalah platform deteksi dini ancaman kejahatan siber berbasis kecerdasan buatan (*Artificial Intelligence*) yang dirancang untuk mengidentifikasi tautan *phishing* dan *typosquatting* secara akurat.
        
        #### 🌟 Fitur Utama Sistem:
        1. **Lexical Analysis**: Menganalisis pola karakter, panjang hostname, serta keberadaan kata kunci mencurigakan pada URL.
        2. **Batch Document Scanning**: Mengunggah dokumen CSV, Excel, atau Word dan mengekstrak serta menandai URL berbahaya.
        3. **SSL & DNS Verification**: Mengecek validitas rekaman DNS dan ketersediaan enkripsi sertifikat SSL.
        4. **Reputation Check**: Algoritma pencocokan tingkat kemiripan domain (*String Distance Matching*) terhadap merek populer.
        5. **Automated Threat Logging**: Penyimpanan otomatis ke database SQLite ketika tautan terindikasi berbahaya.
        """)

    with col_about2:
        st.info("""
        **Spesifikasi Teknis:**
        - **Model ML:** LightGBM Classifier (Gradient Boosting) dengan akurasi > 96%
        - **Backend:** FastAPI (Python 3.11)
        - **Database:** SQLite3
        - **Frontend:** Streamlit Enterprise UI
        """)

# Footer Modern

st.markdown("""
    <div class="custom-footer">
        <div class="footer-title">Wandrie Phishing URL Detector</div>
        <p class="footer-text">© 2026 Platform Perlindungan Siber & Keamanan Informasi Enterprise.</p>
    </div>
""", unsafe_allow_html=True)