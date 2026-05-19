"""
SMBkits — Google Search Scraper
Playwright로 Google 검색 → 이메일/웹사이트/인스타 추출
Gemini API 불필요 — 쿼터 제한 없음
"""

import os
import sys
import re
import asyncio
import random
import gspread
from playwright.async_api import async_playwright
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv("scrapers/.env", override=True)

DAILY_LIMIT  = 500    # 하루 처리 업체 수 (Google 차단 방지)
PAGE_DELAY   = (2, 4) # 페이지 간 랜덤 딜레이(초)

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_file(
    os.environ.get("CREDS_FILE", "scrapers/credentials.json"), scopes=SCOPES
)
gc    = gspread.authorize(creds)
sheet = gc.open_by_key(os.environ["SHEET_ID"]).worksheet(os.environ["SHEET_NAME"])

headers = sheet.row_values(1)

def col(name):
    return headers.index(name) + 1

web_col     = col("website")
insta_col   = col("instagram")
email_col   = col("email")
rating_col  = col("google_rating")
reviews_col = col("review_count")
phone_col   = col("phone") if "phone" in headers else None

for col_name in ["phone", "scraper_done"]:
    if col_name not in headers:
        sheet.update_cell(1, len(headers) + 1, col_name)
        headers.append(col_name)

phone_col = col("phone")
done_col  = col("scraper_done")

# ── 상수 ────────────────────────────────────────────────────
IMG_EXT    = (".png",".jpg",".jpeg",".gif",".svg",".webp",".ico")
SPAM_WORDS = ["noreply","no-reply","example","sentry","wixpress",
              "wordpress","cloudflare","support@","admin@","postmaster@"]
SOCIAL_EXCLUDE = ["instagram.com","facebook.com","twitter.com",
                  "tripadvisor.com","yelp.com","google.com","michelin.com","booking.com"]
BOOKING_PLATFORMS = ["sevenrooms.com","opentable.com","resy.com","tock.com",
                     "quandoo.com","chope.co","tablecheck.com","bentobox.com","toasttab.com"]
BIO_PLATFORMS = ["linktr.ee","beacons.ai","bento.me","bio.site","linkinbio"]

def extract_email(text):
    for e in re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text):
        el = e.lower()
        if any(el.endswith(x) for x in IMG_EXT): continue
        if any(x in el for x in SPAM_WORDS): continue
        return e
    return ""

def extract_instagram(text):
    m = re.search(r"instagram\.com/([A-Za-z0-9_.]+)", text)
    if m:
        handle = m.group(1).rstrip("/")
        if handle not in ("p","reel","explore","accounts","stories"):
            return "@" + handle
    return ""

def extract_phone(text):
    # 국가코드 포함 전화번호
    m = re.search(r"\+\d[\d\s\-().]{7,20}", text)
    return m.group(0).strip() if m else ""

# ── 타겟 추출 ────────────────────────────────────────────────
all_records = sheet.get_all_records()
print(f"총 {len(all_records)}개 리드 탐색 중...")

targets = []
for i, rec in enumerate(all_records, start=2):
    if not rec.get("scraper_done"):
        targets.append({
            "row": i,
            "name": rec.get("business_name", ""),
            "city": rec.get("city", ""),
            "country": rec.get("country", ""),
        })
    if len(targets) >= DAILY_LIMIT:
        break

print(f"미처리: {len(targets)}개 | 오늘 처리: {min(len(targets), DAILY_LIMIT)}개\n")

# ── 검색 쿼리 패턴 ────────────────────────────────────────────
def search_queries(name, city, country):
    return [
        f'"{name}" {city} email contact',
        f'"{name}" {city} "@" reservations',
        f'"{name}" {city} private dining press',
        f'"{name}" {city} site:sevenrooms.com OR site:resy.com OR site:opentable.com OR site:tock.com',
    ]

async def get_page_email(page, url, timeout=10000):
    """URL 방문 후 이메일 추출"""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        await page.wait_for_timeout(random.randint(1000, 2000))
        html = await page.content()
        email = extract_email(html)
        if email:
            return email
        # mailto: 링크
        mailto = await page.query_selector("a[href^='mailto:']")
        if mailto:
            href = await mailto.get_attribute("href")
            e = href.replace("mailto:", "").split("?")[0].strip()
            if e and "@" in e:
                return e
    except Exception:
        pass
    return ""

