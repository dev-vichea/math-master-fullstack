"""
Prometheus metrics for math OCR pipeline monitoring.

Tracks key performance indicators:
- Processing time by stage and endpoint
- Fallback rate (document pipeline → legacy)
- OCR confidence scores
- Region counts and types
- Error rates and types
"""

from __future__ import annotations

from typing import Any
from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps

# =============================================================================
# Pipeline Performance Metrics
# =============================================================================

# Processing time by stage
pipeline_stage_duration = Histogram(
    'ocr_pipeline_stage_duration_seconds',
    'Duration of each pipeline stage',
    ['stage'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Total pipeline processing time
pipeline_total_duration = Histogram(
    'ocr_pipeline_total_duration_seconds',
    'Total pipeline processing time',
    ['pipeline_type'],  # 'document' or 'legacy'
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# =============================================================================
# OCR Quality Metrics
# =============================================================================

# OCR confidence scores
ocr_confidence_score = Histogram(
    'ocr_confidence_score',
    'OCR confidence scores',
    ['ocr_engine'],  # 'tesseract', 'kiri', 'pix2tex'
    buckets=[0.0, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0]
)

# Processing status distribution
processing_status_total = Counter(
    'ocr_processing_status_total',
    'Count of processing statuses',
    ['status']  # 'success', 'partial', 'needs_review', 'failed'
)

# =============================================================================
# Document Structure Metrics
# =============================================================================

# Number of regions detected
regions_detected_total = Histogram(
    'ocr_regions_detected_total',
    'Number of text regions detected',
    buckets=[0, 1, 3, 5, 10, 20, 50]
)

# Regions by type
regions_by_type_total = Counter(
    'ocr_regions_by_type_total',
    'Count of regions by classification type',
    ['region_type']  # 'header', 'instruction', 'problem_content', etc.
)

# Problems detected
problems_detected_total = Histogram(
    'ocr_problems_detected_total',
    'Number of math problems detected per document',
    buckets=[0, 1, 3, 5, 10, 20, 50]
)

# =============================================================================
# Fallback and Error Metrics
# =============================================================================

# Fallback rate
pipeline_fallback_total = Counter(
    'ocr_pipeline_fallback_total',
    'Count of fallbacks from document to legacy pipeline',
    ['reason']  # 'no_text', 'no_problems', 'error', 'image_format'
)

# Error rate by type
pipeline_errors_total = Counter(
    'ocr_pipeline_errors_total',
    'Count of pipeline errors',
    ['error_type', 'stage']
)

# Warning count
pipeline_warnings_total = Counter(
    'ocr_pipeline_warnings_total',
    'Count of pipeline warnings',
    ['warning_type']
)

# =============================================================================
# API Endpoint Metrics
# =============================================================================

# Requests by endpoint
api_requests_total = Counter(
    'ocr_api_requests_total',
    'Total API requests',
    ['endpoint', 'status']  # endpoint: '/math/ocr', '/math/vision', etc.
)

# Request duration
api_request_duration = Histogram(
    'ocr_api_request_duration_seconds',
    'API request duration',
    ['endpoint'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# Image size
api_image_size_bytes = Histogram(
    'ocr_api_image_size_bytes',
    'Uploaded image size in bytes',
    buckets=[10_000, 50_000, 100_000, 500_000, 1_000_000, 5_000_000, 10_000_000]
)

# =============================================================================
# System Resource Metrics
# =============================================================================

# Active requests
active_requests_gauge = Gauge(
    'ocr_active_requests',
    'Number of currently processing requests'
)

# Cache metrics
cache_size_gauge = Gauge(
    'ocr_cache_size_entries',
    'Number of entries in OCR cache'
)

cache_hit_total = Counter(
    'ocr_cache_hit_total',
    'Number of cache hits'
)

cache_miss_total = Counter(
    'ocr_cache_miss_total',
    'Number of cache misses'
)

# =============================================================================
# System Information
# =============================================================================

system_info = Info(
    'ocr_system',
    'OCR system information'
)

# =============================================================================
# Helper Decorators
# =============================================================================

def track_stage_duration(stage_name: str):
    """Decorator to track duration of pipeline stages."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                pipeline_stage_duration.labels(stage=stage_name).observe(duration)
        return wrapper
    return decorator


def track_api_request(endpoint: str):
    """Decorator to track API request metrics."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            active_requests_gauge.inc()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                
                # Determine status from result
                status = 'success' if result.get('success') else 'error'
                api_requests_total.labels(endpoint=endpoint, status=status).inc()
                api_request_duration.labels(endpoint=endpoint).observe(duration)
                
                return result
            except Exception:
                duration = time.time() - start
                api_requests_total.labels(endpoint=endpoint, status='error').inc()
                api_request_duration.labels(endpoint=endpoint).observe(duration)
                raise
            finally:
                active_requests_gauge.dec()
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            active_requests_gauge.inc()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                
                status = 'success' if result.get('success') else 'error'
                api_requests_total.labels(endpoint=endpoint, status=status).inc()
                api_request_duration.labels(endpoint=endpoint).observe(duration)
                
                return result
            except Exception:
                duration = time.time() - start
                api_requests_total.labels(endpoint=endpoint, status='error').inc()
                api_request_duration.labels(endpoint=endpoint).observe(duration)
                raise
            finally:
                active_requests_gauge.dec()
        
        # Return appropriate wrapper based on whether function is async
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# =============================================================================
# Metric Recording Functions
# =============================================================================

def record_pipeline_result(
    pipeline_type: str,
    duration: float,
    status: str,
    regions_count: int = 0,
    problems_count: int = 0,
    confidence: float = 0.0,
    warnings: list[str] | None = None,
):
    """
    Record metrics from a pipeline execution.
    
    Args:
        pipeline_type: 'document' or 'legacy'
        duration: Total processing time in seconds
        status: 'success', 'partial', 'needs_review', or 'failed'
        regions_count: Number of text regions detected
        problems_count: Number of problems extracted
        confidence: Average OCR confidence
        warnings: List of warning messages
    """
    # Duration
    pipeline_total_duration.labels(pipeline_type=pipeline_type).observe(duration)
    
    # Status
    processing_status_total.labels(status=status).inc()
    
    # Regions and problems
    if regions_count > 0:
        regions_detected_total.observe(regions_count)
    if problems_count >= 0:
        problems_detected_total.observe(problems_count)
    
    # Confidence
    if confidence > 0:
        ocr_confidence_score.labels(ocr_engine='tesseract').observe(confidence)
    
    # Warnings
    if warnings:
        for warning in warnings:
            # Extract warning type from message
            warning_type = warning.split(':')[0] if ':' in warning else 'unknown'
            pipeline_warnings_total.labels(warning_type=warning_type).inc()


def record_fallback(reason: str):
    """Record a fallback from document to legacy pipeline."""
    pipeline_fallback_total.labels(reason=reason).inc()


def record_error(error_type: str, stage: str):
    """Record a pipeline error."""
    pipeline_errors_total.labels(error_type=error_type, stage=stage).inc()


def record_regions_by_type(regions_by_type: dict[str, int]):
    """Record count of regions by type."""
    for region_type, count in regions_by_type.items():
        for _ in range(count):
            regions_by_type_total.labels(region_type=region_type).inc()


def record_image_size(size_bytes: int):
    """Record uploaded image size."""
    api_image_size_bytes.observe(size_bytes)


def record_cache_hit():
    """Record cache hit."""
    cache_hit_total.inc()


def record_cache_miss():
    """Record cache miss."""
    cache_miss_total.inc()


def update_cache_size(size: int):
    """Update current cache size."""
    cache_size_gauge.set(size)


def set_system_info(info: dict[str, Any]):
    """Set system information metrics."""
    system_info.info(info)


# =============================================================================
# Initialization
# =============================================================================

def initialize_metrics():
    """Initialize system metrics on startup."""
    import platform
    try:
        import pytesseract
        tesseract_version = pytesseract.get_tesseract_version()
    except Exception:
        tesseract_version = "not_available"
    
    set_system_info({
        'python_version': platform.python_version(),
        'platform': platform.system(),
        'tesseract_version': str(tesseract_version),
        'pipeline_version': 'phase_1',
    })
