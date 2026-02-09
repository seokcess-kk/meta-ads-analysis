# Meta Ad Analyzer - Design Document

## Document Information
- **Feature Name**: meta-ad-analyzer
- **Plan Reference**: [meta-ad-analyzer.plan.md](../../01-plan/features/meta-ad-analyzer.plan.md)
- **Created**: 2026-02-09
- **Status**: Design
- **Version**: 1.0

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Next.js 14 (App Router)                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │ /ads        │  │ /ads/[id]   │  │ /trends     │  (Core)      │   │
│  │  │ Gallery     │  │ Detail Modal│  │ Dashboard   │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              SERVER                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Application                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │ /api/v1/ads │  │ /api/v1/    │  │ /api/v1/    │              │   │
│  │  │             │  │ analysis    │  │ trends      │  (Core)      │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Background Workers (Celery)                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │ Ad Collector│  │ Image       │  │ Copy        │              │   │
│  │  │ Task        │  │ Analyzer    │  │ Analyzer    │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ PostgreSQL  │ │ Redis       │ │ AWS S3      │ │ Claude API  │
│ (Data)      │ │ (Queue/     │ │ (Images)    │ │ (AI)        │
│             │ │  Cache)     │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

### 1.2 Project Structure (Monorepo)

```
meta-ads-analysis/
├── docker-compose.yml
├── .env.example
├── docs/
│   ├── 01-plan/
│   ├── 02-design/
│   └── META_AD_ANALYZER_SPEC.md
│
├── backend/                      # Python FastAPI
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── alembic/                  # DB migrations
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app entry
│   │   ├── config.py             # Settings (pydantic)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py           # Dependencies (DB session, etc)
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py     # Main router
│   │   │       ├── ads.py        # /ads endpoints
│   │   │       └── analysis.py   # /analysis endpoints
│   │   ├── models/               # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── ad.py
│   │   │   └── analysis.py
│   │   ├── schemas/              # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── ad.py
│   │   │   └── analysis.py
│   │   ├── services/             # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── collector.py      # Meta API collector
│   │   │   ├── analyzer.py       # AI analysis orchestrator
│   │   │   └── storage.py        # S3 operations
│   │   ├── workers/              # Celery tasks
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py
│   │   │   ├── collect_task.py
│   │   │   └── analyze_task.py
│   │   └── core/                 # Core utilities
│   │       ├── __init__.py
│   │       ├── database.py       # DB connection
│   │       ├── claude.py         # Claude API client
│   │       └── exceptions.py
│   └── tests/
│
├── frontend/                     # Next.js 14
│   ├── package.json
│   ├── Dockerfile
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx          # Home → redirect to /ads
│   │   │   ├── ads/
│   │   │   │   ├── page.tsx      # Gallery
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx  # Detail (or modal)
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── ui/               # shadcn/ui components
│   │   │   ├── ads/
│   │   │   │   ├── AdCard.tsx
│   │   │   │   ├── AdGrid.tsx
│   │   │   │   ├── AdDetailModal.tsx
│   │   │   │   └── AdFilter.tsx
│   │   │   └── layout/
│   │   │       ├── Header.tsx
│   │   │       └── Sidebar.tsx
│   │   ├── lib/
│   │   │   ├── api.ts            # API client (fetch wrapper)
│   │   │   └── utils.ts
│   │   ├── hooks/
│   │   │   └── useAds.ts         # SWR/React Query hooks
│   │   ├── stores/               # Zustand stores
│   │   │   └── filterStore.ts
│   │   └── types/
│   │       └── ad.ts
│   └── public/
│
└── scripts/
    ├── seed_data.py              # Initial data seeding
    └── test_collector.py         # Manual collector test
```

---

## 2. Database Schema

### 2.1 ERD (Entity Relationship Diagram)

