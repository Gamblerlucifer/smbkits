"""
SMBkits — Instagram Email Scraper
instagram handle → 프로필 방문 → Contact 이메일 추출
비즈니스 계정은 Email 버튼에 이메일 노출됨
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

DAILY_LIMIT = 300   # Instagram 차단 방지 보수적 설정

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

email_col = col("email")
insta_col = col("instagram")

# instagram 있고 email 없는 행 추출
all_records = sheet.get_all_records()
print(f"총 {len(all_records)}개 리드 탐색 중...")

targets = []
for i, rec in enumerate(all_records, start=2):
    ig = rec.get("instagram", "").strip()
    if ig and not rec.get("email"):
        handle = ig.lstrip("@").split("/")[-1].strip()
        if handle:
            targets.append((i, handle, rec.get("business_name", "")))
    if len(targets) >= DAILY_LIMIT:
        break

print(f"Instagram 이메일 추출 대상: {len(targets)}개\n")

SPAM_WORDS = ["noreply","no-reply","example","sentry","wixpress",
              "wordpress","cloudflare","support@","admin@","postmaster@"]
IMG_EXT    = (".png",".jpg",".jpeg",".gif",".svg",".webp",".ico")

def extract_email(text):
    for e in re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text):
        el = e.lower()
        if any(el.endswith(x) for x in IMG_EXT): continue
        if any(x in el for x in SPAM_WORDS): continue
        return e
    return ""

async def get_instagram_email(page, handle):
    # 모바일 버전이 Contact 버튼 노출 더 잘 됨
    url = f"https://www.instagram.com/{handle}/"
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(random.randint(2000, 3500))

        html = await page.content()

        # 1. HTML에서 직접 이메일 추출
        email = extract_email(html)
        if email:
            return email

        # 2. "Email" 링크 (mailto:) 클릭
        mailto = await page.query_selector("a[href^='mailto:']")
        if mailto:
            href = await mailto.get_attribute("href")
            email = href.replace("mailto:", "").split("?")[0].strip()
            if email and "@" in email:
                return email

        # 3. Contact/Email 버튼 찾기
        for sel in ["a[href*='email']", "div[role='button']:has-text('Email')",
                    "a:has-text('Email')", "button:has-text('Email')"]:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.click()
                    await page.wait_for_timeout(1500)
                    html2 = await page.content()
                    email = extract_email(html2)
                    if email:
                        return email
            except Exception:
                continue

    except Exception as e:
        print(f"  접속 실패: {str(e)[:60]}")

    return ""

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            # 모바일 UA — Instagram Contact 버튼 노출에 유리
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            viewport={"width": 390, "height": 844},
            locale="en-US",
        )
        page = await context.new_page()

        found = 0
        for row_num, handle, name in targets:
            print(f"[{row_num}] @{handle} ({name})")
            email = await get_instagram_email(page, handle)

            if email:
                sheet.update_cell(row_num, email_col, email)
                print(f"  -> {email}")
                found += 1
            else:
                print(f"  -> 이메일 없음")

            await asyncio.sleep(random.uniform(3, 6))

        await browser.close()

    print(f"\n완료 — {found}/{len(targets)}개 이메일 추출")

if __name__ == "__main__":
    asyncio.run(main())
