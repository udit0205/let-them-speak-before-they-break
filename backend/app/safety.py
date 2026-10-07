import re
from dataclasses import dataclass


@dataclass
class SafetyAssessment:
    immediate_danger: bool
    level: str
    matched: list[str]


# This layer is intentionally separate from the LLM. It is a coarse, deterministic
# first-pass signal, not a clinical risk assessment and not a replacement for human review.
HIGH_RISK_PATTERNS = [
    r"\bi\s*(want|wanna|plan|intend|am going|going)\s*to\s*(kill|end)\s*(myself|my life)\b",
    r"\bi\s*(will|am going to|am about to)\s*suicide\b",
    r"\bsuicide\s*(tonight|today|now|in a few minutes)\b",
    r"\bkill myself\b",
    r"\bend my life\b",
    r"\bself[- ]?harm\s*(now|tonight|today)\b",
    r"\bi\s*have\s*(a|the)\s*(gun|knife|weapon)\s*(and|so)\b",
    r"\bi\s*(am|i'm)\s*about to\s*(hurt|kill)\b",
    r"\bgoing to hurt (him|her|them|someone)\b",
]

MEDIUM_RISK_PATTERNS = [
    r"\b( suicidal|suicide|kill myself|self[- ]?harm)\b",
    r"\bi\s*(don't want to live|dont want to live)\b",
    r"\bno reason to live\b",
    r"\bwant to disappear forever\b",
    r"\bhurt myself\b",
]


def assess(text: str) -> SafetyAssessment:
    normalized = " ".join(text.lower().strip().split())
    high = [p for p in HIGH_RISK_PATTERNS if re.search(p, normalized)]
    if high:
        return SafetyAssessment(True, "high", high)
    medium = [p for p in MEDIUM_RISK_PATTERNS if re.search(p, normalized)]
    if medium:
        return SafetyAssessment(False, "elevated", medium)
    return SafetyAssessment(False, "none", [])


def safety_response(emergency_number: str, mental_health_helpline: str) -> str:
    return (
        "I’m really glad you said that here. I’m an AI, so I can’t keep you safe by myself. "
        "If you may hurt yourself or someone else right now, please move away from anything you could use to cause harm "
        "and get a real person with you. In India, you can call emergency services at "
        f"{emergency_number} now. You can also call Tele-MANAS at {mental_health_helpline} for mental-health support. "
        "If calling feels hard, send someone you trust a simple message: ‘I’m not safe alone right now. Please stay with me.’ "
        "Stay with me here too, and tell me only this: are you in immediate danger right now?"
    )
