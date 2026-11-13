"""
web/ratelimit.py - Quản lý giới hạn lượt sử dụng và số tiến trình đồng thời.
Bao gồm 2 bộ đếm độc lập:
1. Bộ đếm kiểm tra SEO (DAILY_LIMIT, MAX_PARALLEL_CHECKS)
2. Bộ đếm gọi AI (AI_DAILY_LIMIT, MAX_PARALLEL_AI)
"""

import os
import threading
import time
from typing import Dict, Tuple


class RateLimiter:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_date = time.strftime("%Y-%m-%d")
        self.daily_seo_counts: Dict[str, int] = {}
        self.daily_ai_counts: Dict[str, int] = {}
        self.active_seo_slots = 0
        self.active_ai_slots = 0

    def _reset_if_new_day(self):
        today = time.strftime("%Y-%m-%d")
        if today != self.current_date:
            self.current_date = today
            self.daily_seo_counts.clear()
            self.daily_ai_counts.clear()

    # --- SEO CHECKS ---
    def check_seo_limit(self, ip: str) -> Tuple[bool, str, int]:
        daily_limit = int(os.environ.get("DAILY_LIMIT", "5"))
        with self.lock:
            self._reset_if_new_day()
            if daily_limit <= 0:
                return True, "", 9999

            used = self.daily_seo_counts.get(ip, 0)
            remaining = max(0, daily_limit - used)
            if used >= daily_limit:
                return (
                    False,
                    f"Hôm nay bạn đã dùng hết {daily_limit} lượt kiểm tra SEO miễn phí trên máy chủ này.",
                    0,
                )
            return True, "", remaining

    def acquire_seo_slot(self) -> Tuple[bool, str]:
        max_parallel = int(os.environ.get("MAX_PARALLEL_CHECKS", "2"))
        with self.lock:
            if max_parallel > 0 and self.active_seo_slots >= max_parallel:
                return False, "Đang đông người dùng, thử lại sau 1 phút."
            self.active_seo_slots += 1
            return True, ""

    def release_seo_slot(self):
        with self.lock:
            if self.active_seo_slots > 0:
                self.active_seo_slots -= 1

    def increment_seo_count(self, ip: str):
        with self.lock:
            self._reset_if_new_day()
            self.daily_seo_counts[ip] = self.daily_seo_counts.get(ip, 0) + 1

    # --- AI CALLS ---
    def check_ai_limit(self, ip: str) -> Tuple[bool, str, int]:
        ai_daily_limit = int(os.environ.get("AI_DAILY_LIMIT", "20"))
        with self.lock:
            self._reset_if_new_day()
            if ai_daily_limit <= 0:
                return True, "", 9999

            used = self.daily_ai_counts.get(ip, 0)
            remaining = max(0, ai_daily_limit - used)
            if used >= ai_daily_limit:
                return (
                    False,
                    "Hôm nay bạn đã dùng hết lượt AI miễn phí trên máy chủ này.",
                    0,
                )
            return True, "", remaining

    def acquire_ai_slot(self) -> Tuple[bool, str]:
        max_parallel_ai = int(os.environ.get("MAX_PARALLEL_AI", "2"))
        with self.lock:
            if max_parallel_ai > 0 and self.active_ai_slots >= max_parallel_ai:
                return False, "Đang đông người dùng gọi AI, thử lại sau 1 phút."
            self.active_ai_slots += 1
            return True, ""

    def release_ai_slot(self):
        with self.lock:
            if self.active_ai_slots > 0:
                self.active_ai_slots -= 1

    def increment_ai_count(self, ip: str):
        with self.lock:
            self._reset_if_new_day()
            self.daily_ai_counts[ip] = self.daily_ai_counts.get(ip, 0) + 1

    def get_remaining(self, ip: str) -> Dict[str, int]:
        with self.lock:
            self._reset_if_new_day()
            daily_limit = int(os.environ.get("DAILY_LIMIT", "5"))
            ai_daily_limit = int(os.environ.get("AI_DAILY_LIMIT", "20"))

            seo_used = self.daily_seo_counts.get(ip, 0)
            ai_used = self.daily_ai_counts.get(ip, 0)

            return {
                "seo_remaining": 9999 if daily_limit <= 0 else max(0, daily_limit - seo_used),
                "ai_remaining": 9999 if ai_daily_limit <= 0 else max(0, ai_daily_limit - ai_used),
            }


limiter = RateLimiter()