```
┌─────────────────────────┐
│       ads_raw           │
├─────────────────────────┤
│ id (PK)                 │
│ ad_id (UNIQUE)          │
│ page_name               │
│ page_id                 │
│ ad_creative_body        │
│ ad_creative_link_title  │
│ ad_snapshot_url         │
│ start_date              │
│ stop_date               │
│ duration_days           │
│ platforms[]             │
│ currency                │
│ spend_lower             │
│ spend_upper             │
│ impressions_lower       │
│ impressions_upper       │
│ target_country          │
│ industry                │
│ region                  │
│ image_url               │
│ image_s3_path           │
│ collected_at            │
│ created_at              │
│ updated_at              │
└──────────┬──────────────┘
           │
           │ 1:N
           ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│   ads_analysis_image    │       │   ads_analysis_copy     │
├─────────────────────────┤       ├─────────────────────────┤
│ id (PK)                 │       │ id (PK)                 │
│ ad_id (FK, UNIQUE)      │       │ ad_id (FK, UNIQUE)      │
│ has_person              │       │ headline                │
│ person_type             │       │ headline_length         │
│ text_ratio              │       │ body                    │
│ has_chart               │       │ cta                     │
│ logo_position           │       │ core_message            │
│ primary_color           │       │ numbers (JSONB)         │
│ secondary_color         │       │ regions[]               │
│ tertiary_color          │       │ discount_info           │
│ color_tone              │       │ free_benefit            │
│ saturation              │       │ social_proof            │
│ layout_type             │       │ urgency                 │
│ atmosphere              │       │ differentiation         │
│ emphasis_elements[]     │       │ formality               │
│ mentioned_regions[]     │       │ emotion                 │
│ analysis_raw (JSONB)    │       │ style                   │
│ analyzed_at             │       │ target_audience         │
│ created_at              │       │ keywords[]              │
│ updated_at              │       │ analysis_raw (JSONB)    │
└─────────────────────────┘       │ analyzed_at             │
                                  │ created_at              │
                                  │ updated_at              │
                                  └─────────────────────────┘
```

### 2.2 Table Definitions (SQL)

