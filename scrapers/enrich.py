"""
SMBkits — Enrichment Pipeline
Google Sheets → Michelin 상세 페이지(website) → Google Places API(rating/reviews) → Claude(sentiment)

Usage:
    python scrapers/enrich.py
"""

import asyncio
import os
import re
import time
import requests
from playwright.async_api import async_playwright
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv("scrapers/.env")

SHEET_ID         = os.getenv("SHEET_ID")
SHEET_NAME       = os.getenv("SHEET_NAME")
CREDS_FILE       = os.getenv("CREDS_FILE")
PLACES_API_KEY   = os.getenv("GOOGLE_PLACES_API_KEY")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# 컬럼 인덱스 (1-based → 0-based)
COL = {
    "business_name":  0,
    "category":       1,
    "city":           2,
    "country":        3,
    "website":        4,
    "instagram":      5,
    "email":          6,
    "source_type":    7,
    "authority_grade":8,
    "google_rating":  9,
    "review_count":   10,
    "premium_score":  11,
    "negative_review":12,
    "sentiment_score":13,
    "outreach_status":14,
    "reply_status":   15,
    "notes":          16,
}

# ── Google Sheets ─────────────────────────────────────────
def get_sheet():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# ── Michelin 상세 페이지 → website ──────────────────────────
async def fetch_website(page, detail_url):
    """Michelin 상세 페이지에서 업장 공식 웹사이트 URL 추출"""
    try:
        await page.goto(detail_url, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(1500)

        # 공식 웹사이트 링크 (소셜/유튜브/리뷰 사이트 제외)
        SOCIAL_EXCLUDE = ["youtube.com", "instagram.com", "facebook.com", "twitter.com",
                          "tripadvisor.com", "yelp.com", "google.com", "t.co", "youtu.be"]
        link = await page.query_selector("a.restaurant-details__heading--link")
        if not link:
            link = await page.query_selector("a[data-dtm-restaurant-website]")
        if not link:
            # 외부 링크 후보 전체 수집 후 소셜 제외
            all_links = await page.query_selector_all("a[href*='http']:not([href*='michelin'])")
            for candidate in all_links:
                href_candidate = await candidate.get_attribute("href") or ""
                if not any(s in href_candidate for s in SOCIAL_EXCLUDE):
                    link = candidate
                    break

        href = await link.get_attribute("href") if link else ""
        # 소셜 사이트 최종 검증
        if href and any(s in href for s in SOCIAL_EXCLUDE):
            return ""
        return href.strip() if href else ""
    except Exception as e:
        print(f"  website 추출 실패: {e}")
        return ""

# ── 웹사이트 → email 추출 ────────────────────────────────
async def fetch_email(page, website_url):
    """업장 웹사이트 contact 페이지에서 이메일 추출"""
    if not website_url:
        return ""
    try:
        await page.goto(website_url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(1000)

        # 페이지 텍스트에서 이메일 패턴 추출
        content = await page.content()
        emails = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", content)

        # 이미지/파일명 패턴 제거 (.png @2x 등)
        IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".2x", ".3x")
        SPAM_WORDS = ["example", "sentry", "pixel", "noreply", "no-reply", "wixpress",
                      "schema", "support@", "admin@", "postmaster@", "abuse@", "mailer@",
                      "wordpress", "jquery", "cloudflare", "analytics"]
        def clean_emails(raw):
            result = []
            for e in raw:
                e_low = e.lower()
                if any(e_low.endswith(x) for x in IMG_EXT):
                    continue
                if any(x in e_low for x in SPAM_WORDS):
                    continue
                # TLD가 png/jpg 같은 이미지 확장자면 제거
                tld = e_low.rsplit(".", 1)[-1]
                if tld in {"png", "jpg", "jpeg", "gif", "svg", "webp", "ico"}:
                    continue
                result.append(e)
            return result

        filtered = clean_emails(emails)

        # contact 페이지도 시도
        if not filtered:
            contact_urls = [
                website_url.rstrip("/") + "/contact",
                website_url.rstrip("/") + "/about",
                website_url.rstrip("/") + "/contact-us",
            ]
            for url in contact_urls:
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=10000)
                    content = await page.content()
                    emails = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", content)
                    filtered = clean_emails(emails)
                    if filtered:
                        break
                except:
                    continue

        return filtered[0] if filtered else ""
    except Exception as e:
        return ""

