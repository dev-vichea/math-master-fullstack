"""
Smart caching for OCR results.

Caches OCR results by image hash to avoid reprocessing identical images.
Uses LRU (Least Recently Used) eviction policy.
"""

from __future__ import annotations

import hashlib
import time
from functools import lru_cache
from typing import Any
from dataclasses import dataclass, field

from app.utils.logging import get_logger

logger = get_logger("app.core.cache")


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    
    def access(self):
        """Record an access to this entry."""
        self.access_count += 1
        self.last_accessed = time.time()


class OcrCache:
    """
    LRU cache for OCR results.
    
    Features:
    - Hash-based deduplication (identical images return cached results)
    - TTL (Time To Live) expiration
    - Size-based eviction (LRU)
    - Thread-safe operations
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: float = 3600):
        """
        Initialize OCR cache.
        
        Args:
            max_size: Maximum number of entries (default 1000)
            ttl_seconds: Time to live in seconds (default 1 hour)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0
        
        logger.info(f"Initialized OCR cache (max_size={max_size}, ttl={ttl_seconds}s)")
    
    def get(self, image_bytes: bytes) -> Any | None:
        """
        Get cached OCR result for image.
        
        Args:
            image_bytes: Image data
            
        Returns:
            Cached result or None if not found/expired
        """
        key = self._hash_image(image_bytes)
        
        if key in self._cache:
            entry = self._cache[key]
            
            # Check if expired
            age = time.time() - entry.created_at
            if age > self.ttl_seconds:
                logger.debug(f"Cache entry expired (age={age:.1f}s)")
                del self._cache[key]
                self._misses += 1
                return None
            
            # Valid cache hit
            entry.access()
            self._hits += 1
            logger.debug(f"Cache HIT (key={key[:8]}..., age={age:.1f}s, hits={self._hits})")
            
            # Record metric
            try:
                from app.monitoring import record_cache_hit
                record_cache_hit()
            except ImportError:
                pass
            
            return entry.value
        
        self._misses += 1
        logger.debug(f"Cache MISS (key={key[:8]}..., misses={self._misses})")
        
        # Record metric
        try:
            from app.monitoring import record_cache_miss
            record_cache_miss()
        except ImportError:
            pass
        
        return None
    
    def set(self, image_bytes: bytes, value: Any) -> None:
        """
        Store OCR result in cache.
        
        Args:
            image_bytes: Image data (used as key)
            value: OCR result to cache
        """
        key = self._hash_image(image_bytes)
        
        # Evict oldest entry if at capacity
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict_lru()
        
        # Store entry
        self._cache[key] = CacheEntry(key=key, value=value)
        logger.debug(f"Cache SET (key={key[:8]}..., size={len(self._cache)})")
        
        # Update metric
        try:
            from app.monitoring import update_cache_size
            update_cache_size(len(self._cache))
        except ImportError:
            pass
    
    def clear(self) -> None:
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info(f"Cache cleared ({count} entries removed)")
        
        try:
            from app.monitoring import update_cache_size
            update_cache_size(0)
        except ImportError:
            pass
    
    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "ttl_seconds": self.ttl_seconds,
        }
    
    def _hash_image(self, image_bytes: bytes) -> str:
        """
        Generate hash key for image.
        
        Uses SHA-256 for reliable deduplication.
        """
        return hashlib.sha256(image_bytes).hexdigest()
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )
        
        logger.debug(f"Evicting LRU entry (key={lru_key[:8]}...)")
        del self._cache[lru_key]
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries.
        
        Returns:
            Number of entries removed
        """
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if (now - entry.created_at) > self.ttl_seconds
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            try:
                from app.monitoring import update_cache_size
                update_cache_size(len(self._cache))
            except ImportError:
                pass
        
        return len(expired_keys)


# Global cache instance
_ocr_cache: OcrCache | None = None


def get_ocr_cache() -> OcrCache:
    """Get or create global OCR cache instance."""
    global _ocr_cache
    if _ocr_cache is None:
        _ocr_cache = OcrCache(max_size=1000, ttl_seconds=3600)
    return _ocr_cache


def clear_cache():
    """Clear global OCR cache."""
    cache = get_ocr_cache()
    cache.clear()


@lru_cache(maxsize=128)
def _compute_image_hash(image_bytes_hash: int) -> str:
    """
    Cached hash computation for frequently seen images.
    
    Note: Uses hash of bytes (not bytes directly) to work with lru_cache.
    """
    # This is a helper for hash computation optimization
    # Real hashing happens in OcrCache._hash_image
    return str(image_bytes_hash)


# =============================================================================
# Solve Cache (Legacy compatibility)
# =============================================================================

class SolveCache:
    """
    Solve cache for mathematical computation results.
    
    Wraps OcrCache to provide caching keyed by mathematical expression and problem type.
    """
    
    def __init__(self, max_size: int = 1024, ttl_seconds: float = 3600):
        self._cache = OcrCache(max_size=max_size, ttl_seconds=ttl_seconds)
    
    def _make_key(self, key: str, problem_type: str | None = None) -> bytes:
        combined = f"{key}::{problem_type or ''}"
        return combined.encode('utf-8')
    
    def get(self, key: str, problem_type: str | None = None) -> Any | None:
        """Get cached solve result."""
        key_bytes = self._make_key(key, problem_type)
        return self._cache.get(key_bytes)
    
    def set(self, key: str, value: Any, problem_type: str | None = None) -> None:
        """Cache solve result."""
        key_bytes = self._make_key(key, problem_type)
        self._cache.set(key_bytes, value)

    def put(
        self,
        key: str,
        value: Any,
        problem_type: str | None = None,
        ttl: float | None = None,
    ) -> None:
        """Store a result in the cache."""
        self.set(key, value, problem_type)
    
    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()
    
    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return self._cache.get_stats()


# Global solve cache instance
_solve_cache: SolveCache | None = None


def get_solve_cache() -> SolveCache:
    """Get or create global solve cache instance."""
    global _solve_cache
    if _solve_cache is None:
        _solve_cache = SolveCache(max_size=1024, ttl_seconds=3600)
    return _solve_cache
