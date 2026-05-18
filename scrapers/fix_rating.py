"""
SMBkits — Rating/Website 빠른 보완 스크립트
rating 없는 행만 Places API 호출 (Playwright 없음 → 빠름)

Usage:
    python scrapers/fix_rating.py
"""

import os
import re
import time
import requests
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

SOCIAL_EXCLUDE = ["instagram.com", "facebook.com", "twitter.com", "youtube.com",
                  "tripadvisor.com", "yelp.com", "google.com", "t.co",
                  "sevenrooms.com", "resy.com", "opentable.com", "inline.app",
                  "booking.com", "airbnb.com", "zomato.com", "tabelog.com"]

IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico")
SPAM_WORDS = ["example", "sentry", "pixel", "noreply", "no-reply", "wixpress",
              "schema", "wordpress", "jquery", "cloudflare", "analytics",
              "support@", "admin@", "postmaster@", "abuse@"]

def is_social(url):
    return any(s in url for s in SOCIAL_EXCLUDE)

def extract_email(url):
    """requests로 페이지 + contact 페이지에서 이메일 추출"""
    if not url or is_social(url):
        return ""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for target in [url, url.rstrip("/") + "/contact", url.rstrip("/") + "/about"]:
        try:
            res = requests.get(target, headers=headers, timeout=8)
            emails = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", res.text)
            filtered = []
            for e in emails:
                e_low = e.lower()
                if any(e_low.endswith(x) for x in IMG_EXT): continue
                if any(x in e_low for x in SPAM_WORDS): continue
                tld = e_low.rsplit(".", 1)[-1]
                if tld in {"png","jpg","jpeg","gif","svg","webp","ico"}: continue
                filtered.append(e)
            if filtered:
                return filtered[0]
        except:
            continue
    return ""

load_dotenv("scrapers/.env")

SHEET_ID       = os.getenv("SHEET_ID")
SHEET_NAME     = os.getenv("SHEET_NAME")
CREDS_FILE     = os.getenv("CREDS_FILE")
PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

COL = {
    "business_name":  0,
    "city":           2,
    "country":        3,
    "website":        4,
    "email":          6,
    "google_rating":  9,
    "review_count":   10,
    "negative_review":12,
    "sentiment_score":13,
    "outreach_status":14,
}

def get_sheet():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

def fetch_places(name, city, country):
    # country 없으면 도시만, 둘 다 없으면 이름만
    parts = [p for p in [name, city, country] if p.strip()]
    query = " ".join(parts)
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": PLACES_API_KEY,
        "X-Goog-FieldMask": "places.rating,places.userRatingCount,places.reviews,places.websiteUri",
    }
    body = {"textQuery": query, "languageCode": "en"}
    try:
        res = requests.post(url, headers=headers, json=body, timeout=10)
        data = res.json()
        places = data.get("places", [])
        if not places:
            # 오류 원인 출력
            if "error" in data:
                print(f"  API 오류: {data['error'].get('status')} - {data['error'].get('message','')[:80]}")
            return None
        p = places[0]
        reviews  = p.get("reviews", [])
        negative = [r.get("text", {}).get("text", "") for r in reviews if r.get("rating", 5) <= 2]
        return {
            "rating":      p.get("rating", ""),
            "review_count":p.get("userRatingCount", ""),
            "negative":    negative[0][:300] if negative else "",
            "website_uri": p.get("websiteUri", ""),
        }
    except Exception as e:
        print(f"  Places API 오류: {e}")
        return None

def analyze_sentiment(negative_review, rating):
    if not negative_review:
        return min(100, int(float(rating) * 20)) if rating else 50
    negative_words = ["rude", "slow", "cold", "dirty", "bad", "terrible",
                      "awful", "horrible", "worst", "disappointed", "never again"]
    count = sum(1 for w in negative_words if w in negative_review.lower())
    base = min(100, int(float(rating) * 20)) if rating else 50
    return max(0, base - count * 5)

def main():
    sheet = get_sheet()
    all_rows = sheet.get_all_values()
    rows = all_rows[1:]

    # rating 없는 행만 필터
    targets = [(i, r) for i, r in enumerate(rows)
               if not (len(r) > 9 and r[COL["google_rating"]])]

    print(f"Rating 없는 행: {len(targets)}개 / 전체 {len(rows)}개")
    print(f"예상 소요: 약 {len(targets) * 0.6 / 60:.0f}분\n")

    for idx, (i, row) in enumerate(targets):
        name    = row[COL["business_name"]] if len(row) > 0 else ""
        city    = row[COL["city"]]    if len(row) > 2 else ""
        country = row[COL["country"]] if len(row) > 3 else ""

        if not name:
            continue

        print(f"[{idx+1}/{len(targets)}] {name} - {city}, {country}")

        # full_row 초기화 (여기서!)
        full_row = list(row) + [""] * (17 - len(row))

        places = fetch_places(name, city, country)
        if not places:
            print(f"  Places: 없음")
            time.sleep(0.3)
            continue

        rating       = places["rating"]
        review_count = places["review_count"]
        negative     = places["negative"]
        website_uri  = places["website_uri"]
        sentiment    = analyze_sentiment(negative, rating)

        # 소셜 URL 필터링
        if is_social(website_uri):
            website_uri = ""

        # website 보완
        current_website = full_row[COL["website"]]
        if is_social(current_website):
            current_website = ""
        website = current_website or website_uri

        # 이메일 추출 (website 있을 때만)
        email = full_row[COL["email"]]
        if website and not email:
            email = extract_email(website)

        print(f"  rating: {rating} ({review_count}개) | website: {website or '없음'} | email: {email or '없음'}")

        row_num = i + 2
        full_row[COL["google_rating"]]   = rating
        full_row[COL["review_count"]]    = review_count
        full_row[COL["negative_review"]] = negative
        full_row[COL["sentiment_score"]] = sentiment
        full_row[COL["website"]]         = website
        full_row[COL["email"]]           = email

        sheet.update(range_name=f"A{row_num}:Q{row_num}", values=[full_row])
        time.sleep(0.5)

    print(f"\n완료 — rating 보완 완료")

if __name__ == "__main__":
    main()
