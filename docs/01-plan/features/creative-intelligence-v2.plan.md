# Creative Intelligence Platform v2.0 Plan

> AI 기반 광고 크리에이티브 인텔리전스 플랫폼

## 1. Overview

### 1.1 Product Vision
**"경쟁사 광고 크리에이티브를 수집하고 AI로 분석하여 마케팅 인사이트를 제공하는 플랫폼"**

### 1.2 핵심 가치 제안
- 경쟁사 광고 크리에이티브 자동 수집 및 모니터링
- Claude AI 기반 이미지/카피 심층 분석
- 트렌드 패턴 발견 및 인사이트 리포트 생성
- 광고 아이디어 레퍼런스 라이브러리 구축

### 1.3 Target Users
| 사용자 | 니즈 |
|--------|------|
| 마케터 | 경쟁사 광고 벤치마킹, 크리에이티브 아이디어 |
| 광고 기획자 | 트렌드 분석, 레퍼런스 수집 |
| 브랜드 매니저 | 시장 모니터링, 경쟁사 동향 파악 |
| 에이전시 | 클라이언트 경쟁사 분석 리포트 |

---

## 2. Current State (v1.0 완료)

### 2.1 구현 완료
| 기능 | 상태 | 비고 |
|------|------|------|
| Meta Ad Library API 연동 | ✅ | 광고 수집 |
| 키워드 기반 광고 검색 | ✅ | 다국어 지원 |
| Playwright 스크린샷 캡처 | ✅ | 이미지 문제 해결 |
| Claude Vision 이미지 분석 | ✅ | 구성, 색상, 레이아웃 |
| Claude 카피 분석 | ✅ | 톤, 구조, 키워드 |
| Ad Gallery UI | ✅ | 필터링, 페이지네이션 |
| 광고 상세 모달 | ✅ | 분석 결과 표시 |
| 광고 삭제 기능 | ✅ | cascade delete |

### 2.2 현재 한계
- 단순 수집/분석만 가능, 인사이트 도출 부족
- 경쟁사별 모니터링 기능 없음
- 트렌드 분석 대시보드 없음
- 분석 결과 활용 기능 부족

---

## 3. v2.0 Feature Roadmap

### Phase 1: 경쟁사 모니터링 (P0 - 핵심)

#### 3.1.1 Competitor Watchlist
```
기능: 특정 광고주(page_id) 등록 및 자동 모니터링
- 경쟁사 Facebook Page 등록
- 신규 광고 자동 감지 및 알림
- 히스토리 추적
```

**API 활용:**
```python
# page_id 기반 검색
params = {
    "search_page_ids": ["competitor_page_id_1", "competitor_page_id_2"],
    ...
}
```

**데이터 모델:**
```sql
CREATE TABLE competitors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    page_id VARCHAR(255) UNIQUE,
    industry VARCHAR(50),
    created_at TIMESTAMP
);

CREATE TABLE competitor_alerts (
    id SERIAL PRIMARY KEY,
    competitor_id INT REFERENCES competitors(id),
    ad_id VARCHAR(255),
    detected_at TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);
```

#### 3.1.2 Competitor Dashboard
- 경쟁사별 광고 카운트 추이
- 신규 광고 타임라인
- 플랫폼별 활동 비교 (FB/IG/Messenger)

---

### Phase 2: AI 인사이트 고도화 (P1)

#### 3.2.1 Creative Trend Analysis
```
기능: 수집된 광고들의 크리에이티브 트렌드 분석
- 색상 트렌드 (시간대별 주요 색상 변화)
- 레이아웃 패턴 (텍스트 비율, 인물 사용 등)
- 카피 톤 트렌드 (감정, 스타일 분포)
```

**분석 대시보드:**
| 인사이트 | 시각화 |
|---------|--------|
| 주요 색상 분포 | Color Pie Chart |
| 인물 사용 비율 | Progress Bar |
| 평균 텍스트 비율 | Gauge |
| CTA 유형 분포 | Bar Chart |
| 톤 분포 (격식/감정) | Radar Chart |

