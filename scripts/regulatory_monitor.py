#!/usr/bin/env python
"""
Regulatory Monitoring Service
Monitors healthcare regulations (GDPR, HIPAA, EU AI Act) for real-time changes
Uses web scraping, APIs, and NLP-based change detection
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
import re

try:
    import requests
    from bs4 import BeautifulSoup
    import feedparser
except ImportError:
    print("Install required packages: pip install requests beautifulsoup4 feedparser")
    raise

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RegulatorySource:
    """Base class for regulatory data sources"""
    
    def __init__(self, name: str, source_type: str, url: str, headers: Optional[Dict] = None):
        self.name = name
        self.source_type = source_type  # 'web', 'api', 'rss'
        self.url = url
        self.headers = headers or {
            'User-Agent': 'IRAQAF-Regulatory-Monitor/1.0 (+https://github.com/iraqaf)'
        }
        self.session = requests.Session()
        
    def fetch(self) -> Optional[str]:
        """Fetch content from source"""
        raise NotImplementedError
        
    def parse(self, content: str) -> List[Dict]:
        """Parse fetched content into structured data"""
        raise NotImplementedError


class WebScraperSource(RegulatorySource):
    """Web scraper for HTML-based regulatory sources"""
    
    def __init__(self, name: str, url: str, selectors: Dict[str, str]):
        super().__init__(name, 'web', url)
        self.selectors = selectors  # CSS selectors for title, date, content
        
    def fetch(self) -> Optional[str]:
        """Fetch HTML content with retries"""
        try:
            response = self.session.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ Fetched {self.name}: {len(response.text)} bytes")
            return response.text
        except requests.RequestException as e:
            logger.error(f"❌ Failed to fetch {self.name}: {e}")
            return None
            
    def parse(self, html: str) -> List[Dict]:
        """Extract regulatory documents from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        documents = []
        
        # Find all regulation entries using CSS selectors
        items = soup.select(self.selectors.get('items', 'div.regulation-item'))
        
        for item in items[:10]:  # Limit to recent 10
            try:
                title_elem = item.select_one(self.selectors.get('title', 'h2'))
                date_elem = item.select_one(self.selectors.get('date', '.date'))
                content_elem = item.select_one(self.selectors.get('content', '.content'))
                
                if title_elem:
                    doc = {
                        'title': title_elem.get_text(strip=True),
                        'date': date_elem.get_text(strip=True) if date_elem else 'Unknown',
                        'content': content_elem.get_text(strip=True) if content_elem else '',
                        'url': item.get('href', self.url),
                        'source': self.name,
                        'fetched_at': datetime.now().isoformat()
                    }
                    documents.append(doc)
            except Exception as e:
                logger.warning(f"Error parsing item: {e}")
                continue
                
        return documents


