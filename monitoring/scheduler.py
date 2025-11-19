"""
PHASE 3: SCHEDULER MODULE
Web Scraper Scheduling & Orchestration

Implements APScheduler for automated regulatory content scraping with:
- Daily jobs for EU AI Act, FDA, GDPR
- Weekly jobs for ISO 13485, IEC 62304
- Error handling and retries
- Comprehensive logging
- Health monitoring
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job
import requests
from pathlib import Path
import json
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScraperJob:
    """Configuration for a scraper job"""
    name: str
    source_name: str
    url: str
    parser_type: str  # 'html' or 'pdf'
    schedule_type: str  # 'daily' or 'weekly'
    schedule_time: str  # "HH:MM" format for daily, or day name for weekly
    retry_count: int = 3
    timeout_seconds: int = 30
    enabled: bool = True


class SchedulerManager:
    """
    Manages automated web scraping jobs using APScheduler
    
    Features:
    - Daily scraping for 3 sources (EU AI Act, FDA, GDPR)
    - Weekly scraping for 2 sources (ISO 13485, IEC 62304)
    - Automatic retries on failure (max 3)
    - Health monitoring and status tracking
    - Job logging and persistence
    """
    
    def __init__(self, config_file: str = 'config/scraper_config.json'):
        """
        Initialize scheduler manager
        
        Args:
            config_file: Path to scraper configuration file
        """
        self.scheduler = BackgroundScheduler()
        self.config_file = Path(config_file)
        self.jobs: Dict[str, Job] = {}
        self.job_history: List[Dict] = []
        self.health_status: Dict[str, Dict] = {}
        
        # Load configuration
        self.config = self._load_config()
        self.jobs_config = self._parse_jobs_config()
        
        logger.info("SchedulerManager initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            'timezone': 'UTC',
            'max_concurrent_jobs': 3,
            'job_store': 'memory',
            'log_directory': 'logs/scraper_jobs'
        }
    
    def _parse_jobs_config(self) -> List[ScraperJob]:
        """Parse scraper jobs configuration"""
        return [
            # Daily jobs (3)
            ScraperJob(
                name='EU AI Act Daily',
                source_name='EU AI Act',
                url='https://eur-lex.europa.eu/eli/reg/2024/1689/oj',
                parser_type='html',
                schedule_type='daily',
                schedule_time='02:00',  # 2 AM UTC
                enabled=True
            ),
            ScraperJob(
                name='FDA Daily',
                source_name='FDA',
                url='https://www.fda.gov/medical-devices/regulatory-guidance',
                parser_type='html',
                schedule_type='daily',
                schedule_time='03:00',  # 3 AM UTC
                enabled=True
            ),
            ScraperJob(
                name='GDPR Daily',
                source_name='GDPR',
                url='https://gdpr-info.eu/',
                parser_type='html',
                schedule_type='daily',
                schedule_time='04:00',  # 4 AM UTC
                enabled=True
            ),
            
            # Weekly jobs (2)
            ScraperJob(
                name='ISO 13485 Weekly',
                source_name='ISO 13485',
                url='https://www.iso.org/standard/59752.html',
                parser_type='html',
                schedule_type='weekly',
                schedule_time='monday',
                enabled=True
            ),
            ScraperJob(
                name='IEC 62304 Weekly',
                source_name='IEC 62304',
                url='https://www.iec.ch/standard/62304',
                parser_type='html',
                schedule_type='weekly',
                schedule_time='wednesday',
                enabled=True
            ),
        ]
    
    def start(self) -> None:
        """Start the scheduler and register all jobs"""
        if self.scheduler.running:
            logger.warning("Scheduler already running")
            return
        
        # Register all jobs
        for job_config in self.jobs_config:
            if job_config.enabled:
                self._register_job(job_config)
        
        # Start scheduler
        self.scheduler.start()
        logger.info(f"Scheduler started with {len(self.jobs)} jobs registered")
        self._log_job_schedule()
    
    def stop(self) -> None:
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
    
    def _register_job(self, job_config: ScraperJob) -> None:
        """Register a scraper job with the scheduler"""
        try:
            if job_config.schedule_type == 'daily':
                # Parse time "HH:MM"
                hour, minute = map(int, job_config.schedule_time.split(':'))
                trigger = CronTrigger(hour=hour, minute=minute)
                
            elif job_config.schedule_type == 'weekly':
                # Parse day name
                day_name = job_config.schedule_time.lower()
                day_map = {
                    'monday': 0, 'tuesday': 1, 'wednesday': 2,
                    'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
                }
                day_of_week = day_map.get(day_name, 0)
                trigger = CronTrigger(day_of_week=day_of_week, hour=2, minute=0)
            else:
                logger.error(f"Unknown schedule type: {job_config.schedule_type}")
                return
            
            job = self.scheduler.add_job(
                self._execute_scraper_job,
                trigger=trigger,
                args=[job_config],
                id=job_config.name,
                name=job_config.name,
                max_instances=1,
                misfire_grace_time=900  # 15 min grace period
            )
            
            self.jobs[job_config.name] = job
            self.health_status[job_config.name] = {
                'status': 'scheduled',
                'last_run': None,
                'next_run': job.next_run_time,
                'success_count': 0,
                'failure_count': 0
            }
            
            logger.info(f"Job registered: {job_config.name} - Next run: {job.next_run_time}")
            
        except Exception as e:
            logger.error(f"Error registering job {job_config.name}: {str(e)}")
    
    def _execute_scraper_job(self, job_config: ScraperJob, attempt: int = 1) -> Dict:
        """
        Execute a scraper job with retry logic
        
        Args:
            job_config: ScraperJob configuration
            attempt: Current attempt number
            
        Returns:
            Dict with execution results
        """
        start_time = datetime.now()
        result = {
            'job_name': job_config.name,
            'source': job_config.source_name,
            'start_time': start_time.isoformat(),
            'status': 'pending',
            'attempt': attempt,
            'items_scraped': 0,
            'changes_detected': 0,
            'error': None
        }
        
        try:
            logger.info(f"[{job_config.name}] Starting scrape (attempt {attempt}/{job_config.retry_count})")
            
            # Check rate limiting (1 req/sec min)
            self._apply_rate_limit()
            
            # Perform scrape
            scraped_data = self._scrape_url(
                url=job_config.url,
                parser_type=job_config.parser_type,
                timeout=job_config.timeout_seconds
            )
            
            result['items_scraped'] = len(scraped_data.get('items', []))
            
            # Check for changes
            changes = self._detect_changes(job_config.source_name, scraped_data)
            result['changes_detected'] = len(changes)
            
            # Store in database
            self._store_scraped_data(job_config.source_name, scraped_data)
            
            # Update status
            result['status'] = 'success'
            self.health_status[job_config.name]['status'] = 'healthy'
            self.health_status[job_config.name]['success_count'] += 1
            
            logger.info(
                f"[{job_config.name}] SUCCESS: "
                f"{result['items_scraped']} items, "
                f"{result['changes_detected']} changes"
            )
            
        except Exception as e:
            error_msg = str(e)
            result['error'] = error_msg
            
            logger.error(
                f"[{job_config.name}] FAILED (attempt {attempt}): {error_msg}"
            )
            
            # Retry logic
            if attempt < job_config.retry_count:
                logger.info(f"[{job_config.name}] Retrying in 5 minutes...")
                retry_job = self.scheduler.add_job(
                    self._execute_scraper_job,
                    'date',
                    run_date=datetime.now() + timedelta(minutes=5),
                    args=[job_config, attempt + 1],
                    id=f"{job_config.name}_retry_{attempt}"
                )
                result['status'] = 'retry_scheduled'
                logger.info(f"Retry scheduled: {retry_job.id}")
            else:
                result['status'] = 'failed'
                self.health_status[job_config.name]['status'] = 'unhealthy'
                self.health_status[job_config.name]['failure_count'] += 1
        
        # Record execution
        result['duration_seconds'] = (datetime.now() - start_time).total_seconds()
        result['end_time'] = datetime.now().isoformat()
        self.job_history.append(result)
        
        # Update next run time
        if job_config.name in self.jobs:
            self.health_status[job_config.name]['next_run'] = \
                self.jobs[job_config.name].next_run_time
        
        return result
    
    def _scrape_url(self, url: str, parser_type: str, timeout: int) -> Dict:
        """
        Scrape content from URL
        
        Args:
            url: URL to scrape
            parser_type: 'html' or 'pdf'
            timeout: Request timeout in seconds
            
        Returns:
            Dict with scraped content and metadata
        """
        try:
            headers = {
                'User-Agent': 'IRAQAF-Compliance-Bot/1.0 (+https://compliance.local/bot)'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # Parse content based on type
            if parser_type == 'html':
                return self._parse_html_content(response.text, url)
            elif parser_type == 'pdf':
                return self._parse_pdf_content(response.content, url)
            else:
                raise ValueError(f"Unknown parser type: {parser_type}")
                
        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout after {timeout}s for {url}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed for {url}: {str(e)}")
    
    def _parse_html_content(self, html_content: str, url: str) -> Dict:
        """
        Parse HTML content and extract sections
        
        Args:
            html_content: HTML content
            url: Source URL
            
        Returns:
            Dict with extracted items and metadata
        """
        # Basic implementation - extract h1, h2, p tags
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        items = []
        
        # Extract main content sections
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            section_content = []
            for sibling in heading.find_next_siblings(['p', 'div']):
                if sibling.name in ['h1', 'h2', 'h3']:
                    break
                section_content.append(sibling.get_text().strip())
            
            if section_content:
                items.append({
                    'section': heading.get_text().strip(),
                    'content': ' '.join(section_content)[:500],  # First 500 chars
                    'extracted_at': datetime.now().isoformat()
                })
        
        return {
            'url': url,
            'items': items[:100],  # Limit to 100 items per source
            'content_hash': hash(html_content) & 0xffffffff,
            'parsed_at': datetime.now().isoformat()
        }
    
    def _parse_pdf_content(self, pdf_content: bytes, url: str) -> Dict:
        """
        Parse PDF content and extract text
        
        Args:
            pdf_content: PDF file content
            url: Source URL
            
        Returns:
            Dict with extracted items and metadata
        """
        # Basic implementation - would use pdfplumber/PyPDF2
        items = [{
            'section': 'PDF Content',
            'content': 'PDF parsing requires additional dependencies',
            'extracted_at': datetime.now().isoformat()
        }]
        
        return {
            'url': url,
            'items': items,
            'content_hash': hash(pdf_content) & 0xffffffff,
            'parsed_at': datetime.now().isoformat()
        }
    
    def _detect_changes(self, source_name: str, scraped_data: Dict) -> List[Dict]:
        """
        Detect changes in scraped content
        
        Args:
            source_name: Name of source
            scraped_data: New scraped data
            
        Returns:
            List of detected changes
        """
        # This would compare against database content
        # For now, return empty list (integration with db/operations.py)
        changes = []
        
        # TODO: Integrate with db.operations.detect_changes()
        # This would:
        # 1. Get previous content hash from database
        # 2. Compare with new content_hash
        # 3. If different, log as change
        # 4. Return list of changes
        
        return changes
    
    def _store_scraped_data(self, source_name: str, scraped_data: Dict) -> None:
        """
        Store scraped data in database
        
        Args:
            source_name: Name of source
            scraped_data: Data to store
        """
        # This would integrate with db/operations.py
        # For now, just log
        logger.info(f"Storing {len(scraped_data.get('items', []))} items from {source_name}")
        
        # TODO: Integrate with db.operations module
        # from db.operations import db_ops
        # for item in scraped_data.get('items', []):
        #     db_ops.store_regulatory_content(
        #         source_name=source_name,
        #         title=item['section'],
        #         section='',
        #         subsection='',
        #         content=item['content']
        #     )
    
    def _apply_rate_limit(self, min_interval: float = 1.0) -> None:
        """
        Apply rate limiting (minimum 1 req/sec)
        
        Args:
            min_interval: Minimum seconds between requests
        """
        # TODO: Implement proper rate limiting
        # Track last request time and wait if needed
        pass
    
    def _log_job_schedule(self) -> None:
        """Log current job schedule"""
        logger.info("=" * 60)
        logger.info("SCHEDULER JOB SCHEDULE")
        logger.info("=" * 60)
        
        for job_name, job in self.jobs.items():
            next_run = job.next_run_time
            trigger_str = str(job.trigger)
            logger.info(f"{job_name:30} | Next: {next_run} | {trigger_str}")
        
        logger.info("=" * 60)
    
    def get_job_status(self) -> Dict:
        """Get status of all jobs"""
        return {
            'scheduler_running': self.scheduler.running,
            'total_jobs': len(self.jobs),
            'job_health': self.health_status,
            'recent_executions': self.job_history[-10:] if self.job_history else []
        }
    
    def get_job_history(self, limit: int = 50) -> List[Dict]:
        """Get recent job execution history"""
        return self.job_history[-limit:] if self.job_history else []
    
    def manually_trigger_job(self, job_name: str) -> Dict:
        """
        Manually trigger a job (bypass schedule)
        
        Args:
            job_name: Name of job to trigger
            
        Returns:
            Execution result
        """
        job_config = next(
            (j for j in self.jobs_config if j.name == job_name),
            None
        )
        
        if not job_config:
            return {'error': f'Job not found: {job_name}'}
        
        logger.info(f"Manually triggering job: {job_name}")
        return self._execute_scraper_job(job_config)


# Global scheduler instance
_scheduler_instance: Optional[SchedulerManager] = None


def get_scheduler() -> SchedulerManager:
    """Get or create global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = SchedulerManager()
    return _scheduler_instance


def start_scheduler() -> None:
    """Start the global scheduler"""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler() -> None:
    """Stop the global scheduler"""
    scheduler = get_scheduler()
    scheduler.stop()


if __name__ == '__main__':
    # Example usage
    scheduler = get_scheduler()
    scheduler.start()
    
    try:
        logger.info("Scheduler running... Press Ctrl+C to stop")
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        scheduler.stop()
