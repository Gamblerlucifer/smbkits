"""
시트 중복 제거 — tripadvisor_url 기준 첫 번째만 유지
"""
import os, sys, gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv("scrapers/.env", override=True)

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(
    os.environ.get("CREDS_FILE", "scrapers/credentials.json"), scopes=SCOPES
)
gc    = gspread.authorize(creds)
sheet = gc.open_by_key(os.environ["SHEET_ID"]).worksheet(os.environ["SHEET_NAME"])

all_values = sheet.get_all_values()
header = all_values[0]
rows   = all_values[1:]

url_col  = header.index("tripadvisor_url")
name_col = header.index("business_name")
city_col = header.index("city")

seen_urls  = set()
seen_names = set()
keep = [header]
dup_url = 0
dup_name = 0

for row in rows:
    url      = (row[url_col].strip().split("?")[0]  if url_col  < len(row) else "")
    name     = (row[name_col].strip().lower()        if name_col < len(row) else "")
    city     = (row[city_col].strip().lower()        if city_col < len(row) else "")
    name_key = f"{name}|{city}"

    if url and url in seen_urls:
        dup_url += 1
        continue
    if name and name_key in seen_names:
        dup_name += 1
        continue

    if url:  seen_urls.add(url)
    if name: seen_names.add(name_key)
    keep.append(row)

print(f"전체: {len(rows)}행 | URL중복: {dup_url} | 이름중복: {dup_name} | 유지: {len(keep)-1}행")

sheet.clear()
sheet.update(values=keep, range_name="A1")
print("완료")
