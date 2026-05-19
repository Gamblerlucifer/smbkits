"""
SMBkits — TripAdvisor Fine Dining Scraper
파인다이닝 목록 → 페이지네이션 → 상세 페이지 → 추출 → 시트 저장
"""

import os, sys, re, asyncio, random, gspread
import browser_cookie3
from playwright.async_api import async_playwright
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv("scrapers/.env", override=True)

# ── 도시 설정 (geo ID는 TripAdvisor URL에서 확인) ──────────────
CITIES = [
    {"name": "London",    "country": "UK",          "geo": 186338},
    {"name": "Paris",     "country": "France",      "geo": 187147},
    {"name": "Tokyo",     "country": "Japan",       "geo": 298184},
    {"name": "New York",  "country": "USA",         "geo": 60763},
    {"name": "Singapore", "country": "Singapore",   "geo": 294260},
    {"name": "Hong Kong", "country": "Hong Kong",   "geo": 294217},
    {"name": "Dubai",     "country": "UAE",         "geo": 295424},
    {"name": "Barcelona", "country": "Spain",       "geo": 187497},
    {"name": "Rome",      "country": "Italy",       "geo": 187791},
    {"name": "Sydney",    "country": "Australia",   "geo": 255060},
]

PAGE_SIZE   = 30    # TripAdvisor 페이지당 업체 수
MAX_PAGES   = 10    # 도시당 최대 페이지 (도시당 300개)
DELAY       = (3, 6)

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(
    os.environ.get("CREDS_FILE", "scrapers/credentials.json"), scopes=SCOPES
)
gc    = gspread.authorize(creds)
sheet = gc.open_by_key(os.environ["SHEET_ID"]).worksheet(os.environ["SHEET_NAME"])

headers = sheet.row_values(1)
def col(name): return headers.index(name) + 1

# 이미 수집된 TripAdvisor URL 목록 (중복 방지)
existing = set()
for rec in sheet.get_all_records():
    url = rec.get("tripadvisor_url", "")
    if url: existing.add(url)
print(f"기존 수집: {len(existing)}개\n")

def list_url(geo, offset=0):
    return (
        f"https://www.tripadvisor.com/FindRestaurants"
        f"?geo={geo}&establishmentTypes=10591&priceTypes=10954"
        f"&broadened=false&offset={offset}"
    )

async def get_detail(page, url, city_name, country):
    row = {
        "business_name": "", "cuisine": "", "price_range": "",
        "city": city_name,   "country": country, "address": "",
        "email": "", "website": "", "phone": "",
        "rating": "", "review_count": "", "tripadvisor_url": url,
        "outreach_status": "", "last_sent_at": "", "scraper_done": "Y",
    }
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        await page.wait_for_selector("h1", timeout=10000)
        await page.wait_for_timeout(random.randint(1500, 2500))

        # 이름
        el = await page.query_selector("h1")
        if el: row["business_name"] = (await el.inner_text()).strip()

        # 이메일
        el = await page.query_selector("a[href^='mailto:']")
        if el:
            href = await el.get_attribute("href")
            row["email"] = href.replace("mailto:", "").split("?")[0].strip()

        # 웹사이트
        el = await page.query_selector("a[data-automation='restaurantsWebsiteButton']")
        if el:
            href = await el.get_attribute("href") or ""
            # TripAdvisor redirect URL에서 실제 URL 추출
            m = re.search(r"url=([^&]+)", href)
            row["website"] = m.group(1) if m else href.split("?")[0]

        # 전화
        el = await page.query_selector("a[href^='tel:']")
        if el:
            href = await el.get_attribute("href")
            row["phone"] = href.replace("tel:", "").strip()

        # 주소
        el = await page.query_selector("button[data-automation='restaurantsMapLinkOnName'], span[data-automation='restaurantsMapLinkOnName']")
        if el: row["address"] = (await el.inner_text()).strip()

        # 평점 / 리뷰수 (JSON-LD)
        html = await page.content()
        m = re.search(r'"ratingValue"\s*:\s*([\d.]+)', html)
        if m: row["rating"] = float(m.group(1))
        m = re.search(r'"reviewCount"\s*:\s*(\d+)', html)
        if m: row["review_count"] = int(m.group(1))

        # 요리 종류
        m = re.search(r'"servesCuisine"\s*:\s*"([^"]+)"', html)
        if m: row["cuisine"] = m.group(1)

        # 가격대 ($$$$)
        m = re.search(r'priceRange["\s:]+(\$+)', html)
        if m: row["price_range"] = m.group(1)

    except Exception as e:
        print(f"    오류: {str(e)[:80]}")

    return row