#### 3.2.2 Industry Benchmark
```
기능: 산업별 크리에이티브 벤치마크
- 산업별 평균 광고 집행 기간
- 산업별 선호 플랫폼
- 산업별 크리에이티브 특성
```

#### 3.2.3 Creative Similarity Detection
```
기능: 유사 크리에이티브 그룹핑
- 이미지 특성 기반 클러스터링
- 카피 스타일 유사도 분석
- "이 광고와 비슷한 광고" 추천
```

---

### Phase 3: 리포트 & 협업 (P2)

#### 3.3.1 Insight Report Generator
```
기능: AI 기반 인사이트 리포트 자동 생성
- 주간/월간 트렌드 리포트
- 경쟁사 모니터링 리포트
- 산업별 크리에이티브 분석 리포트
```

**리포트 구성:**
```markdown
# Weekly Creative Intelligence Report

## Executive Summary
- 이번 주 수집 광고: 150개
- 주요 트렌드: 밝은 색상, 짧은 카피
- 경쟁사 동향: A사 신규 캠페인 감지

## Trend Analysis
### Color Trends
- Primary: Blue (#0066FF) 증가
- 전주 대비: Warm → Cool 톤 이동

### Copy Trends
- 평균 길이: 45자 (전주 52자)
- 주요 CTA: "지금 시작하기", "무료 체험"

## Competitor Watch
### CompanyA
- 신규 광고 5개 감지
- 주요 메시지: 할인 프로모션

## Recommendations
- 트렌드 기반 추천 크리에이티브 방향
```

#### 3.3.2 Collection & Tagging
```
기능: 광고 컬렉션 관리
- 폴더/태그 기반 광고 정리
- 팀 공유 기능
- 코멘트 및 메모
```

---

### Phase 4: 확장 기능 (P3)

#### 3.4.1 EU/UK Targeting Insights (API 추가 필드)
```
기능: EU/UK 광고의 타겟팅 정보 수집 및 분석
- target_ages, target_gender, target_locations
- eu_total_reach, demographic breakdown
```

**추가 수집 필드:**
```python
"fields": [
    # 기존 필드
    ...,
    # EU/UK 전용 필드
    "target_ages",
    "target_gender",
    "target_locations",
    "eu_total_reach",
    "age_country_gender_reach_breakdown",
]
```

#### 3.4.2 Multi-Platform Expansion
```
기능: Google Ads, TikTok 등 확장 (향후)
- Google Ads Transparency Center
- TikTok Creative Center
```

---

## 4. Technical Architecture

### 4.1 System Overview
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  Ad Gallery  │  Competitor  │   Insights   │    Reports     │
│              │   Monitor    │  Dashboard   │                │
└──────────────┴──────────────┴──────────────┴────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  /api/ads    │ /api/compete │ /api/insight │  /api/report   │
└──────────────┴──────────────┴──────────────┴────────────────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Services Layer                            │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  Collector   │  Competitor  │   Insight    │    Report      │
│   Service    │   Monitor    │   Analyzer   │   Generator    │
└──────────────┴──────────────┴──────────────┴────────────────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
├──────────────┬──────────────┬──────────────────────────────┤
│  PostgreSQL  │    Redis     │         Claude AI            │
│   (Ads DB)   │   (Cache)    │   (Vision + Text Analysis)   │
└──────────────┴──────────────┴──────────────────────────────┘
```

### 4.2 New Data Models

```sql
-- 경쟁사 관리
CREATE TABLE competitors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    page_id VARCHAR(255) UNIQUE NOT NULL,
    page_url TEXT,
    industry VARCHAR(50),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 경쟁사-광고 연결
ALTER TABLE ads_raw ADD COLUMN competitor_id INT REFERENCES competitors(id);

-- 광고 컬렉션
CREATE TABLE collections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE collection_ads (
    collection_id INT REFERENCES collections(id),
    ad_id VARCHAR(255) REFERENCES ads_raw(ad_id),
    added_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (collection_id, ad_id)
);