async def scrape_restaurant(page, rec):
    name    = rec["name"]
    city    = rec["city"]
    country = rec["country"]

    result = {"website": "", "email": "", "instagram": "", "phone": "", "google_rating": None, "review_count": None}

    for query in search_queries(name, city, country):
        try:
            search_url = "https://www.google.com/search?q=" + query.replace(" ", "+")
            await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(random.randint(*[x * 1000 for x in PAGE_DELAY]))

            html = await page.content()

            # 이메일 직접 추출
            if not result["email"]:
                result["email"] = extract_email(html)

            # 인스타그램
            if not result["instagram"]:
                result["instagram"] = extract_instagram(html)

            # 전화번호
            if not result["phone"]:
                result["phone"] = extract_phone(html)

            # Google 평점 (Knowledge Panel)
            if not result["google_rating"]:
                m = re.search(r'(\d\.\d)\s*/\s*5|"(\d\.\d)"\s*stars?', html, re.IGNORECASE)
                if m:
                    result["google_rating"] = float(m.group(1) or m.group(2))

            # 공식 웹사이트 찾기 (예약 플랫폼·소셜 제외)
            if not result["website"]:
                links = re.findall(r'href="(https?://[^"]+)"', html)
                for link in links:
                    if any(s in link for s in SOCIAL_EXCLUDE): continue
                    if any(s in link for s in ["google.com","cache:","translate"]): continue
                    if any(p in link for p in BOOKING_PLATFORMS):
                        # 예약 플랫폼 → 이메일 추출 시도
                        if not result["email"]:
                            email = await get_page_email(page, link)
                            if email:
                                result["email"] = email
                        continue
                    if any(p in link for p in BIO_PLATFORMS):
                        # bio 페이지 → 이메일 추출
                        if not result["email"]:
                            email = await get_page_email(page, link)
                            if email:
                                result["email"] = email
                        continue
                    # 공식 사이트 후보
                    if name.lower().split()[0] in link.lower() or city.lower() in link.lower():
                        result["website"] = link.split("?")[0]
                        break

            if result["email"]:
                break  # 이메일 찾으면 쿼리 종료

        except Exception as e:
            if "ERR_TOO_MANY_REDIRECTS" not in str(e):
                print(f"    검색 오류: {str(e)[:60]}")
            continue

    # 공식 사이트 있고 이메일 없으면 직접 크롤
    if result["website"] and not result["email"]:
        for path in ["", "/contact", "/about", "/private-dining", "/press", "/reservations", "/events"]:
            url = result["website"].rstrip("/") + path
            email = await get_page_email(page, url)
            if email:
                result["email"] = email
                break

    return result

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        page = await context.new_page()

        found_email = 0
        for rec in targets:
            row_num = rec["row"]
            name    = rec["name"]
            print(f"[{row_num}] {name[:30]}")

            result = await scrape_restaurant(page, rec)

            sheet_updates = []
            if result["website"]:   sheet_updates.append((row_num, web_col,     result["website"]))
            if result["email"]:     sheet_updates.append((row_num, email_col,   result["email"]))
            if result["phone"]:     sheet_updates.append((row_num, phone_col,   result["phone"]))
            if result["instagram"]: sheet_updates.append((row_num, insta_col,   result["instagram"]))
            if result["google_rating"]:  sheet_updates.append((row_num, rating_col,  result["google_rating"]))
            if result["review_count"]:   sheet_updates.append((row_num, reviews_col, result["review_count"]))
            sheet_updates.append((row_num, done_col, "Y"))

            if sheet_updates:
                sheet.batch_update([
                    {"range": gspread.utils.rowcol_to_a1(r, c), "values": [[v]]}
                    for r, c, v in sheet_updates
                ])

            if result["email"]:
                found_email += 1

            print(f"  web:{result['website'][:35] or '-'} | ig:{result['instagram'] or '-'} | email:{result['email'] or '-'}")
            await asyncio.sleep(random.uniform(*PAGE_DELAY))

        await browser.close()

    print(f"\n완료 — {found_email}/{len(targets)}개 이메일 수집")

if __name__ == "__main__":
    asyncio.run(main())
