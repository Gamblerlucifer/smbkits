"""
SMBkits — Gemini Search Grounding Scraper
gemini-3.1-flash-lite + Google Search Grounding
rating + website + email + confidence 추출 | GitHub Actions OK (CAPTCHA 없음)

Usage:
    python scrapers/gemini_scraper.py --limit 200
    python scrapers/gemini_scraper.py --limit 200 --category "cafe"
    python scrapers/gemini_scraper.py --chunk 0 --total-chunks 4 --limit 200
"""

import os
import re
import json
import time
import random
import requests
import gspread
from google import genai
from google.genai import types
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import argparse
import sys

load_dotenv("scrapers/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SHEET_ID       = os.getenv("SHEET_ID")
SHEET_NAME     = os.getenv("SHEET_NAME")
CREDS_FILE     = os.getenv("CREDS_FILE")

MODEL = "gemini-3.1-flash-lite"

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

BATCH_SIZE = 20

# 공식 웹사이트가 아닌 도메인 (hallucination 필터)
SOCIAL_EXCLUDE = [
    "instagram.com", "facebook.com", "twitter.com", "x.com", "youtube.com",
    "tripadvisor.com", "yelp.com", "google.com", "t.co",
    "michelin.com", "sevenrooms.com", "resy.com", "opentable.com",
    "booking.com", "airbnb.com", "zomato.com", "tabelog.com",
    "foursquare.com", "tiktok.com", "pinterest.com", "linkedin.com",
    "maps.google", "goo.gl", "bit.ly", "linktr.ee",
]

IMG_EXT    = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico")
SPAM_WORDS = ["example", "sentry", "pixel", "noreply", "no-reply", "wixpress",
              "schema", "wordpress", "jquery", "cloudflare", "analytics",
              "support@", "admin@", "postmaster@", "abuse@"]

def is_social(url: str) -> bool:
    return any(s in url for s in SOCIAL_EXCLUDE) if url else False

def is_valid_website(url: str) -> bool:
    """URL이 공식 웹사이트로 쓸만한지 검증"""
    if not url:
        return False
    if is_social(url):
        return False
    # 너무 짧은 URL 제외 (예: http://a.com)
    if len(url) < 12:
        return False
    # 숫자만 있는 도메인 제외
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        if not domain:
            return False
    except Exception:
        return False
    return True

def get_sheet():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

client = genai.Client(api_key=GEMINI_API_KEY)

def query_gemini(name: str, city: str, country: str, category: str = "restaurant") -> dict | None:
    prompt = f"""Find the official business information for this {category} using Google Search.
Business: "{name}"
Location: {city}, {country}
Category: {category}

Respond STRICTLY in this JSON format only, no markdown, no explanation:
{{"website_url": "https://example.com", "google_rating": 4.5, "total_reviews": 1234, "confidence": 90}}

Field rules:
- website_url: official {category} website ONLY. Must NOT be michelin.com, tripadvisor.com, yelp.com, instagram.com, facebook.com, google.com, booking.com, or any aggregator/social. Set null if official website not found.
- google_rating: Google Maps star rating (1.0–5.0). Set null if not found.
- total_reviews: total number of Google reviews as integer. Set null if not found.
- confidence: integer 0–100. How confident are you this data is correct and for the right business? Penalize heavily if: business may be closed, name is ambiguous, website seems wrong, or data is from wrong location."""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    response_mime_type="application/json",
                    temperature=0,
                ),
            )
            text = response.text
            if not text:
                return None

            result = json.loads(text)
            rating     = str(result.get("google_rating") or "")
            reviews    = str(result.get("total_reviews") or "")
            website    = result.get("website_url") or ""
            confidence = int(result.get("confidence") or 0)

            # hallucination 필터: 소셜/집계 사이트면 버림
            if website and not is_valid_website(website):
                print(f"  [필터] 비공식 URL 제거: {website}")
                website = ""
                confidence = max(0, confidence - 30)

            return {
                "rating": rating,
                "review_count": reviews,
                "website_uri": website,
                "confidence": confidence,
            }

        except Exception as e:
            err_str = str(e)
            # 503/429: 일시적 과부하 → exponential backoff 재시도
            if any(code in err_str for code in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"]):
                wait = (2 ** attempt) * 5  # 5s → 10s → 20s
                print(f"  [재시도 {attempt+1}/{max_retries}] {err_str[:60]}... {wait}초 대기")
                time.sleep(wait)
                continue
            # 그 외 에러는 즉시 포기
            print(f"  Gemini 오류: {e}")
            return None

    print(f"  [최대 재시도 초과] 행 스킵")
    return None

def extract_email(url: str) -> str:
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
        except Exception:
            continue
    return ""

def batch_write(sheet, pending: list):
    if not pending:
        return
    data = [{"range": f"A{p['row_num']}:Q{p['row_num']}", "values": [p["full_row"]]} for p in pending]
    sheet.batch_update(data)
    print(f"  [Sheets] {len(pending)}행 저장 완료")

def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk",        type=int,   default=0,            help="청크 인덱스")
    parser.add_argument("--total-chunks", type=int,   default=1,            help="전체 청크 수")
    parser.add_argument("--limit",        type=int,   default=200,          help="처리할 최대 행 수")
    parser.add_argument("--category",     type=str,   default="restaurant", help="업종 카테고리")
    parser.add_argument("--min-confidence", type=int, default=0,            help="confidence 미만이면 website/email 저장 안 함")
    args = parser.parse_args()

    sheet    = get_sheet()
    all_rows = sheet.get_all_values()
    rows     = all_rows[1:]

    unprocessed = [(i, r) for i, r in enumerate(rows)
                   if not (len(r) > 9 and r[COL["google_rating"]])]

    my_rows = [x for j, x in enumerate(unprocessed) if j % args.total_chunks == args.chunk]
    my_rows = my_rows[:args.limit]

    print(f"미처리: {len(unprocessed)}행 | 이번 실행: {len(my_rows)}행 | "
          f"모델: {MODEL} | 업종: {args.category}\n")

    pending = []

    for idx, (i, row) in enumerate(my_rows):
        name    = row[COL["business_name"]] if len(row) > 0 else ""
        city    = row[COL["city"]]          if len(row) > 2 else ""
        country = row[COL["country"]]       if len(row) > 3 else ""

        if not name:
            continue

        print(f"[{idx+1}/{len(my_rows)}] {name} - {city}, {country}")

        full_row = list(row) + [""] * (17 - len(row))

        # 기존 website 먼저 확보 (Gemini 실패해도 크롤러에 넘길 수 있도록)
        current_website = full_row[COL["website"]]
        if is_social(current_website):
            current_website = ""

        result = query_gemini(name, city, country, args.category)

        if not result:
            # Gemini 실패해도 기존 website가 있으면 email 추출은 계속
            email = full_row[COL["email"]]
            if current_website and not email:
                email = extract_email(current_website)
                if email:
                    print(f"  [Gemini 실패, 기존 website 활용] email: {email}")
                    full_row[COL["email"]] = email
                    pending.append({"row_num": i + 2, "full_row": full_row})
            time.sleep(2)
            continue

        rating       = result["rating"]
        review_count = result["review_count"]
        website_uri  = result["website_uri"]
        confidence   = result["confidence"]

        # confidence 낮으면 Gemini 결과 website 사용 안 함
        if confidence < args.min_confidence:
            website_uri = ""
            print(f"  [저신뢰도 {confidence}] website 저장 스킵")

        website = current_website or website_uri

        # 이메일 추출 (website 있고 이메일 없을 때)
        email = full_row[COL["email"]]
        if website and not email:
            email = extract_email(website)

        # sentiment_score: rating × 20 (100점 만점), 없으면 50
        sentiment = min(100, int(float(rating) * 20)) if rating else 50

        print(f"  rating: {rating or '-'} ({review_count}개) | conf: {confidence} | "
              f"website: {website or '없음'} | email: {email or '없음'}")

        full_row[COL["google_rating"]]   = rating
        full_row[COL["review_count"]]    = review_count
        full_row[COL["sentiment_score"]] = sentiment
        full_row[COL["website"]]         = website
        full_row[COL["email"]]           = email

        pending.append({"row_num": i + 2, "full_row": full_row})

        if len(pending) >= BATCH_SIZE:
            batch_write(sheet, pending)
            pending.clear()

        # Tier 1 유료 ~1,000 RPM → 0.5초 간격으로 충분
        time.sleep(random.uniform(0.5, 1.0))

    batch_write(sheet, pending)
    print(f"\n완료")

if __name__ == "__main__":
    main()