-- 인사이트 캐시
CREATE TABLE insight_snapshots (
    id SERIAL PRIMARY KEY,
    insight_type VARCHAR(50), -- 'color_trend', 'layout_trend', etc.
    period VARCHAR(20), -- 'weekly', 'monthly'
    data JSONB,
    generated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 5. Implementation Priority

### 5.1 Effort vs Impact Matrix

```
                    High Impact
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
    │  P2: Reports      │  P0: Competitor   │
    │  (Medium Effort)  │  (Medium Effort)  │
    │                   │                   │
Low ├───────────────────┼───────────────────┤ High
Effort                  │                   Effort
    │                   │                   │
    │  P3: EU Fields    │  P1: Trends       │
    │  (Low Effort)     │  (High Effort)    │
    │                   │                   │
    └───────────────────┼───────────────────┘
                        │
                    Low Impact
```

### 5.2 Implementation Order

| 순서 | Feature | 예상 작업 | 의존성 |
|------|---------|----------|--------|
| 1 | Competitor Watchlist | Backend API + DB | - |
| 2 | Competitor Dashboard | Frontend UI | 1 |
| 3 | Color/Layout Trend Chart | Aggregation Query | 기존 분석 데이터 |
| 4 | Insight Dashboard | Frontend UI | 3 |
| 5 | Report Generator | Claude API | 3, 4 |
| 6 | Collection Feature | Full Stack | - |
| 7 | EU Targeting Fields | Collector 수정 | - |

---

## 6. Success Metrics

### 6.1 Product Metrics
| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| 수집 광고 수 | 1000+/월 | DB count |
| 분석 완료율 | 90%+ | analyzed/collected |
| 경쟁사 등록 수 | 20+/user | competitors table |
| 리포트 생성 수 | 10+/월 | reports table |

### 6.2 Technical Metrics
| 지표 | 목표 |
|------|------|
| API 응답 시간 | < 500ms |
| 스크린샷 캡처 성공률 | > 95% |
| AI 분석 정확도 | 사용자 피드백 기반 |

---

## 7. Timeline

```
Week 1-2: Phase 1 (Competitor Monitoring)
├── Competitor CRUD API
├── Competitor Dashboard UI
└── Auto-detection Scheduler

Week 3-4: Phase 2 (Insights)
├── Trend Aggregation Queries
├── Insight Dashboard UI
└── Chart Components

Week 5-6: Phase 2 cont. + Phase 3
├── Report Generator Service
├── Report UI
└── Collection Feature

Week 7-8: Phase 4 + Polish
├── EU Fields Integration
├── Performance Optimization
└── Bug Fixes & Testing
```

---

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Meta API Rate Limit | 수집 지연 | 요청 간격 조절, 캐싱 |
| 스크린샷 캡처 실패 | 이미지 없음 | 재시도 로직, 대체 이미지 |
| AI 분석 비용 | 운영비 증가 | 배치 처리, 캐싱 |
| 데이터 정확도 | 인사이트 신뢰도 | 사용자 피드백 루프 |

---

## 9. Out of Scope

다음 항목은 v2.0 범위에서 **제외**:

- ❌ 광고 성과 데이터 (CTR, 전환율) - API 미제공
- ❌ 상세 타겟팅 정보 (관심사, 행동) - API 미제공
- ❌ 광고 집행 기능 - 분석 플랫폼 목적
- ❌ 다중 사용자/팀 기능 - v3.0 고려
- ❌ 유료 결제 시스템 - v3.0 고려

---

## 10. Appendix

### A. API Reference
- [Meta Ad Library API](https://developers.facebook.com/docs/marketing-api/reference/ad-library/)
- [Claude API](https://docs.anthropic.com/claude/reference)

### B. Related Documents
- [v1.0 Design Doc](../02-design/features/meta-ad-analyzer.design.md)
- [v1.0 Analysis Report](../03-analysis/meta-ad-analyzer.analysis.md)
