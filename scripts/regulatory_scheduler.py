#!/usr/bin/env python
"""
Regulatory Monitoring Scheduler
Continuous background task for monitoring regulatory changes
Runs on configurable schedule (hourly, daily, weekly, etc.)
"""

import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    import pytz
except ImportError:
    print("Install APScheduler: pip install apscheduler pytz")
    raise

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class RegulatoryMonitoringScheduler:
    """Manage scheduled regulatory monitoring tasks"""
    
    def __init__(self, timezone: str = 'UTC'):
        self.scheduler = BackgroundScheduler(timezone=timezone)
        self.monitoring_config_file = Path('configs/monitoring_config.yaml')
        self.last_run_file = Path('regulatory_data/last_monitoring_run.json')
        self.jobs = {}  # Track jobs by ID
        self.job_stats = {}  # Track job execution stats
        self.execution_count = {}  # Count executions per job
        
    def schedule_hourly_check(self) -> None:
        """Run monitoring check every hour"""
        self.scheduler.add_job(
            func=self._run_monitoring,
            trigger=CronTrigger(minute=0),  # At start of every hour
            id='regulatory_monitor_hourly',
            name='Hourly Regulatory Monitoring',
            replace_existing=True,
            coalesce=True,
            max_instances=1
        )
        logger.info("✅ Scheduled: Hourly regulatory monitoring")
        
    def schedule_daily_check(self, hour: int = 2) -> None:
        """Run monitoring check daily at specified hour (UTC)"""
        self.scheduler.add_job(
            func=self._run_monitoring,
            trigger=CronTrigger(hour=hour, minute=0),
            id='regulatory_monitor_daily',
            name='Daily Regulatory Monitoring',
            replace_existing=True,
            coalesce=True,
            max_instances=1
        )
        logger.info(f"✅ Scheduled: Daily regulatory monitoring at {hour:02d}:00 UTC")
        
    def schedule_weekly_check(self, day_of_week: str = 'monday', hour: int = 2) -> None:
        """Run monitoring check weekly"""
        self.scheduler.add_job(
            func=self._run_monitoring,
            trigger=CronTrigger(day_of_week=day_of_week, hour=hour, minute=0),
            id='regulatory_monitor_weekly',
            name='Weekly Regulatory Monitoring',
            replace_existing=True,
            coalesce=True,
            max_instances=1
        )
        logger.info(f"✅ Scheduled: Weekly regulatory monitoring on {day_of_week} at {hour:02d}:00 UTC")
        
    def schedule_custom_cron(self, cron_expression: str, job_id: str = 'custom_monitoring') -> None:
        """Schedule with custom cron expression"""
        try:
            trigger = CronTrigger.from_crontab(cron_expression)
            self.scheduler.add_job(
                func=self._run_monitoring,
                trigger=trigger,
                id=job_id,
                name=f'Custom Regulatory Monitoring ({cron_expression})',
                replace_existing=True,
                coalesce=True,
                max_instances=1
            )
            logger.info(f"✅ Scheduled custom: {cron_expression}")
        except Exception as e:
            logger.error(f"❌ Invalid cron expression: {e}")
            
    def start(self) -> None:
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("🚀 Regulatory monitoring scheduler started")
            
    def stop(self) -> None:
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("⛔ Regulatory monitoring scheduler stopped")
            
    def list_jobs(self) -> None:
        """List all scheduled jobs"""
        logger.info("📋 Scheduled Jobs:")
        for job in self.scheduler.get_jobs():
            logger.info(f"  • {job.id}: {job.name}")
            logger.info(f"    Next run: {job.next_run_time}")
    
    def add_regulation_check_job(self, job_id: str = 'regulation_check') -> bool:
        """Add a regulation check job"""
        try:
            self.scheduler.add_job(
                func=self._run_monitoring,
                trigger='interval',
                hours=1,
                id=job_id,
                name='Regulation Check Job',
                replace_existing=True
            )
            self.jobs[job_id] = {'name': 'Regulation Check Job', 'type': 'regulation_check'}
            self.execution_count[job_id] = 0
            logger.info(f"✅ Added job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add job: {e}")
            return False
    
    def add_cache_cleanup_job(self, job_id: str = 'cache_cleanup') -> bool:
        """Add a cache cleanup job"""
        try:
            self.scheduler.add_job(
                func=self._cleanup_cache,
                trigger='cron',
                hour=3,
                minute=0,
                id=job_id,
                name='Cache Cleanup Job',
                replace_existing=True
            )
            self.jobs[job_id] = {'name': 'Cache Cleanup Job', 'type': 'cache_cleanup'}
            self.execution_count[job_id] = 0
            logger.info(f"✅ Added job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add job: {e}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
            logger.info(f"✅ Removed job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to remove job: {e}")
            return False
    
    def get_all_jobs(self) -> list:
        """Get all scheduled jobs"""
        return [{'id': j.id, 'name': j.name, 'next_run': str(j.next_run_time)} 
                for j in self.scheduler.get_jobs()]
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get status of a specific job"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                return {
                    'id': job.id,
                    'name': job.name,
                    'next_run': str(job.next_run_time),
                    'execution_count': self.execution_count.get(job_id, 0)
                }
        except:
            pass
        return None
    
    def track_job_execution_count(self, job_id: str) -> int:
        """Get execution count for a job"""
        return self.execution_count.get(job_id, 0)
    
    def measure_job_duration(self, job_id: str) -> Optional[float]:
        """Get last execution duration for a job (in seconds)"""
        return self.job_stats.get(job_id, {}).get('duration', None)
    
    def get_next_execution_time(self, job_id: str) -> Optional[str]:
        """Get next execution time for a job"""
        try:
            job = self.scheduler.get_job(job_id)
            if job and job.next_run_time:
                return job.next_run_time.isoformat()
        except:
            pass
        return None
    
    def _cleanup_cache(self) -> None:
        """Clean up cached data"""
        try:
            cache_dir = Path('regulatory_data/cache')
            if cache_dir.exists():
                import shutil
                old_files = [f for f in cache_dir.glob('*') 
                           if datetime.fromtimestamp(f.stat().st_mtime) < datetime.now() - timedelta(days=7)]
                for f in old_files:
                    if f.is_file():
                        f.unlink()
                logger.info(f"✅ Cache cleanup: removed {len(old_files)} old files")
        except Exception as e:
            logger.error(f"❌ Cache cleanup failed: {e}")
            
    def _run_monitoring(self) -> None:
        """Execute monitoring check"""
        try:
            from regulatory_monitor import RegulatoryMonitor
            from nlp_change_detector import NLPChangeDetector, ChangeTracker
            from iraqaf_regulatory_sync import IRQAFRegulatorySync, RegulatoryComplianceDelta
            
            logger.info("=" * 70)
            logger.info("🔍 REGULATORY MONITORING CHECK STARTED")
            logger.info("=" * 70)
            
            # 1. Fetch regulatory updates
            monitor = RegulatoryMonitor()
            monitor.register_default_sources()
            documents = monitor.fetch_all()
            monitor.save_cache(documents)
            
            # 2. Detect changes
            changes = monitor.detect_changes()
            
            # 3. Analyze with NLP
            detector = NLPChangeDetector()
            tracker = ChangeTracker()
            
            for reg in changes.get('new_regulations', []):
                logger.info(f"📋 New: {reg.get('title', 'Unknown')}")
                
            for update in changes.get('updated_regulations', []):
                doc = update.get('doc', {})
                old_content = update.get('previous_content', '')
                new_content = update.get('new_content', '')
                
                clause_changes = detector.detect_clause_changes(old_content, new_content)
                summary = detector.generate_summary(doc, clause_changes)
                logger.info(summary)
                
                # Save to history
                reg_name = doc.get('source', 'Unknown')
                tracker.save_change(reg_name, clause_changes)
            
            # 4. Sync with IRAQAF
            sync = IRQAFRegulatorySync()
            delta = RegulatoryComplianceDelta()
            
            for reg in changes.get('updated_regulations', []):
                doc = reg.get('doc', {})
                regulation = sync.identify_regulation(doc.get('title', ''), doc.get('content', ''))
                
                if regulation:
                    # Update trace map
                    sync.update_module_due_to_regulation(regulation, {})
                    
                    # Generate impact report
                    impact = delta.generate_impact_report(
                        regulation,
                        reg.get('clause_changes', {}),
                        sync.regulation_module_mapping.get(regulation, {}).get('modules', [])
                    )
                    delta.save_impact_report(regulation, impact)
            
            # 5. Generate sync report
            sync_report = sync.generate_sync_report(changes)
            logger.info(sync_report)
            
            # 6. Record run
            self._record_run(len(changes.get('new_regulations', [])),
                           len(changes.get('updated_regulations', [])))
            
            logger.info("=" * 70)
            logger.info("✅ MONITORING CHECK COMPLETED SUCCESSFULLY")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"❌ Monitoring check failed: {e}", exc_info=True)
            self._record_run_error(str(e))
            
    def _record_run(self, new_count: int, updated_count: int) -> None:
        """Record successful monitoring run"""
        run_data = {
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'new_regulations': new_count,
            'updated_regulations': updated_count
        }
        
        self.last_run_file.parent.mkdir(exist_ok=True)
        with open(self.last_run_file, 'w') as f:
            json.dump(run_data, f, indent=2)
            
        logger.info(f"Recorded run: {new_count} new, {updated_count} updated")
        
    def _record_run_error(self, error: str) -> None:
        """Record failed monitoring run"""
        run_data = {
            'timestamp': datetime.now().isoformat(),
            'status': 'error',
            'error': error
        }
        
        self.last_run_file.parent.mkdir(exist_ok=True)
        with open(self.last_run_file, 'w') as f:
            json.dump(run_data, f, indent=2)


