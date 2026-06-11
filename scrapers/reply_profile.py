"""
SMBkits — 답장 리뷰 프로필 생성기
관심 있는 레스토랑에게 보낼 리뷰 응대 프로필 HTML 이메일 생성

Usage:
    python scrapers/reply_profile.py --url "https://www.tripadvisor.com/Restaurant_Review-..."
    python scrapers/reply_profile.py --name "Rasoi Ghar"  # CSV에서 URL 자동 검색
"""

import os, sys, re, asyncio, argparse, json, csv
import browser_cookie3
from playwright.async_api import async_playwright
from google import genai
from google.genai import types
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)

CSV_PATH    = os.path.join(os.path.dirname(__file__), "results.csv")
GEMINI_KEY  = os.getenv("GEMINI_API_KEY")
MODEL       = "gemini-3.1-flash-lite"

gemini = genai.Client(api_key=GEMINI_KEY)


# ─── CSV에서 레스토랑 찾기 ────────────────────────────────────────────────────
def find_in_csv(name: str) -> dict | None:
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if name.lower() in row.get("business_name", "").lower():
                return row
    return None


# ─── TripAdvisor 리뷰 스크래핑 ────────────────────────────────────────────────
def get_chrome_cookies():
    try:
        jar = browser_cookie3.chrome(domain_name=".tripadvisor.com")
        return [{"name": c.name, "value": c.value, "domain": c.domain,
                 "path": c.path, "secure": c.secure} for c in jar]
    except Exception:
        return []


async def scrape_one(page, url: str) -> dict:
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_selector("h1", timeout=20000)

    # 레스토랑 기본 정보
    name = await page.evaluate("() => document.querySelector('h1')?.innerText || ''")

    # 평점
    rating = ""
    for sel in ["[data-automation='bubbleRatingValue']", "[class*='biGQs _P fiohW uuBRH']", "span.ZDEqb"]:
        el = await page.query_selector(sel)
        if el:
            rating = (await el.evaluate("el => el.innerText")).strip()
            if rating: break

    # 리뷰 수
    review_count = ""
    for sel in ["[data-automation='reviewCount']", "[class*='biGQs _P pZUbB KxBGd']", "span.IcelI"]:
        el = await page.query_selector(sel)
        if el:
            review_count = (await el.evaluate("el => el.innerText")).strip()
            if review_count: break

    # 리뷰 로드
    try:
        await page.wait_for_selector("[data-test-target='reviews-tab']", timeout=12000)
        tab = await page.query_selector("[data-test-target='reviews-tab']")
        if tab:
            await tab.evaluate("el => el.scrollIntoView({block:'center'})")
        await page.wait_for_selector("[data-automation='reviewCard']", timeout=12000)
    except Exception:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.6)")
        try:
            await page.wait_for_selector("[data-automation='reviewCard']", timeout=6000)
        except Exception:
            pass

    # 리뷰 최대 10개 수집
    cards = await page.query_selector_all("[data-automation='reviewCard']")
    reviews = []
    for card in cards[:10]:
        title_el = await card.query_selector("svg[data-automation='bubbleRatingImage'] title")
        stars = 0
        if title_el:
            t = await title_el.evaluate("el => el.textContent")
            m = re.search(r'(\d+)\s*of\s*5|중\s*(\d+)', t)
            if m:
                stars = int(m.group(1) or m.group(2))
        body_el = await card.query_selector("[data-test-target='review-body']")
        if not body_el:
            continue
        text = (await body_el.evaluate("el => el.innerText")).strip()
        if len(text) >= 20:
            reviews.append({"stars": stars, "text": text[:400]})

    positives = [r for r in reviews if r["stars"] >= 4]
    negatives = [r for r in reviews if 1 <= r["stars"] <= 3]

    return {
        "name": name.strip(),
        "rating": rating.strip(),
        "review_count": review_count.strip(),
        "positives": positives[:3],
        "negatives": negatives[:3],
    }


async def scrape_multiple(urls: list[str]) -> list[dict | None]:
    """브라우저를 한 번만 띄우고 URL만 바꿔가며 순차 스크래핑 (재실행으로 인한 차단 회피)"""
    cookies = get_chrome_cookies()
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        await ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        if cookies:
            await ctx.add_cookies(cookies)
        page = await ctx.new_page()

        # 워밍업: 트립어드바이저 메인에 먼저 진입해 잠시 머문 뒤 실제 페이지들로 이동 (DataDome 회피)
        await page.goto("https://www.tripadvisor.com/", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)

        for i, url in enumerate(urls):
            try:
                data = await scrape_one(page, url)
                results.append(data)
            except Exception as e:
                print(f"  실패: {url} - {e}")
                results.append(None)
            if i < len(urls) - 1:
                await page.wait_for_timeout(3000)

        await browser.close()

    return results


# ─── Gemini로 응대 예시 생성 ──────────────────────────────────────────────────
def generate_responses(data: dict) -> dict:
    positive = data["positives"][0]["text"] if data["positives"] else ""
    negative = data["negatives"][0]["text"] if data["negatives"] else ""
    name = data["name"]

    prompt = f"""You are a hospitality consultant helping {name} craft professional TripAdvisor responses.

Positive review: "{positive}"
Critical review: "{negative}"

Write TWO responses:
1. A warm, specific thank-you response to the positive review (50-70 words)
2. A professional, empathetic response to the critical review that acknowledges the issue and invites them back (60-80 words)

Rules:
- Sound human and specific to the actual review content
- No generic phrases like "We value your feedback"
- Fine dining tone — dignified but warm
- Do NOT mention the restaurant name in every sentence

Respond ONLY in this exact JSON format:
{{"positive_response": "...", "negative_response": "..."}}"""

    try:
        resp = gemini.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.9,
            ),
        )
        return json.loads(resp.text)
    except Exception as e:
        print(f"Gemini 오류: {e}")
        return {"positive_response": "", "negative_response": ""}