```sql
-- ads_raw: 광고 원본 데이터
CREATE TABLE ads_raw (
    id SERIAL PRIMARY KEY,
    ad_id VARCHAR(255) UNIQUE NOT NULL,
    page_name VARCHAR(255),
    page_id VARCHAR(255),
    ad_creative_body TEXT,
    ad_creative_link_title TEXT,
    ad_creative_link_description TEXT,
    ad_snapshot_url TEXT,
    start_date DATE,
    stop_date DATE,
    duration_days INTEGER GENERATED ALWAYS AS (
        CASE
            WHEN stop_date IS NOT NULL THEN stop_date - start_date
            ELSE CURRENT_DATE - start_date
        END
    ) STORED,
    platforms TEXT[] DEFAULT '{}',
    currency VARCHAR(10),
    spend_lower INTEGER,
    spend_upper INTEGER,
    impressions_lower INTEGER,
    impressions_upper INTEGER,
    target_country VARCHAR(10) DEFAULT 'KR',
    industry VARCHAR(50) NOT NULL,
    region VARCHAR(50),
    image_url TEXT,
    image_s3_path TEXT,
    collected_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for ads_raw
CREATE INDEX idx_ads_industry ON ads_raw(industry);
CREATE INDEX idx_ads_region ON ads_raw(region);
CREATE INDEX idx_ads_duration ON ads_raw(duration_days);
CREATE INDEX idx_ads_start_date ON ads_raw(start_date);
CREATE INDEX idx_ads_collected_at ON ads_raw(collected_at);

-- ads_analysis_image: 이미지 분석 결과
CREATE TABLE ads_analysis_image (
    id SERIAL PRIMARY KEY,
    ad_id VARCHAR(255) UNIQUE NOT NULL REFERENCES ads_raw(ad_id) ON DELETE CASCADE,
    has_person BOOLEAN,
    person_type VARCHAR(50),  -- student/teacher/parent/none
    text_ratio INTEGER,       -- 0-100
    has_chart BOOLEAN,
    logo_position VARCHAR(50), -- top_left/top_right/bottom_left/bottom_right/center/none
    primary_color VARCHAR(7),  -- HEX code
    secondary_color VARCHAR(7),
    tertiary_color VARCHAR(7),
    color_tone VARCHAR(20),    -- bright/medium/dark
    saturation VARCHAR(20),    -- high/medium/low
    layout_type VARCHAR(50),   -- top_bottom_split/left_right_split/center_focus/full_text
    atmosphere VARCHAR(50),    -- serious/energetic/friendly/premium
    emphasis_elements TEXT[] DEFAULT '{}',
    mentioned_regions TEXT[] DEFAULT '{}',
    analysis_raw JSONB,        -- Full Claude response
    analyzed_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ads_analysis_copy: 카피 분석 결과
CREATE TABLE ads_analysis_copy (
    id SERIAL PRIMARY KEY,
    ad_id VARCHAR(255) UNIQUE NOT NULL REFERENCES ads_raw(ad_id) ON DELETE CASCADE,
    headline TEXT,
    headline_length INTEGER,
    body TEXT,
    cta TEXT,
    core_message VARCHAR(50),  -- achievement/social_proof/free_trial/discount/management
    numbers JSONB,             -- [{"value": 83, "unit": "%", "context": "선택률"}]
    regions TEXT[] DEFAULT '{}',
    discount_info VARCHAR(255),
    free_benefit VARCHAR(255),
    social_proof VARCHAR(255),
    urgency VARCHAR(255),
    differentiation TEXT,
    formality VARCHAR(20),     -- formal/informal/medium
    emotion VARCHAR(20),       -- rational/emotional/balanced
    style VARCHAR(20),         -- challenging/stable
    target_audience VARCHAR(50), -- 고등학생/재수생/학부모
    keywords TEXT[] DEFAULT '{}',
    analysis_raw JSONB,
    analyzed_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- collect_jobs: 수집 작업 상태 추적
CREATE TABLE collect_jobs (
    id SERIAL PRIMARY KEY,
    job_id UUID UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending/running/completed/failed
    keywords TEXT[] DEFAULT '{}',
    industry VARCHAR(50),
    country VARCHAR(10) DEFAULT 'KR',
    target_count INTEGER,
    collected_count INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 3. API Design

### 3.1 API Endpoints (MVP Scope)

#### 3.1.1 광고 수집 API

```yaml
POST /api/v1/ads/collect:
  summary: 광고 수집 작업 시작
  request:
    body:
      keywords: string[]      # 검색 키워드 (예: ["입시학원", "대치동 학원"])
      industry: string        # 업종 (예: "입시학원")
      country: string         # 국가 코드 (기본: "KR")
      limit: integer          # 수집 목표 수 (기본: 50, 최대: 200)
  response:
    201:
      job_id: string          # UUID
      status: "pending"
      estimated_time: integer # 예상 소요 시간 (초)

GET /api/v1/ads/collect/{job_id}:
  summary: 수집 작업 상태 조회
  response:
    200:
      job_id: string
      status: "pending" | "running" | "completed" | "failed"
      progress: integer       # 0-100
      collected_count: integer
      target_count: integer
      error_message: string | null
```

#### 3.1.2 광고 조회 API

```yaml
GET /api/v1/ads:
  summary: 광고 목록 조회
  query:
    industry: string          # 업종 필터
    region: string            # 지역 필터
    min_duration: integer     # 최소 게재 기간 (일)
    max_duration: integer     # 최대 게재 기간 (일)
    start_date: date          # 시작일 이후
    end_date: date            # 종료일 이전
    page: integer             # 페이지 번호 (기본: 1)
    limit: integer            # 페이지 크기 (기본: 20, 최대: 100)
    sort: string              # 정렬 기준 (기본: "-duration_days")
  response:
    200:
      items: Ad[]
      total: integer
      page: integer
      pages: integer
      has_next: boolean