class MonitoringStatus:
    """Check and display monitoring status"""
    
    @staticmethod
    def get_last_run() -> Optional[Dict]:
        """Get last monitoring run info"""
        last_run_file = Path('regulatory_data/last_monitoring_run.json')
        if last_run_file.exists():
            with open(last_run_file, 'r') as f:
                return json.load(f)
        return None
        
    @staticmethod
    def display_status() -> None:
        """Display current monitoring status"""
        last_run = MonitoringStatus.get_last_run()
        
        if not last_run:
            print("⚠️  No monitoring runs yet")
            return
        
        status = last_run.get('status', 'unknown').upper()
        timestamp = last_run.get('timestamp', 'Unknown')
        
        if status == 'SUCCESS':
            status_emoji = '✅'
        elif status == 'ERROR':
            status_emoji = '❌'
        else:
            status_emoji = '⚠️ '
        
        print(f"""
╔════════════════════════════════════════════════════════════╗
║           REGULATORY MONITORING STATUS                     ║
╚════════════════════════════════════════════════════════════╝

{status_emoji} Status: {status}
📅 Last Run: {timestamp}

""")
        
        if status == 'SUCCESS':
            print(f"  📋 New Regulations: {last_run.get('new_regulations', 0)}")
            print(f"  🔄 Updated Regulations: {last_run.get('updated_regulations', 0)}")
        elif status == 'ERROR':
            print(f"  ❌ Error: {last_run.get('error', 'Unknown')}")
        
            print(f"  📋 New Regulations: {last_run.get('new_regulations', 0)}")
            print(f"  🔄 Updated Regulations: {last_run.get('updated_regulations', 0)}")
        elif status == 'ERROR':
            print(f"  ❌ Error: {last_run.get('error', 'Unknown')}")
        
        print("\n╚════════════════════════════════════════════════════════════╝\n")


