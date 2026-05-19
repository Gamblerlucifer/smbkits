"""
SMBkits — One-Shot Gemini Scraper
gemini-2.0-flash + Search Grounding (1,500 RPD 무료)
website / email / phone / instagram / google_rating 한 번에 추출
"""

import os
import sys
import json
import time
import random
import gspread
from google import genai
from google.genai import types
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv("scrapers/.env", override=True)

DAILY_LIMIT = 1490   # 1,500 RPD 무료 한도, 안전 마진 10
RPM_DELAY   = 5.0    # 분당 12회 (안전)
MODEL       = "gemini-2.0-flash"

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
reviews_col = col("review_count")

if "phone" not in headers:
    sheet.update_cell(1, len(headers) + 1, "phone")
    headers.append("phone")
phone_col = col("phone")

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

PROMPT = """Find official contact details for this restaurant using Google Search.

Restaurant: "{name}"
Location: {city}, {country}

Return ONLY valid JSON (no markdown):
{{
  "website": "official URL or null",
  "email": "contact email or null",
  "phone": "phone with country code or null",
  "instagram": "@handle or null",
  "google_rating": 4.5,
  "total_reviews": 1234
}}

Rules:
- website: official site ONLY, not tripadvisor/yelp/google/instagram/facebook/michelin
- email: real contact email only, not noreply/support/admin
- phone: include country code
- instagram: @handle only
- google_rating: Google Maps float or null
- total_reviews: integer or null"""

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
        if result.get("website"):       updates.append((row_num, web_col,     result["website"]))
        if result.get("email"):         updates.append((row_num, email_col,   result["email"]))
        if result.get("phone"):         updates.append((row_num, phone_col,   result["phone"]))
        if result.get("instagram"):     updates.append((row_num, insta_col,   result["instagram"]))
        if result.get("google_rating"): updates.append((row_num, rating_col,  result["google_rating"]))
        if result.get("total_reviews"): updates.append((row_num, reviews_col, result["total_reviews"]))

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
