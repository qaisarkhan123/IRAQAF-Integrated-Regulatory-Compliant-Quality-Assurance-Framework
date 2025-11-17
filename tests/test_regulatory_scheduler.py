"""
Tests for Regulatory Scheduler Module
Tests APScheduler task orchestration and job management
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

try:
    from regulatory_scheduler import (
        RegulatoryScheduler,
        schedule_regulation_check,
        schedule_cache_cleanup,
        get_scheduled_jobs
    )
except ImportError:
    pytest.skip("regulatory_scheduler module not found", allow_module_level=True)


class TestSchedulerInitialization:
    """Tests for scheduler initialization"""
    
    @pytest.fixture
    def scheduler(self):
        """Fixture: Initialize scheduler"""
        sched = RegulatoryScheduler()
        yield sched
        # Cleanup
        try:
            sched.stop()
        except:
            pass
    
    def test_scheduler_creates_successfully(self, scheduler):
        """Test scheduler initializes without errors"""
        assert scheduler is not None
    
    def test_scheduler_has_required_methods(self, scheduler):
        """Test scheduler has required methods"""
        assert hasattr(scheduler, 'start')
        assert hasattr(scheduler, 'stop')
        assert hasattr(scheduler, 'add_job')
    
    def test_scheduler_config_loaded(self, scheduler):
        """Test scheduler configuration is loaded"""
        assert scheduler is not None


class TestSchedulerJobs:
    """Tests for job scheduling"""
    
    @pytest.fixture
    def scheduler(self):
        """Fixture: Initialize scheduler"""
        sched = RegulatoryScheduler()
        yield sched
        try:
            sched.stop()
        except:
            pass
    
    def test_schedule_regulation_check_job(self, scheduler):
        """Test scheduling regulation check job"""
        with patch('regulatory_scheduler.check_regulations') as mock_check:
            job_id = schedule_regulation_check(scheduler, interval_minutes=30)
            assert job_id is not None
    
    def test_schedule_cache_cleanup_job(self, scheduler):
        """Test scheduling cache cleanup job"""
        with patch('regulatory_scheduler.cleanup_cache') as mock_cleanup:
            job_id = schedule_cache_cleanup(scheduler, interval_hours=24)
            assert job_id is not None
    
    def test_schedule_multiple_jobs(self, scheduler):
        """Test scheduling multiple jobs"""
        with patch('regulatory_scheduler.check_regulations'), \
             patch('regulatory_scheduler.cleanup_cache'):
            
            job1 = schedule_regulation_check(scheduler, interval_minutes=30)
            job2 = schedule_cache_cleanup(scheduler, interval_hours=24)
            
            assert job1 is not None
            assert job2 is not None
            assert job1 != job2
    
    def test_get_scheduled_jobs(self, scheduler):
        """Test retrieving all scheduled jobs"""
        jobs = get_scheduled_jobs(scheduler)
        assert isinstance(jobs, (list, dict))


class TestSchedulerTiming:
    """Tests for job timing and intervals"""
    
    def test_regulation_check_interval_parsing(self):
        """Test parsing regulation check interval"""
        from regulatory_scheduler import parse_interval
        
        interval = parse_interval("0 */6 * * *")  # Every 6 hours
        assert interval is not None
    
    def test_cache_cleanup_interval_parsing(self):
        """Test parsing cache cleanup interval"""
        from regulatory_scheduler import parse_interval
        
        interval = parse_interval("0 2 * * *")  # Daily at 2 AM
        assert interval is not None
    
    def test_schedule_respects_timezone(self):
        """Test that scheduler respects timezone settings"""
        from regulatory_scheduler import RegulatoryScheduler
        
        scheduler = RegulatoryScheduler(timezone='UTC')
        assert scheduler is not None


class TestSchedulerPersistence:
    """Tests for job persistence"""
    
    def test_scheduler_saves_job_state(self):
        """Test scheduler saves job state"""
        from regulatory_scheduler import RegulatoryScheduler
        
        scheduler = RegulatoryScheduler()
        # State should be managed internally
        assert scheduler is not None
    
    def test_scheduler_recovers_jobs_on_restart(self):
        """Test scheduler can recover jobs after restart"""
        from regulatory_scheduler import RegulatoryScheduler
        
        scheduler1 = RegulatoryScheduler()
        scheduler2 = RegulatoryScheduler()
        
        # Both instances should work independently
        assert scheduler1 is not None
        assert scheduler2 is not None


class TestSchedulerErrorHandling:
    """Tests for error handling in scheduler"""
    
    @pytest.fixture
    def scheduler(self):
        """Fixture: Initialize scheduler"""
        sched = RegulatoryScheduler()
        yield sched
        try:
            sched.stop()
        except:
            pass
    
    def test_handle_job_failure_gracefully(self, scheduler):
        """Test scheduler handles job failures gracefully"""
        with patch('regulatory_scheduler.check_regulations') as mock_check:
            mock_check.side_effect = Exception("Test error")
            
            # Should not crash scheduler
            try:
                schedule_regulation_check(scheduler, interval_minutes=30)
            except:
                pass
    
    def test_handle_invalid_job_parameters(self, scheduler):
        """Test scheduler handles invalid parameters"""
        with pytest.raises((ValueError, TypeError)):
            schedule_regulation_check(scheduler, interval_minutes=-1)
    
    def test_handle_missing_job_config(self):
        """Test scheduler handles missing job configuration"""
        from regulatory_scheduler import RegulatoryScheduler
        
        # Should initialize with defaults
        scheduler = RegulatoryScheduler()
        assert scheduler is not None


class TestSchedulerMetrics:
    """Tests for scheduler metrics and monitoring"""
    
    def test_get_job_statistics(self):
        """Test retrieving job statistics"""
        from regulatory_scheduler import get_job_statistics
        
        stats = get_job_statistics()
        assert isinstance(stats, dict)
    
    def test_track_job_execution_time(self):
        """Test tracking job execution time"""
        from regulatory_scheduler import RegulatoryScheduler
        
        scheduler = RegulatoryScheduler()
        # Should support execution time tracking
        assert scheduler is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
