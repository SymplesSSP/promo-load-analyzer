"""Data models for Promo Load Analyzer."""

from .page_detection import PageDetectionResult
from .promotion import AutoCartRule, PromotionData, StrikedPriceData

__all__ = [
    "PageDetectionResult",
    "PromotionData",
    "StrikedPriceData",
    "AutoCartRule",
]
