"""
SMBkits — Gmail 받은편지함 자동 모니터
3개 계정 IMAP 체크 → 바운스/자동답장/실제답장 분류
- 바운스 → Sheets outreach_status = bounced
- 실제 답장 → 콘솔 출력 + 별도 로그

Usage:
    python scrapers/inbox_monitor.py
    python scrapers/inbox_monitor.py --dry-run
"""

import os, sys, imaplib, email, re, csv, time, argparse
from email.header import decode_header
from datetime import datetime, timezone
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

ACCOUNTS = [
    {"name": "James Harrison", "email": "jamessmbkits@gmail.com", "pw": os.getenv("SMTP_JAMES_PW", "").replace(" ", "")},
    {"name": "Alex Bennett",   "email": "alexsmbkits@gmail.com",  "pw": os.getenv("SMTP_ALEX_PW",  "").replace(" ", "")},
    {"name": "Sarah Mitchell", "email": "sarahsmbkits@gmail.com", "pw": os.getenv("SMTP_SARAH_PW", "").replace(" ", "")},
]

# 바운스 키워드 (제목 또는 발신자)
BOUNCE_SUBJECTS = [
    "delivery status notification",
    "mail delivery failed",
    "mail delivery subsystem",
    "undeliverable",
    "delivery failure",
    "address not found",
    "주소를 찾을 수 없음",
    "전송이 완료되지 않음",
    "전송되지 않았습니다",
    "mailer-daemon",
    "postmaster",
]

BOUNCE_SENDERS = [
    "mailer-daemon",
    "postmaster",
    "mail delivery",
    "mail+",
]

# 자동 답장 키워드
AUTO_REPLY_SUBJECTS = [
    "automatic reply",
    "auto reply",
    "auto-reply",
    "out of office",
    "away from",
    "vacation",
    "réponse automatique",
    "자동 응답",
    "congés",
    "fermé",
]


def decode_str(s):
    if not s:
        return ""
    parts = decode_header(s)
    result = []
    for part, enc in parts:
        if isinstance(part, bytes):
            result.append(part.decode(enc or "utf-8", errors="replace"))
        else:
            result.append(str(part))
    return "".join(result)


def is_bounce(sender: str, subject: str) -> bool:
    s = subject.lower()
    f = sender.lower()
    return (
        any(k in s for k in BOUNCE_SUBJECTS) or
        any(k in f for k in BOUNCE_SENDERS)
    )


def is_auto_reply(subject: str) -> bool:
    s = subject.lower()
    return any(k in s for k in AUTO_REPLY_SUBJECTS)


def extract_original_recipient(body: str) -> str:
    """바운스 메일 본문에서 원래 수신자 이메일 추출"""
    patterns = [
        r'(?:to|recipient|수신자)[:\s]+([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
        r'([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
    ]
    for pat in patterns:
        m = re.search(pat, body, re.IGNORECASE)
        if m:
            addr = m.group(1).lower()
            # SMBkits 자체 주소 제외
            if "smbkits" not in addr and "gmail.com" not in addr:
                return addr
    return ""


def get_email_body(msg) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                    break
                except Exception:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode("utf-8", errors="replace")
        except Exception:
            pass
    return body[:2000]


