"""
SMBkits — TripAdvisor GraphQL API 스크래퍼
브라우저 없이 내부 GraphQL API 직접 호출
Chrome 쿠키 → DataDome 우회
"""

import os, sys, re, json, time, requests, gspread, browser_cookie3
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv("scrapers/.env", override=True)

GRAPHQL_URL = "https://www.tripadvisor.com/data/graphql/ids"
DELAY       = 0.8   # 요청 간격(초)

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
def col(name): return headers_row.index(name) + 1

existing = set(r.get("tripadvisor_url","") for r in sheet.get_all_records() if r.get("tripadvisor_url"))
print(f"기존 수집: {len(existing)}개\n")

# ── Chrome 쿠키 로드 ────────────────────────────────────────
def get_session():
    s = requests.Session()
    s.headers.update({
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "same-origin",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    })
    try:
        jar = browser_cookie3.chrome(domain_name=".tripadvisor.com")
        for c in jar:
            s.cookies.set(c.name, c.value, domain=c.domain)
        print(f"Chrome 쿠키 로드 완료")
    except Exception as e:
        print(f"쿠키 로드 실패 (계속 진행): {e}")
    return s

session = get_session()

def gql_post(body, referrer="https://www.tripadvisor.com/"):
    session.headers["referrer"] = referrer
    r = session.post(GRAPHQL_URL, json=body, timeout=15)
    time.sleep(DELAY)
    if r.status_code == 200:
        return r.json()
    print(f"  API {r.status_code}: {r.text[:80]}")
    return []

# ── 도시 파인다이닝 location ID 목록 가져오기 ─────────────────
def get_location_ids(geo, offset=0):
    """FindRestaurants 페이지 HTML에서 locationId 배열 추출"""
    url = f"https://www.tripadvisor.com/FindRestaurants?geo={geo}&establishmentTypes=10591&priceTypes=10954&broadened=false&offset={offset}"
    session.headers["referrer"] = f"https://www.tripadvisor.com/FindRestaurants?geo={geo}&establishmentTypes=10591&priceTypes=10954&broadened=false"
    r = session.get(url, timeout=20)
    time.sleep(DELAY)

    # __NEXT_DATA__ JSON에서 locationId 추출
    m = re.search(r'"locationIds"\s*:\s*\[([^\]]+)\]', r.text)
    if m:
        ids = [int(x.strip()) for x in m.group(1).split(",") if x.strip().isdigit()]
        return ids

    # fallback: URL 패턴에서 location ID 추출
    ids = list(dict.fromkeys(
        int(x) for x in re.findall(r'/Restaurant_Review-g\d+-d(\d+)-', r.text)
    ))
    return ids

# ── 업체 상세 정보 ────────────────────────────────────────────
def get_details(location_id, geo):
    referrer = f"https://www.tripadvisor.com/FindRestaurants?geo={geo}&establishmentTypes=10591&priceTypes=10954&broadened=false"
    body = [
        {
            "variables": {"request": {"id": str(location_id), "type": "location"}},
            "extensions": {"preRegisteredQueryId": "25f9ddb1ce629144"}
        },
        {
            "variables": {"ids": [location_id]},
            "extensions": {"preRegisteredQueryId": "496720f897546a4e"}
        }
    ]
    resp = gql_post(body, referrer=referrer)

    result = {"name":"","email":"","website":"","phone":"","address":"","rating":"","reviews":"","cuisine":"","price":""}
    if not resp or not isinstance(resp, list):
        return result

    for item in resp:
        data = item.get("data", {})

        # 25f9ddb1ce629144 응답 파싱
        loc = data.get("locations", [{}])[0] if data.get("locations") else {}
        if not loc:
            loc = data.get("location", {}) or {}

        result["name"]    = result["name"]    or loc.get("name","")
        result["email"]   = result["email"]   or loc.get("email","")
        result["website"] = result["website"] or loc.get("website","")
        result["phone"]   = result["phone"]   or loc.get("phone","")
        result["rating"]  = result["rating"]  or loc.get("rating","")
        result["reviews"] = result["reviews"] or loc.get("num_reviews","")

        addr = loc.get("address_obj", {})
        result["address"] = result["address"] or addr.get("address_string","")

        cuisines = loc.get("cuisine", [])
        result["cuisine"] = result["cuisine"] or ", ".join(c.get("name","") for c in cuisines)
        result["price"]   = result["price"]   or loc.get("price_level","")

    return result

# ── 메인 ─────────────────────────────────────────────────────
total = 0

for city in CITIES:
    print(f"\n{'='*40}\n{city['name']} ({city['country']})\n{'='*40}")
    city_count = 0

    for offset in range(0, 300, 30):
        ids = get_location_ids(city["geo"], offset)
        if not ids:
            print(f"  offset {offset}: location ID 없음, 종료")
            break

        new_ids = [i for i in ids if f"https://www.tripadvisor.com/Restaurant_Review-d{i}.html" not in existing]
        print(f"  offset {offset}: {len(ids)}개 중 신규 {len(new_ids)}개")

        if not new_ids:
            break

        for loc_id in new_ids:
            ta_url = f"https://www.tripadvisor.com/Restaurant_Review-d{loc_id}.html"
            det = get_details(loc_id, city["geo"])

            row = [
                det["name"], det["cuisine"], det["price"],
                city["name"], city["country"], det["address"],
                det["email"], det["website"], det["phone"],
                det["rating"], det["reviews"], ta_url,
                "", "", "Y",
            ]
            sheet.append_row(row)
            existing.add(ta_url)

            status = "O" if det["email"] else "-"
            print(f"  [{status}] {det['name'][:35]:<35} {det['email'] or '이메일없음'}")
            city_count += 1
            total += 1

    print(f"  {city['name']} 완료: {city_count}개")

print(f"\n전체 완료 — {total}개 수집")