GET /api/v1/ads/{ad_id}:
  summary: 광고 상세 조회 (분석 결과 포함)
  response:
    200:
      ad: Ad
      image_analysis: ImageAnalysis | null
      copy_analysis: CopyAnalysis | null
    404:
      error: "Ad not found"
```

#### 3.1.3 분석 API

```yaml
POST /api/v1/analysis/image/{ad_id}:
  summary: 이미지 분석 요청 (비동기)
  response:
    202:
      status: "queued"
      message: "Image analysis queued"
    400:
      error: "Image not found for this ad"

POST /api/v1/analysis/copy/{ad_id}:
  summary: 카피 분석 요청 (비동기)
  response:
    202:
      status: "queued"
      message: "Copy analysis queued"
    400:
      error: "No copy text found for this ad"

POST /api/v1/analysis/batch:
  summary: 여러 광고 일괄 분석 요청
  request:
    body:
      ad_ids: string[]        # 광고 ID 목록 (최대 50개)
      types: string[]         # ["image", "copy"] 분석 유형
  response:
    202:
      queued_count: integer
      skipped_count: integer  # 이미 분석된 건수
```

### 3.2 Response Schemas

```typescript
// Ad (광고 기본 정보)
interface Ad {
  id: number;
  ad_id: string;
  page_name: string;
  page_id: string;
  ad_creative_body: string | null;
  ad_creative_link_title: string | null;
  ad_snapshot_url: string | null;
  start_date: string;           // ISO date
  stop_date: string | null;
  duration_days: number;
  platforms: string[];
  industry: string;
  region: string | null;
  image_url: string | null;
  image_s3_path: string | null;
  collected_at: string;         // ISO datetime
  has_image_analysis: boolean;
  has_copy_analysis: boolean;
}

// ImageAnalysis (이미지 분석 결과)
interface ImageAnalysis {
  id: number;
  ad_id: string;
  composition: {
    has_person: boolean;
    person_type: string | null;
    text_ratio: number;
    has_chart: boolean;
    logo_position: string | null;
  };
  colors: {
    primary: string;          // HEX
    secondary: string | null;
    tertiary: string | null;
    tone: string;
    saturation: string;
  };
  layout: {
    type: string;
    atmosphere: string;
    emphasis_elements: string[];
  };
  mentioned_regions: string[];
  analyzed_at: string;
}

// CopyAnalysis (카피 분석 결과)
interface CopyAnalysis {
  id: number;
  ad_id: string;
  structure: {
    headline: string | null;
    headline_length: number;
    body: string | null;
    cta: string | null;
    core_message: string;
  };
  numbers: Array<{
    value: number;
    unit: string;
    context: string;
  }>;
  offer: {
    discount_info: string | null;
    free_benefit: string | null;
    social_proof: string | null;
    urgency: string | null;
    differentiation: string | null;
  };
  tone: {
    formality: string;
    emotion: string;
    style: string;
  };
  target_audience: string | null;
  keywords: string[];
  regions: string[];
  analyzed_at: string;
}
```

---

## 4. AI Analysis Prompts

### 4.1 Image Analysis Prompt (Claude Vision)

```markdown
# 광고 이미지 분석 요청

다음 광고 이미지를 분석하여 JSON 형식으로 응답해주세요.

## 분석 항목

1. **구성요소 (composition)**
   - has_person: 인물 포함 여부 (boolean)
   - person_type: 인물 유형 (student/teacher/parent/none)
   - text_ratio: 이미지 내 텍스트 비율 (0-100 정수)
   - has_chart: 차트/그래프 포함 여부 (boolean)
   - logo_position: 로고 위치 (top_left/top_right/bottom_left/bottom_right/center/none)

2. **색상 (colors)**
   - primary: 주요 색상 HEX 코드 (예: "#1E3A8A")
   - secondary: 보조 색상 HEX 코드 또는 null
   - tertiary: 세 번째 색상 HEX 코드 또는 null
   - tone: 명도 (bright/medium/dark)
   - saturation: 채도 (high/medium/low)

