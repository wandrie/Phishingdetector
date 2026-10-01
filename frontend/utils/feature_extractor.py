import re
import urllib.parse
from difflib import SequenceMatcher

POPULAR_BRANDS = ["facebook", "google", "instagram", "whatsapp", "bankmandiri", "bca", "bri", "bni", "paypal", "netflix", "tokopedia", "shopee"]
SCAM_KEYWORDS = ["wheel", "spin", "event", "invitationcode", "claim", "bonus", "free", "gift", "reward", "promo", "slot", "gacor", "judi", "unban"]

def is_typosquatting(hostname: str) -> bool:
    parts = hostname.lower().replace('www.', '').split('.')
    main_domain = parts[0] if parts else ""
    for brand in POPULAR_BRANDS:
        if main_domain != brand:
            ratio = SequenceMatcher(None, main_domain, brand).ratio()
            if ratio >= 0.80:
                return True
    return False

def extract_features_from_url(url: str, feature_list: list) -> dict:
    url_cleaned = url.strip()
    
    if not (url_cleaned.startswith("http://") or url_cleaned.startswith("https://")):
        full_url = "https://" + url_cleaned
        raw_input = url_cleaned
    else:
        full_url = url_cleaned
        raw_input = re.sub(r'^https?://', '', url_cleaned)

    parsed_url = urllib.parse.urlparse(full_url)
    hostname = parsed_url.hostname or ""
    path = parsed_url.path or ""
    query = parsed_url.query or ""
    fragment = parsed_url.fragment or ""

    # PERBAIKAN BUGHASH/FRAGMENT:
    # Gabungkan Path, Query, dan Fragment agar kata setelah '#' (seperti #/wheelspinevent) tetap terhitung
    full_path_str = f"{path}/{query}/{fragment}".lower()

    features = {}

    # -------------------------------------------------------------
    # 1. Fitur Leksikal & Struktur URL
    # -------------------------------------------------------------
    features['length_url'] = len(full_url)
    features['length_hostname'] = len(hostname)
    features['ip'] = 1 if re.search(r'(\d{1,3}\.){3}\d{1,3}', hostname) else 0
    features['nb_dots'] = full_url.count('.')
    features['nb_hyphens'] = full_url.count('-')
    features['nb_at'] = full_url.count('@')
    features['nb_qm'] = full_url.count('?')
    features['nb_and'] = full_url.count('&')
    features['nb_or'] = full_url.count('|')
    features['nb_eq'] = full_url.count('=')
    features['nb_underscore'] = full_url.count('_')
    features['nb_tilde'] = full_url.count('~')
    features['nb_percent'] = full_url.count('%')
    features['nb_slash'] = full_url.count('/')
    features['nb_star'] = raw_input.count('*')
    features['nb_colon'] = full_url.count(':')
    features['nb_comma'] = full_url.count(',')
    features['nb_semicolumn'] = full_url.count(';')
    features['nb_dollar'] = full_url.count('$')
    features['nb_space'] = full_url.count(' ') + full_url.count('%20')
    features['nb_www'] = 1 if 'www' in hostname.lower() else 0
    features['nb_com'] = 1 if ('com' in hostname.lower() or 'co.id' in hostname.lower()) else 0
    features['nb_dslash'] = full_path_str.count('//')
    features['http_in_path'] = 1 if 'http' in full_path_str else 0
    features['https_token'] = 1 if 'https' in hostname.lower() else 0
    
    features['ratio_digits_url'] = sum(c.isdigit() for c in full_url) / len(full_url) if len(full_url) > 0 else 0
    features['ratio_digits_host'] = sum(c.isdigit() for c in hostname) / len(hostname) if len(hostname) > 0 else 0
    
    features['punycode'] = 1 if hostname.startswith('xn--') else 0
    features['port'] = 1 if parsed_url.port is not None else 0
    features['tld_in_path'] = 1 if re.search(r'\.(com|org|net|info|biz|gov|edu|co\.id|id)', full_path_str) else 0
    features['tld_in_subdomain'] = 1 if hostname.count('.') > 2 else 0
    features['abnormal_subdomain'] = 0
    
    # Hitung Subdomain
    domain_parts = hostname.split('.')
    if hostname.endswith('.co.id') or hostname.endswith('.com.id') or hostname.endswith('.go.id'):
        subdomain_count = max(0, len(domain_parts) - 3)
    else:
        subdomain_count = max(0, len(domain_parts) - 2)
    features['nb_subdomains'] = subdomain_count

    features['prefix_suffix'] = 1 if '-' in hostname else 0
    features['shortening_service'] = 1 if re.search(r'bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|tinyurl|tr\.im|is\.gd|cli\.gs', hostname) else 0

    # Parsing Kata Terpanjang dari Seluruh Path + Fragment
    path_words = [w for w in re.split(r'[/_.-?#&=]', full_path_str) if w]
    features['longest_word_path'] = max([len(w) for w in path_words]) if path_words else 0

    # -------------------------------------------------------------
    # 2. Indikator Sinyal Anomali (Phish Hints)
    # -------------------------------------------------------------
    has_scam_kw = any(kw in full_path_str for kw in SCAM_KEYWORDS)
    is_typo = is_typosquatting(hostname)
    
    # Berikan sinyal phish_hints = 1 jika terindikasi typo/scam
    features['phish_hints'] = 1 if (has_scam_kw or is_typo) else 0

    # -------------------------------------------------------------
    # 3. Adjustment Fitur Reputasi (Jika Ada Indikasi Phishing)
    # -------------------------------------------------------------
    if has_scam_kw or is_typo:
        features['google_index'] = 1         # Phishing
        features['page_rank'] = 0            # Phishing
        features['domain_age'] = -1          # Phishing
        features['web_traffic'] = 0          # Phishing
        features['nb_hyperlinks'] = 2        # Phishing
    else:
        features['google_index'] = 0
        features['page_rank'] = 3
        features['domain_age'] = 365
        features['web_traffic'] = 1000
        features['nb_hyperlinks'] = 20

    features['ratio_intHyperlinks'] = 0.5
    features['ratio_extHyperlinks'] = 0.5
    features['whois_registered_domain'] = 0
    features['dns_record'] = 0
    features['ssl_final_state'] = 1 if full_url.startswith("https://") else 0

    # -------------------------------------------------------------
    # 4. Alignment Kolom
    # -------------------------------------------------------------
    final_extracted_features = {}
    for feat in feature_list:
        final_extracted_features[feat] = features.get(feat, 0)

    return final_extracted_features