class APISource(RegulatorySource):
    """API-based regulatory data source"""
    
    def __init__(self, name: str, url: str, params: Optional[Dict] = None):
        super().__init__(name, 'api', url)
        self.params = params or {}
        
    def fetch(self) -> Optional[str]:
        """Fetch from API"""
        try:
            response = self.session.get(self.url, headers=self.headers, 
                                       params=self.params, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ Fetched from {self.name} API")
            return response.text
        except requests.RequestException as e:
            logger.error(f"❌ API fetch failed for {self.name}: {e}")
            return None
            
    def parse(self, json_str: str) -> List[Dict]:
        """Parse JSON API response"""
        try:
            data = json.loads(json_str)
            documents = []
            
            # Handle different API response formats
            results = data.get('results', [])
            if not results:
                results = data.get('items', [])
            if not results and isinstance(data, list):
                results = data
                
            for item in results[:10]:
                doc = {
                    'title': item.get('title', item.get('name', 'Untitled')),
                    'date': item.get('date', item.get('published_date', 'Unknown')),
                    'content': item.get('summary', item.get('description', '')),
                    'url': item.get('url', item.get('link', self.url)),
                    'source': self.name,
                    'fetched_at': datetime.now().isoformat()
                }
                documents.append(doc)
                
            logger.info(f"Parsed {len(documents)} documents from {self.name}")
            return documents
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error for {self.name}: {e}")
            return []


class RSSSource(RegulatorySource):
    """RSS feed-based regulatory updates"""
    
    def __init__(self, name: str, url: str):
        super().__init__(name, 'rss', url)
        
    def fetch(self) -> Optional[str]:
        """Fetch RSS feed"""
        try:
            response = self.session.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ Fetched RSS feed: {self.name}")
            return response.text
        except requests.RequestException as e:
            logger.error(f"❌ RSS fetch failed for {self.name}: {e}")
            return None
            
    def parse(self, feed_data: str) -> List[Dict]:
        """Parse RSS feed"""
        feed = feedparser.parse(feed_data)
        documents = []
        
        for entry in feed.entries[:10]:
            doc = {
                'title': entry.get('title', 'Untitled'),
                'date': entry.get('published', entry.get('updated', 'Unknown')),
                'content': entry.get('summary', entry.get('description', '')),
                'url': entry.get('link', self.url),
                'source': self.name,
                'fetched_at': datetime.now().isoformat()
            }
            documents.append(doc)
            
        logger.info(f"Parsed {len(documents)} entries from {self.name} RSS")
        return documents


class RegulatoryMonitor:
    """Main regulatory monitoring service"""
    
    def __init__(self, data_dir: str = 'regulatory_data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.sources: Dict[str, RegulatorySource] = {}
        self.cache_file = self.data_dir / 'regulations_cache.json'
        self.changes_file = self.data_dir / 'detected_changes.json'
        
    def register_source(self, source: RegulatorySource) -> None:
        """Register a regulatory data source"""
        self.sources[source.name] = source
        logger.info(f"Registered source: {source.name}")
        
    def fetch_all(self) -> Dict[str, List[Dict]]:
        """Fetch from all registered sources"""
        all_documents = {}
        
        for name, source in self.sources.items():
            logger.info(f"Fetching from {name}...")
            content = source.fetch()
            if content:
                documents = source.parse(content)
                all_documents[name] = documents
                logger.info(f"✅ {name}: {len(documents)} documents")
            else:
                all_documents[name] = []
                
        return all_documents
        
    def save_cache(self, documents: Dict[str, List[Dict]]) -> None:
        """Save fetched documents to cache"""
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'documents': documents
        }
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        logger.info(f"Cache saved: {self.cache_file}")
        
    def load_cache(self) -> Dict[str, List[Dict]]:
        """Load cached documents"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                return data.get('documents', {})
        return {}
        
    def compute_hash(self, content: str) -> str:
        """Compute hash of content for change detection"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
        
    def extract_clauses(self, text: str) -> List[str]:
        """Extract clauses/sections from regulation text"""
        # Split by numbered sections (Article X, Section X, etc.)
        pattern = r'(?:Article|Section|§|Clause)\s+\d+(?:\.\d+)*'
        matches = re.finditer(pattern, text)
        
        clauses = []
        positions = [(m.start(), m.group()) for m in matches]
        
        for i, (start, clause_label) in enumerate(positions):
            end = positions[i+1][0] if i+1 < len(positions) else len(text)
            clause_text = text[start:end]
            clauses.append({
                'label': clause_label,
                'text': clause_text[:500]  # Limit to 500 chars
            })
            
        return clauses
        
    def detect_changes(self) -> Dict[str, any]:
        """Detect changes from previous fetch"""
        current = self.fetch_all()
        previous = self.load_cache()
        
        changes = {
            'timestamp': datetime.now().isoformat(),
            'new_regulations': [],
            'updated_regulations': [],
            'affected_modules': set()
        }
        
        for source_name, current_docs in current.items():
            previous_docs = previous.get(source_name, [])
            
            # Build index of previous by title hash
            prev_index = {
                self.compute_hash(doc.get('title', '')): doc 
                for doc in previous_docs
            }
            
            for doc in current_docs:
                doc_hash = self.compute_hash(doc.get('title', ''))
                
                if doc_hash not in prev_index:
                    # New regulation
                    changes['new_regulations'].append(doc)
                    changes['affected_modules'].add(self._map_to_module(doc, source_name))
                else:
                    # Check if content changed
                    prev_content = prev_index[doc_hash].get('content', '')
                    curr_content = doc.get('content', '')
                    
                    if self.compute_hash(prev_content) != self.compute_hash(curr_content):
                        changes['updated_regulations'].append({
                            'doc': doc,
                            'previous_content': prev_content[:200],
                            'new_content': curr_content[:200]
                        })
                        changes['affected_modules'].add(self._map_to_module(doc, source_name))
        
        # Save changes
        with open(self.changes_file, 'w') as f:
            changes['affected_modules'] = list(changes['affected_modules'])
            json.dump(changes, f, indent=2)
            
        logger.info(f"Change detection: {len(changes['new_regulations'])} new, "
                   f"{len(changes['updated_regulations'])} updated")
        
        return changes
        
    def _map_to_module(self, doc: Dict, source: str) -> str:
        """Map regulatory document to IRAQAF module (L1-L5)"""
        title = (doc.get('title', '') + doc.get('content', '')).lower()
        
        # GDPR → Governance + Privacy (L1, L2)
        if 'gdpr' in title or 'personal data' in title:
            return 'L1-Governance' if 'consent' in title else 'L2-Privacy'
            
        # HIPAA → Privacy + Operations (L2, L5)
        if 'hipaa' in title or 'phi' in title or 'protected health':
            return 'L2-Privacy'
            
        # EU AI Act → Fairness + Explainability (L3, L4)
        if 'ai act' in title or 'artificial intelligence' in title:
            return 'L3-Fairness' if 'bias' in title else 'L4-Explainability'
            
        return 'L1-Governance'  # Default


def main():
    """Example usage"""
    monitor = RegulatoryMonitor()
    
    # Register data sources
    
    # GDPR from Official Journal (RSS)
    gdpr_rss = RSSSource(
        'GDPR-Official',
        'https://eur-lex.europa.eu/rss/oj-l-all.xml'
    )
    monitor.register_source(gdpr_rss)
    
    # HIPAA from HHS (API)
    hipaa_api = APISource(
        'HIPAA-HHS',
        'https://www.hhs.gov/hipaa/for-professionals/index.html'
    )
    monitor.register_source(hipaa_api)
    
    # EU AI Act from EUR-Lex (RSS)
    ai_act_rss = RSSSource(
        'EU-AI-Act',
        'https://eur-lex.europa.eu/rss/oj-c-all.xml'
    )
    monitor.register_source(ai_act_rss)
    
    # Fetch all sources
    logger.info("=" * 60)
    logger.info("Starting regulatory monitoring...")
    logger.info("=" * 60)
    
    documents = monitor.fetch_all()
    monitor.save_cache(documents)
    
    # Detect changes
    changes = monitor.detect_changes()
    
    # Report results
    logger.info("=" * 60)
    logger.info("MONITORING RESULTS")
    logger.info("=" * 60)
    logger.info(f"New Regulations: {len(changes['new_regulations'])}")
    logger.info(f"Updated Regulations: {len(changes['updated_regulations'])}")
    logger.info(f"Affected Modules: {changes['affected_modules']}")
    
    for reg in changes['new_regulations']:
        logger.info(f"  📋 NEW: {reg['title'][:60]} ({reg['source']})")
        
    for update in changes['updated_regulations']:
        logger.info(f"  🔄 UPDATED: {update['doc']['title'][:60]}")
    
    logger.info("=" * 60)
    
    return changes


if __name__ == '__main__':
    main()