3. **레이아웃 (layout)**
   - type: 레이아웃 유형 (top_bottom_split/left_right_split/center_focus/full_text)
   - atmosphere: 분위기 (serious/energetic/friendly/premium)
   - emphasis_elements: 강조 요소 배열 (예: ["numbers", "statistics", "logo"])

4. **지역 정보 (regions)**
   - mentioned_regions: 이미지 내 언급된 지역명 배열 (예: ["강남", "대치동"])

## 응답 형식 (JSON만 응답)

```json
{
  "composition": {
    "has_person": true,
    "person_type": "student",
    "text_ratio": 45,
    "has_chart": false,
    "logo_position": "bottom_right"
  },
  "colors": {
    "primary": "#1E3A8A",
    "secondary": "#F59E0B",
    "tertiary": "#FFFFFF",
    "tone": "bright",
    "saturation": "high"
  },
  "layout": {
    "type": "top_bottom_split",
    "atmosphere": "serious",
    "emphasis_elements": ["numbers", "statistics"]
  },
  "mentioned_regions": ["강남", "대치동"]
}
```

주의: JSON 외 다른 텍스트 없이 순수 JSON만 응답해주세요.
```

### 4.2 Copy Analysis Prompt (Claude Text)

```markdown
# 광고 카피 분석 요청

다음 광고 카피를 분석하여 JSON 형식으로 응답해주세요.

## 광고 카피
---
{ad_creative_body}
---
{ad_creative_link_title}
---

## 분석 항목

1. **카피 구조 (structure)**
   - headline: 헤드라인 (가장 눈에 띄는 문구)
   - headline_length: 헤드라인 글자 수
   - body: 본문 내용
   - cta: CTA 문구 (예: "상담 신청하기", "자세히 보기")
   - core_message: 핵심 메시지 유형 (achievement/social_proof/free_trial/discount/management)

2. **숫자 정보 (numbers)**
   - 배열 형태로, 각 숫자의 값(value), 단위(unit), 맥락(context) 포함

3. **제안 (offer)**
   - discount_info: 할인 정보 (예: "30% 할인")
   - free_benefit: 무료 혜택 (예: "무료 상담")
   - social_proof: 사회적 증거 (예: "83%가 선택")
   - urgency: 긴급성 (예: "선착순 30명", "마감 임박")
   - differentiation: 차별화 포인트

4. **톤앤매너 (tone)**
   - formality: 격식 수준 (formal/informal/medium)
   - emotion: 감정 소구 (rational/emotional/balanced)
   - style: 스타일 (challenging/stable)

5. **타겟 및 키워드**
   - target_audience: 타겟 오디언스 (고등학생/재수생/학부모/일반)
   - keywords: 주요 키워드 배열 (5-10개)
   - regions: 언급된 지역명 배열

## 응답 형식 (JSON만 응답)

```json
{
  "structure": {
    "headline": "목동 입시생 83%가 선택한 이유",
    "headline_length": 16,
    "body": "소규모 맞춤 관리로 평균 2등급 상승",
    "cta": "상담 신청하기",
    "core_message": "social_proof"
  },
  "numbers": [
    {"value": 83, "unit": "%", "context": "선택률"},
    {"value": 2, "unit": "등급", "context": "성적 향상"}
  ],
  "offer": {
    "discount_info": null,
    "free_benefit": "무료 학습 진단",
    "social_proof": "83% 선택",
    "urgency": null,
    "differentiation": "소규모 맞춤 관리"
  },
  "tone": {
    "formality": "formal",
    "emotion": "rational",
    "style": "stable"
  },
  "target_audience": "고등학생",
  "keywords": ["선택", "소규모", "맞춤", "관리", "등급", "상승"],
  "regions": ["목동"]
}
```

