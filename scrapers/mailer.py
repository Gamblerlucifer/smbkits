"""
SMBkits — Cold Email Mailer
Gemini API 개인화 생성 → Gmail SMTP 3계정 순환 발송
랜덤 워밍업 발송량 + 랜덤 제목/내용 + 랜덤 딜레이

Usage:
    python scrapers/mailer.py                      # 캠페인 시작일 기준 자동 주차
    python scrapers/mailer.py --week 2 --dry-run   # 수동 주차 지정 + 테스트
"""

import os
import json
import time
import random
import smtplib
import gspread
from datetime import datetime, date, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai
from google.genai import types
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import argparse
import sys

load_dotenv("scrapers/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SHEET_ID       = os.getenv("SHEET_ID")
SHEET_NAME     = os.getenv("SHEET_NAME")
CREDS_FILE     = os.getenv("CREDS_FILE")

MODEL = "gemini-3.1-flash-lite"

SMTP_ACCOUNTS = [
    {
        "name":  "James Harrison",
        "title": "Reputation Response, SMBkits",
        "email": "jamessmbkits@gmail.com",
        "pw":    os.getenv("SMTP_JAMES_PW", "").replace(" ", ""),
    },
    {
        "name":  "Alex Bennett",
        "title": "Local Positioning, SMBkits",
        "email": "alexsmbkits@gmail.com",
        "pw":    os.getenv("SMTP_ALEX_PW", "").replace(" ", ""),
    },
    {
        "name":  "Sarah Mitchell",
        "title": "Brand Voice, SMBkits",
        "email": "sarahsmbkits@gmail.com",
        "pw":    os.getenv("SMTP_SARAH_PW", "").replace(" ", ""),
    },
]

# 워밍업 주차별 계정당 일일 발송 범위 (랜덤 상승/하락)
WARMUP = {
    1: (1, 4),
    2: (3, 7),
    3: (6, 12),
    4: (10, 20),
    5: (18, 30),
    6: (25, 35),
}

COL = {
    "business_name":   0,
    "city":            2,
    "country":         3,
    "website":         4,
    "email":           6,
    "google_rating":   9,
    "review_count":    10,
    "negative_review": 12,
    "sentiment_score": 13,
    "outreach_status": 14,
}

LOG_HEADERS = ["timestamp", "recipient", "sender_email", "sender_name", "sequence", "subject", "body_preview"]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# 캠페인 시작일 — 수정하지 말 것 (주차 자동 계산 기준)
CAMPAIGN_START = date(2026, 5, 19)

def current_week() -> int:
    """캠페인 시작일로부터 오늘이 몇 주차인지 자동 계산 (1~6 범위 클램프)"""
    days = (date.today() - CAMPAIGN_START).days
    return max(1, min(6, days // 7 + 1))


def get_sheet():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)


def get_log_sheet():
    """Email_Logs 탭 반환 — 없으면 자동 생성 + 헤더 삽입"""
    creds  = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    wb     = client.open_by_key(SHEET_ID)
    try:
        ws = wb.worksheet("Email_Logs")
    except gspread.exceptions.WorksheetNotFound:
        ws = wb.add_worksheet(title="Email_Logs", rows=10000, cols=len(LOG_HEADERS))
        ws.append_row(LOG_HEADERS, value_input_option="RAW")
        print("  [Email_Logs] 탭 신규 생성 완료")
    return ws


def hours_since_sending(status: str) -> float:
    """'sending:2026-05-20T07:43:21.123456' 형식에서 경과 시간(시) 반환"""
    try:
        ts_str = status.split(":", 1)[1]
        ts = datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - ts).total_seconds() / 3600
    except Exception:
        return 99  # 파싱 실패 → stale 처리


def days_since(status: str) -> int:
    """'d0:2026-05-18' 형식에서 경과 일수 계산"""
    try:
        date_str = status.split(":")[1]
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (date.today() - d).days
    except Exception:
        return 0


# 국가 → 언어 매핑
LANG_MAP = {
    "Taiwan":    "Traditional Chinese (繁體中文)",
    "Hong Kong": "Traditional Chinese (繁體中文)",
    "Macau":     "Traditional Chinese (繁體中文)",
    "Japan":     "Japanese (日本語)",
    "Korea":     "Korean (한국어)",
    "France":    "French (Français)",
    "Italy":     "Italian (Italiano)",
    "Spain":     "Spanish (Español)",
    "Germany":   "German (Deutsch)",
}

def get_lang(country: str) -> str:
    return LANG_MAP.get(country, "English")


def generate_email(lead: dict, sequence: str, sender_name: str = "James") -> dict | None:
    """Gemini로 개인화 이메일 생성 — 제목·내용 매번 다르게"""
    name    = lead.get("business_name", "")
    city    = lead.get("city", "")
    country = lead.get("country", "")
    rating  = lead.get("google_rating", "")
    reviews = lead.get("review_count", "")
    neg_rev = lead.get("negative_review", "")
    lang    = get_lang(country)
    first_name = sender_name.split()[0]  # "James Harrison" → "James"

    if sequence == "d0":
        neg_section = (
            f"Recent negative review text: \"{neg_rev[:200]}\""
            if neg_rev else "No negative review text available."
        )
        prompt = f"""You are writing a cold outreach email on behalf of SMBkits (smbkits.com),
a private AI reputation management tool for premium independent restaurants.

Sender: {sender_name} (sign off with first name only: {first_name})
Target restaurant:
- Name: {name}
- Location: {city}, {country}
- Google Rating: {rating} stars ({reviews} reviews)
- {neg_section}
- Write in: {lang}

Write a SHORT, conversational cold email. Follow this exact flow:
1. Opening: acknowledge their strong reputation ({rating} stars, {reviews} reviews) — make them feel seen (1-2 sentences)
2. Reputation signal: mention that while reviewing their online presence, you came across a recent guest comment. Include a SHORT, softened quote in quotation marks — pick 3-5 words from the negative review text that are the least harsh (e.g. "waiting time felt a little long" or "portion felt slightly small"). Attribute it to "a recent Google review". Keep it neutral, not confrontational.
3. Empathy: acknowledge that responding to every review thoughtfully while running a full kitchen and floor operation is genuinely difficult. (1 sentence)
4. Soft offer: mention you put together a complimentary "Online Reputation & Response Profile" specifically for {name} — they just need to reply to this email and you'll send it over. No link, no signup.
5. CTA: end with a simple low-friction ask — "If you'd like to take a look, just reply to this email."
6. Do NOT include any sign-off or signature — it will be added automatically.

STRICT RULES:
- Subject: personal, curiosity-driven. Never use: "partnership", "opportunity", "collaboration", "exciting"
- Body: under 170 words, plain text, no bullet points, no bold
- Line breaks between every paragraph
- Never directly quote harsh review content — frame issues as professional observations
- Never say "our AI could draft a reply" or push the website link as CTA
- Sound like a real human consultant, not a marketer
- Every email must use different wording and structure

Respond ONLY in this exact JSON format (no markdown):
{{"subject": "...", "body": "..."}}"""

    elif sequence == "d3":
        prompt = f"""Write a very short follow-up cold email for {name} in {city}.

Sender first name: {first_name} (sign off with {first_name} only — never use another name)
Write in: {lang}

Context: {first_name} emailed them 3 days ago about their Google reviews and smbkits.com.
They haven't replied yet.

RULES:
- 2-3 sentences only
- Casual, human tone
- Reference the previous email naturally
- No pressure
- Do NOT include any sign-off or signature
- Different wording every time

Respond ONLY in JSON (no markdown):
{{"subject": "...", "body": "..."}}"""

    elif sequence == "d10":
        prompt = f"""Write a final short breakup-style cold email for {name} in {city}.

Sender first name: {first_name} (sign off with {first_name} only — never use another name)
Write in: {lang}

Context: Last follow-up. {reviews} Google reviews, {rating} star rating.
{first_name} has emailed them twice already about smbkits.com.

RULES:
- 2-3 sentences only
- Mention one specific stat ({reviews} reviews OR {rating} stars)
- Mention smbkits.com once
- Friendly, no hard feelings
- Do NOT include any sign-off or signature
- Different wording every time

Respond ONLY in JSON (no markdown):
{{"subject": "...", "body": "..."}}"""

    else:
        return None

    try:
        response = gemini_client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=1.2,  # 높은 temperature → 다양한 문장 생성
            ),
        )
        result = json.loads(response.text)
        return {
            "subject": result.get("subject", ""),
            "body":    result.get("body", ""),
        }
    except Exception as e:
        print(f"  Gemini 생성 오류: {e}")
        return None


