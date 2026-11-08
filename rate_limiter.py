# -*- coding: utf-8 -*-
"""
JoinRateLimiter: منظم معدل الانضمام للمجموعات والقنوات لمنع قيود وحظر تيليجرام
================================================================================
يتحكم بمعدل الانضمام تلقائياً مع فواصل زمنية متغيرة وحدود للدقيقة والساعة.
"""
import os
import time
import random
import logging
import asyncio
from collections import deque

logger = logging.getLogger("JoinRateLimiter")

class JoinRateLimiter:
    def __init__(self, max_per_minute=None, max_per_hour=None, min_delay=None, max_delay=None):
        self.max_per_minute = max_per_minute if max_per_minute is not None else int(os.getenv('JOIN_MAX_PER_MINUTE', 5))
        self.max_per_hour = max_per_hour if max_per_hour is not None else int(os.getenv('JOIN_MAX_PER_HOUR', 30))
        self.min_delay = min_delay if min_delay is not None else float(os.getenv('JOIN_MIN_DELAY_SECONDS', 5))
        self.max_delay = max_delay if max_delay is not None else float(os.getenv('JOIN_MAX_DELAY_SECONDS', 10))

        self.minute_window = deque()
        self.hour_window = deque()

    def _clean(self, now):
        while self.minute_window and (now - self.minute_window[0]) > 60:
            self.minute_window.popleft()
        while self.hour_window and (now - self.hour_window[0]) > 3600:
            self.hour_window.popleft()

    def acquire_sync(self):
        """حجب متزامن للالتزام بالحدود الزمنية ومعدل الانضمام"""
        now = time.time()
        self._clean(now)

        # فحص حد الدقيقة (الافتراضي 5 انضمامات / دقيقة)
        while len(self.minute_window) >= self.max_per_minute:
            sleep_time = max(1.0, 60.0 - (now - self.minute_window[0]) + 0.5)
            logger.info(f"⏳ JoinRateLimiter: بلوغ حد الدقيقة ({self.max_per_minute}/دقيقة)، انتظار {sleep_time:.1f}ثانية")
            time.sleep(sleep_time)
            now = time.time()
            self._clean(now)

        # فحص حد الساعة (الافتراضي 30 انضمام / ساعة)
        while len(self.hour_window) >= self.max_per_hour:
            sleep_time = max(5.0, 3600.0 - (now - self.hour_window[0]) + 1.0)
            logger.info(f"⏳ JoinRateLimiter: بلوغ حد الساعة ({self.max_per_hour}/ساعة)، انتظار {sleep_time:.1f}ثانية")
            time.sleep(sleep_time)
            now = time.time()
            self._clean(now)

        # تأخير عشوائي بين min_delay و max_delay (الافتراضي 5-10 ثوانٍ)
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.debug(f"JoinRateLimiter: تأخير أمان عشوائي {delay:.2f} ثانية قبل الانضمام")
        time.sleep(delay)

        record_now = time.time()
        self.minute_window.append(record_now)
        self.hour_window.append(record_now)

    async def acquire(self):
        """حجب غير متزامن Coroutine للالتزام بالحدود الزمنية"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.acquire_sync)

# مثيل عالمي للاستخدام عبر خيوط التطبيق
join_limiter = JoinRateLimiter()
