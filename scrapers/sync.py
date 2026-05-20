"""
SMBkits — 로컬 CSV → Google Sheets 동기화
- 시트에 없는 신규 행만 append (tripadvisor_url 기준 중복 제거)
- 이미 있는 행의 outreach_status 등은 건드리지 않음

Usage:
    python scrapers/sync.py            # 기본 실행
    python scrapers/sync.py --dry-run  # 실제 업로드 없이 카운트만 출력
"""

import os, sys, csv, time, argparse
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CSV_PATH = os.path.join(os.path.dirname(__file__), "results.csv")

HEADERS = [
    "business_name", "cuisine", "price_range",
    "city", "country", "address",
    "email", "website", "phone",
    "rating", "review_count", "tripadvisor_url",
    "strength_review", "weak_review",
    "outreach_status", "last_sent_at", "scraper_done",
]

BATCH = 200  # 한 번에 시트에 append할 행 수


def get_sheet():
    creds_file = os.environ.get("CREDS_FILE", "scrapers/credentials.json")
    creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    gc = gspread.authorize(creds)
    return gc.open_by_key(os.environ["SHEET_ID"]).worksheet(os.environ["SHEET_NAME"])


def load_sheet_urls(sheet) -> set:
    """시트에서 tripadvisor_url 컬럼 전체 읽기 (헤더 제외)"""
    all_values = sheet.get_all_values()
    if not all_values:
        return set()
    header = all_values[0]
    try:
        url_col = header.index("tripadvisor_url")
    except ValueError:
        return set()
    return {row[url_col].strip() for row in all_values[1:] if len(row) > url_col and row[url_col].strip()}


def load_csv() -> list[dict]:
    """로컬 CSV 전체 로드"""
    if not os.path.exists(CSV_PATH):
        print(f"CSV 없음: {CSV_PATH}")
        return []
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="실제 업로드 없이 카운트만 출력")
    args = parser.parse_args()

    print("Google Sheets 연결 중...")
    sheet = get_sheet()

    print("시트 기존 URL 로드 중...")
    sheet_urls = load_sheet_urls(sheet)
    print(f"  시트 기존 행: {len(sheet_urls)}개")

    print("로컬 CSV 로드 중...")
    csv_rows = load_csv()
    print(f"  CSV 전체 행: {len(csv_rows)}개")

    # 신규 행만 필터 (tripadvisor_url 기준)
    new_rows = [
        r for r in csv_rows
        if r.get("tripadvisor_url", "").strip() and
           r["tripadvisor_url"].strip() not in sheet_urls
    ]
    print(f"  신규 (미업로드): {len(new_rows)}개\n")

    if not new_rows:
        print("업로드할 신규 행 없음. 완료.")
        return

    if args.dry_run:
        print("*** DRY RUN — 실제 업로드 없음 ***")
        for r in new_rows[:5]:
            print(f"  {r.get('business_name','?')[:30]} | {r.get('email','')}")
        if len(new_rows) > 5:
            print(f"  ... 외 {len(new_rows)-5}개")
        return

    # BATCH 단위로 append
    total = 0
    for i in range(0, len(new_rows), BATCH):
        chunk = new_rows[i:i + BATCH]
        data = [[r.get(h, "") for h in HEADERS] for r in chunk]
        sheet.append_rows(data, value_input_option="RAW")
        total += len(chunk)
        print(f"  업로드: {total}/{len(new_rows)}행")
        if i + BATCH < len(new_rows):
            time.sleep(1.5)  # API 쿼터 여유

    print(f"\n완료 — {total}행 업로드됨")


if __name__ == "__main__":
    main()
