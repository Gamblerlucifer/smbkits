"""
SMBkits — Google Search Stealth Scraper (undetected-chromedriver)
브라우저 탐지 우회 + 쿠키 유지 + 인간형 딜레이

Usage:
    python scrapers/gmaps_scraper.py --limit 500
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
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False

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

def is_social(url):
    return any(s in url for s in SOCIAL_EXCLUDE) if url else False

def get_sheet():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

def make_driver():
    """undetected-chromedriver 인스턴스 생성"""
    options = uc.ChromeOptions()
    options.add_argument("--lang=en-US")
    options.add_argument("--no-sandbox")
    options.add_argument(f"--window-size={random.randint(1200,1920)},{random.randint(700,1080)}")
    # headless=True: 화면 없이 실행 (로컬 백그라운드용)
    driver = uc.Chrome(options=options, headless=True, use_subprocess=True)
    driver.set_page_load_timeout(20)
    return driver

def human_scroll(driver):
    """인간형 스크롤 시뮬레이션"""
    total = random.randint(300, 700)
    steps = random.randint(3, 6)
    for _ in range(steps):
        driver.execute_script(f"window.scrollBy(0, {total // steps});")
        time.sleep(random.uniform(0.1, 0.3))

def search_google(driver, name, city, country):
    """Google Search 지식 패널에서 rating + website 파싱"""
    query   = f"{name} {city} {country}"
    encoded = requests.utils.quote(query)
    url     = f"https://www.google.com/search?q={encoded}&hl=en&gl=us"

    try:
        driver.get(url)
        time.sleep(random.uniform(1.5, 3.5))
        human_scroll(driver)

        html = driver.page_source

        # CAPTCHA 실제 감지
        if "Our systems have detected unusual traffic" in html or len(html) < 5000:
            print("  CAPTCHA 감지")
            return None

        rating = review_count = website = ""

        # ── Rating ───────────────────────────────────────────
        m = re.search(r'"ratingValue"\s*:\s*"?([\d.]+)"?', html)
        if m:
            rating = m.group(1)

        if not rating:
            m = re.search(r'Rated ([\d.]+) out of 5', html)
            if m:
                rating = m.group(1)

        if not rating:
            # 지식 패널 텍스트 직접 파싱
            try:
                els = driver.find_elements(By.CSS_SELECTOR, '[data-attrid*="rating"] span, [aria-label*="stars"] span')
                for el in els:
                    txt = el.text.strip()
                    if re.match(r'^[1-5]\.\d$', txt):
                        rating = txt
                        break
            except:
                pass

        # ── Review count ─────────────────────────────────────
        m = re.search(r'([\d,]+)\s+(?:Google\s+)?reviews?', html, re.IGNORECASE)
        if m:
            review_count = m.group(1).replace(",", "")

        if not review_count:
            m = re.search(r'"reviewCount"\s*:\s*"?([\d]+)"?', html)
            if m:
                review_count = m.group(1)

        # ── Website ──────────────────────────────────────────
        try:
            for sel in [
                '[data-attrid*="website"] a',
                '[data-attrid*="url"] a',
                'a[jsname][href^="http"]:not([href*="google."])',
            ]:
                els = driver.find_elements(By.CSS_SELECTOR, sel)
                for el in els:
                    href = el.get_attribute("href") or ""
                    if href and "google." not in href and not is_social(href):
                        website = href.split("?")[0]
                        break
                if website:
                    break
        except:
            pass

        # JSON-LD fallback
        if not website:
            m = re.search(r'"url"\s*:\s*"(https?://(?!(?:www\.)?google\.)[^"]+)"', html)
            if m:
                candidate = m.group(1)
                if not is_social(candidate):
                    website = candidate

        return {"rating": rating, "review_count": review_count, "website_uri": website}

    except Exception as e:
        print(f"  오류: {e}")
        return None

def extract_email(url):
    if not url or is_social(url):
        return ""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
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
    parser.add_argument("--limit",        type=int, default=200, help="처리할 최대 행 수")
    args = parser.parse_args()

    if not UC_AVAILABLE:
        print("undetected-chromedriver 미설치: pip install undetected-chromedriver selenium")
        sys.exit(1)

    sheet    = get_sheet()
    all_rows = sheet.get_all_values()
    rows     = all_rows[1:]

    unprocessed = [(i, r) for i, r in enumerate(rows)
                   if not (len(r) > 9 and r[COL["google_rating"]])]

    my_rows = [x for j, x in enumerate(unprocessed) if j % args.total_chunks == args.chunk]
    my_rows = my_rows[:args.limit]

    print(f"미처리 전체: {len(unprocessed)}행 | 이번 실행: {len(my_rows)}행\n")
    if not my_rows:
        print("처리할 행 없음")
        return

    driver      = make_driver()
    restart_every = 100   # N건마다 브라우저 재시작 (메모리/쿠키 누적 방지)

    try:
        for idx, (i, row) in enumerate(my_rows):
            # 브라우저 주기적 재시작
            if idx > 0 and idx % restart_every == 0:
                print(f"  [브라우저 재시작] {idx}건 처리 완료")
                driver.quit()
                time.sleep(random.uniform(5, 10))
                driver = make_driver()

            name    = row[COL["business_name"]] if len(row) > 0 else ""
            city    = row[COL["city"]]          if len(row) > 2 else ""
            country = row[COL["country"]]       if len(row) > 3 else ""

            if not name:
                continue

            print(f"[{idx+1}/{len(my_rows)}] {name} - {city}, {country}")

            result = search_google(driver, name, city, country)
            if not result:
                continue

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

    finally:
        driver.quit()

    print(f"\n완료 — {len(my_rows)}행 처리")

if __name__ == "__main__":
    main()
