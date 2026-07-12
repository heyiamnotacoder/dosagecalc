"""
Bounded in-process drug-PK dossier cache for multi-user single-dyno deploys (e.g. Render).

Shared by all requests on the worker. LRU + max payload bytes + TTL.
Never cache unavailable/null dossiers. Multi-dyno needs Redis later.
"""

from __future__ import annotations

import json
import os
import threading
import time
from collections import OrderedDict
from typing import Any, Optional


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


class PkCache:
    def __init__(
        self,
        max_entries: Optional[int] = None,
        max_bytes: Optional[int] = None,
        ttl_seconds: Optional[int] = None,
    ):
        self.max_entries = max_entries if max_entries is not None else _env_int("PK_CACHE_MAX_ENTRIES", 80)
        self.max_bytes = max_bytes if max_bytes is not None else _env_int("PK_CACHE_MAX_BYTES", 2_000_000)
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else _env_int("PK_CACHE_TTL_SECONDS", 86400)
        self._lock = threading.Lock()
        self._data: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._bytes = 0

    @staticmethod
    def make_key(drug: str, indication: str | None = None) -> str:
        d = (drug or "").strip().lower()
        ind = (indication or "").strip().lower()
        return f"{d}|{ind}"

    def stats(self) -> dict:
        with self._lock:
            return {
                "entries": len(self._data),
                "bytes": self._bytes,
                "max_entries": self.max_entries,
                "max_bytes": self.max_bytes,
                "ttl_seconds": self.ttl_seconds,
            }

    def get(self, drug: str, indication: str | None = None) -> Optional[dict]:
        key = self.make_key(drug, indication)
        now = time.time()
        with self._lock:
            item = self._data.get(key)
            if not item:
                return None
            if now - item["cached_at"] > self.ttl_seconds:
                self._evict_key(key)
                return None
            self._data.move_to_end(key)
            return {
                "dossier": item["dossier"],
                "source_mode": item.get("source_mode", "live"),
                "cached": True,
                "cached_at": item["cached_at"],
            }

    def set(self, drug: str, indication: str | None, dossier: dict, source_mode: str = "live") -> bool:
        """Store live dossier only. Returns False if rejected."""
        if source_mode != "live" or not dossier:
            return False
        # reject empty/null core PK
        if dossier.get("cl_adult_l_h") is None and dossier.get("vd_adult_l") is None:
            return False
        key = self.make_key(drug, indication)
        try:
            raw = json.dumps(dossier, default=str)
        except (TypeError, ValueError):
            return False
        size = len(raw.encode("utf-8"))
        if size > self.max_bytes:
            return False
        with self._lock:
            if key in self._data:
                self._evict_key(key)
            while (
                len(self._data) >= self.max_entries
                or self._bytes + size > self.max_bytes
            ) and self._data:
                oldest = next(iter(self._data))
                self._evict_key(oldest)
            if self._bytes + size > self.max_bytes:
                return False
            self._data[key] = {
                "dossier": dossier,
                "source_mode": source_mode,
                "cached_at": time.time(),
                "size": size,
            }
            self._bytes += size
            return True

    def _evict_key(self, key: str) -> None:
        item = self._data.pop(key, None)
        if item:
            self._bytes = max(0, self._bytes - int(item.get("size", 0)))

    def clear(self) -> None:
        with self._lock:
            self._data.clear()
            self._bytes = 0


# Process-wide shared pool
CACHE = PkCache()
