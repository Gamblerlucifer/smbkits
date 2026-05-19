"""
SMBkits — One-Shot Gemini Scraper
레스토랑 이름 + 도시 + 국가 → Gemini Search Grounding 한 번 →
website + email + phone + instagram + google_rating 전부 추출

Free tier (AI Studio): 1,500 RPD | 초과 시 429 (과금 없음)
"""

import os
import json
import time
import gspread
from google import genai
from google.genai import types
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv("scrapers/.env")

DAILY_LIMIT = 490   # gemini-3.1-flash-lite 무료 한도 500 RPD, 안전 마진 10
RPM_DELAY   = 5.0   # 15 RPM 한도 → 5초 간격 = 분당 12회 (안전)
MODEL       = "gemini-3.1-flash-lite"

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# ── 인증 ────────────────────────────────────────────────────
creds_file = os.environ.get("CREDS_FILE", "scrapers/credentials.json")
creds      = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
gc         = gspread.authorize(creds)
sheet      = gc.open_by_key(os.environ["SHEET_ID"]).worksheet(os.environ["SHEET_NAME"])

gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# ── 헤더 동적 파악 ──────────────────────────────────────────
headers   = sheet.row_values(1)

def col(name):
    return headers.index(name) + 1   # 1-based

name_col    = col("business_name")
city_col    = col("city")
country_col = col("country")
web_col     = col("website")
insta_col   = col("instagram")
email_col   = col("email")
rating_col  = col("google_rating")

# phone 컬럼 없으면 동적 추가
if "phone" not in headers:
    ph_col_idx = len(headers) + 1
    sheet.update_cell(1, ph_col_idx, "phone")
    headers.append("phone")
phone_col = col("phone")

# ── 타겟 추출 ───────────────────────────────────────────────
all_records = sheet.get_all_records()
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
print(f"총 {len(all_records)}개 리드 중 미싱 데이터 탐색 중...")

targets = []
for i, rec in enumerate(all_records, start=2):
    if not rec.get("email") or not rec.get("website"):
        targets.append((i, rec.get("business_name", ""), rec.get("city", ""), rec.get("country", "")))
    if len(targets) >= DAILY_LIMIT:
        break

print(f"오늘 처리할 타겟: {len(targets)}개 (무료 한도 {DAILY_LIMIT} 락인)")

# ── Gemini 원샷 폭격 ────────────────────────────────────────
PROMPT = """You are a business data researcher.
Find official contact details for this restaurant using Google Search.

Restaurant: "{name}"
Location: {city}, {country}

Return ONLY a valid JSON object. No markdown, no explanation:
{{
  "website": "official website URL or null",
  "email": "direct contact email or null",
  "phone": "phone with country code or null",
  "instagram": "@handle or null",
  "google_rating": 4.5
}}

Rules:
- website: official site ONLY — NOT tripadvisor/yelp/google/instagram/facebook/michelin
- email: real contact email — NOT noreply/support/admin
- phone: include country code (e.g. +63 917 139 5254)
- instagram: just @handle
- google_rating: Google Maps float or null"""

for row_num, name, city, country in targets:
    print(f"[{row_num}행] {name} ({city}, {country})")
    try:
        resp = gemini.models.generate_content(
            model=MODEL,
            contents=PROMPT.format(name=name, city=city, country=country),
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                response_mime_type="application/json",
                temperature=0,
            ),
        )
        result = json.loads(resp.text)

        updates = []
        if result.get("website"):   updates.append((row_num, web_col,   result["website"]))
        if result.get("email"):     updates.append((row_num, email_col, result["email"]))
        if result.get("phone"):     updates.append((row_num, phone_col, result["phone"]))
        if result.get("instagram"): updates.append((row_num, insta_col, result["instagram"]))
        if result.get("google_rating"): updates.append((row_num, rating_col, result["google_rating"]))

        if updates:
            sheet.batch_update([
                {"range": gspread.utils.rowcol_to_a1(r, c), "values": [[v]]}
                for r, c, v in updates
            ])
        print(f"  OK email:{result.get('email')} | web:{result.get('website')} | ig:{result.get('instagram')}")

    except Exception as e:
        print(f"  FAIL ({type(e).__name__}): {str(e)[:100]}")

    time.sleep(RPM_DELAY)

print("완료 — 오늘 자 무과금 마이닝 임무 완수")
