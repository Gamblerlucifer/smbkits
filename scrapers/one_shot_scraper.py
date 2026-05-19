"""
SMBkits — Batch One-Shot Scraper
gemini-2.5-flash + Search Grounding
15개 업체를 API 1회 호출로 처리 → 하루 22,500개 (1,500 RPD × 15)
"""

import os
import sys
import re
import json
import time
import requests
import gspread
from google import genai
from google.genai import types
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv("scrapers/.env", override=True)

BATCH_SIZE  = 15      # 1회 API 호출당 처리 업체 수
DAILY_LIMIT = 1490    # RPD 한도 (1,500 - 안전마진 10)
RPM_DELAY   = 15.0    # 15초 간격 = 분당 4회 (Search Grounding RPM 안전)

# 모델 폴백 체인: (model_id, use_search_grounding)
MODELS = [
    ("gemini-2.5-flash",      True),   # Search Grounding, RPD ~20
    ("gemini-3.1-flash-lite", False),  # 텍스트만, RPD 500
    ("gemma-3-27b-it",        False),  # 텍스트만, RPD 높음
]
current_model_idx = 0

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

web_col     = col("website")
insta_col   = col("instagram")
email_col   = col("email")
rating_col  = col("google_rating")
reviews_col = col("review_count")

if "phone" not in headers:
    sheet.update_cell(1, len(headers) + 1, "phone")
    headers.append("phone")
phone_col = col("phone")

# scraper_done 컬럼: 시도한 행 마킹 → 재실행 시 스킵
if "scraper_done" not in headers:
    sheet.update_cell(1, len(headers) + 1, "scraper_done")
    headers.append("scraper_done")
done_col = col("scraper_done")

# ── 이메일 크롤링 ────────────────────────────────────────────
IMG_EXT    = (".png",".jpg",".jpeg",".gif",".svg",".webp",".ico")
SPAM_WORDS = ["noreply","no-reply","example","sentry","wixpress",
              "wordpress","cloudflare","support@","admin@","postmaster@"]
SOCIAL_EXCLUDE = ["instagram.com","facebook.com","twitter.com",
                  "tripadvisor.com","yelp.com","google.com","michelin.com","booking.com"]

def clean_instagram(val):
    if not val: return ""
    m = re.search(r"instagram\.com/([A-Za-z0-9_.]+)", val)
    if m: return "@" + m.group(1).rstrip("/")
    return val if val.startswith("@") else ""

def crawl_email(url):
    if not url or any(s in url for s in SOCIAL_EXCLUDE): return ""
    hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for target in [url, url.rstrip("/") + "/contact", url.rstrip("/") + "/about"]:
        try:
            res = requests.get(target, headers=hdrs, timeout=8)
            for e in re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", res.text):
                el = e.lower()
                if any(el.endswith(x) for x in IMG_EXT): continue
                if any(x in el for x in SPAM_WORDS): continue
                return e
        except Exception:
            continue
    return ""

# ── 타겟 추출: scraper_done 없는 행만 ────────────────────────
all_records = sheet.get_all_records()
print(f"총 {len(all_records)}개 리드 탐색 중...")

targets = []
for i, rec in enumerate(all_records, start=2):
    if not rec.get("scraper_done"):   # 아직 시도 안 한 행만
        targets.append({
            "row": i,
            "name": rec.get("business_name", ""),
            "city": rec.get("city", ""),
            "country": rec.get("country", ""),
        })
    if len(targets) >= DAILY_LIMIT * BATCH_SIZE:
        break

print(f"미처리: {len(targets)}개 | 오늘 처리: {min(len(targets), DAILY_LIMIT * BATCH_SIZE)}개 "
      f"(배치 {BATCH_SIZE}개 × {DAILY_LIMIT} 호출)\n")

