"""
OCR result caching for improved performance.

Caches OCR results using image content hash to avoid reprocessing identical images.
Supports:
- In-memory LRU cache
- Optional persistent cache (file-based or Redis)
- Configurable TTL and cache size
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from app.core.logging import get_logger
from app.ocr.engines.base import MathVisionEngine, VisionResult

logger = get_logger("app.ocr.extraction.cache")


class CachedOCREngine(MathVisionEngine):
    """
    OCR engine wrapper with caching support.

    Caches OCR results by image hash to avoid redundant processing.
    """

    def __init__(
        self,
        engine: MathVisionEngine,
        cache_size: int = 1000,
        ttl_seconds: int | None = 3600,
        persistent_cache_dir: Path | None = None,
    ):
        """
        Initialize cached OCR engine.

        Args:
            engine: Underlying OCR engine to wrap
            cache_size: Maximum number of results to cache in memory
            ttl_seconds: Time-to-live for cache entries (None = no expiration)
            persistent_cache_dir: Optional directory for persistent file cache
        """
        self.engine = engine
        self.cache_size = cache_size
        self.ttl_seconds = ttl_seconds
        self.persistent_cache_dir = persistent_cache_dir

        # In-memory cache: {image_hash: (result, timestamp)}
        self._memory_cache: dict[str, tuple[VisionResult, float]] = {}
        self._cache_hits = 0
        self._cache_misses = 0

        if persistent_cache_dir:
            persistent_cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Persistent cache enabled at: {persistent_cache_dir}")

    def detect(self, image_bytes: bytes) -> VisionResult:
        """
        Detect text with caching.

        Checks cache first, runs OCR only if cache miss.
        """
        # Calculate image hash
        image_hash = self._hash_image(image_bytes)

        # Check memory cache
        cached_result = self._get_from_memory_cache(image_hash)
        if cached_result:
            self._cache_hits += 1
            logger.debug(f"Memory cache HIT for image {image_hash[:8]}")
            return cached_result

        # Check persistent cache if enabled
        if self.persistent_cache_dir:
            cached_result = self._get_from_persistent_cache(image_hash)
            if cached_result:
                self._cache_hits += 1
                logger.debug(f"Persistent cache HIT for image {image_hash[:8]}")
                # Also store in memory cache
                self._put_to_memory_cache(image_hash, cached_result)
                return cached_result

        # Cache miss - run OCR
        self._cache_misses += 1
        logger.debug(f"Cache MISS for image {image_hash[:8]}, running OCR")

        result = self.engine.detect(image_bytes)

        # Cache the result
        self._put_to_memory_cache(image_hash, result)
        if self.persistent_cache_dir:
            self._put_to_persistent_cache(image_hash, result)

        return result

    def _hash_image(self, image_bytes: bytes) -> str:
        """Calculate SHA-256 hash of image bytes."""
        return hashlib.sha256(image_bytes).hexdigest()

    def _get_from_memory_cache(self, image_hash: str) -> VisionResult | None:
        """Retrieve result from memory cache if not expired."""
        if image_hash not in self._memory_cache:
            return None

        result, timestamp = self._memory_cache[image_hash]

        # Check TTL
        if self.ttl_seconds and (time.time() - timestamp > self.ttl_seconds):
            del self._memory_cache[image_hash]
            logger.debug(f"Cache entry {image_hash[:8]} expired")
            return None

        return result

    def _put_to_memory_cache(self, image_hash: str, result: VisionResult) -> None:
        """Store result in memory cache with LRU eviction."""
        # Evict oldest entries if cache is full
        if len(self._memory_cache) >= self.cache_size:
            # Simple FIFO eviction (could use OrderedDict for true LRU)
            oldest_key = next(iter(self._memory_cache))
            del self._memory_cache[oldest_key]
            logger.debug(f"Evicted cache entry {oldest_key[:8]}")

        self._memory_cache[image_hash] = (result, time.time())

    def _get_from_persistent_cache(self, image_hash: str) -> VisionResult | None:
        """Retrieve result from persistent file cache."""
        if not self.persistent_cache_dir:
            return None

        cache_file = self.persistent_cache_dir / f"{image_hash}.json"

        if not cache_file.exists():
            return None

        try:
            cache_data = json.loads(cache_file.read_text(encoding="utf-8"))

            # Check TTL
            if self.ttl_seconds:
                cached_time = cache_data.get("timestamp", 0)
                if time.time() - cached_time > self.ttl_seconds:
                    cache_file.unlink()
                    logger.debug(f"Persistent cache entry {image_hash[:8]} expired")
                    return None

            # Reconstruct VisionResult
            result_data = cache_data["result"]
            return VisionResult(
                detected_text=result_data.get("detected_text"),
                confidence=result_data.get("confidence", 0.0),
                error_message=result_data.get("error_message"),
                exercise_metadata=result_data.get("exercise_metadata"),
            )

        except Exception as e:
            logger.warning(f"Failed to read persistent cache {image_hash[:8]}: {e}")
            return None

    def _put_to_persistent_cache(self, image_hash: str, result: VisionResult) -> None:
        """Store result in persistent file cache."""
        if not self.persistent_cache_dir:
            return

        cache_file = self.persistent_cache_dir / f"{image_hash}.json"

        try:
            cache_data = {
                "timestamp": time.time(),
                "result": {
                    "detected_text": result.detected_text,
                    "confidence": result.confidence,
                    "error_message": result.error_message,
                    "exercise_metadata": result.exercise_metadata,
                },
            }

            cache_file.write_text(json.dumps(cache_data, ensure_ascii=False), encoding="utf-8")

        except Exception as e:
            logger.warning(f"Failed to write persistent cache {image_hash[:8]}: {e}")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total_requests if total_requests > 0 else 0.0

        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "memory_cache_size": len(self._memory_cache),
            "memory_cache_capacity": self.cache_size,
        }

    def clear_cache(self) -> None:
        """Clear all cached results."""
        self._memory_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0

        # Clear persistent cache if enabled
        if self.persistent_cache_dir and self.persistent_cache_dir.exists():
            for cache_file in self.persistent_cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete cache file {cache_file}: {e}")

        logger.info("Cache cleared")


def create_cached_engine(
    engine: MathVisionEngine,
    cache_size: int = 1000,
    ttl_seconds: int | None = 3600,
    persistent: bool = False,
) -> CachedOCREngine:
    """
    Wrap an OCR engine with caching.

    Args:
        engine: OCR engine to cache
        cache_size: Maximum cache size
        ttl_seconds: Cache entry TTL (None = no expiration)
        persistent: Enable persistent file cache

    Returns:
        Cached OCR engine

    Example:
        >>> from app.ocr.factory import create_vision_engine
        >>> engine = create_vision_engine("tesseract")
        >>> cached = create_cached_engine(engine, cache_size=500, ttl_seconds=1800)
        >>> result = cached.detect(image_bytes)
        >>> stats = cached.get_cache_stats()
    """
    persistent_dir = None
    if persistent:
        from pathlib import Path

        persistent_dir = Path(".cache/ocr")

    return CachedOCREngine(
        engine=engine,
        cache_size=cache_size,
        ttl_seconds=ttl_seconds,
        persistent_cache_dir=persistent_dir,
    )