SIGNATURE_HTML = """
<br><br>
--<br>
<span style="font-family:sans-serif;font-size:13px;">
<strong>{name}</strong><br>
{title} | <a href="https://smbkits.com" style="color:#888;text-decoration:none;">smbkits.com</a><br><br>
<a href="https://smbkits.com">
  <img src="https://smbkits.com/logo.png" alt="SMBkits" height="28" style="display:block;">
</a>
</span>
"""

def send_email(account: dict, to_email: str, subject: str, body: str) -> bool:
    """Gmail SMTP SSL로 발송 (HTML — plain text 본문 + 서명)"""
    try:
        sig  = SIGNATURE_HTML.format(name=account["name"], title=account["title"])
        html_body = "<div style='font-family:sans-serif;font-size:14px;line-height:1.6'>"
        html_body += body.replace("\n", "<br>")
        html_body += sig + "</div>"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{account['name']} <{account['email']}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html",  "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(account["email"], account["pw"])
            server.sendmail(account["email"], to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"  SMTP 오류 ({account['email']}): {e}")
        return False


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser()
    parser.add_argument("--week",       type=int,  default=0,  help="워밍업 주차 (1~6). 미입력시 캠페인 시작일 기준 자동 계산")
    parser.add_argument("--dry-run",    action="store_true",   help="실제 발송 없이 출력만")
    parser.add_argument("--test-email", type=str, default="",  help="테스트 발송 주소 (Sheets 무시)")
    parser.add_argument("--countries",  type=str, default="",  help="발송 대상 국가 쉼표 구분 (예: Japan,Korea). 미입력시 전체")
    args = parser.parse_args()

    # ── 랜덤 슬립 (automation footprint 방지) ───────────────────
    # cron 트리거 후 0~45분 랜덤 대기 → 실제 발송 07:43~08:28 local
    if not args.dry_run and not args.test_email:
        jitter = random.randint(0, 45 * 60)
        print(f"[Jitter] {jitter // 60}분 {jitter % 60}초 후 발송 시작...\n")
        time.sleep(jitter)
    # ────────────────────────────────────────────────────────────

    # ── 테스트 발송 모드 (3개 계정 전부 발송) ───────────────────
    if args.test_email:
        fake_lead = {
            "business_name":  "The Grand Table",
            "city":           "London",
            "country":        "United Kingdom",
            "google_rating":  "4.6",
            "review_count":   "892",
            "negative_review": "waiting time was longer than expected and the portion felt small for the price.",
        }
        for account in SMTP_ACCOUNTS:
            print(f"[TEST] {account['name']} → {args.test_email}")
            content = generate_email(fake_lead, "d0", sender_name=account["name"])
            if content:
                lines = content["body"].strip().splitlines()
                if lines and lines[-1].strip().lower() in [
                    account["name"].split()[0].lower(), "best,", "regards,", "thanks,"
                ]:
                    content["body"] = "\n".join(lines[:-1]).strip()
                print(f"  제목: {content['subject']}")
                success = send_email(account, args.test_email, content["subject"], content["body"])
                print(f"  {'OK' if success else 'FAIL'}\n")
        return
    # ────────────────────────────────────────────────────────────

    week   = args.week if args.week > 0 else current_week()
    lo, hi = WARMUP[week]
    today  = date.today().strftime("%Y-%m-%d")

    # 국가 필터
    target_countries = [c.strip() for c in args.countries.split(",") if c.strip()] if args.countries else []
    if target_countries:
        print(f"[국가 필터] {', '.join(target_countries)}\n")

    # 계정별 오늘 목표 건수 (랜덤)
    per_account = {acc["email"]: random.randint(lo, hi) for acc in SMTP_ACCOUNTS}
    total_target = sum(per_account.values())
    print(f"[Week {week}] 오늘 목표: {total_target}건 | {per_account}\n")
    if args.dry_run:
        print("*** DRY RUN 모드 — 실제 발송 없음 ***\n")

    sheet     = get_sheet()
    log_sheet = get_log_sheet()
    all_rows  = sheet.get_all_values()
    rows      = all_rows[1:]

    # 시퀀스별 리드 분류
    d0_leads, d3_leads, d10_leads = [], [], []

    for i, row in enumerate(rows):
        email   = row[COL["email"]]           if len(row) > 6  else ""
        status  = row[COL["outreach_status"]]  if len(row) > 14 else ""
        country = row[COL["country"]]          if len(row) > 3  else ""
        # 유효한 이메일 형식 검증 (@ 포함, 도메인에 점 있음, 이미지 확장자 제외)
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            continue
        if any(email.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")):
            continue
        if target_countries and country not in target_countries:
            continue

        # 이메일 시퀀스 미시작 상태 — 스크래퍼 상태값(enriched/pending 등) 포함
        is_new = (not status) or (status not in ("",) and not any(
            status.startswith(p) for p in ("d0:", "d3:", "d10:", "sending:")
        ))

        if is_new:
            d0_leads.append((i, row))
        elif status.startswith("sending:") and hours_since_sending(status) >= 2:
            # 2시간 이상 sending 상태 = 크래시로 멈춘 것 → d0 재시도
            d0_leads.append((i, row))
        elif status.startswith("sending:"):
            # 2시간 미만 = 다른 인스턴스가 처리 중 → 스킵
            continue
        elif status.startswith("d0:") and days_since(status) >= 3:
            d3_leads.append((i, row))
        elif status.startswith("d3:") and days_since(status) >= 7:
            d10_leads.append((i, row))

    print(f"D0(신규): {len(d0_leads)}건 | D+3 대기: {len(d3_leads)}건 | D+10 대기: {len(d10_leads)}건\n")

    # 발송 큐: d10 → d3 → d0 우선순위
    queue = (
        [(i, row, "d10") for i, row in d10_leads] +
        [(i, row, "d3")  for i, row in d3_leads]  +
        [(i, row, "d0")  for i, row in d0_leads]
    )

    sent_count = {acc["email"]: 0 for acc in SMTP_ACCOUNTS}
    total_sent = 0

    for i, row, sequence in queue:
        # 모든 계정 목표 달성 시 종료
        available = [
            acc for acc in SMTP_ACCOUNTS
            if sent_count[acc["email"]] < per_account[acc["email"]]
        ]
        if not available:
            break

        account  = random.choice(available)
        to_email = row[COL["email"]] if len(row) > 6 else ""
        if not to_email:
            continue

        lead = {
            "business_name":  row[COL["business_name"]]  if len(row) > 0  else "",
            "city":           row[COL["city"]]            if len(row) > 2  else "",
            "country":        row[COL["country"]]         if len(row) > 3  else "",
            "google_rating":  row[COL["google_rating"]]   if len(row) > 9  else "",
            "review_count":   row[COL["review_count"]]    if len(row) > 10 else "",
            "negative_review":row[COL["negative_review"]] if len(row) > 12 else "",
        }

        print(f"[{sequence.upper()}] {lead['business_name']} → {to_email}")
        print(f"  발송자: {account['name']} <{account['email']}>")

        content = generate_email(lead, sequence, sender_name=account["name"])
        if not content:
            continue

        print(f"  제목: {content['subject']}")
        print(f"  내용 미리보기: {content['body'][:80]}...")

        # 발송 전 선점 — UTC ISO timestamp으로 stale 2시간 판단
        if not args.dry_run:
            ts_now = datetime.now(timezone.utc).isoformat()
            sheet.update_cell(i + 2, COL["outreach_status"] + 1, f"sending:{ts_now}")

        if not args.dry_run:
            success = send_email(account, to_email, content["subject"], content["body"])
        else:
            success = True  # dry-run은 항상 성공 처리

        if success:
            sent_count[account["email"]] += 1
            total_sent += 1
            new_status = f"{sequence}:{today}"

            if not args.dry_run:
                # 메인 시트 상태 확정
                sheet.update_cell(i + 2, COL["outreach_status"] + 1, new_status)
                # Email_Logs 탭에 발송 내용 영구 기록
                log_row = [
                    datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                    to_email,
                    account["email"],
                    account["name"],
                    sequence,
                    content["subject"],
                    content["body"][:200] + ("..." if len(content["body"]) > 200 else ""),
                ]
                try:
                    log_sheet.append_row(log_row, value_input_option="RAW")
                except Exception as e:
                    print(f"  [로그 오류] {e}")

            print(f"  ✅ {'[DRY]' if args.dry_run else ''} 완료 | 상태: {new_status}")
        else:
            # 발송 실패 시 선점 롤백 → 다음 실행에서 재시도 가능
            if not args.dry_run:
                sheet.update_cell(i + 2, COL["outreach_status"] + 1, "")
            print(f"  ❌ 실패 | 상태 롤백")

        # 랜덤 딜레이 (인간 행동 모방) — dry-run은 스킵
        if not args.dry_run:
            delay = random.randint(60, 180)
            print(f"  ⏳ {delay}초 대기...\n")
            time.sleep(delay)
        else:
            print()

    print(f"\n=== 완료 | 총 {total_sent}건 발송 ===")
    for acc in SMTP_ACCOUNTS:
        print(f"  {acc['name']}: {sent_count[acc['email']]}건")


if __name__ == "__main__":
    main()