주의: JSON 외 다른 텍스트 없이 순수 JSON만 응답해주세요.
```

---

## 5. Frontend Components

### 5.1 Page Structure

```
/                           → Redirect to /ads
/ads                        → AdGalleryPage (광고 갤러리)
/ads?duration=30            → 필터 적용된 갤러리
/ads/[id]                   → AdDetailPage (또는 Modal)
```

### 5.2 Component Hierarchy

```
App
├── Header
│   ├── Logo
│   └── Navigation
│
├── AdGalleryPage
│   ├── AdFilter
│   │   ├── DurationFilter (MVP: 게재기간만)
│   │   └── SortSelect
│   ├── AdGrid
│   │   └── AdCard (반복)
│   │       ├── AdThumbnail
│   │       ├── AdMeta (page_name, duration)
│   │       └── AnalysisBadge
│   ├── Pagination
│   └── AdDetailModal (선택 시)
│       ├── AdImage (확대)
│       ├── AdBasicInfo
│       ├── ImageAnalysisPanel
│       │   ├── CompositionSection
│       │   ├── ColorPalette
│       │   └── LayoutInfo
│       └── CopyAnalysisPanel
│           ├── StructureSection
│           ├── NumbersSection
│           ├── OfferSection
│           └── ToneSection
│
└── Footer
```

### 5.3 Key Component Specifications

#### AdCard.tsx
```typescript
interface AdCardProps {
  ad: Ad;
  onClick: (ad: Ad) => void;
}

// 표시 정보:
// - 썸네일 이미지 (없으면 placeholder)
// - page_name (광고주)
// - duration_days + "일 게재중/완료"
// - 분석 상태 뱃지 (완료/대기/분석중)
```

#### AdDetailModal.tsx
```typescript
interface AdDetailModalProps {
  ad: Ad;
  imageAnalysis: ImageAnalysis | null;
  copyAnalysis: CopyAnalysis | null;
  isOpen: boolean;
  onClose: () => void;
}

// 레이아웃:
// - 좌측: 광고 이미지 (확대)
// - 우측: 기본 정보 + 탭 (이미지 분석 / 카피 분석)
```

#### AdFilter.tsx (MVP)
```typescript
interface AdFilterProps {
  onFilterChange: (filters: FilterState) => void;
}

interface FilterState {
  minDuration: number | null;  // 최소 게재기간
  sort: 'duration_desc' | 'duration_asc' | 'date_desc';
}

