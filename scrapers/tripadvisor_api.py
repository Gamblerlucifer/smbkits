"""
SMBkits — TripAdvisor 스크래퍼 (curl_cffi)
Chrome TLS 핑거프린트 완전 모방 → DataDome 우회
브라우저 불필요, GitHub Actions 가능
"""

import os, sys, re, json, time, gspread, asyncio
from curl_cffi import requests
from playwright.async_api import async_playwright
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv("scrapers/.env", override=True)

DELAY = 2.0

CITIES = [
    {"name": "London",    "country": "UK",        "geo": 186338},
    {"name": "Paris",     "country": "France",    "geo": 187147},
    {"name": "Tokyo",     "country": "Japan",     "geo": 298184},
    {"name": "New York",  "country": "USA",       "geo": 60763},
    {"name": "Singapore", "country": "Singapore", "geo": 294260},
    {"name": "Hong Kong", "country": "Hong Kong", "geo": 294217},
    {"name": "Dubai",     "country": "UAE",       "geo": 295424},
    {"name": "Barcelona", "country": "Spain",     "geo": 187497},
    {"name": "Rome",      "country": "Italy",     "geo": 187791},
    {"name": "Sydney",    "country": "Australia", "geo": 255060},
]

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(
    os.environ.get("CREDS_FILE", "scrapers/credentials.json"), scopes=SCOPES
)
gc    = gspread.authorize(creds)
sheet = gc.open_by_key(os.environ["SHEET_ID"]).worksheet(os.environ["SHEET_NAME"])

headers_row = sheet.row_values(1)
existing = set(r.get("tripadvisor_url","") for r in sheet.get_all_records() if r.get("tripadvisor_url"))
print(f"기존 수집: {len(existing)}개\n")

async def get_datadome_cookie():
    """Playwright로 TripAdvisor 한 번 방문 → DataDome 쿠키 추출"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await page.goto("https://www.tripadvisor.com/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(4)
        cookies = await context.cookies()
        await browser.close()
    cookie_dict = {c["name"]: c["value"] for c in cookies}
    dd = cookie_dict.get("datadome", "")
    print(f"DataDome 쿠키: {'획득' if dd else '실패'}")
    return cookie_dict

cookie_jar = asyncio.run(get_datadome_cookie())
session = requests.Session(impersonate="chrome124", cookies=cookie_jar)

def get(url, **kwargs):
    r = session.get(url, timeout=20, **kwargs)
    time.sleep(DELAY)
    return r

def get_location_ids(geo, offset=0):
    url = f"https://www.tripadvisor.com/FindRestaurants?geo={geo}&establishmentTypes=10591&priceTypes=10954&broadened=false&offset={offset}"
    r = get(url)
    if r.status_code != 200:
        print(f"    HTTP {r.status_code}")
        return []
    # location ID 추출
    ids = list(dict.fromkeys(
        int(x) for x in re.findall(r"/Restaurant_Review-g\d+-d(\d+)-", r.text)
    ))
    return ids

def get_detail(loc_id, geo):
    url = f"https://www.tripadvisor.com/Restaurant_Review-g{geo}-d{loc_id}.html"
    r = get(url, headers={"Referer": f"https://www.tripadvisor.com/FindRestaurants?geo={geo}&establishmentTypes=10591&priceTypes=10954&broadened=false"})
    html = r.text

    result = {"name":"","email":"","website":"","phone":"","address":"","rating":"","reviews":"","cuisine":"","price":""}
    if r.status_code != 200:
        return result

    # 이메일
    m = re.search(r'href="mailto:([^"?]+)', html)
    if m: result["email"] = m.group(1).strip()

    # 웹사이트
    m = re.search(r'data-automation="restaurantsWebsiteButton"[^>]*href="([^"]+)"', html)
    if not m:
        m = re.search(r'"website"\s*:\s*"([^"]+)"', html)
    if m: result["website"] = m.group(1).split("?")[0]

    # 전화
    m = re.search(r'href="tel:([^"]+)"', html)
    if m: result["phone"] = m.group(1).strip()

    # 이름
    m = re.search(r'"name"\s*:\s*"([^"]+)"', html)
    if m: result["name"] = m.group(1)

    # 주소
    m = re.search(r'"address"\s*:\s*\{[^}]*"streetAddress"\s*:\s*"([^"]+)"', html)
    if m: result["address"] = m.group(1)

    # 평점/리뷰
    m = re.search(r'"ratingValue"\s*:\s*([\d.]+)', html)
    if m: result["rating"] = float(m.group(1))
    m = re.search(r'"reviewCount"\s*:\s*(\d+)', html)
    if m: result["reviews"] = int(m.group(1))

    # 요리/가격
    m = re.search(r'"servesCuisine"\s*:\s*"([^"]+)"', html)
    if m: result["cuisine"] = m.group(1)
    m = re.search(r'priceRange[^$]*(\$+)', html)
    if m: result["price"] = m.group(1)

    return result

total = 0

for city in CITIES:
    print(f"\n{'='*40}\n{city['name']} ({city['country']})\n{'='*40}")
    city_count = 0
    seen_ids = set()

    for offset in range(0, 300, 30):
        ids = get_location_ids(city["geo"], offset)
        new_ids = []
        for i in ids:
            ta_url = f"https://www.tripadvisor.com/Restaurant_Review-g{city['geo']}-d{i}.html"
            if str(i) not in seen_ids and ta_url not in existing:
                seen_ids.add(str(i))
                new_ids.append(i)

        print(f"  offset {offset}: {len(ids)}개 중 신규 {len(new_ids)}개")
        if not new_ids:
            break

        for loc_id in new_ids:
            ta_url = f"https://www.tripadvisor.com/Restaurant_Review-g{city['geo']}-d{loc_id}.html"
            d = get_detail(loc_id, city["geo"])

            row = [
                d["name"], d["cuisine"], d["price"],
                city["name"], city["country"], d["address"],
                d["email"], d["website"], d["phone"],
                d["rating"], d["reviews"], ta_url,
                "", "", "Y",
            ]
            sheet.append_row(row)
            existing.add(ta_url)

            status = "O" if d["email"] else "-"
            print(f"  [{status}] {d['name'][:35]:<35} {d['email'] or '없음'}")
            city_count += 1
            total += 1

    print(f"  {city['name']} 완료: {city_count}개")

print(f"\n전체 완료 — {total}개")
