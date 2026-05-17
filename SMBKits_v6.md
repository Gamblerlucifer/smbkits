# SMBKits — 마스터플랜 & 실행 체크리스트 v6.0
> 최초 작성: 2026-05-16 | 최종 업데이트: 2026-05-18
> v6.1: Gemini·GPT 전략 보고서 핵심 반영 (Supabase 스키마·프롬프트·대시보드 원칙)

---

## 현재 진행 상황

```
✓ Next.js 프로젝트 생성 (C:\Users\jjun1\Desktop\Project\smbkits)
✓ GitHub 연결 (github.com/Gamblerlucifer/smbkits)
✓ Vercel 배포 (smbkits.vercel.app · 팀: MJM)
✓ 도메인 구매 및 연결 완료 (smbkits.com · 2026-05-18)
✓ 투웨이 전략 확정
✓ Way 2 프리미엄 랜딩 페이지 완성
✓ 7개 도구 상세 페이지 완성
✓ SEO 전체 구현 (메타데이터·JSON-LD·사이트맵·robots)
✓ OG 이미지 생성 (public/og/*.jpg — 8개, 텍스트 보완 필요)

→ 지금: Phase 1 리드 DB 구축 준비
```

### 2026-05-18 작업 내역
- JSON-LD 정리: `SoftwareApplication` + `AggregateOffer` 전 페이지 제거
- JSON-LD 정리: `github sameAs` Organization에서 제거
- FAQPage 스키마 추가: 전체 9개 페이지 (각 3개 질문)
- 키워드 확장: 전체 9개 페이지 (reputation repair, local SEO, review reply management 등)
- `@import url(...)` 제거: page.tsx 렌더 블로킹 해소
- sitemap.ts: 메인 페이지 `changeFrequency` monthly → weekly
- `public/og/*.jpg` 8개 생성 (sharp, 1200×630, 다크 배경 — 텍스트 추가 필요)

---

## 투웨이 전략

> 같은 7개 도구, 완전히 다른 두 개의 시장 진입

|  | Way 2 — 프리미엄 (지금) | Way 1 — 커피슬로건 (나중) |
|--|----------------------|------------------------|
| **타겟** | 미슐랭·Forbes·SCA 등 인증 프리미엄 업장 | 전 세계 전 업종 일반 소상공인 |
| **가격** | $24.99 / $49.99 / $99.99/월 | $4.99/월 |
| **랜딩** | 프라이빗 브랜드 인프라 포지셔닝 | "오늘 커피값이 한 달 플랜입니다" |
| **슬로건** | Reputation, once damaged, rarely recovers. | You paid $5 for your morning coffee. That's our monthly plan. |
| **콜드메일** | 인증기관별 전용 스크래퍼 (직접 파싱) | Outscraper (Google Maps 전 업종) |
| **7개 도구** | 동일 | 동일 |

---

## 7개 AI 도구

| # | 도구명 (UI 표시) | 내부 코드명 | 기능 | 가격 |
|---|----------------|-----------|------|------|
| 1 | **Reputation Response** | Review Reply AI | 리뷰 감정 분석 → 등급별 처리 | $19/월 |
| 2 | **Social Presence** | Social Caption AI | 사진·메뉴 → SNS 캡션 생성 | $15/월 |
| 3 | **Local Positioning** | Competitor Intel | 경쟁 업체 리뷰 분석 리포트 | $29/월 |
| 4 | **Reputation Recovery** | Review Booster | 만족 고객 → 리뷰 요청 자동화 | $19/월 |
| 5 | **Brand Voice Library** | Menu Description AI | 메뉴·서비스 설명 문구 생성 | $9 일회성 |
| 6 | **Visibility Intelligence** | Local SEO Checker | Google 검색 노출 진단 | $29/월 |
| 7 | **Brand Responses** | Staff Reply Templates | 고객 불만 대응 스크립트 | $12/월 |

### Reputation Response — 핵심 로직

```
리뷰 수신 → Claude API 감정 분석 (1~5단계)
  ├── 4~5단계 (긍정) → 브랜드 톤 응답 자동 발행
  ├── 3단계 (중립)  → 초안 생성 → 오너 승인 후 발행
  └── 1~2단계 (부정) → 오너 즉시 알림 → 직접 대응
                       (AI 초안 참고용만 · 강제 발행 없음)
```