# ── 배치 프롬프트 ────────────────────────────────────────────
PROMPT_TEMPLATE = """Search Google for each of the following restaurants and extract their contact info.
Return a JSON array with one object per restaurant, in the same order.

Restaurants:
{restaurant_list}

Return ONLY a valid JSON array:
[
  {{
    "name": "exact restaurant name as given",
    "website": "official website URL or null",
    "email": "contact email or null",
    "phone": "phone with country code or null",
    "instagram": "instagram URL or null",
    "google_rating": 4.5,
    "review_count": 1234
  }},
  ...
]

Rules:
- website: official site ONLY, not tripadvisor/yelp/google/instagram/facebook/michelin
- email: real contact email only, not noreply/support/admin
- phone: include country code
- google_rating: Google Maps float or null
- review_count: integer or null
- Return exactly {count} objects in the array"""

def parse_array(text):
    m = re.search(r"```json\s*(\[.*?\])\s*```", text, re.DOTALL)
    if m: return json.loads(m.group(1))
    m = re.search(r"(\[.*?\])", text, re.DOTALL)
    if m: return json.loads(m.group(1))
    return []

# ── 배치 실행 ────────────────────────────────────────────────
batches = [targets[i:i+BATCH_SIZE] for i in range(0, len(targets), BATCH_SIZE)]
total_done = 0

for b_idx, batch in enumerate(batches[:DAILY_LIMIT]):
    restaurant_list = "\n".join(
        [f"{j+1}. {r['name']} ({r['city']}, {r['country']})" for j, r in enumerate(batch)]
    )
    print(f"[배치 {b_idx+1}/{min(len(batches), DAILY_LIMIT)}] {len(batch)}개 처리 중...")

    try:
        # 모델 폴백 체인: 2.5 Flash → 3.1 Flash Lite → Gemma
        resp = None
        while current_model_idx < len(MODELS):
            model_id, use_grounding = MODELS[current_model_idx]
            config = types.GenerateContentConfig(
                tools=[{"google_search": {}}] if use_grounding else None
            )
            succeeded = False
            for attempt in range(2):
                try:
                    resp = gemini.models.generate_content(
                        model=model_id,
                        contents=PROMPT_TEMPLATE.format(
                            restaurant_list=restaurant_list,
                            count=len(batch)
                        ),
                        config=config,
                    )
                    succeeded = True
                    break
                except Exception as e:
                    err = str(e)
                    if "429" in err or "RESOURCE_EXHAUSTED" in err:
                        if attempt == 0:
                            print(f"  [{model_id}] 429 → 30초 대기 후 재시도...")
                            time.sleep(30)
                    else:
                        raise
            if succeeded:
                break
            print(f"  [{model_id}] RPD 소진 → 다음 모델로 전환")
            current_model_idx += 1

        if not resp:
            raise Exception("모든 모델 한도 초과")
        results = parse_array(resp.text)

        sheet_updates = []
        for j, item in enumerate(results):
            if j >= len(batch): break
            row_num   = batch[j]["row"]
            website   = item.get("website") or ""
            email     = item.get("email") or ""
            instagram = clean_instagram(item.get("instagram") or "")
            phone     = item.get("phone") or ""

            if website and not email:
                email = crawl_email(website)

            if website:                     sheet_updates.append((row_num, web_col,     website))
            if email:                       sheet_updates.append((row_num, email_col,   email))
            if phone:                       sheet_updates.append((row_num, phone_col,   phone))
            if instagram:                   sheet_updates.append((row_num, insta_col,   instagram))
            if item.get("google_rating"):   sheet_updates.append((row_num, rating_col,  item["google_rating"]))
            if item.get("review_count"):    sheet_updates.append((row_num, reviews_col, item["review_count"]))
            # 결과 유무 관계없이 시도 완료 마킹
            sheet_updates.append((row_num, done_col, "Y"))

            name = batch[j]['name']
            print(f"  [{row_num}] {name[:25]:<25} web:{website[:30] or '-'} | ig:{instagram or '-'} | email:{email or '-'}")

        if sheet_updates:
            sheet.batch_update([
                {"range": gspread.utils.rowcol_to_a1(r, c), "values": [[v]]}
                for r, c, v in sheet_updates
            ])

        total_done += len(batch)

    except Exception as e:
        print(f"  FAIL: {str(e)[:120]}")

    time.sleep(RPM_DELAY)

print(f"\n완료 — 총 {total_done}개 처리")