# ── Google Places API → rating, review_count, reviews ────
def fetch_places_data(name, city, country):
    """Places API (New) Text Search"""
    query = f"{name} {city} {country}"
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": PLACES_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.rating,places.userRatingCount,places.reviews,places.priceLevel,places.websiteUri",
    }
    body = {"textQuery": query, "languageCode": "en"}

    try:
        res = requests.post(url, headers=headers, json=body, timeout=10)
        data = res.json()
        places = data.get("places", [])
        if not places:
            return None
        place = places[0]

        rating       = place.get("rating", "")
        review_count = place.get("userRatingCount", "")
        reviews      = place.get("reviews", [])
        price_level  = place.get("priceLevel", "")
        website_uri  = place.get("websiteUri", "")

        # 부정 리뷰 추출 (rating 1~2)
        negative = [r.get("text", {}).get("text", "") for r in reviews
                    if r.get("rating", 5) <= 2]

        return {
            "rating":        rating,
            "review_count":  review_count,
            "negative":      negative[0][:300] if negative else "",
            "price_level":   price_level,
            "all_reviews":   reviews,
            "website_uri":   website_uri,
        }
    except Exception as e:
        print(f"  Places API 오류: {e}")
        return None

# ── 감정 분석 (규칙 기반 · Claude API 없이) ──────────────
def analyze_sentiment(negative_review, rating):
    """간단한 규칙 기반 감정 분석 — Claude API 연동 전 임시"""
    if not negative_review:
        score = min(100, int(float(rating) * 20)) if rating else 50
        return score

    negative_words = ["rude", "slow", "cold", "dirty", "bad", "terrible",
                      "awful", "horrible", "worst", "disappointed", "never again"]
    count = sum(1 for w in negative_words if w in negative_review.lower())
    base = min(100, int(float(rating) * 20)) if rating else 50
    return max(0, base - count * 5)

# ── 메인 enrichment 루프 ──────────────────────────────────
async def enrich():
    sheet = get_sheet()
    all_rows = sheet.get_all_values()
    header = all_rows[0]
    rows = all_rows[1:]

    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print(f"총 {len(rows)}개 행 enrichment 시작\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        for i, row in enumerate(rows):
            # 이미 enriched + rating 있으면 스킵
            if row[COL["outreach_status"]] == "enriched" and row[COL["google_rating"]]:
                continue

            name    = row[COL["business_name"]]
            city    = row[COL["city"]]
            country = row[COL["country"]]
            detail_url = row[COL["notes"]]

            print(f"[{i+1}/{len(rows)}] {name} - {city}, {country}")

            # 1. Michelin 상세 → website
            website = ""
            if detail_url and "michelin.com" in detail_url:
                website = await fetch_website(page, detail_url)
                print(f"  website: {website or '없음'}")

            # 2. 웹사이트 → email
            email = ""
            if website:
                email = await fetch_email(page, website)
                print(f"  email: {email or '없음'}")

            # 3. Google Places API
            places = fetch_places_data(name, city, country)
            rating = review_count = negative = ""
            if places:
                rating       = places["rating"]
                review_count = places["review_count"]
                negative     = places["negative"]
                # Places에서 website 보완 (Michelin에서 못 가져온 경우)
                if not website and places.get("website_uri"):
                    website = places["website_uri"]
                print(f"  rating: {rating} ({review_count}개 리뷰)")

            # 4. 감정 분석
            sentiment = analyze_sentiment(negative, rating) if places else ""

            # 5. Sheets 업데이트 (행 전체를 한번에 — API 호출 최소화)
            row_num = i + 2  # 1-based + header
            # 현재 행 복사 후 필드 업데이트
            full_row = list(row) + [""] * (17 - len(row))  # 17컬럼 보장
            full_row[COL["website"]]        = website
            full_row[COL["email"]]          = email
            full_row[COL["google_rating"]]  = rating
            full_row[COL["review_count"]]   = review_count
            full_row[COL["negative_review"]]= negative
            full_row[COL["sentiment_score"]]= sentiment
            full_row[COL["outreach_status"]]= "enriched"
            sheet.update(range_name=f"A{row_num}:Q{row_num}", values=[full_row])

            await asyncio.sleep(1.2)  # Sheets API rate limit 대응

        await browser.close()

    print("\n완료 — enrichment 전체 완료")

if __name__ == "__main__":
    asyncio.run(enrich())
