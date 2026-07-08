"""
SMBkits — TripAdvisor Fine Dining Scraper
파인다이닝 목록 → 페이지네이션 → 상세 페이지 → 추출 → 로컬 CSV 저장
"""

import os, sys, re, asyncio, random, csv
import browser_cookie3
from playwright.async_api import async_playwright
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv("scrapers/.env", override=True)

# ── 도시 설정 (geo ID는 TripAdvisor URL에서 확인) ──────────────
CITIES = [
    {"name": "Tokyo",         "country": "Japan",        "geo": 298184},
   # ── 1순위: 영어권 (북미) ────────────────────────────────────
    {"name": "London",        "country": "UK",           "geo": 186338},
    {"name": "New York",      "country": "USA",          "geo": 60763},
    {"name": "Los Angeles",   "country": "USA",          "geo": 32655},
    {"name": "Las Vegas",     "country": "USA",          "geo": 45963},
    {"name": "San Francisco", "country": "USA",          "geo": 60713},
    {"name": "Chicago",       "country": "USA",          "geo": 35805},
    {"name": "Miami",         "country": "USA",          "geo": 34438},
    {"name": "Toronto",       "country": "Canada",       "geo": 60963},
    # ── 2순위: 영어권 (오세아니아) ──────────────────────────────
    {"name": "Sydney",        "country": "Australia",    "geo": 255060},
    {"name": "Melbourne",     "country": "Australia",    "geo": 255100},
    # ── 2순위: 영어권 (아시아·중동 영어 비즈니스) ───────────────
    {"name": "Singapore",     "country": "Singapore",    "geo": 294260},
    {"name": "Hong Kong",     "country": "Hong Kong",    "geo": 294217},
    {"name": "Dubai",         "country": "UAE",          "geo": 295424},
    {"name": "Abu Dhabi",     "country": "UAE",          "geo": 297338},
    # ── 2순위: 영어권 (유럽 영어 공용어) ────────────────────────
    {"name": "Dublin",        "country": "Ireland",      "geo": 186605},
    {"name": "Valletta",      "country": "Malta",        "geo": 190711},
    # ── 3순위: 기타 언어권 (고영어구사율 유럽) ──────────────────
    {"name": "Amsterdam",     "country": "Netherlands",  "geo": 188590},
    {"name": "Copenhagen",    "country": "Denmark",      "geo": 189541},
    {"name": "Stockholm",     "country": "Sweden",       "geo": 189850},
    {"name": "Reykjavik",     "country": "Iceland",      "geo": 189952},
    # ── 3순위: 기타 언어권 (유럽) ───────────────────────────────
    {"name": "Paris",         "country": "France",       "geo": 187147},
    {"name": "Barcelona",     "country": "Spain",        "geo": 187497},
    {"name": "Madrid",        "country": "Spain",        "geo": 187514},
    {"name": "Rome",          "country": "Italy",        "geo": 187791},
    {"name": "Milan",         "country": "Italy",        "geo": 187849},
    {"name": "Brussels",      "country": "Belgium",      "geo": 188671},
    # ── 3순위: 기타 언어권 (동남아) ─────────────────────────────
    {"name": "Bangkok",       "country": "Thailand",     "geo": 293916},
    # ── 총알받이: 일본 (마지막 — 세션 말미 차단 흡수) ───────────
    {"name": "Osaka",         "country": "Japan",        "geo": 294211},
]

PAGE_SIZE = 30    # TripAdvisor 페이지당 업체 수
MAX_PAGES = 10    # 도시당 최대 페이지 (도시당 300개)
DELAY     = (1.5, 3)

HEADERS = [
    "business_name", "cuisine", "price_range",
    "city", "country", "address",
    "email", "website", "phone",
    "rating", "review_count", "tripadvisor_url",
    "strength_review", "weak_review",
    "outreach_status", "last_sent_at", "scraper_done",
]

CSV_PATH = "scrapers/results.csv"

def load_existing() -> set:
    """기존 CSV에서 수집된 URL 로드 (중복 방지)"""
    existing = set()
    if not os.path.exists(CSV_PATH):
        return existing
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get("tripadvisor_url", "").strip()
            if url:
                existing.add(url)
    return existing

def init_csv():
    """CSV 없으면 헤더 생성"""
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADERS)

def append_csv(row: dict):
    """CSV에 한 줄 즉시 append"""
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([row.get(h, "") for h in HEADERS])

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
        "strength_review": "", "weak_review": "",
        "outreach_status": "", "last_sent_at": "", "scraper_done": "Y",
    }
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("h1", timeout=10000)

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

        # 이메일 없으면 리뷰 추출 스킵
        if not row["email"]:
            return row

        # 강점/약점 리뷰 추출
        try:
            await page.evaluate("window.scrollBy(0, 1200)")
            # reviews-tab 컨테이너 먼저 대기 → 그 안에 reviewCard 파싱
            try:
                await page.wait_for_selector("[data-test-target='reviews-tab']", timeout=12000)
                await page.wait_for_selector("[data-automation='reviewCard']", timeout=8000)
            except Exception:
                pass  # 리뷰 없는 업체

            strength, weak = "", ""
            cards = await page.query_selector_all("[data-automation='reviewCard']")

            for card in cards[:20]:
                title_el = await card.query_selector("svg title")
                stars = 0
                if title_el:
                    title_text = await title_el.inner_text()
                    m2 = re.search(r'중\s*(\d+)', title_text)       # 한국어
                    if m2:
                        stars = int(m2.group(1))
                    else:
                        m2 = re.search(r'(\d+)\s*of\s*5', title_text)  # 영어
                        if m2: stars = int(m2.group(1))

                body_el = await card.query_selector("[data-test-target='review-body']")
                if not body_el:
                    continue
                text = (await body_el.inner_text()).strip()
                if len(text) < 15:
                    continue

                if stars >= 4 and not strength:
                    strength = text[:250]
                elif 1 <= stars <= 3 and not weak:
                    weak = text[:250]
                if strength and weak:
                    break

            row["strength_review"] = strength
            row["weak_review"]     = weak
        except Exception:
            pass

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
    init_csv()
    existing = load_existing()
    print(f"기존 수집: {len(existing)}개\n")

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
                    print(f"  페이지 {page_idx+1}: 결과 없음 → debug 저장")
                    break

                # 목록에서 상세 링크 수집
                links = await page.query_selector_all("a[href*='/Restaurant_Review']")
                hrefs = []
                seen = set()
                for link in links:
                    href = await link.get_attribute("href")
                    if not href or "/Restaurant_Review" not in href:
                        continue
                    try:
                        card = await link.evaluate_handle("el => el.closest('[data-test]') || el.parentElement.parentElement.parentElement")
                        card_text = await card.evaluate("el => el.innerText")
                        if "스폰서" in card_text or "Sponsored" in card_text:
                            continue
                    except Exception:
                        pass
                    full = "https://www.tripadvisor.com" + href if href.startswith("/") else href
                    full = full.split("?")[0].split("#")[0]
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
                    append_csv(row)  # 즉시 로컬 저장

                    status = "O" if row["email"] else "-"
                    print(f"    [{status}] {row['business_name'][:30]:<30} {row['email'] or '이메일없음'}")

                    city_count += 1
                    total += 1
                    await asyncio.sleep(random.uniform(*DELAY))

                await asyncio.sleep(random.uniform(*DELAY))

            print(f"  {city['name']} 완료: {city_count}개")

        await browser.close()
    print(f"\n전체 완료 — {total}개 수집 → {CSV_PATH}")

if __name__ == "__main__":
    asyncio.run(main())
