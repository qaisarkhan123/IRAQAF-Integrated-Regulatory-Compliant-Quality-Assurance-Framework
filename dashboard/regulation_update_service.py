"""
Regulation Update Service
Automatically fetches and monitors updates to regulatory frameworks.
"""

import json
import sqlite3
import hashlib
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
import time
import logging
from bs4 import BeautifulSoup
import difflib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegulationUpdateService:
    def __init__(self, db_path: Optional[str] = None, sources_path: Optional[str] = None):
        """Initialize the regulation update service."""
        if db_path is None:
            db_path = Path(__file__).parent / "evidence" / "regulation_versions.db"
        
        if sources_path is None:
            sources_path = Path(__file__).parent / "configs" / "regulation_sources.json"
        
        self.db_path = Path(db_path)
        self.sources_path = Path(sources_path)
        
        # Create directories if needed
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.sources_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Load sources configuration
        self.sources = self._load_sources()
        
        # Scheduler state
        self.scheduler_running = False
        self.scheduler_thread = None
        
        # Request session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RegulationMonitor/1.0)'
        })
    
    def _init_database(self):
        """Initialize the database schema for regulation versions."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Regulation versions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regulation_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                framework TEXT NOT NULL,
                version_tag TEXT NOT NULL,
                raw_text TEXT,
                text_hash TEXT,
                created_at TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 0,
                source_url TEXT,
                UNIQUE(framework, version_tag)
            )
        ''')
        
        # Regulation changes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regulation_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                framework TEXT NOT NULL,
                old_version_id INTEGER,
                new_version_id INTEGER,
                diff_summary TEXT,
                diff_details TEXT,
                requires_review BOOLEAN DEFAULT 1,
                approved BOOLEAN DEFAULT 0,
                rejected BOOLEAN DEFAULT 0,
                created_at TEXT NOT NULL,
                reviewed_at TEXT,
                reviewed_by TEXT,
                FOREIGN KEY(old_version_id) REFERENCES regulation_versions(id),
                FOREIGN KEY(new_version_id) REFERENCES regulation_versions(id)
            )
        ''')
        
        # Polling status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS polling_status (
                framework TEXT PRIMARY KEY,
                last_polled TEXT,
                next_poll TEXT,
                status TEXT,
                error_message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_sources(self) -> List[Dict]:
        """Load regulation sources configuration."""
        try:
            with open(self.sources_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Sources configuration not found at {self.sources_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing sources configuration: {e}")
            return []
    
    def fetch_latest_text(self, source: Dict) -> Optional[str]:
        """
        Fetch the latest text from a regulation source.
        
        Args:
            source: Source configuration dict
        
        Returns:
            Fetched text content or None on error
        """
        url = source.get('url')
        source_type = source.get('source_type', 'html')
        selector = source.get('selector', 'body')
        
        if not url:
            logger.error(f"No URL provided for source: {source}")
            return None
        
        try:
            logger.info(f"Fetching {source['framework']} from {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            if source_type == 'html':
                soup = BeautifulSoup(response.text, 'html.parser')
                element = soup.select_one(selector) if selector else soup.body
                if element:
                    # Extract text content
                    text = element.get_text(separator='\n', strip=True)
                    return text
                else:
                    logger.warning(f"Selector '{selector}' not found, using full body")
                    return soup.get_text(separator='\n', strip=True)
            elif source_type == 'rss':
                # For RSS feeds, extract text from items
                soup = BeautifulSoup(response.text, 'xml')
                items = soup.find_all('item')
                texts = []
                for item in items:
                    title = item.find('title')
                    description = item.find('description')
                    if title:
                        texts.append(title.get_text())
                    if description:
                        texts.append(description.get_text())
                return '\n\n'.join(texts)
            else:
                # Plain text
                return response.text
        
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {source['framework']}: {e}")
            return None
    
    def diff_regulation_text(self, old_text: str, new_text: str) -> Dict:
        """
        Compare two regulation texts and generate a diff summary.
        
        Args:
            old_text: Previous version text
            new_text: New version text
        
        Returns:
            Dict with diff summary and details
        """
        if old_text == new_text:
            return {
                "changed": False,
                "summary": "No changes detected",
                "added_lines": 0,
                "removed_lines": 0,
                "changed_lines": 0
            }
        
        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()
        
        # Generate unified diff
        diff = list(difflib.unified_diff(
            old_lines, new_lines,
            lineterm='',
            n=3
        ))
        
        added_count = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        removed_count = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        changed_count = min(added_count, removed_count)  # Approximate
        
        # Generate summary
        if added_count == 0 and removed_count == 0:
            summary = "No changes detected"
        elif added_count > removed_count * 2:
            summary = f"Significant additions: {added_count} lines added, {removed_count} lines removed"
        elif removed_count > added_count * 2:
            summary = f"Significant removals: {removed_count} lines removed, {added_count} lines added"
        else:
            summary = f"Changes detected: {added_count} lines added, {removed_count} lines removed"
        
        return {
            "changed": True,
            "summary": summary,
            "added_lines": added_count,
            "removed_lines": removed_count,
            "changed_lines": changed_count,
            "diff_details": '\n'.join(diff[:100])  # First 100 lines of diff
        }
    
    def _get_text_hash(self, text: str) -> str:
        """Generate a hash of the text for comparison."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _get_active_version(self, framework: str) -> Optional[Dict]:
        """Get the currently active version for a framework."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM regulation_versions
            WHERE framework = ? AND is_active = 1
            ORDER BY created_at DESC
            LIMIT 1
        ''', (framework,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def _save_version(self, framework: str, version_tag: str, raw_text: str, 
                     source_url: str, is_active: bool = False) -> int:
        """Save a new regulation version."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        text_hash = self._get_text_hash(raw_text)
        created_at = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO regulation_versions 
            (framework, version_tag, raw_text, text_hash, created_at, is_active, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (framework, version_tag, raw_text, text_hash, created_at, is_active, source_url))
        
        version_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return version_id
    
    def _create_change_record(self, framework: str, old_version_id: Optional[int],
                             new_version_id: int, diff_summary: Dict) -> int:
        """Create a change record for a regulation update."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        created_at = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO regulation_changes
            (framework, old_version_id, new_version_id, diff_summary, diff_details,
             requires_review, approved, rejected, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            framework, old_version_id, new_version_id,
            diff_summary.get('summary', ''),
            diff_summary.get('diff_details', ''),
            True, False, False, created_at
        ))
        
        change_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return change_id
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check for updates across all configured regulation sources.
        
        Returns:
            List of detected changes
        """
        changes_detected = []
        
        for source in self.sources:
            framework = source['framework']
            
            try:
                # Fetch latest text
                new_text = self.fetch_latest_text(source)
                if not new_text:
                    logger.warning(f"Failed to fetch text for {framework}")
                    self._update_polling_status(framework, 'error', f"Failed to fetch from {source['url']}")
                    continue
                
                # Get current active version
                active_version = self._get_active_version(framework)
                
                # Generate version tag
                version_tag = f"{datetime.now().strftime('%Y%m%d')}_official"
                new_hash = self._get_text_hash(new_text)
                
                # Check if this version already exists
                if active_version and active_version['text_hash'] == new_hash:
                    logger.info(f"{framework}: No changes detected")
                    self._update_polling_status(framework, 'success', None)
                    continue
                
                # Save new version (inactive initially)
                new_version_id = self._save_version(
                    framework, version_tag, new_text,
                    source['url'], is_active=False
                )
                
                # Compare with old version if exists
                if active_version:
                    old_text = active_version.get('raw_text', '')
                    diff_summary = self.diff_regulation_text(old_text, new_text)
                    
                    if diff_summary['changed']:
                        # Create change record
                        change_id = self._create_change_record(
                            framework,
                            active_version['id'],
                            new_version_id,
                            diff_summary
                        )
                        
                        changes_detected.append({
                            'framework': framework,
                            'change_id': change_id,
                            'old_version': active_version['version_tag'],
                            'new_version': version_tag,
                            'summary': diff_summary['summary']
                        })
                        
                        logger.info(f"{framework}: Changes detected - {diff_summary['summary']}")
                else:
                    # First version - auto-activate
                    self._activate_version(framework, new_version_id)
                    logger.info(f"{framework}: Initial version saved and activated")
                
                self._update_polling_status(framework, 'success', None)
            
            except Exception as e:
                logger.error(f"Error checking updates for {framework}: {e}")
                self._update_polling_status(framework, 'error', str(e))
        
        return changes_detected
    
    def _activate_version(self, framework: str, version_id: int):
        """Activate a version and deactivate others."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Deactivate all versions for this framework
        cursor.execute('''
            UPDATE regulation_versions
            SET is_active = 0
            WHERE framework = ?
        ''', (framework,))
        
        # Activate the new version
        cursor.execute('''
            UPDATE regulation_versions
            SET is_active = 1
            WHERE id = ?
        ''', (version_id,))
        
        conn.commit()
        conn.close()
    
    def _update_polling_status(self, framework: str, status: str, error_message: Optional[str]):
        """Update polling status for a framework."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        source = next((s for s in self.sources if s['framework'] == framework), None)
        
        if source:
            poll_interval = timedelta(hours=source.get('poll_interval_hours', 24))
            next_poll = (datetime.now() + poll_interval).isoformat()
        else:
            next_poll = now
        
        cursor.execute('''
            INSERT OR REPLACE INTO polling_status
            (framework, last_polled, next_poll, status, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (framework, now, next_poll, status, error_message))
        
        conn.commit()
        conn.close()
    
    def approve_change(self, change_id: int, reviewed_by: str = 'admin') -> bool:
        """Approve a regulation change and activate the new version."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get change record
        cursor.execute('SELECT * FROM regulation_changes WHERE id = ?', (change_id,))
        change = cursor.fetchone()
        
        if not change:
            conn.close()
            return False
        
        change_dict = dict(change)
        
        # Mark as approved
        cursor.execute('''
            UPDATE regulation_changes
            SET approved = 1, requires_review = 0, reviewed_at = ?, reviewed_by = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), reviewed_by, change_id))
        
        # Activate new version
        self._activate_version(change_dict['framework'], change_dict['new_version_id'])
        
        conn.commit()
        conn.close()
        
        logger.info(f"Change {change_id} approved and version activated for {change_dict['framework']}")
        return True
    
    def reject_change(self, change_id: int, reviewed_by: str = 'admin') -> bool:
        """Reject a regulation change."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE regulation_changes
            SET rejected = 1, requires_review = 0, reviewed_at = ?, reviewed_by = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), reviewed_by, change_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Change {change_id} rejected")
        return True
    
    def get_pending_updates(self) -> List[Dict]:
        """Get all pending regulation updates requiring review."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                rc.*,
                ov.version_tag as old_version_tag,
                nv.version_tag as new_version_tag
            FROM regulation_changes rc
            LEFT JOIN regulation_versions ov ON rc.old_version_id = ov.id
            LEFT JOIN regulation_versions nv ON rc.new_version_id = nv.id
            WHERE rc.requires_review = 1 AND rc.approved = 0 AND rc.rejected = 0
            ORDER BY rc.created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def start_scheduler(self):
        """Start the background scheduler for periodic updates."""
        if self.scheduler_running:
            logger.warning("Scheduler already running")
            return
        
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("Regulation update scheduler started")
    
    def stop_scheduler(self):
        """Stop the background scheduler."""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Regulation update scheduler stopped")
    
    def _scheduler_loop(self):
        """Background scheduler loop."""
        while self.scheduler_running:
            try:
                if not self.sources:
                    time.sleep(3600)  # Wait 1 hour if no sources
                    continue
                
                # Check which frameworks need polling
                conn = sqlite3.connect(str(self.db_path))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get all frameworks from sources
                frameworks = [s['framework'] for s in self.sources]
                placeholders = ','.join('?' * len(frameworks))
                current_time = datetime.now().isoformat()
                
                cursor.execute(f'''
                    SELECT framework FROM polling_status
                    WHERE framework IN ({placeholders})
                    AND (next_poll <= ? OR next_poll IS NULL)
                ''', frameworks + [current_time])
                
                frameworks_to_check = [row['framework'] for row in cursor.fetchall()]
                conn.close()
                
                # If any framework needs checking, or if it's the first run (no status records)
                if frameworks_to_check or len(frameworks_to_check) == 0:
                    try:
                        # check_for_updates() checks all sources and respects polling intervals
                        self.check_for_updates()
                    except Exception as e:
                        logger.error(f"Error in update check: {e}")
                
                # Sleep for 1 hour before next check
                time.sleep(3600)
            
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def get_regulation_version(self, framework: str) -> Optional[str]:
        """Get the active regulation version text for a framework."""
        active_version = self._get_active_version(framework)
        if active_version:
            return active_version.get('raw_text')
        return None