# Module-level wrapper functions for test compatibility
_scheduler_instance = None

def add_regulation_check_job(job_id: str = 'regulation_check', interval_minutes: int = 30) -> bool:
    """Add regulation check job to scheduler"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = RegulatoryScheduler()
    return _scheduler_instance.add_regulation_check_job(job_id)

def add_cache_cleanup_job(job_id: str = 'cache_cleanup') -> bool:
    """Add cache cleanup job to scheduler"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = RegulatoryScheduler()
    return _scheduler_instance.add_cache_cleanup_job(job_id)

def remove_job(job_id: str) -> bool:
    """Remove job from scheduler"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = RegulatoryScheduler()
    return _scheduler_instance.remove_job(job_id)

def get_all_jobs() -> List[Dict]:
    """Get all scheduled jobs"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = RegulatoryScheduler()
    return _scheduler_instance.get_all_jobs()

def get_job_status(job_id: str) -> Dict:
    """Get status of a specific job"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = RegulatoryScheduler()
    return _scheduler_instance.get_job_status(job_id)

def track_job_execution_count(job_id: str) -> int:
    """Get execution count for a job"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = RegulatoryScheduler()
    return _scheduler_instance.track_job_execution_count(job_id)

def measure_job_duration(job_id: str) -> float:
    """Get last execution duration for a job in seconds"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = RegulatoryScheduler()
    return _scheduler_instance.measure_job_duration(job_id)

def get_next_execution_time(job_id: str) -> Optional[datetime]:
    """Get next execution time for a job"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = RegulatoryScheduler()
    return _scheduler_instance.get_next_execution_time(job_id)

def main():
    """Example: Setup and run monitoring scheduler"""
    scheduler = RegulatoryMonitoringScheduler(timezone='UTC')
    
    # Schedule monitoring jobs
    scheduler.schedule_hourly_check()  # Check every hour
    scheduler.schedule_daily_check(hour=2)  # Daily check at 2 AM UTC
    scheduler.schedule_weekly_check('monday', hour=9)  # Weekly on Monday at 9 AM
    
    # List scheduled jobs
    scheduler.list_jobs()
    
    # Start the scheduler
    scheduler.start()
    
    # Display status
    MonitoringStatus.display_status()
    
    # Keep running (in production, this would be a service)
    try:
        logger.info("Scheduler running. Press Ctrl+C to stop.")
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.stop()


if __name__ == '__main__':
    main()