// MVP에서는 게재기간 필터만 구현
// - 7일 이상 / 14일 이상 / 30일 이상 / 60일 이상
```

---

## 6. Implementation Order

### 6.1 Week 1-2: 인프라 + 수집

| 순서 | 작업 | 파일/위치 | 의존성 |
|------|------|----------|--------|
| 1 | Docker Compose 설정 | `docker-compose.yml` | - |
| 2 | Backend 프로젝트 초기화 | `backend/` | 1 |
| 3 | Database 스키마 (Alembic) | `backend/alembic/` | 2 |
| 4 | Config 설정 (환경변수) | `backend/app/config.py` | 2 |
| 5 | Database 연결 | `backend/app/core/database.py` | 3, 4 |
| 6 | SQLAlchemy Models | `backend/app/models/` | 5 |
| 7 | Pydantic Schemas | `backend/app/schemas/` | 6 |
| 8 | Meta API Collector | `backend/app/services/collector.py` | 4 |
| 9 | S3 Storage Service | `backend/app/services/storage.py` | 4 |
| 10 | Celery 설정 | `backend/app/workers/celery_app.py` | 4 |
| 11 | Collect Task | `backend/app/workers/collect_task.py` | 8, 9, 10 |
| 12 | Ads API Endpoints | `backend/app/api/v1/ads.py` | 6, 7 |

### 6.2 Week 3-4: AI 분석 + 기본 UI

| 순서 | 작업 | 파일/위치 | 의존성 |
|------|------|----------|--------|
| 13 | Claude API Client | `backend/app/core/claude.py` | 4 |
| 14 | Analyzer Service | `backend/app/services/analyzer.py` | 13 |
| 15 | Analyze Tasks | `backend/app/workers/analyze_task.py` | 10, 14 |
| 16 | Analysis API Endpoints | `backend/app/api/v1/analysis.py` | 14, 15 |
| 17 | Frontend 초기화 | `frontend/` | - |
| 18 | API Client (Frontend) | `frontend/src/lib/api.ts` | 17 |
| 19 | Types 정의 | `frontend/src/types/ad.ts` | 17 |
| 20 | AdCard Component | `frontend/src/components/ads/AdCard.tsx` | 19 |
| 21 | AdGrid Component | `frontend/src/components/ads/AdGrid.tsx` | 20 |
| 22 | AdFilter Component | `frontend/src/components/ads/AdFilter.tsx` | 19 |
| 23 | AdDetailModal | `frontend/src/components/ads/AdDetailModal.tsx` | 19 |
| 24 | Gallery Page | `frontend/src/app/ads/page.tsx` | 21, 22, 23 |
| 25 | useAds Hook | `frontend/src/hooks/useAds.ts` | 18 |

---

## 7. Environment Variables

### 7.1 Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/meta_ads

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=meta-ads-images

# Claude API
ANTHROPIC_API_KEY=your-anthropic-api-key

# Meta API (Ad Library)
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret
META_ACCESS_TOKEN=your-meta-access-token

# App
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

### 7.2 Frontend (.env.local)

```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# App
NEXT_PUBLIC_APP_NAME=Meta Ad Analyzer
```

---

## 8. Testing Strategy

### 8.1 Backend Tests

```
backend/tests/
├── conftest.py              # Fixtures (DB session, test client)
├── test_api/
│   ├── test_ads.py          # Ads API tests
│   └── test_analysis.py     # Analysis API tests
├── test_services/
│   ├── test_collector.py    # Meta API collector tests
│   └── test_analyzer.py     # Claude analyzer tests
└── test_workers/
    └── test_tasks.py        # Celery task tests
```

### 8.2 Frontend Tests

```
frontend/
├── __tests__/
│   ├── components/
│   │   ├── AdCard.test.tsx
│   │   └── AdFilter.test.tsx
│   └── hooks/
│       └── useAds.test.ts
└── cypress/                  # E2E tests (Core phase)
```

---

## 9. Acceptance Criteria (MVP)

### 9.1 광고 수집 시스템
- [ ] Meta Ad Library API 호출하여 입시학원 광고 100개 수집
- [ ] 이미지 다운로드 후 S3 업로드
- [ ] 수집 진행률 API로 조회 가능
- [ ] 수집 실패 시 에러 로깅

### 9.2 AI 분석 엔진
- [ ] Claude Vision API로 이미지 분석 (색상, 레이아웃, 구성요소)
- [ ] Claude Text API로 카피 분석 (구조, 톤, 키워드)
- [ ] 분석 결과 JSON으로 DB 저장
- [ ] 분석 정확도 80% 이상 (내부 평가)

### 9.3 광고 갤러리 UI
- [ ] 광고 목록 그리드 형태로 표시
- [ ] 게재기간 필터 (7일/14일/30일/60일 이상)
- [ ] 광고 클릭 시 상세 모달 표시
- [ ] 이미지/카피 분석 결과 탭으로 확인

---

## 10. Appendix

### 10.1 Meta Ad Library API Reference
- Endpoint: `https://graph.facebook.com/v18.0/ads_archive`
- Required fields: `ad_id, page_name, ad_creative_body, ad_snapshot_url, ...`
- Rate limit: 200 calls/hour

### 10.2 Claude API Pricing (2026 기준 예상)
- Claude 3.5 Sonnet: ~$3/1M input tokens, ~$15/1M output tokens
- Vision: Additional ~$0.024/image

---

## Changelog

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-02-09 | 초기 Design 문서 작성 | Claude |
