"""
SMBkits — One-Shot Gemini Scraper
gemini-3.1-flash-lite + Search Grounding
website / email / phone / instagram / google_rating 한 번에 추출
Free tier: 500 RPD / 15 RPM
"""

import os
import sys
import json
import time
import gspread
from google import genai
from google.genai import types
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv("scrapers/.env", override=True)  # 시스템 환경변수보다 .env 우선

DAILY_LIMIT = 490
RPM_DELAY   = 10.0
MODEL       = "gemini-3.1-flash-lite"

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds  = Credentials.from_service_account_file(
    os.environ.get("CREDS_FILE", "scrapers/credentials.json"), scopes=SCOPES
)
gc     = gspread.authorize(creds)
sheet  = gc.open_by_key(os.environ["SHEET_ID"]).worksheet(os.environ["SHEET_NAME"])
gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 헤더 동적 파악
headers = sheet.row_values(1)

def col(name):
    return headers.index(name) + 1

name_col    = col("business_name")
city_col    = col("city")
country_col = col("country")
web_col     = col("website")
insta_col   = col("instagram")
email_col   = col("email")
rating_col  = col("google_rating")

if "phone" not in headers:
    sheet.update_cell(1, len(headers) + 1, "phone")
    headers.append("phone")
phone_col = col("phone")

# 타겟: website 또는 email 없는 행
all_records = sheet.get_all_records()
print(f"총 {len(all_records)}개 리드 탐색 중...")

targets = []
for i, rec in enumerate(all_records, start=2):
    if not rec.get("email") or not rec.get("website"):
        targets.append((
            i,
            rec.get("business_name", ""),
            rec.get("city", ""),
            rec.get("country", ""),
        ))
    if len(targets) >= DAILY_LIMIT:
        break

print(f"오늘 처리: {len(targets)}개 / 한도 {DAILY_LIMIT}\n")

PROMPT = """Find official contact info for this restaurant via Google Search.

Restaurant: "{name}"
Location: {city}, {country}

Return ONLY valid JSON (no markdown):
{{
  "website": "official URL or null",
  "email": "contact email or null",
  "phone": "phone with country code or null",
  "instagram": "@handle or null",
  "google_rating": 4.5
}}

Rules:
- website: official site ONLY, not tripadvisor/yelp/google/instagram/facebook/michelin
- email: real contact email, not noreply/support/admin
- phone: include country code
- google_rating: Google Maps float or null"""

for row_num, name, city, country in targets:
    print(f"[{row_num}] {name} ({city}, {country})")
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
        if result.get("website"):       updates.append((row_num, web_col,   result["website"]))
        if result.get("email"):         updates.append((row_num, email_col, result["email"]))
        if result.get("phone"):         updates.append((row_num, phone_col, result["phone"]))
        if result.get("instagram"):     updates.append((row_num, insta_col, result["instagram"]))
        if result.get("google_rating"): updates.append((row_num, rating_col, result["google_rating"]))

        if updates:
            sheet.batch_update([
                {"range": gspread.utils.rowcol_to_a1(r, c), "values": [[v]]}
                for r, c, v in updates
            ])

        print(f"  web:{result.get('website') or '-'} | "
              f"email:{result.get('email') or '-'} | "
              f"ig:{result.get('instagram') or '-'} | "
              f"tel:{result.get('phone') or '-'}")

    except Exception as e:
        print(f"  FAIL: {str(e)[:120]}")

    time.sleep(RPM_DELAY)

print("\n완료")
