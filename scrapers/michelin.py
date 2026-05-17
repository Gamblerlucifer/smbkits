"""
SMBkits — Michelin Guide Scraper
guide.michelin.com → Google Sheets Lead DB

Usage:
    python scrapers/michelin.py
"""

import asyncio
import time
import json
import re
from playwright.async_api import async_playwright
import gspread
from google.oauth2.service_account import Credentials

# ── Config ────────────────────────────────────────────────
SHEET_ID      = "1P7i1J9hC1uWS4zvxLOlL2RtFNBw-wj9VzNIU5edspUw"
SHEET_NAME    = "SMBkits Lead DB"
CREDS_FILE    = "scrapers/credentials.json"
BASE_URL      = "https://guide.michelin.com/en/restaurants/page"
SORT          = "rating"  # distance(IP기준) 대신 rating으로 전세계 커버

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── Google Sheets ─────────────────────────────────────────
def get_sheet():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    return sheet

def get_existing_keys(sheet):
    """중복 방지: 이미 있는 name+city 조합 세트 반환"""
    records = sheet.get_all_values()
    existing = set()
    for row in records[1:]:  # skip header
        if row[0] and row[2]:
            existing.add(f"{row[0].strip().lower()}|{row[2].strip().lower()}")
    return existing

def append_rows(sheet, rows):
    if rows:
        sheet.append_rows(rows, value_input_option="RAW")
        print(f"  → {len(rows)}개 행 추가 완료")

# ── Michelin Scraper ──────────────────────────────────────
async def scrape_michelin():
    sheet = get_sheet()
    existing_keys = get_existing_keys(sheet)
    print(f"기존 데이터: {len(existing_keys)}개")

    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        # 마지막 페이지 번호 확인
        first_url = f"{BASE_URL}/1?sort={SORT}"
        await page.goto(first_url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)
        last_page = await page.evaluate("""() => {
            const links = [...document.querySelectorAll('.pagination a')];
            const nums = links.map(a => parseInt(a.textContent.trim())).filter(n => !isNaN(n));
            return nums.length ? Math.max(...nums) : 1;
        }""")
        print(f"총 {last_page}페이지 감지")

        page_num = 1
        while page_num <= last_page:
            url = f"{BASE_URL}/{page_num}?sort={SORT}"
            print(f"\n[페이지 {page_num}/{last_page}] {url}")

            if page_num > 1:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)

            # 레스토랑 카드 추출
            cards = await page.query_selector_all(".card__menu")
            if not cards:
                print("  → 카드 없음. 종료.")
                break

            print(f"  카드 {len(cards)}개 발견")
            batch = []

            for card in cards:
                try:
                    # data-* 속성으로 직접 추출 (가장 안정적)
                    el = await card.query_selector(".js-bookmark-restaurant")
                    if not el:
                        continue

                    name       = await el.get_attribute("data-restaurant-name") or ""
                    city       = await el.get_attribute("data-dtm-city") or ""
                    country    = await el.get_attribute("data-restaurant-selection") or ""
                    distinction = await el.get_attribute("data-dtm-distinction") or ""

                    distinction_map = {
                        "THREE_STARS":  "★★★ Star",
                        "TWO_STARS":    "★★ Star",
                        "ONE_STAR":     "★ Star",
                        "BIB_GOURMAND": "Bib Gourmand",
                        "SELECTED":     "Selected",
                        "3 star":       "★★★ Star",
                        "2 star":       "★★ Star",
                        "1 star":       "★ Star",
                        "bib":          "Bib Gourmand",
                        "selected":     "Selected",
                    }
                    authority_grade = distinction_map.get(distinction, distinction)

                    # 상세 페이지 URL
                    link_el = await card.query_selector("a[href*='/restaurant/']")
                    href = await link_el.get_attribute("href") if link_el else ""
                    detail_url = f"https://guide.michelin.com{href}" if href.startswith("/") else href

                    # 중복 체크
                    key = f"{name.lower()}|{city.lower()}"
                    if key in existing_keys:
                        continue

                    row = [
                        name,           # business_name
                        "Restaurant",   # category
                        city,           # city
                        country,        # country
                        "",             # website (상세 페이지에서 추출 예정)
                        "",             # instagram
                        "",             # email
                        "Michelin",     # source_type
                        authority_grade,# authority_grade
                        "",             # google_rating
                        "",             # review_count
                        "",             # premium_score
                        "",             # negative_review
                        "",             # sentiment_score
                        "pending",      # outreach_status
                        "",             # reply_status
                        detail_url,     # notes (상세 URL 임시 저장)
                    ]
                    batch.append(row)
                    existing_keys.add(key)

                except Exception as e:
                    print(f"  카드 파싱 오류: {e}")
                    continue

            if batch:
                results.extend(batch)
                append_rows(sheet, batch)
                print(f"  ✓ {len(batch)}개 신규 추가")

            page_num += 1
            await asyncio.sleep(1)  # 서버 부담 방지

        await browser.close()

    print(f"\n완료 — 총 {len(results)}개 신규 레스토랑 추가")
    return results


if __name__ == "__main__":
    asyncio.run(scrape_michelin())
