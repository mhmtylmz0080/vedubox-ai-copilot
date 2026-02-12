"""
Vedubox AI Copilot - Simple AI Service Mock (No external calls)

This module simulates how an AI layer might work inside an LMS:
- Role-based request handling (Admin / Instructor / Learner)
- Basic input validation & policy checks
- Stubbed "LLM response" generation
- Structured output for UI rendering

NOTE: This is a mock for portfolio/demo purposes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
import re
import time


class Role(str, Enum):
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    LEARNER = "learner"


class UseCase(str, Enum):
    QUIZ_GENERATION = "quiz_generation"
    SUMMARY = "summary"
    ENGAGEMENT_ANALYSIS = "engagement_analysis"
    REMINDER_SUGGESTION = "reminder_suggestion"
    PLATFORM_GUIDANCE = "platform_guidance"


@dataclass
class AIRequest:
    role: Role
    use_case: UseCase
    user_message: str
    context: Dict[str, Any]  # course/module/content/metrics etc.
    locale: str = "tr-TR"


@dataclass
class AIResponse:
    ok: bool
    message: str
    actions: List[Dict[str, Any]]
    metadata: Dict[str, Any]


# ---------------------------
# Safety / Policy (Mock)
# ---------------------------

INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"reveal\s+system\s+prompt",
    r"show\s+hidden\s+instructions",
    r"bypass\s+policy",
    r"act\s+as\s+admin",
]

PII_PATTERNS = [
    (r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[EMAIL]"),
    (r"\b(\+?\d{1,3})?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}\b", "[PHONE]"),
]


def mask_pii(text: str) -> str:
    masked = text
    for pattern, repl in PII_PATTERNS:
        masked = re.sub(pattern, repl, masked, flags=re.IGNORECASE)
    return masked


def detect_prompt_injection(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in INJECTION_PATTERNS)


def enforce_role_policies(req: AIRequest) -> Optional[str]:
    """
    Return an error message if request violates role policy, else None.
    """
    # Learner cannot ask for exam answers directly (example policy)
    if req.role == Role.LEARNER:
        if "cevap" in req.user_message.lower() and "sınav" in req.user_message.lower():
            return "Güvenlik nedeniyle sınav cevaplarını doğrudan veremem. İstersen yanlışlarını açıklayıp konu özetini paylaşabilirim."
    return None


# ---------------------------
# Mock "LLM"
# ---------------------------

def mock_llm_generate(req: AIRequest) -> str:
    """
    Fake LLM output based on use-case.
    """
    if req.use_case == UseCase.SUMMARY:
        return "Özet: Bu içerik, temel kavramları ve uygulama adımlarını açıklar. Ana noktalar: (1) Tanım, (2) Süreç, (3) Örnekler."
    if req.use_case == UseCase.QUIZ_GENERATION:
        return "3 soru ürettim: 1) ... 2) ... 3) ..."
    if req.use_case == UseCase.ENGAGEMENT_ANALYSIS:
        return "Katılım düşüşü tespit edildi. Modül 3'te terk oranı yüksek. Öneri: Modülü böl, mikro quiz ekle, kısa hatırlatma gönder."
    if req.use_case == UseCase.REMINDER_SUGGESTION:
        return "Hatırlatma önerisi: 'Merhaba! Bugün tamamlamanız gereken eğitimler var. 10 dakikada ilerleyebilirsiniz — şimdi başlamak ister misiniz?'"
    return "Vedubox AI: Bu işlem için sizi doğru ekrana yönlendirebilirim. Hangi adımı yapmak istiyorsunuz?"


def suggested_actions(req: AIRequest) -> List[Dict[str, Any]]:
    """
    Return UI actions (buttons) that backend could execute after user confirmation.
    """
    actions: List[Dict[str, Any]] = []

    if req.role == Role.ADMIN and req.use_case == UseCase.PLATFORM_GUIDANCE:
        actions.append({"type": "NAVIGATE", "label": "Eğitim Oluştur", "target": "/admin/course/create"})
        actions.append({"type": "NAVIGATE", "label": "Raporlar", "target": "/admin/reports"})
    if req.role == Role.INSTRUCTOR and req.use_case == UseCase.QUIZ_GENERATION:
        actions.append({"type": "OPEN_MODAL", "label": "Quiz Sorularını Gör", "target": "quiz_preview"})
    if req.role == Role.INSTRUCTOR and req.use_case == UseCase.ENGAGEMENT_ANALYSIS:
        actions.append({"type": "OPEN_MODAL", "label": "Hatırlatma Mesajı Oluştur", "target": "reminder_builder"})
    if req.role == Role.LEARNER and req.use_case in (UseCase.SUMMARY, UseCase.PLATFORM_GUIDANCE):
        actions.append({"type": "NAVIGATE", "label": "Bugünkü Yapılacaklar", "target": "/learner/today"})

    return actions


# ---------------------------
# Main Handler
# ---------------------------

def handle_ai_request(req: AIRequest) -> AIResponse:
    start = time.time()

    # 1) Basic sanitization
    user_message = mask_pii(req.user_message)

    # 2) Injection detection
    if detect_prompt_injection(user_message):
        return AIResponse(
            ok=False,
            message="Güvenlik nedeniyle bu isteği işleyemiyorum. Lütfen talebinizi normal bir şekilde yeniden yazın.",
            actions=[],
            metadata={"reason": "prompt_injection_detected"},
        )

    # 3) Role policy
    role_err = enforce_role_policies(req)
    if role_err:
        return AIResponse(
            ok=True,
            message=role_err,
            actions=[],
            metadata={"policy": "role_restriction"},
        )

    # 4) Generate response (mock)
    result_text = mock_llm_generate(req)

    # 5) Attach suggested actions
    actions = suggested_actions(req)

    latency_ms = int((time.time() - start) * 1000)

    return AIResponse(
        ok=True,
        message=result_text,
        actions=actions,
        metadata={
            "role": req.role.value,
            "use_case": req.use_case.value,
            "latency_ms": latency_ms,
            "pii_masked": user_message != req.user_message,
        },
    )
