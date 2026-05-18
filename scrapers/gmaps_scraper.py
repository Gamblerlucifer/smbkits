"""
SMBkits — Google Search Direct Request Scraper
Playwright 없이 requests + Tor SOCKS5로 구글 검색 HTML 직접 파싱
webdriver 흔적 제로, 속도 10배

Usage:
    python scrapers/gmaps_scraper.py --chunk 0 --total-chunks 4 --limit 200
"""

import os
import re
import random
import time
import requests
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import argparse
import sys

try:
    from stem import Signal
    from stem.control import Controller
    TOR_AVAILABLE = True
except ImportError:
    TOR_AVAILABLE = False

load_dotenv("scrapers/.env")

SHEET_ID   = os.getenv("SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")
CREDS_FILE = os.getenv("CREDS_FILE")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

COL = {
    "business_name":  0,
    "city":           2,
    "country":        3,
    "website":        4,
    "email":          6,
    "google_rating":  9,
    "review_count":   10,
    "negative_review":12,
    "sentiment_score":13,
    "outreach_status":14,
}

SOCIAL_EXCLUDE = ["instagram.com", "facebook.com", "twitter.com", "youtube.com",
                  "tripadvisor.com", "yelp.com", "google.com", "t.co",
                  "sevenrooms.com", "resy.com", "opentable.com", "inline.app",
                  "booking.com", "airbnb.com", "zomato.com", "tabelog.com"]

IMG_EXT    = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico")
SPAM_WORDS = ["example", "sentry", "pixel", "noreply", "no-reply", "wixpress",
              "schema", "wordpress", "jquery", "cloudflare", "analytics",
              "support@", "admin@", "postmaster@", "abuse@"]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

TOR_PROXY       = "socks5h://127.0.0.1:9050"   # socks5h = DNS도 Tor 경유
TOR_ROTATE_EVERY = 10

def is_social(url):
    return any(s in url for s in SOCIAL_EXCLUDE) if url else False

def get_sheet():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

def make_session():
    """Chrome 헤더 + Tor SOCKS5 세션 생성"""
    s = requests.Session()
    if TOR_AVAILABLE:
        s.proxies = {"http": TOR_PROXY, "https": TOR_PROXY}
    ua = random.choice(USER_AGENTS)
    s.headers.update({
        "User-Agent":                ua,
        "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language":           "en-US,en;q=0.9",
        "Accept-Encoding":           "gzip, deflate, br",
        "DNT":                       "1",
        "Connection":                "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest":            "document",
        "Sec-Fetch-Mode":            "navigate",
        "Sec-Fetch-Site":            "none",
        "Sec-Ch-Ua":                 '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile":          "?0",
        "Sec-Ch-Ua-Platform":        '"Windows"',
    })
    return s

def rotate_tor_ip():
    if not TOR_AVAILABLE:
        return
    try:
        with Controller.from_port(port=9051) as ctrl:
            ctrl.authenticate()
            ctrl.signal(Signal.NEWNYM)
        time.sleep(3)   # 새 회로 안정화
        print("  [Tor] 새 IP 회로 교체 완료")
    except Exception as e:
        print(f"  [Tor] 회로 교체 실패: {e}")

def search_google(session, name, city, country):
    """Google Search HTML 직접 파싱 → rating + website"""
    query   = f"{name} {city} {country}"
    encoded = requests.utils.quote(query)
    url     = f"https://www.google.com/search?q={encoded}&hl=en&gl=us&num=5"

    try:
        resp = session.get(url, timeout=20)
        html = resp.text

        # CAPTCHA / 비정상 트래픽 감지
        if "unusual traffic" in html or "recaptcha" in html.lower() or resp.status_code == 429:
            print("  CAPTCHA/차단 감지")
            return None

        rating = review_count = website = ""

        # ── Rating (다중 패턴 폴백) ──────────────────────────
        # JSON-LD ratingValue
        m = re.search(r'"ratingValue"\s*:\s*"?([\d.]+)"?', html)
        if m:
            rating = m.group(1)

        # aria-label "Rated X.X out of 5"
        if not rating:
            m = re.search(r'Rated ([\d.]+) out of 5', html)
            if m:
                rating = m.group(1)

        # 지식 패널 텍스트 패턴
        if not rating:
            m = re.search(r'\b([1-4]\.\d|5\.0)\b', html)
            if m:
                rating = m.group(1)

        # ── Review count ─────────────────────────────────────
        m = re.search(r'([\d,]+)\s+(?:Google\s+)?reviews?', html, re.IGNORECASE)
        if m:
            review_count = m.group(1).replace(",", "")

        # JSON-LD reviewCount
        if not review_count:
            m = re.search(r'"reviewCount"\s*:\s*"?([\d]+)"?', html)
            if m:
                review_count = m.group(1)

        # ── Website ──────────────────────────────────────────
        # 지식 패널 공식 웹사이트 (href 직접 추출)
        for pat in [
            r'data-attrid="[^"]*(?:website|url)[^"]*"[^>]*href="([^"]+)"',
            r'href="(https?://(?!(?:www\.)?google\.)[^"]+)"[^>]*data-attrid',
        ]:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                candidate = m.group(1).split("&")[0]
                if not is_social(candidate):
                    website = candidate
                    break

        # fallback: JSON-LD url 필드
        if not website:
            m = re.search(r'"url"\s*:\s*"(https?://(?!(?:www\.)?google\.)[^"]+)"', html)
            if m:
                candidate = m.group(1)
                if not is_social(candidate):
                    website = candidate

        return {"rating": rating, "review_count": review_count, "website_uri": website}

    except Exception as e:
        print(f"  요청 오류: {e}")
        return None

