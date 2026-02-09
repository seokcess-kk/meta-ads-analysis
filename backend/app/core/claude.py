import base64
import json
import logging
from typing import Any, Dict, Optional

import anthropic
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Image Analysis Prompt
IMAGE_ANALYSIS_PROMPT = """# 광고 이미지 분석 요청

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

주의: JSON 외 다른 텍스트 없이 순수 JSON만 응답해주세요."""

# Copy Analysis Prompt Template
COPY_ANALYSIS_PROMPT = """# 광고 카피 분석 요청

다음 광고 카피를 분석하여 JSON 형식으로 응답해주세요.

## 광고 카피
---
{body}
---
{title}
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
{{
  "structure": {{
    "headline": "목동 입시생 83%가 선택한 이유",
    "headline_length": 16,
    "body": "소규모 맞춤 관리로 평균 2등급 상승",
    "cta": "상담 신청하기",
    "core_message": "social_proof"
  }},
  "numbers": [
    {{"value": 83, "unit": "%", "context": "선택률"}},
    {{"value": 2, "unit": "등급", "context": "성적 향상"}}
  ],
  "offer": {{
    "discount_info": null,
    "free_benefit": "무료 학습 진단",
    "social_proof": "83% 선택",
    "urgency": null,
    "differentiation": "소규모 맞춤 관리"
  }},
  "tone": {{
    "formality": "formal",
    "emotion": "rational",
    "style": "stable"
  }},
  "target_audience": "고등학생",
  "keywords": ["선택", "소규모", "맞춤", "관리", "등급", "상승"],
  "regions": ["목동"]
}}
```

주의: JSON 외 다른 텍스트 없이 순수 JSON만 응답해주세요."""


class ClaudeClient:
    """Claude API client for image and text analysis."""

    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"

    async def analyze_image(self, image_url: str) -> Optional[Dict[str, Any]]:
        """
        Analyze ad image using Claude Vision.

        Args:
            image_url: URL of the image to analyze

        Returns:
            Parsed analysis result or None if failed
        """
        try:
            # Download image
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.get(image_url)
                response.raise_for_status()
                image_data = response.content

            # Encode to base64
            image_base64 = base64.standard_b64encode(image_data).decode("utf-8")

            # Determine media type
            content_type = response.headers.get("content-type", "image/png")
            media_type = content_type.split(";")[0].strip()

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": IMAGE_ANALYSIS_PROMPT,
                            },
                        ],
                    }
                ],
            )

            # Parse response
            response_text = message.content[0].text
            return self._parse_json_response(response_text)

        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return None

    async def analyze_copy(
        self, body: Optional[str], title: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze ad copy text using Claude.

        Args:
            body: Ad creative body text
            title: Ad creative link title

        Returns:
            Parsed analysis result or None if failed
        """
        if not body and not title:
            return None

        try:
            prompt = COPY_ANALYSIS_PROMPT.format(
                body=body or "(없음)",
                title=title or "(없음)",
            )

            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            response_text = message.content[0].text
            return self._parse_json_response(response_text)

        except Exception as e:
            logger.error(f"Error analyzing copy: {e}")
            return None

    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from Claude response."""
        try:
            # Try to find JSON in the response
            text = text.strip()

            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]

            text = text.strip()

            return json.loads(text)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {text}")
            return None


# Singleton instance
claude_client = ClaudeClient()