def check_inbox(account: dict, delete: bool = False) -> dict:
    """IMAP으로 받은편지함 체크 — 오늘 받은 메일 분류 + 옵션으로 바운스/자동답장 삭제"""
    results = {"bounces": [], "auto_replies": [], "real_replies": []}

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(account["email"], account["pw"])
        mail.select("INBOX")

        # 오늘 이후 메일만
        today = datetime.now().strftime("%d-%b-%Y")
        _, data = mail.search(None, f'(SINCE "{today}")')
        ids = data[0].split()

        print(f"  [{account['name']}] {len(ids)}개 메일 확인")

        for uid in ids:
            _, msg_data = mail.fetch(uid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            sender  = decode_str(msg.get("From", ""))
            subject = decode_str(msg.get("Subject", ""))
            body    = get_email_body(msg)

            if is_bounce(sender, subject):
                recipient = extract_original_recipient(body)
                results["bounces"].append({
                    "sender":    sender,
                    "subject":   subject,
                    "recipient": recipient,
                })
                if delete:
                    mail.store(uid, "+FLAGS", "\\Deleted")
            elif is_auto_reply(subject):
                results["auto_replies"].append({
                    "sender":  sender,
                    "subject": subject,
                })
                if delete:
                    mail.store(uid, "+FLAGS", "\\Deleted")
            else:
                results["real_replies"].append({
                    "sender":  sender,
                    "subject": subject,
                    "preview": body[:300],
                    "account": account["name"],
                })

        if delete:
            mail.expunge()
            print(f"  [{account['name']}] 바운스/자동답장 삭제 완료")

        mail.logout()

    except Exception as e:
        print(f"  [{account['name']}] IMAP 오류: {e}")

    return results


def get_sheet():
    creds = Credentials.from_service_account_file(
        os.getenv("CREDS_FILE", "scrapers/credentials.json"), scopes=SCOPES
    )
    gc = gspread.authorize(creds)
    return gc.open_by_key(os.getenv("SHEET_ID")).worksheet(os.getenv("SHEET_NAME"))


def mark_bounced(sheet, bounced_emails: list[str], dry_run: bool):
    """Sheets에서 바운스된 이메일 주소 찾아서 status = bounced 표시"""
    if not bounced_emails:
        return

    all_rows = sheet.get_all_values()
    header   = all_rows[0]
    email_col  = header.index("email")
    status_col = header.index("outreach_status")

    bounced_set = {e.lower().strip() for e in bounced_emails if e}
    updates = []

    for i, row in enumerate(all_rows[1:], start=2):
        addr = row[email_col].lower().strip() if len(row) > email_col else ""
        if addr in bounced_set:
            current = row[status_col] if len(row) > status_col else ""
            if current != "bounced":
                updates.append({"range": f"O{i}", "values": [["bounced"]]})
                print(f"  bounced → {addr}")

    if updates and not dry_run:
        sheet.batch_update(updates)
        print(f"  Sheets {len(updates)}건 bounced 업데이트 완료")
    elif dry_run:
        print(f"  [DRY RUN] {len(updates)}건 bounced 처리 예정")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--delete",  action="store_true", help="바운스/자동답장 자동 삭제")
    args = parser.parse_args()

    print(f"=== SMBkits 받은편지함 모니터 {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")

    all_bounces      = []
    all_auto_replies = []
    all_real_replies = []

    for account in ACCOUNTS:
        print(f"[{account['name']}] 체크 중...")
        res = check_inbox(account, delete=args.delete)
        all_bounces      += res["bounces"]
        all_auto_replies += res["auto_replies"]
        all_real_replies += res["real_replies"]
        time.sleep(1)

    # 바운스된 원래 수신자 이메일 목록
    bounced_emails = [b["recipient"] for b in all_bounces if b["recipient"]]

    print(f"\n── 결과 ──────────────────────────────")
    print(f"바운스:    {len(all_bounces)}건")
    print(f"자동답장:  {len(all_auto_replies)}건")
    print(f"실제답장:  {len(all_real_replies)}건")

    if all_bounces:
        print(f"\n[바운스 목록]")
        for b in all_bounces:
            print(f"  → {b['recipient'] or '?'} | {b['subject'][:60]}")

    if all_auto_replies:
        print(f"\n[자동 답장]")
        for a in all_auto_replies:
            print(f"  → {a['sender'][:40]} | {a['subject'][:50]}")

    if all_real_replies:
        print(f"\n{'='*50}")
        print(f"★ 실제 답장 {len(all_real_replies)}건 ★")
        print(f"{'='*50}")
        for r in all_real_replies:
            print(f"\n  계정:   {r['account']}")
            print(f"  발신자: {r['sender']}")
            print(f"  제목:   {r['subject']}")
            print(f"  내용:   {r['preview'][:200]}")

    # Sheets 바운스 업데이트
    if bounced_emails:
        print(f"\nSheets 바운스 업데이트 중...")
        sheet = get_sheet()
        mark_bounced(sheet, bounced_emails, args.dry_run)

    print(f"\n완료.")


if __name__ == "__main__":
    main()
