"""
SMBkits — 리뷰 보충 스크래퍼
이메일 있는데 strength_review / weak_review 비어있는 행만 재방문해서 채움

Usage:
    python scrapers/fill_reviews.py
"""

import os, sys, re, asyncio, random, csv
import browser_cookie3
from playwright.async_api import async_playwright
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)

CSV_PATH = os.path.join(os.path.dirname(__file__), "results.csv")
DELAY    = (1.5, 3)

HEADERS = [
    "business_name", "cuisine", "price_range",
    "city", "country", "address",
    "email", "website", "phone",
    "rating", "review_count", "tripadvisor_url",
    "strength_review", "weak_review",
    "outreach_status", "last_sent_at", "scraper_done",
]


def load_csv() -> list[dict]:
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def save_csv(rows: list[dict]):
    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        w.writerows(rows)


def get_chrome_cookies():
    try:
        jar = browser_cookie3.chrome(domain_name=".tripadvisor.com")
        cookies = []
        for c in jar:
            cookies.append({
                "name": c.name, "value": c.value,
                "domain": c.domain, "path": c.path, "secure": c.secure,
            })
        print(f"Chrome 쿠키 {len(cookies)}개 로드")
        return cookies
    except Exception as e:
        print(f"쿠키 로드 실패: {e}")
        return []


async def fetch_reviews(page, url: str) -> tuple[str, str]:
    """리뷰만 긁어서 (strength, weak) 반환"""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("h1", timeout=10000)

        try:
            await page.wait_for_selector("[data-test-target='reviews-tab']", timeout=12000)
            tab_el = await page.query_selector("[data-test-target='reviews-tab']")
            if tab_el:
                await tab_el.evaluate("el => el.scrollIntoView({block:'center'})")
            else:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.6)")
            await page.wait_for_selector("[data-automation='reviewCard']", timeout=12000)
        except Exception:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.6)")
            try:
                await page.wait_for_selector("[data-automation='reviewCard']", timeout=6000)
            except Exception:
                pass

        strength, weak = "", ""
        cards = await page.query_selector_all("[data-automation='reviewCard']")
        print(f"      리뷰카드: {len(cards)}개")

        for card in cards[:20]:
            title_el = await card.query_selector("svg[data-automation='bubbleRatingImage'] title")
            stars = 0
            if title_el:
                title_text = await title_el.evaluate("el => el.textContent")
                m2 = re.search(r'중\s*(\d+)', title_text)
                if m2:
                    stars = int(m2.group(1))
                else:
                    m2 = re.search(r'(\d+)\s*of\s*5', title_text)
                    if m2: stars = int(m2.group(1))

            body_el = await card.query_selector("[data-test-target='review-body']")
            if not body_el:
                continue
            text = (await body_el.evaluate("el => el.innerText")).strip()
            if len(text) < 15:
                continue

            if stars >= 4 and not strength:
                strength = text[:250]
            elif 1 <= stars <= 3 and not weak:
                weak = text[:250]
            if strength and weak:
                break

        return strength, weak

    except Exception as e:
        print(f"      오류: {str(e)[:80]}")
        return "", ""


async def main():
    rows = load_csv()

    # 이메일 있는데 리뷰 하나라도 빈 행
    targets = [
        (i, r) for i, r in enumerate(rows)
        if r.get("email", "").strip()
        and (not r.get("strength_review", "").strip() or not r.get("weak_review", "").strip())
    ]

    print(f"보충 대상: {len(targets)}개\n")
    if not targets:
        print("보충할 항목 없음.")
        return

    chrome_cookies = get_chrome_cookies()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        if chrome_cookies:
            await context.add_cookies(chrome_cookies)
        page = await context.new_page()

        done = 0
        for i, row in targets:
            url = row.get("tripadvisor_url", "").strip()
            if not url:
                continue

            print(f"[{done+1}/{len(targets)}] {row['business_name'][:35]}")
            strength, weak = await fetch_reviews(page, url)

            if strength or weak:
                rows[i]["strength_review"] = strength
                rows[i]["weak_review"]     = weak
                save_csv(rows)  # 즉시 저장
                print(f"      ✅ 저장 완료")
            else:
                print(f"      ⚠️  리뷰 없음")

            done += 1
            await asyncio.sleep(random.uniform(*DELAY))

        await browser.close()

    print(f"\n완료 — {done}개 처리")


if __name__ == "__main__":
    asyncio.run(main())