# ─── HTML 이메일 생성 ─────────────────────────────────────────────────────────
def build_html(data: dict, responses: dict) -> str:
    name = data["name"]
    rating = data["rating"]
    count = data["review_count"]

    pos_review = data["positives"][0]["text"] if data["positives"] else "N/A"
    neg_review = data["negatives"][0]["text"] if data["negatives"] else "N/A"
    pos_stars = data["positives"][0]["stars"] if data["positives"] else "-"
    neg_stars = data["negatives"][0]["stars"] if data["negatives"] else "-"

    pos_resp = responses.get("positive_response", "")
    neg_resp = responses.get("negative_response", "")

    html = f"""
<div style="font-family: Georgia, serif; font-size: 14px; line-height: 1.7; color: #222; max-width: 640px;">

<p>As promised, here is the review response profile for <strong>{name}</strong>.</p>

<h3 style="border-bottom: 1px solid #ccc; padding-bottom: 6px; font-size: 15px;">
  TripAdvisor Snapshot
</h3>
<table style="width: 100%; border-collapse: collapse; margin-bottom: 24px; font-size: 13px;">
  <tr style="background: #f7f7f7;">
    <td style="padding: 8px 12px; border: 1px solid #ddd; font-weight: bold;">Rating</td>
    <td style="padding: 8px 12px; border: 1px solid #ddd;">{rating} / 5</td>
  </tr>
  <tr>
    <td style="padding: 8px 12px; border: 1px solid #ddd; font-weight: bold;">Total Reviews</td>
    <td style="padding: 8px 12px; border: 1px solid #ddd;">{count}</td>
  </tr>
  <tr style="background: #f7f7f7;">
    <td style="padding: 8px 12px; border: 1px solid #ddd; font-weight: bold;">Recent Positive</td>
    <td style="padding: 8px 12px; border: 1px solid #ddd;">{"⭐" * int(pos_stars) if str(pos_stars).isdigit() else ""} ({pos_stars}/5)</td>
  </tr>
  <tr>
    <td style="padding: 8px 12px; border: 1px solid #ddd; font-weight: bold;">Recent Critical</td>
    <td style="padding: 8px 12px; border: 1px solid #ddd;">{"⭐" * int(neg_stars) if str(neg_stars).isdigit() else ""} ({neg_stars}/5)</td>
  </tr>
</table>

<h3 style="border-bottom: 1px solid #ccc; padding-bottom: 6px; font-size: 15px;">
  Response Examples
</h3>

<table style="width: 100%; border-collapse: collapse; font-size: 13px;">
  <thead>
    <tr style="background: #2c2c2c; color: #fff;">
      <th style="padding: 10px 12px; text-align: left; width: 50%;">Guest Review</th>
      <th style="padding: 10px 12px; text-align: left; width: 50%;">Suggested Response</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background: #f0faf0; vertical-align: top;">
      <td style="padding: 10px 12px; border: 1px solid #ddd;">
        <span style="color: #2e7d32; font-weight: bold;">★ Positive ({pos_stars}/5)</span><br><br>
        <em>"{pos_review[:250]}{"..." if len(pos_review) > 250 else ""}"</em>
      </td>
      <td style="padding: 10px 12px; border: 1px solid #ddd;">{pos_resp}</td>
    </tr>
    <tr style="background: #fff8f0; vertical-align: top;">
      <td style="padding: 10px 12px; border: 1px solid #ddd;">
        <span style="color: #c62828; font-weight: bold;">▼ Critical ({neg_stars}/5)</span><br><br>
        <em>"{neg_review[:250]}{"..." if len(neg_review) > 250 else ""}"</em>
      </td>
      <td style="padding: 10px 12px; border: 1px solid #ddd;">{neg_resp}</td>
    </tr>
  </tbody>
</table>

<p style="margin-top: 24px; color: #555; font-size: 13px;">
  This is a sample of what SMBkits generates — tailored to your actual reviews,
  in your tone, updated as new reviews come in. Happy to walk you through it if useful.
</p>

</div>
"""
    return html


# ─── 메인 ─────────────────────────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url",  type=str, nargs="+", default=[], help="TripAdvisor URL (복수 가능)")
    parser.add_argument("--name", type=str, nargs="+", default=[], help="레스토랑 이름 (CSV 검색, 복수 가능)")
    args = parser.parse_args()

    urls = list(args.url)

    for nm in args.name:
        row = find_in_csv(nm)
        if row:
            urls.append(row.get("tripadvisor_url", ""))
            print(f"CSV에서 찾음: {row['business_name']} → {row.get('tripadvisor_url','')}")
        else:
            print(f"CSV에서 '{nm}' 찾을 수 없음")

    if not urls:
        print("--url 또는 --name 을 입력하세요")
        return

    print(f"스크래핑 중: {len(urls)}개 URL (브라우저 1회 실행)")
    results = await scrape_multiple(urls)

    for data in results:
        if data is None:
            continue
        print(f"\n  {data['name']} | {data['rating']} | {data['review_count']}")
        print(f"  긍정 리뷰: {len(data['positives'])}개 | 부정 리뷰: {len(data['negatives'])}개")

        print("  Gemini 응대 생성 중...")
        responses = generate_responses(data)

        html = build_html(data, responses)

        out_path = os.path.join(os.path.dirname(__file__), f"profile_{data['name'][:20].replace(' ','_')}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"  완료 → {out_path}")

    print("\n전체 완료. 브라우저에서 열어 확인 후 Gmail에 붙여넣기 하세요.")


if __name__ == "__main__":
    asyncio.run(main())