---

## 가격 구조

**Way 2 — 프리미엄**

| 등급 | 월간 | 연간 | 타겟 |
|------|------|------|------|
| Premium | $24.99 | $249.99 | 미슐랭 1스타 · Bib Gourmand |
| Elite | $49.99 | $499.99 | 2스타 · World's 50 Best |
| Prestige | $99.99 | $999.99 | 3스타 · 최고 등급 |

**Way 1 — 커피슬로건**

| 플랜 | 월간 | 연간 |
|------|------|------|
| Free | $0 | — |
| Standard | $4.99 | $49.99 |
| Plus | $9.99 | $99.99 |

---

## Phase 0 — 랜딩 페이지 (지금)

### Way 2 프리미엄 랜딩 (`app/page.tsx`)
- [x] 헤드라인 · 히어로 섹션
- [x] 인증기관 마키 (미슐랭·World's 50 Best·Forbes·SCA·Decanter·Tabelog)
- [x] 핵심 가치 스테이트먼트
- [x] Reputation Response 흐름 설명
- [x] 7개 도구 리스트
- [x] 프라이빗 액세스 신청 폼
- [x] GitHub push → Vercel 자동 배포 확인
- [x] www.smbkits.com DNS 정상 접속 확인 (2026-05-18 완료)
- [ ] OG 이미지 텍스트 추가 (현재: 다크 배경만)

### 각 도구 상세 페이지 (7개)
- [x] app/reputation-response/page.tsx
- [x] app/social-presence/page.tsx
- [x] app/local-positioning/page.tsx
- [x] app/reputation-recovery/page.tsx
- [x] app/brand-voice/page.tsx
- [x] app/visibility-intelligence/page.tsx
- [x] app/brand-responses/page.tsx

### Way 1 커피슬로건 랜딩 (Phase 5 · MRR $500+ 이후)
- [ ] 별도 레포 생성 (local.smbkits.com)
- [ ] Vercel 서브도메인 연결
- [ ] 커피슬로건 랜딩 제작

---

## Phase 1 — 리드 DB 구축

### 타겟 업종 전체 맵

#### 인증 리스트 있음 → Way 2 스크래퍼 직접 파싱

| 업종 | 인증/리스트 | 소스 URL | 난이도 | 우선순위 |
|------|------------|---------|--------|---------|
| 레스토랑 | Michelin Guide | guide.michelin.com | ★☆☆ | 1 |
| 레스토랑 | World's 50 Best | theworlds50best.com | ★☆☆ | 1 |
| 레스토랑 | Tabelog 3.5+ | tabelog.com | ★★☆ | 2 |
| 바 | World's 50 Best Bars | theworlds50best.com | ★☆☆ | 1 |
| 바 | Spirited Awards | tales.community | ★★☆ | 3 |
| 스파 | Forbes 5-Star Spa | forbestravelguide.com | ★★☆ | 2 |
| 스파 | ISPA 인증 | experienceispa.com | ★★☆ | 2 |
| 카페 | SCA 인증 | sca.coffee | ★★☆ | 2 |
| 와인바·와인숍 | Decanter 95점+ | decanter.com | ★★☆ | 2 |
| 와인바·와인숍 | Wine Spectator | winespectator.com | ★★☆ | 3 |
| 위스키바 | Whisky Advocate 90점+ | whiskyadvocate.com | ★★☆ | 3 |

#### 인증 리스트 없음 → 플랫폼 필터링 또는 수동 수집

| 업종 | 접근 방법 | 난이도 | 우선순위 |
|------|----------|--------|---------|
| 살롱·헤어·네일 | Yelp 4.5+ · Google Maps 고평점 (Outscraper) | ★★☆ | Way 1 우선 |
| 웰니스·필라테스·요가 스튜디오 | Mindbody 상위 리스트 · Google Maps | ★★☆ | Way 1 우선 |
| 반려동물 미용·호텔 | 지역 커뮤니티 리스트 · Google Maps 수동 | ★★★ | Way 1 우선 |
| 프리미엄 베이커리·파티스리 | Zagat · 지역 매체 수상 리스트 | ★★★ | 추후 검토 |

> **전략:** 인증 리스트 있는 업종 → Way 2 직접 파싱 우선
> 인증 없는 업종 → Way 1 Outscraper로 대량 처리 또는 MRR $500 이후 검토

---

### Premium Score System
> 인증 없는 업종의 핵심 필터 — "Premium Signal Density"

| 요소 | 가중치 |
|------|--------|
| Google 평점 | 15% |
| 리뷰 수 | 10% |
| 재방문 언급 | 15% |
| 사진 품질 | 15% |
| Instagram 태그 품질 | 10% |
| 예약 난이도 | 10% |
| 감정 분석 안정성 | 10% |
| Interior consistency | 5% |
| 가격대 | 5% |
| 브랜드 언어 수준 | 5% |

→ 최종 출력: **Premium Confidence Score 0~100**
→ 인증 업종도 동일 스코어 산출 (비교 기준 통일)

---

### 파이프라인 아키텍처

```
GitHub Actions
     ↓
Playwright Scraper (인증 리스트 직접 파싱 / Google Maps)
     ↓
Normalization (업종·도시·국가 표준화)
     ↓
Google Places Enrichment (평점·리뷰·사진·예약)
     ↓
Claude API Sentiment (감정 분석 1~5단계 · 부정 리뷰 추출)
     ↓
Premium Score Engine (0~100)
     ↓
Google Sheets DB
     ↓
Hunter.io 이메일 추출 → NeverBounce 검증
     ↓
Cold Outreach (Instantly.ai)
```

---

### Google Sheets DB 컬럼 구조

| 컬럼 | 설명 |
|------|------|
| business_name | 업장명 |
| category | 업종 |
| city | 도시 |
| country | 국가 |
| website | 공식 사이트 |
| instagram | 인스타그램 |
| email | 대표 이메일 |
| source_type | Michelin / Maps 등 |
| authority_grade | 인증 등급 |
| google_rating | 평점 |
| review_count | 리뷰 수 |
| premium_score | AI 프리미엄 점수 (0~100) |
| negative_review | 최근 부정 리뷰 원문 |
| sentiment_score | 감정 분석 결과 |
| outreach_status | 발송 상태 |
| reply_status | 답장 여부 |
| notes | 메모 |

- [ ] Google Sheets 생성
- [ ] 중복 제거 기준: `business_name + city`

---

### 스크래퍼 실행 순서

**1차 — 바로 시작 (리드 품질 최고 · ROI 최우선):**
- [ ] 미슐랭 레스토랑 — guide.michelin.com
- [ ] World's 50 Best Restaurants + Bars — theworlds50best.com
- [ ] Forbes 5-Star Spa — forbestravelguide.com

**2차 — 1차 완료 후:**
- [ ] SCA 인증 카페 — sca.coffee
- [ ] Tabelog 3.5+ — tabelog.com
- [ ] Decanter 95점+ — decanter.com
- [ ] ISPA 인증 스파 — experienceispa.com

**3차 — Premium Score 기반 (인증 없음):**
- [ ] 살롱·헤어·네일 — Google Maps + Premium Score 70+
- [ ] 웰니스·필라테스·요가 — Google Maps + Premium Score 70+
- [ ] 반려동물 미용·호텔 — Google Maps + Premium Score 70+

**보류:**
- [ ] Spirited Awards, Wine Spectator, Whisky Advocate — 3차 이후 판단

---

### 이메일 추출 & 검증
- [ ] Hunter.io 가입 (무료 25건/월)
- [ ] 각 업장 웹사이트 → Hunter.io → 이메일 추출
- [ ] NeverBounce 검증 (무료 1,000건)

### 콜드 이메일 발송 전 데이터 무결성 검증 (Instantly.ai 연동 전 필수)

발송 스크립트 가동 전 Sheets에서 반드시 수동 확인:

| 항목 | 내용 | 이유 |
|------|------|------|
| `unanswered_reviews_count` | 미답변 리뷰 총량 누락 없이 카운트 | 콜드 메일 본문에 `"Your restaurant has [X] unanswered reviews."` 개인화 인젝션 |
| `owner_email` | null 리드 사전 격리 | 공란 리드가 있으면 발송 엔진 중단 |
| `email_status` | NeverBounce Valid 판정 확인 | 신규 발송 도메인 평판 보호 · 스팸함 방지 |

---

## Phase 2 — 콜드 이메일 파이프라인

### 발송 준비
- [ ] Gmail 발송 전용 계정 3개 생성
- [ ] Mailgun 가입 (무료 5,000건/월)
- [ ] Brevo 가입 (무료 300건/일)
- [ ] SPF / DKIM / DMARC 설정
- [ ] Gemini API 키 확보
- [ ] Instantly.ai 가입 + 워밍업 시작

**워밍업 스케줄:**
```
Week 1~2:  하루 5건
Week 3~4:  하루 10건
Week 5~6:  하루 20건
Week 7+:   하루 30건/계정 (3개 계정 → 최대 90건/일)
```

### Way 2 발송 (1차: 미슐랭 50개)
- [ ] 미슐랭 1스타 이상 50개 선정 (영어 리뷰 있음·웹사이트 있음·이메일 확보)
- [ ] 하루 25건씩 발송
- [ ] 답장 모니터링 + 수동 대응

---

## Phase 3 — 수요 검증

**기준: 관심 표현 5명 이상 → Phase 4 개발 착수**

- [ ] 어떤 업종이 답장률 높은지 기록
- [ ] 어떤 도구에 관심 보이는지 기록

### 피드백 수집 로그

| 날짜 | 업장명 | 인증등급 | 관심도구 | 피드백 |
|------|--------|---------|---------|--------|
|      |        |         |         |        |

---

## Phase 4 — 개발 (수요 검증 완료 후)

### 인프라 세팅
- [ ] Supabase 프로젝트 생성
- [ ] Stripe 계정 생성
- [ ] Anthropic API 키 발급

### Supabase 멀티 테넌시 스키마

```sql
-- 1. 비즈니스 테넌트 마스터
CREATE TABLE businesses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  name TEXT NOT NULL,
  tier TEXT DEFAULT 'way2_premium',       -- way2_premium | way1_mass
  website_url TEXT,
  google_maps_id TEXT UNIQUE,
  stripe_customer_id TEXT,
  subscription_status TEXT DEFAULT 'inactive'
);

-- 2. 브랜드 보이스 라이브러리 (Tonal Discipline 핵심)
CREATE TABLE brand_voices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  persona_description TEXT,               -- "미슐랭 2스타에 준하는 정중함과 극도의 절제"
  allowed_warmth_level INT DEFAULT 2,     -- 1(Executive) ~ 5(Emotional)
  forbidden_words TEXT[],                 -- ["존맛", "개이득", "대박", "가성비"]
  essential_brand_points TEXT[]           -- ["자가제면", "나파밸리 와인 페어링"]
);

-- 3. 리뷰 데이터 + 감정 트리아지 관리
CREATE TABLE reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
  platform TEXT DEFAULT 'google',
  author_name TEXT NOT NULL,
  rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  review_text TEXT,
  review_date TIMESTAMPTZ,
  triage_level TEXT DEFAULT 'routine_positive', -- routine_positive | neutral_feedback | critical_incident
  recovery_state TEXT DEFAULT 'queued',         -- queued | isolated | resolved
  ai_draft_response TEXT,
  is_published BOOLEAN DEFAULT FALSE,
  approved_at TIMESTAMPTZ
);
```

### Claude API — Tonal Discipline 시스템 프롬프트

```typescript
const systemPrompt = `
You are the Private Reputation Infrastructure for a premium independent brand.
Your objective is NOT to write marketing-heavy language or overly enthusiastic fluff.
Your goal is **Tonal Discipline** — clear communication, controlled warmth, strict brand continuity.

[Brand Identity]
- Client: ${brandVoice.business_name}
- Persona: ${brandVoice.persona_description}
- Warmth Level: ${brandVoice.allowed_warmth_level}/5 (1=Executive Composure, 5=Deeply Emotional)

[Forbidden Words]
${brandVoice.forbidden_words.map(w => `- NEVER use: "${w}"`).join('\n')}
- Never look reactive, defensive, or emotional.
- Avoid generic phrasing like "Thank you for your business."

[Essential Brand Points]
${brandVoice.essential_brand_points.map(p => `- Naturally integrate if contextually appropriate: ${p}`).join('\n')}

[Output]
Write a highly disciplined, professionally restrained draft response to the customer review.
`;
```

> 기본 응답: **Claude Haiku** ($0.00044/건) | 복잡한 위기: Claude Sonnet

### Critical Incident Isolation — 3단계 위기 격리 프로토콜

```
1단계 — 실시간 트리아지
  조건: 별점 1~3 OR 키워드 감지 (위생·식중독·불친절·법적대응)
  → triage_level = "critical_incident" 자동 분류

2단계 — 공개 스트림 격리
  → 일반 응답 프로세스 즉시 중단
  → recovery_state = "isolated" 강제 전환
  → 외부 채널 자동 답글 원천 차단

3단계 — 오너 프라이빗 에스컬레이션
  → 이메일/Webhook 알림 발송:
     "Critical reputation signal detected. Isolated privately for leadership judgment."
  → 대시보드 내부에서만 비공개 대응안 열람 가능
  → 오너가 직접 승인 후 발행
```

### 온보딩 플로우 (가입 → 즉시 세팅)

```
콜드 메일 클릭
  → smbkits.com 랜딩
  → 신청 폼 제출
  → Next.js Server Action 실행
  → Stripe 결제 웹훅
  → Supabase businesses 레코드 생성
  → brand_voices 초기값 자동 세팅
  → 대시보드 접근 권한 부여
```

### 개발 순서 (Claude Code — 7개 동시 MVP)

```
Day 1~5:   Reputation Response (핵심 인프라)
             Google OAuth · 리뷰 수집 · 감정 분석 · Stripe

Day 6~8:   Social Presence + Brand Voice Library

Day 9~11:  Local Positioning + Reputation Recovery

Day 12~14: Visibility Intelligence + Brand Responses
```

**공통 인프라 (Day 1~5 완성 후 전부 재사용):**
- Google OAuth + Places API
- Claude Haiku API 호출 패턴
- Stripe 결제 (플랜별)
- Supabase 멀티 테넌트 DB
- Resend 이메일 알림

### 배포
- [ ] 7개 도구 페이지 전부 작동 확인
- [ ] Stripe 결제 테스트
- [ ] Google Search Console 등록 + Sitemap 제출

---

## 대시보드 설계 원칙 — "Quiet Restraint" 유지

> GPT 독립 평가: "기능 개발 단계에서 가장 위험한 건 너무 빨리 SaaS처럼 변하는 것"

### ❌ 절대 넣지 않을 것

| 금지 요소 | 이유 |
|----------|------|
| Analytics 대시보드 / Charts 남발 | "growth tool" 느낌 → 포지셔닝 붕괴 |
| AI Assistant 인터페이스 | automation smell → 프리미엄 이미지 훼손 |
| Notification flood | 오너의 시간을 침해하는 느낌 |
| Engagement KPI | mass SaaS 문법 |
| CRM / Helpdesk / Chatbot 요소 | "운영툴"로 강등 |
| Mass onboarding 플로우 | invite-only 포지셔닝 훼손 |
| Template 강조 | "Managed with judgment, not templates" 카피와 충돌 |

### ✅ 유지할 것

- **Invite-only** 온보딩 유지 (가격 비공개 포함)
- 대시보드 UI = "private operating layer" 느낌
- 7개 도구 = 멀티탭 사이드바 (좌측), 심플한 레이아웃
- 모든 AI 초안은 **오너 승인 후 발행** (자동 발행 없음)
- 위기 리뷰는 **격리 후 알림** (공개 채널에 자동 노출 없음)
- 고객 지원 = Claude API 응답 (비용 ≈ $0, 체감 = 전담 서비스)

---

## Phase 5 — 스케일업 (MRR $500+ 달성 후)

### Way 2 vs Way 1 — 차별화 구조
> 같은 7개 도구, 다른 서비스 레이어 → 알아도 괜찮음

| | Way 2 $99 | Way 1 $4.99 |
|--|-----------|-------------|
| 7개 도구 | 동일 | 동일 |
| 온보딩 | 전담 셋업 | 셀프 |
| 브랜드 보이스 | 커스텀 구축 | 템플릿 |
| 고객 지원 | 전용 채널 (Claude API 응답) | 없음 |
| 월간 리포트 | 브랜드 리포트 포함 | 없음 |

> 지원 비용 = 거의 $0 (Claude API) · 고객 체감 = 프리미엄 매니지드 서비스

---

### 도메인 구조 (확정)
```
smbkits.com           → Way 2 프리미엄 랜딩 (현재 레포)
local.smbkits.com     → Way 1 커피슬로건 랜딩 (별도 레포)
app.smbkits.com       → 7개 도구 대시보드 (공유 백엔드)
```
> Way 2 고객이 Way 1의 존재를 알면 안 됨 → 완전 분리 필수

- [ ] Way 1 별도 레포 생성 + local.smbkits.com 연결
- [ ] 커피슬로건 랜딩 제작
- [ ] Outscraper 파이프라인 가동 (전 업종 대량 발송)
- [ ] 발송 전용 도메인 추가 구매 + 워밍업
- [ ] 하루 50건 → 100건 확대
- [ ] Product Hunt 런칭 준비
- [ ] Build in Public (X/트위터)
- [ ] Reddit 커뮤니티 참여 (r/restaurantowners, r/smallbusiness)

---

## 포지셔닝 원칙

> 두 보고서 공통 결론: SMBkits는 "AI reputation SaaS"가 아니라
> **"Private Reputation Infrastructure for High-Sensitivity Brands"**

### 실제 오너가 두려워하는 것 (카피 심리적 근거)

리뷰 자체가 아니라:
- **Public embarrassment** — 내부 압박이 외부에 노출되는 것
- **Brand tone collapse** — 직원이 브랜드답지 않은 말투로 답글 다는 것
- **Emotional response exposure** — 감정적으로 반응하는 것이 공개되는 것
- **Reputation inconsistency** — 리뷰마다 톤이 다른 것

→ 문제는 리뷰가 아니라 **"브랜드 품격 붕괴"**

### 고객 티어 우선순위

| Tier | 업종 | 전환 가능성 | 이유 |
|------|------|-----------|------|
| **1** | 미슐랭·오마카세·Forbes Spa·Destination Wellness | 최고 | 리뷰 민감도·owner ego·단가 모두 높음 |
| **2** | Specialty Coffee·Wine Bar·Boutique Salon·Aesthetic Clinic | 높음 | 브랜드 의식 있음 |
| **3** | 일반 로컬 비즈니스 | 낮음 | Way 1으로 처리 |

> Tier 1만 집중. Mass market 진입 시 브랜드 가치 하락.

### 전략적 정체성

**플랫폼** ❌ → **Private Intelligence Firm** ✅

현재 브랜딩 기준으로 플랫폼화보다 "operator-grade private system" 이 훨씬 강함.
기능 추가보다 **현재의 조용한 억제력(quiet restraint)을 유지**하는 것이 핵심.

### GPT 독립 평가 점수 (참고)

| 항목 | 점수 |
|------|------|
| 브랜딩 | 9.5/10 |
| 포지셔닝 | 9.3/10 |
| SEO 방향 | 9.1/10 |
| 시장 차별성 | 8.8/10 |
| 실행 현실성 | 8.5/10 |

---

## 참고: 이메일 시퀀스

### Day 0 — 레스토랑 타겟

**Subject:** Your [Restaurant Name] reviews — I ran an analysis

```
Hi [Owner name],

I ran a quick analysis of [Restaurant Name]'s recent Google reviews.

Here's what I found:

  5★ reviews (positive):  [N]개 → 자동 응답 가능
  3★ reviews (neutral):   [N]개 → 가볍게 응답 필요
  1~2★ reviews (negative): [N]개 → 직접 대응 필요

The [N] negative reviews are the ones that cost you customers.

Here's a draft response for the most recent one:

"[실제 부정 리뷰 원문 요약]"

---
"Thank you for taking the time to share your experience at
[Restaurant Name]. We're truly sorry we didn't meet your
expectations. This is not the standard we hold ourselves to,
and we'd love to make it right. Please reach out to us directly
at [이메일] — we'd like to take care of you personally."
---

Feel free to use it.

I built a tool that does this automatically — positive reviews
get a brand-standard response published immediately. Negative
reviews come straight to your phone. You respond personally.
Your brand stays yours.

smbkits.com — 7 AI tools for independent premium businesses.

✓ Reputation Response (sentiment triage 1~5)  → $19/월
✓ Social Presence (photo → caption)           → $15/월
✓ Local Positioning (competitor review intel)  → $29/월
✓ Reputation Recovery (auto review requests)  → $19/월
✓ Brand Voice Library (menu descriptions)     → $9 one-time
✓ Visibility Intelligence (Google SEO check)  → $29/월
✓ Brand Responses (complaint scripts)         → $12/월

Start with any one. Cancel anytime.

— [이름]
```

### Day 3 — 팔로업

**Subject:** The negative review — did you respond?

```
Hey [Owner name],

Just checking if the draft I sent was useful.

Most owners say the same: "I don't mind good reviews —
I just don't know how to handle bad ones without making it worse."

That's exactly what the triage system handles.

— [이름]
```

### Day 10 — 마지막

**Subject:** Last note — [Restaurant Name]

```
Hi [Owner name],

Restaurants that respond to reviews within 24 hours see
12% more foot traffic. [Restaurant Name] has [X] unanswered reviews.

smbkits.com — 7 AI tools, starting at $9. Try one, cancel anytime.

— [이름]
```

---

## 참고: API 비용

| 모델 | 입력 | 출력 | 용도 |
|------|------|------|------|
| **Claude Haiku 4.5** | $1/MTok | $5/MTok | 리뷰 응답 생성 — 기본 |
| Claude Sonnet 4.6 | $3/MTok | $15/MTok | 복잡한 분석 (필요 시) |

**리뷰 응답 1건당 비용:** ~$0.00044 (0.044센트)

> API 비용은 사실상 무시. 진짜 비용은 Stripe 수수료 (2.9%+$0.30/건).

---

## 참고: 자동화 스택

| 도구 | 역할 | 월 비용 |
|------|------|---------|
| Outscraper | Way 1 리드 스크래핑 | $0~5 |
| Hunter.io | 이메일 추출 | $0~49 |
| NeverBounce | 이메일 검증 | $0~8 |
| Instantly.ai | 시퀀스 발송 + 워밍업 | $37 |
| Mailgun / Brevo | 멀티 SMTP | $0 |
| Claude API | 개인화 초안 생성 | $3~10 |
| Vercel | 호스팅 | $0 |
| Supabase | DB | $0 |
| Stripe | 결제 (수익 발생 후 수수료만) | $0 |

---

## 참고: 리스크 대응

| 리스크 | 대응 |
|--------|------|
| 구글이 AI 응답 무료 내장 | 에이전트(자동 발행+모니터링)로 진화. 업종별 데이터 해자 |
| Claude API 비용 인상 | 마진 99.95% → 99.9%. 사실상 무관 |
| 콜드 이메일 스팸 필터 | 발송 도메인 분리 · SPF/DKIM/DMARC · 하루 30건/계정 초과 금지 |
| 경쟁사 진입 | 6개월 이내 선점. 리뷰 데이터 1만 건 이상이 해자 |

**종료 기준 (Kill Criteria):**
- Month 3: 400건 발송 후 유료 10명 미달 → 타겟/도구 재검토
- Month 6: MRR $500 미달 → 전면 피벗 검토

---

## 수익 현황

| 날짜 | 이벤트 | MRR |
|------|--------|-----|
| 2026-05-16 | 프로젝트 시작 | $0 |

---

*구 파일: SMBKits_마스터플랜_v5.md · SMBKits_Todo.md → 이 파일로 통합*
