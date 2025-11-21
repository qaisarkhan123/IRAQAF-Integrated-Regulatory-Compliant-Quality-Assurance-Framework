"""
L3 Fairness Research Tracker
Automatically tracks latest fairness research and best practices from academic sources
"""

import requests
import json
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import schedule
import time
import threading

logger = logging.getLogger(__name__)

@dataclass
class ResearchPaper:
    """Research paper data structure"""
    title: str
    authors: List[str]
    abstract: str
    url: str
    published_date: str
    source: str
    categories: List[str]
    relevance_score: float
    keywords_found: List[str]

class ResearchTracker:
    """Fairness research tracker with multiple source monitoring"""
    
    def __init__(self, config_file: str = "config/research_sources.json"):
        self.config_file = Path(config_file)
        self.data_dir = Path("data/research")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Fairness-related keywords for filtering
        self.fairness_keywords = [
            "fairness", "bias", "discrimination", "equity", "algorithmic fairness",
            "demographic parity", "equal opportunity", "equalized odds",
            "disparate impact", "group fairness", "individual fairness",
            "counterfactual fairness", "causal fairness", "intersectional fairness",
            "bias mitigation", "debiasing", "fair machine learning",
            "ethical AI", "responsible AI", "AI ethics"
        ]
    
    def _load_config(self) -> Dict:
        """Load research sources configuration"""
        fairness_keywords = [
            "fairness", "bias", "discrimination", "equity", "algorithmic fairness",
            "demographic parity", "equal opportunity", "equalized odds",
            "disparate impact", "group fairness"
        ]
        
        default_config = {
            "arxiv": {
                "enabled": True,
                "categories": ["cs.LG", "cs.CY", "cs.AI"],
                "keywords": fairness_keywords,
                "frequency": "weekly",
                "max_results": 50
            },
            "facct": {
                "enabled": True,
                "url": "https://facctconference.org/",
                "frequency": "monthly"
            },
            "neurips": {
                "enabled": True,
                "workshop": "fairness-ml",
                "frequency": "annual"
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return default_config
        else:
            # Create default config file
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def calculate_relevance_score(self, title: str, abstract: str) -> tuple:
        """Calculate relevance score based on keyword matching"""
        text = f"{title} {abstract}".lower()
        keywords_found = []
        score = 0.0
        
        for keyword in self.fairness_keywords:
            if keyword.lower() in text:
                keywords_found.append(keyword)
                # Weight keywords by importance
                if keyword in ["fairness", "bias", "discrimination"]:
                    score += 3.0
                elif keyword in ["algorithmic fairness", "fair machine learning"]:
                    score += 2.5
                else:
                    score += 1.0
        
        # Normalize score to 0-100
        max_possible_score = len(self.fairness_keywords) * 3.0
        normalized_score = min((score / max_possible_score) * 100, 100)
        
        return normalized_score, keywords_found
    
    def search_arxiv(self, days_back: int = 7) -> List[ResearchPaper]:
        """Search arXiv for recent fairness papers"""
        papers = []
        
        if not self.config["arxiv"]["enabled"]:
            return papers
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Build arXiv query
            categories = "+OR+".join([f"cat:{cat}" for cat in self.config["arxiv"]["categories"]])
            keywords = "+OR+".join([f'all:"{kw}"' for kw in self.config["arxiv"]["keywords"]])
            
            query = f"({categories})+AND+({keywords})"
            url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results={self.config['arxiv']['max_results']}&sortBy=submittedDate&sortOrder=descending"
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', namespace):
                try:
                    title = entry.find('atom:title', namespace).text.strip()
                    abstract = entry.find('atom:summary', namespace).text.strip()
                    
                    # Calculate relevance
                    relevance_score, keywords_found = self.calculate_relevance_score(title, abstract)
                    
                    # Only include papers with reasonable relevance
                    if relevance_score >= 10.0:
                        authors = [author.find('atom:name', namespace).text 
                                 for author in entry.findall('atom:author', namespace)]
                        
                        url = entry.find('atom:id', namespace).text
                        published = entry.find('atom:published', namespace).text
                        
                        # Get categories
                        categories = [cat.get('term') for cat in entry.findall('atom:category', namespace)]
                        
                        paper = ResearchPaper(
                            title=title,
                            authors=authors,
                            abstract=abstract,
                            url=url,
                            published_date=published,
                            source="arXiv",
                            categories=categories,
                            relevance_score=relevance_score,
                            keywords_found=keywords_found
                        )
                        papers.append(paper)
                
                except Exception as e:
                    logger.error(f"Error parsing arXiv entry: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
        
        return papers
    
    def search_facct_proceedings(self) -> List[ResearchPaper]:
        """Search FAccT conference proceedings (placeholder for actual implementation)"""
        papers = []
        
        if not self.config["facct"]["enabled"]:
            return papers
        
        # This would require web scraping of FAccT proceedings
        # For now, return placeholder data
        logger.info("FAccT proceedings search not yet implemented")
        return papers
    
    def extract_best_practices(self, papers: List[ResearchPaper]) -> List[Dict]:
        """Extract best practices from research papers"""
        best_practices = []
        
        for paper in papers:
            if paper.relevance_score >= 70.0:  # High relevance papers
                practice = {
                    "title": f"Best Practice from: {paper.title[:100]}...",
                    "source": paper.source,
                    "url": paper.url,
                    "practice_type": "research_finding",
                    "keywords": paper.keywords_found,
                    "relevance_score": paper.relevance_score,
                    "extracted_date": datetime.now().isoformat(),
                    "recommendation": self._generate_recommendation(paper)
                }
                best_practices.append(practice)
        
        return best_practices
    
    def _generate_recommendation(self, paper: ResearchPaper) -> str:
        """Generate actionable recommendation from paper"""
        # Simple keyword-based recommendation generation
        if "bias mitigation" in paper.keywords_found:
            return "Consider implementing bias mitigation techniques discussed in this paper"
        elif "fairness metrics" in paper.keywords_found:
            return "Evaluate new fairness metrics proposed in this research"
        elif "algorithmic fairness" in paper.keywords_found:
            return "Review algorithmic fairness approaches for potential integration"
        else:
            return "Review this research for potential fairness improvements"
    
    def save_research_data(self, papers: List[ResearchPaper], best_practices: List[Dict]):
        """Save research data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save papers
        papers_file = self.data_dir / f"papers_{timestamp}.json"
        papers_data = [
            {
                "title": p.title,
                "authors": p.authors,
                "abstract": p.abstract,
                "url": p.url,
                "published_date": p.published_date,
                "source": p.source,
                "categories": p.categories,
                "relevance_score": p.relevance_score,
                "keywords_found": p.keywords_found
            }
            for p in papers
        ]
        
        with open(papers_file, 'w') as f:
            json.dump(papers_data, f, indent=2)
        
        # Save best practices
        practices_file = self.data_dir / f"best_practices_{timestamp}.json"
        with open(practices_file, 'w') as f:
            json.dump(best_practices, f, indent=2)
        
        logger.info(f"Saved {len(papers)} papers and {len(best_practices)} best practices")
    
    def get_latest_research(self, limit: int = 20) -> List[Dict]:
        """Get latest research papers"""
        # Get most recent papers file
        papers_files = list(self.data_dir.glob("papers_*.json"))
        if not papers_files:
            return []
        
        latest_file = max(papers_files, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(latest_file, 'r') as f:
                papers = json.load(f)
            return papers[:limit]
        except Exception as e:
            logger.error(f"Error loading latest research: {e}")
            return []
    
    def get_research_trends(self) -> Dict:
        """Analyze research trends from collected data"""
        # Get all papers from last 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        all_papers = []
        
        for papers_file in self.data_dir.glob("papers_*.json"):
            try:
                with open(papers_file, 'r') as f:
                    papers = json.load(f)
                all_papers.extend(papers)
            except Exception:
                continue
        
        # Analyze trends
        keyword_counts = {}
        category_counts = {}
        
        for paper in all_papers:
            # Count keywords
            for keyword in paper.get("keywords_found", []):
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            # Count categories
            for category in paper.get("categories", []):
                category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total_papers": len(all_papers),
            "trending_keywords": sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "popular_categories": sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "analysis_date": datetime.now().isoformat()
        }
    
    def get_best_practices(self) -> List[Dict]:
        """Get latest best practices"""
        practices_files = list(self.data_dir.glob("best_practices_*.json"))
        if not practices_files:
            return []
        
        latest_file = max(practices_files, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(latest_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading best practices: {e}")
            return []
    
    def run_research_update(self):
        """Run complete research update cycle"""
        logger.info("Starting research update cycle")
        
        try:
            # Search for new papers
            papers = []
            papers.extend(self.search_arxiv(days_back=7))
            papers.extend(self.search_facct_proceedings())
            
            # Extract best practices
            best_practices = self.extract_best_practices(papers)
            
            # Save data
            if papers or best_practices:
                self.save_research_data(papers, best_practices)
                logger.info(f"Research update completed: {len(papers)} papers, {len(best_practices)} practices")
            else:
                logger.info("No new research found")
        
        except Exception as e:
            logger.error(f"Error in research update: {e}")
    
    def start_scheduler(self):
        """Start the research tracking scheduler"""
        # Schedule weekly updates
        schedule.every().monday.at("09:00").do(self.run_research_update)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        # Run scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("Research tracker scheduler started")

# Global research tracker instance
research_tracker = ResearchTracker()

def get_research_tracker() -> ResearchTracker:
    """Get the global research tracker instance"""
    return research_tracker

if __name__ == "__main__":
    # Test the research tracker
    tracker = ResearchTracker()
    
    print("Testing arXiv search...")
    papers = tracker.search_arxiv(days_back=30)
    print(f"Found {len(papers)} papers")
    
    if papers:
        print(f"Sample paper: {papers[0].title}")
        print(f"Relevance score: {papers[0].relevance_score}")
        print(f"Keywords found: {papers[0].keywords_found}")
        
        # Extract best practices
        practices = tracker.extract_best_practices(papers)
        print(f"Extracted {len(practices)} best practices")
        
        # Save data
        tracker.save_research_data(papers, practices)
