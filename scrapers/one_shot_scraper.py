"""
SMBkits — One-Shot Scraper (Playwright)
Google 검색 결과 Knowledge Panel → website / phone / rating 추출
website 크롤링 → email 추출
완전 무료, API 비용 없음
"""

import os
import sys
import re
import json
import time
import random
import asyncio
import gspread
from playwright.async_api import async_playwright
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv("scrapers/.env", override=True)

DAILY_LIMIT = 500

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds  = Credentials.from_service_account_file(
    os.environ.get("CREDS_FILE", "scrapers/credentials.json"), scopes=SCOPES
)
gc     = gspread.authorize(creds)
sheet  = gc.open_by_key(os.environ["SHEET_ID"]).worksheet(os.environ["SHEET_NAME"])

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

SOCIAL_EXCLUDE = [
    "instagram.com","facebook.com","twitter.com","x.com",
    "tripadvisor.com","yelp.com","google.com","michelin.com",
    "sevenrooms.com","opentable.com","booking.com","tabelog.com",
    "zomato.com","foursquare.com","tiktok.com","linktr.ee",
]
IMG_EXT    = (".png",".jpg",".jpeg",".gif",".svg",".webp",".ico")
SPAM_WORDS = ["noreply","no-reply","example","sentry","wixpress",
              "wordpress","cloudflare","support@","admin@","postmaster@"]

def is_social(url):
    return any(s in (url or "") for s in SOCIAL_EXCLUDE)

def extract_email(html):
    emails = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", html)
    for e in emails:
        el = e.lower()
        if any(el.endswith(x) for x in IMG_EXT): continue
        if any(x in el for x in SPAM_WORDS): continue
        return e
    return ""

async def scrape_google(page, name, city, country):
    query = f'"{name}" {city} {country} restaurant'
    await page.goto(
        f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=en&gl=us",
        wait_until="domcontentloaded", timeout=20000
    )
    await page.wait_for_timeout(random.randint(1500, 2500))

    result = {"website": "", "phone": "", "rating": "", "reviews": "", "instagram": ""}

    html = await page.content()

    # Website
    for sel in [
        "a[data-attrid*='website']",
        "div[data-attrid*='url'] a",
        "a[ping*='website']",
    ]:
        try:
            el = await page.query_selector(sel)
            if el:
                href = await el.get_attribute("href")
                if href and not is_social(href) and href.startswith("http"):
                    result["website"] = href
                    break
        except Exception:
            pass

    # Phone
    phone_match = re.search(r'(\+?[\d\s\-\(\)]{8,20})', html)
    try:
        for sel in ["[data-attrid*='phone'] span", "[data-dtype='d3ph']", "span[aria-label*='phone']"]:
            el = await page.query_selector(sel)
            if el:
                result["phone"] = (await el.inner_text()).strip()
                break
    except Exception:
        pass

    # Rating
    try:
        el = await page.query_selector("span.Aq14fc")
        if el:
            result["rating"] = (await el.inner_text()).strip()
        el2 = await page.query_selector("span.hqzQac")
        if el2:
            result["reviews"] = re.sub(r"[^\d]", "", await el2.inner_text())
    except Exception:
        pass

    # Instagram handle from search results
    ig_match = re.search(r'instagram\.com/([A-Za-z0-9_.]+)', html)
    if ig_match:
        result["instagram"] = "@" + ig_match.group(1)

    return result

async def crawl_email(page, url):
    if not url or is_social(url):
        return ""
    for target in [url, url.rstrip("/") + "/contact", url.rstrip("/") + "/about"]:
        try:
            await page.goto(target, wait_until="domcontentloaded", timeout=10000)
            email = extract_email(await page.content())
            if email:
                return email
        except Exception:
            continue
    return ""

async def main():
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
                rec.get("website", ""),
                rec.get("instagram", ""),
            ))
        if len(targets) >= DAILY_LIMIT:
            break

    print(f"오늘 처리: {len(targets)}개 / 한도 {DAILY_LIMIT}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US",
        )
        page = await context.new_page()

        for row_num, name, city, country, ex_web, ex_ig in targets:
            print(f"[{row_num}] {name} ({city}, {country})")
            updates = []
            try:
                data    = await scrape_google(page, name, city, country)
                website = ex_web or data["website"]
                email   = await crawl_email(page, website) if website else ""
                ig      = ex_ig or data["instagram"]
                phone   = data["phone"]
                rating  = data["rating"]
                reviews = data["reviews"]

                if website: updates.append((row_num, web_col,     website))
                if email:   updates.append((row_num, email_col,   email))
                if ig:      updates.append((row_num, insta_col,   ig))
                if phone:   updates.append((row_num, phone_col,   phone))
                if rating:  updates.append((row_num, rating_col,  rating))
                if reviews: updates.append((row_num, reviews_col, reviews))

                if updates:
                    sheet.batch_update([
                        {"range": gspread.utils.rowcol_to_a1(r, c), "values": [[v]]}
                        for r, c, v in updates
                    ])

                print(f"  web:{website or '-'} | email:{email or '-'} | ig:{ig or '-'} | tel:{phone or '-'}")

            except Exception as e:
                print(f"  FAIL: {str(e)[:100]}")

            await asyncio.sleep(random.uniform(2, 4))

        await browser.close()
    print("\n완료")

if __name__ == "__main__":
    asyncio.run(main())
