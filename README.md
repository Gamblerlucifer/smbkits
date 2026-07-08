# SMBkits — Global Fine Dining Outreach Pipeline

TripAdvisor 파인다이닝 자동 수집 → Gemini 개인화 이메일 생성 → Gmail 멀티계정 발송

---

## 구조

```
scrapers/
├── tripadvisor_scraper.py   # TripAdvisor 스크래퍼 (Playwright)
├── mailer.py                # 콜드 이메일 발송 (Gemini + Gmail SMTP)
├── setup_sheet.py           # 구글 시트 초기화 (최초 1회)
├── dedup_sheet.py           # 중복 제거 (스크래퍼 완료 후 실행)
└── .env                     # 환경변수 (gitignore)
```

---

## 수집 도시 (29개)

| 지역 | 도시 |
|------|------|
| 아시아 | Tokyo, Osaka, Singapore, Hong Kong, Bangkok |
| 중동 | Dubai, Abu Dhabi |
| 유럽 | Paris, Barcelona, Madrid, Rome, Milan, Amsterdam, Brussels, Copenhagen, Stockholm, Reykjavik, Dublin, Valletta |
| 오세아니아 | Sydney, Melbourne |
| 북미 | New York, Los Angeles, San Francisco, Chicago, Miami, Las Vegas, Toronto |
| 영국 | London (마지막 순서 — DataDome 세션 안정 후) |

도시당 최대 300개 × 29개 = **최대 8,700개 리드**

---

## 시트 컬럼 구조

| # | 컬럼 | 설명 |
|---|------|------|
| 0 | business_name | 업체명 |
| 1 | cuisine | 요리 종류 |
| 2 | price_range | 가격대 ($$$$) |
| 3 | city | 도시 |
| 4 | country | 국가 |
| 5 | address | 주소 |
| 6 | email | 이메일 |
| 7 | website | 웹사이트 |
| 8 | phone | 전화번호 |
| 9 | rating | TripAdvisor 평점 |
| 10 | review_count | 리뷰 수 |
| 11 | tripadvisor_url | TripAdvisor URL |
| 12 | outreach_status | 발송 상태 (d0/d3/d10) |
| 13 | last_sent_at | 마지막 발송일 |
| 14 | scraper_done | 수집 완료 여부 |

---

## 스크래퍼 실행

```bash
cd scrapers
python tripadvisor_scraper.py
```

- Playwright headless=False (DataDome 우회)
- Chrome 쿠키 자동 로드 (browser_cookie3)
- 실거주 IP 필수 (VPN/데이터센터 IP 차단됨)
- 스폰서 링크 자동 제외
- 중복 방지: tripadvisor_url 기준 existing 셋 로드 후 시작

```bash
# 스크래퍼 완료 후 중복 제거
python dedup_sheet.py
```

---

## 메일러 실행

```bash
# 일반 실행 (캠페인 시작일 기준 자동 주차)
python scrapers/mailer.py

# 주차 수동 지정 + 드라이런
python scrapers/mailer.py --week 2 --dry-run

# 특정 국가만 발송
python scrapers/mailer.py --countries Japan,Singapore

# 테스트 발송 (시트 무시, 3계정 전송)
python scrapers/mailer.py --test-email your@email.com
```

### 워밍업 스케줄 (계정당 일일 발송량)

| 주차 | 발송 범위 |
|------|----------|
| 1주 | 1~4건 |
| 2주 | 3~7건 |
| 3주 | 6~12건 |
| 4주 | 10~20건 |
| 5주 | 18~30건 |
| 6주 | 25~35건 |

### 이메일 시퀀스

- **D0**: 초기 콜드메일 (TripAdvisor 리뷰 패턴 언급)
- **D+3**: 짧은 팔로업
- **D+10**: 마지막 브레이크업 메일

### 발송 우선순위

1. D+10 대기 → D+3 대기 → D0 신규
2. 각 목록 내 **개인 메일 우선** (gmail, yahoo, hotmail, outlook, icloud 등)

### 발송 계정 (Gmail SMTP)

- James Harrison — `jamessmbkits@gmail.com`
- Alex Bennett — `alexsmbkits@gmail.com`
- Sarah Mitchell — `sarahsmbkits@gmail.com`

---

## 환경변수 (.env)

```env
GEMINI_API_KEY=
SHEET_ID=
SHEET_NAME=
CREDS_FILE=scrapers/credentials.json
SMTP_JAMES_PW=
SMTP_ALEX_PW=
SMTP_SARAH_PW=
```

---

## 최초 설정

```bash
# 1. 시트 초기화 (기존 데이터 삭제됨 — 주의)
python scrapers/setup_sheet.py

# 2. 패키지 설치
pip install playwright gspread google-auth google-generativeai python-dotenv browser-cookie3
playwright install chromium
```

---

## GitHub Actions

`.github/workflows/mailer.yml` — 매일 오전 8시 KST 자동 발송 (0~45분 랜덤 지터 포함)