def get_chrome_cookies():
    """Chrome에서 TripAdvisor 쿠키 추출"""
    try:
        jar = browser_cookie3.chrome(domain_name=".tripadvisor.com")
        cookies = []
        for c in jar:
            cookies.append({
                "name": c.name,
                "value": c.value,
                "domain": c.domain,
                "path": c.path,
                "secure": c.secure,
            })
        print(f"Chrome 쿠키 {len(cookies)}개 로드")
        return cookies
    except Exception as e:
        print(f"쿠키 로드 실패: {e}")
        return []

async def main():
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
        total = 0

        for city in CITIES:
            print(f"\n{'='*40}")
            print(f"{city['name']} ({city['country']}) 수집 시작")
            print(f"{'='*40}")
            city_count = 0

            for page_idx in range(MAX_PAGES):
                offset = page_idx * PAGE_SIZE
                await page.goto(list_url(city["geo"], offset), wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(4)
                try:
                    await page.wait_for_selector("a[href*='/Restaurant_Review']", timeout=10000)
                except Exception:
                    html = await page.content()
                    with open(f"debug_{city['name']}_{page_idx}.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    print(f"  페이지 {page_idx+1}: 결과 없음 → debug_{city['name']}_{page_idx}.html 저장")
                    break

                # 목록에서 상세 링크 수집
                links = await page.query_selector_all("a[href*='/Restaurant_Review']")
                hrefs = []
                seen = set()
                for link in links:
                    href = await link.get_attribute("href")
                    if not href or "/Restaurant_Review" not in href:
                        continue
                    # 스폰서 링크 제외
                    try:
                        card = await link.evaluate_handle("el => el.closest('[data-test]') || el.parentElement.parentElement.parentElement")
                        card_text = await card.evaluate("el => el.innerText")
                        if "스폰서" in card_text or "Sponsored" in card_text:
                            continue
                    except Exception:
                        pass
                    full = "https://www.tripadvisor.com" + href if href.startswith("/") else href
                    full = full.split("?")[0]
                    # location ID 기준 중복 제거 (스폰서+일반 동일 업체 방지)
                    m = re.search(r"-d(\d+)-", full)
                    loc_id = m.group(1) if m else full
                    if loc_id not in seen and full not in existing:
                        seen.add(loc_id)
                        hrefs.append(full)

                if not hrefs:
                    print(f"  페이지 {page_idx+1}: 새 업체 없음, 종료")
                    break

                print(f"  페이지 {page_idx+1}: {len(hrefs)}개 업체")

                for url in hrefs:
                    row = await get_detail(page, url, city["name"], city["country"])
                    existing.add(url)

                    sheet.append_row([row[h] for h in [
                        "business_name", "cuisine", "price_range",
                        "city", "country", "address",
                        "email", "website", "phone",
                        "rating", "review_count", "tripadvisor_url",
                        "outreach_status", "last_sent_at", "scraper_done",
                    ]])

                    status = "O" if row["email"] else "-"
                    print(f"    [{status}] {row['business_name'][:30]:<30} {row['email'] or '이메일없음'}")

                    city_count += 1
                    total += 1
                    await asyncio.sleep(random.uniform(*DELAY))

                await asyncio.sleep(random.uniform(*DELAY))

            print(f"  {city['name']} 완료: {city_count}개")

        await browser.close()
    print(f"\n전체 완료 — {total}개 수집")

if __name__ == "__main__":
    asyncio.run(main())
