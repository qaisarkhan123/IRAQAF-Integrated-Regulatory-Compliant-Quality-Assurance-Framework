"""
Performance monitoring and profiling utilities for IRAQAF dashboard.
"""

import time
import functools
import logging
from typing import Callable, Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict
import streamlit as st

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Track performance metrics across the dashboard."""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.start_times: Dict[str, float] = {}
        self.warnings: List[Dict[str, Any]] = []

    def start(self, operation: str):
        """Start timing an operation."""
        self.start_times[operation] = time.time()
        logger.debug(f"Started: {operation}")

    def end(self, operation: str):
        """End timing an operation and record duration."""
        if operation not in self.start_times:
            logger.warning(f"No start time for operation: {operation}")
            return

        duration = time.time() - self.start_times[operation]
        self.metrics[operation].append(duration)

        # Log slow operations
        if duration > 2.0:
            self.warnings.append({
                "operation": operation,
                "duration": duration,
                "timestamp": datetime.now()
            })
            logger.warning(f"Slow operation: {operation} took {duration:.2f}s")
        else:
            logger.debug(f"Completed: {operation} in {duration:.3f}s")

        del self.start_times[operation]

    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for an operation."""
        if operation not in self.metrics or not self.metrics[operation]:
            return {}

        times = self.metrics[operation]
        return {
            "count": len(times),
            "total": sum(times),
            "mean": sum(times) / len(times),
            "min": min(times),
            "max": max(times),
            "last": times[-1]
        }

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all operations."""
        return {op: self.get_stats(op) for op in self.metrics.keys()}

    def get_warnings(self) -> List[Dict[str, Any]]:
        """Get all performance warnings."""
        return self.warnings

    def clear(self):
        """Clear all metrics."""
        self.metrics.clear()
        self.start_times.clear()
        self.warnings.clear()


# Global performance monitor instance
_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return _monitor


def timed(operation_name: Optional[str] = None):
    """
    Decorator to automatically time function execution.

    Args:
        operation_name: Custom name for the operation. If None, uses function name.

    Example:
        @timed("load_reports")
        def load_all_reports():
            ...
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_monitor()
            monitor.start(op_name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                monitor.end(op_name)

        return wrapper
    return decorator


def measure_section(section_name: str):
    """
    Context manager for timing code sections.

    Example:
        with measure_section("data_processing"):
            # your code here
            process_data()
    """
    class SectionTimer:
        def __init__(self, name: str):
            self.name = name
            self.monitor = get_monitor()

        def __enter__(self):
            self.monitor.start(self.name)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.monitor.end(self.name)
            return False

    return SectionTimer(section_name)


def get_memory_usage() -> Dict[str, float]:
    """
    Get current memory usage statistics.

    Returns:
        Dictionary with memory metrics in MB
    """
    try:
        import psutil
        import os

        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()

        return {
            "rss_mb": mem_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": mem_info.vms / 1024 / 1024,  # Virtual Memory Size
            "percent": process.memory_percent()
        }
    except ImportError:
        logger.warning("psutil not installed - memory monitoring unavailable")
        return {}
    except Exception as e:
        logger.error(f"Failed to get memory usage: {e}")
        return {}


def show_performance_panel():
    """Display performance monitoring panel in Streamlit."""
    monitor = get_monitor()

    st.markdown("### ⚡ Performance Monitor")

    # Get all stats
    all_stats = monitor.get_all_stats()

    if not all_stats:
        st.info(
            "No performance data collected yet. Interact with the dashboard to see metrics.")
        return

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    total_operations = sum(s["count"] for s in all_stats.values())
    total_time = sum(s["total"] for s in all_stats.values())
    slow_operations = len(monitor.get_warnings())

    with col1:
        st.metric("Total Operations", f"{total_operations:,}")
    with col2:
        st.metric("Total Time", f"{total_time:.2f}s")
    with col3:
        st.metric("Slow Operations", slow_operations,
                  delta=f"{slow_operations} warnings" if slow_operations > 0 else None,
                  delta_color="inverse")

    # Detailed table
    st.markdown("#### 📊 Operation Breakdown")

    import pandas as pd

    rows = []
    for op_name, stats in all_stats.items():
        rows.append({
            "Operation": op_name,
            "Count": stats["count"],
            "Mean (s)": f"{stats['mean']:.3f}",
            "Min (s)": f"{stats['min']:.3f}",
            "Max (s)": f"{stats['max']:.3f}",
            "Total (s)": f"{stats['total']:.2f}",
            "Last (s)": f"{stats['last']:.3f}"
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Total (s)", ascending=False)

    st.dataframe(df, use_container_width=True)

    # Show warnings if any
    warnings = monitor.get_warnings()
    if warnings:
        st.markdown("#### ⚠️ Slow Operations")

        warning_rows = []
        for w in warnings[-10:]:  # Show last 10 warnings
            warning_rows.append({
                "Operation": w["operation"],
                "Duration (s)": f"{w['duration']:.2f}",
                "Time": w["timestamp"].strftime("%H:%M:%S")
            })

        warn_df = pd.DataFrame(warning_rows)
        st.dataframe(warn_df, use_container_width=True)

        st.caption("💡 Operations taking >2s are flagged as slow")

    # Memory usage
    mem_usage = get_memory_usage()
    if mem_usage:
        st.markdown("#### 💾 Memory Usage")

        mem_col1, mem_col2, mem_col3 = st.columns(3)
        with mem_col1:
            st.metric("RSS", f"{mem_usage.get('rss_mb', 0):.1f} MB")
        with mem_col2:
            st.metric("Virtual", f"{mem_usage.get('vms_mb', 0):.1f} MB")
        with mem_col3:
            st.metric("Usage", f"{mem_usage.get('percent', 0):.1f}%")

    # Clear button
    if st.button("🗑️ Clear Performance Data"):
        monitor.clear()
        st.rerun()
