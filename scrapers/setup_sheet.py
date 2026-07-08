"""
시트 헤더 초기화 — 기존 데이터 삭제 후 새 컬럼 구조 세팅
"""
import os, sys, gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv("scrapers/.env", override=True)

HEADERS = [
    "business_name", "cuisine", "price_range",
    "city", "country", "address",
    "email", "website", "phone",
    "rating", "review_count", "tripadvisor_url",
    "strength_review", "weak_review",
    "outreach_status", "last_sent_at", "scraper_done",
]

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(
    os.environ.get("CREDS_FILE", "scrapers/credentials.json"), scopes=SCOPES
)
gc    = gspread.authorize(creds)
sheet = gc.open_by_key(os.environ["SHEET_ID"]).worksheet(os.environ["SHEET_NAME"])

sheet.clear()
sheet.append_row(HEADERS)
print("시트 초기화 완료:", HEADERS)