def extract_email(url):
    if not url or is_social(url):
        return ""
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    for target in [url, url.rstrip("/") + "/contact", url.rstrip("/") + "/about"]:
        try:
            res = requests.get(target, headers=headers, timeout=8)
            emails = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", res.text)
            filtered = []
            for e in emails:
                e_low = e.lower()
                if any(e_low.endswith(x) for x in IMG_EXT): continue
                if any(x in e_low for x in SPAM_WORDS): continue
                if e_low.rsplit(".", 1)[-1] in {"png","jpg","jpeg","gif","svg","webp","ico"}: continue
                filtered.append(e)
            if filtered:
                return filtered[0]
        except:
            continue
    return ""

def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk",        type=int, default=0,   help="청크 인덱스 (0-based)")
    parser.add_argument("--total-chunks", type=int, default=1,   help="전체 병렬 청크 수")
    parser.add_argument("--limit",        type=int, default=200, help="이번 실행에서 처리할 최대 행 수")
    args = parser.parse_args()

    mode = "Tor" if TOR_AVAILABLE else "직접"
    print(f"[{mode} 모드] Chunk {args.chunk}/{args.total_chunks-1}")

    sheet    = get_sheet()
    all_rows = sheet.get_all_values()
    rows     = all_rows[1:]

    unprocessed = [(i, r) for i, r in enumerate(rows)
                   if not (len(r) > 9 and r[COL["google_rating"]])]

    my_rows = [x for j, x in enumerate(unprocessed) if j % args.total_chunks == args.chunk]
    my_rows = my_rows[:args.limit]

    print(f"미처리 전체: {len(unprocessed)}행 | 담당: {len(my_rows)}행\n")
    if not my_rows:
        print("처리할 행 없음 - 완료")
        return

    session = make_session()
    captcha_streak = 0   # 연속 CAPTCHA 카운터

    for idx, (i, row) in enumerate(my_rows):
        name    = row[COL["business_name"]] if len(row) > 0 else ""
        city    = row[COL["city"]]          if len(row) > 2 else ""
        country = row[COL["country"]]       if len(row) > 3 else ""

        if not name:
            continue

        print(f"[{idx+1}/{len(my_rows)}] {name} - {city}, {country}")

        # N건마다 Tor 회로 교체 + 세션 갱신
        if idx > 0 and idx % TOR_ROTATE_EVERY == 0:
            rotate_tor_ip()
            session = make_session()

        result = search_google(session, name, city, country)

        if not result:
            captcha_streak += 1
            if captcha_streak >= 3:
                print("  연속 차단 3회 - Tor 회로 강제 교체")
                rotate_tor_ip()
                session = make_session()
                captcha_streak = 0
            time.sleep(random.uniform(2, 5))
            continue

        captcha_streak = 0
        rating       = result["rating"]
        review_count = result["review_count"]
        website_uri  = result["website_uri"]

        full_row = list(row) + [""] * (17 - len(row))

        current_website = full_row[COL["website"]]
        if is_social(current_website):
            current_website = ""
        website = current_website or website_uri
        if is_social(website):
            website = ""

        email = full_row[COL["email"]]
        if website and not email:
            email = extract_email(website)

        sentiment = min(100, int(float(rating) * 20)) if rating else 50

        print(f"  rating: {rating or '-'} ({review_count}개) | "
              f"website: {website or '없음'} | email: {email or '없음'}")

        row_num = i + 2
        full_row[COL["google_rating"]]   = rating
        full_row[COL["review_count"]]    = review_count
        full_row[COL["sentiment_score"]] = sentiment
        full_row[COL["website"]]         = website
        full_row[COL["email"]]           = email

        sheet.update(range_name=f"A{row_num}:Q{row_num}", values=[full_row])
        time.sleep(random.uniform(1.5, 3.5))

    print(f"\n[Chunk {args.chunk}] 완료")

if __name__ == "__main__":
    main()
