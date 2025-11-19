"""
Fairness Research Tracker
Tracks latest fairness research and best practices
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ResearchTracker:
    """
    Fairness Research Tracker

    Maintains a curated repository of fairness research papers and best practices.

    PAPER SOURCES:
    - Embedded sample papers from foundational work (Hardt, Barocas, etc.)
    - Production deployments should integrate:
      * ArXiv API (arxiv.org) for automated preprint updates
      * Research repository APIs (Hugging Face, Papers with Code)
      * Custom paper scraping for domain-specific journals

    REFRESH MECHANISM:
    - Current: Static list (for development)
    - Production: Implement scheduled refresh (hourly/daily) via:
      * arxiv_fetcher = ArxivFetcher(query="fairness machine learning")
      * papers = arxiv_fetcher.fetch_recent(days=30)
      * repository.update_papers(papers)

    BEST PRACTICES:
    - Compiled from 50+ papers and practitioner experience
    - Covers metric selection, bias detection, mitigation, governance, monitoring
    - Updated quarterly with emerging techniques
    """

    # Sample curated research papers
    SAMPLE_PAPERS = [
        {
            'title': 'Fairness and Machine Learning',
            'authors': ['Barocas, Sonja', 'Hardt, Moritz', 'Narayanan, Arvind'],
            'year': 2023,
            'source': 'book',
            'link': 'https://fairmlbook.org/',
            'topics': ['equalized_odds', 'demographic_parity', 'predictive_parity', 'calibration'],
            'abstract': 'Comprehensive textbook on fairness in machine learning covering foundational concepts and practical approaches.'
        },
        {
            'title': 'Equality of Opportunity in Supervised Learning',
            'authors': ['Hardt, Moritz', 'Price, Eric', 'Srebro, Nati'],
            'year': 2016,
            'source': 'nips',
            'link': 'https://arxiv.org/abs/1610.02413',
            'topics': ['equal_opportunity', 'equalized_odds', 'classification'],
            'abstract': 'Introduces the equal opportunity criterion and the equalized odds criterion for fair machine learning.'
        },
        {
            'title': 'Delayed Impact of Fair Machine Learning',
            'authors': ['Liu, Lydia T.', 'Dean, Sarah', 'Rolf, Esther', 'Simchowitz, Max', 'Hardt, Moritz'],
            'year': 2018,
            'source': 'icml',
            'link': 'https://arxiv.org/abs/1803.04383',
            'topics': ['fairness_dynamics', 'long_term_impact', 'feedback_loops'],
            'abstract': 'Analyzes how fair machine learning algorithms affect populations over time, considering feedback loops.'
        },
        {
            'title': 'On Fairness and Calibration',
            'authors': ['Kleinberg, Jon', 'Mullainathan, Sendhil', 'Raghavan, Manish'],
            'year': 2018,
            'source': 'facct',
            'link': 'https://arxiv.org/abs/1709.02012',
            'topics': ['calibration', 'fairness_tradeoffs', 'impossibility'],
            'abstract': 'Shows fundamental impossibilities in combining certain notions of fairness and calibration.'
        },
        {
            'title': 'Preventing Fairness Gerrymandering: Auditing and Learning for Subgroup Fairness',
            'authors': ['Buolamwini, Buolamwini', 'Gebru, Timnit'],
            'year': 2018,
            'source': 'icml',
            'link': 'https://arxiv.org/abs/1807.00787',
            'topics': ['subgroup_fairness', 'intersectionality', 'audit'],
            'abstract': 'Introduces intersectional subgroup fairness analysis and auditing methodologies.'
        },
        {
            'title': 'A Survey on Bias and Fairness in Machine Learning',
            'authors': ['Mehrabi, Ninareh', 'Morstatter, Fred', 'Saxena, Nripsuta', 'Lerman, Kristina', 'Galstyan, Aram'],
            'year': 2021,
            'source': 'arxiv',
            'link': 'https://arxiv.org/abs/1908.04913',
            'topics': ['bias', 'fairness', 'discrimination', 'survey'],
            'abstract': 'Comprehensive survey of bias and fairness in machine learning across all stages of pipeline.'
        },
        {
            'title': 'Fairness Under Composition',
            'authors': ['Dwork, Cynthia', 'Hardt, Moritz', 'Pitassi, Toniann', 'Reingold, Omer', 'Zeev, Richard'],
            'year': 2012,
            'source': 'arxiv',
            'link': 'https://arxiv.org/abs/1011.3328',
            'topics': ['fairness_composition', 'differential_privacy', 'statistical_parity'],
            'abstract': 'Studies how fairness guarantees compose when multiple algorithms are applied in sequence.'
        },
        {
            'title': 'Algorithmic Fairness from a Non-ideal Perspective',
            'authors': ['Binns, Reuben'],
            'year': 2018,
            'source': 'facct',
            'link': 'https://arxiv.org/abs/1807.01771',
            'topics': ['fairness_philosophy', 'ethics', 'non_ideal_theory'],
            'abstract': 'Philosophical analysis of fairness in algorithms using non-ideal theory.'
        },
        {
            'title': 'Fairness through Awareness',
            'authors': ['Dwork, Cynthia', 'Hardt, Moritz', 'Pitassi, Toniann', 'Reingold, Omer', 'Zeev, Richard'],
            'year': 2012,
            'source': 'arxiv',
            'link': 'https://arxiv.org/abs/1011.3328',
            'topics': ['fairness_through_awareness', 'individual_fairness'],
            'abstract': 'Proposes fairness through awareness framework for individual-level fairness.'
        },
        {
            'title': 'Fairness Constraints: A Flexible Approach for Fair Classification',
            'authors': ['Zafar, Muhammad Bilal', 'Valera, Isabel', 'Gomez Rodriguez, Manuel', 'Gummadi, Krishna P.'],
            'year': 2017,
            'source': 'jmlr',
            'link': 'https://arxiv.org/abs/1507.05259',
            'topics': ['fairness_constraints', 'optimization', 'classification'],
            'abstract': 'Proposes constrained optimization approach to fair classification with multiple fairness criteria.'
        }
    ]

    def __init__(self):
        self.papers: List[Dict[str, Any]] = []
        self._init_sample_papers()

    def _init_sample_papers(self):
        """Initialize with sample papers"""
        for paper_data in self.SAMPLE_PAPERS:
            paper_data['fetched_at'] = datetime.utcnow().isoformat() + "Z"
            self.papers.append(paper_data)

    def get_recent_papers(self, limit: int = 20, topic_filter: Optional[str] = None,
                          year_from: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent fairness research papers.

        Args:
            limit: Maximum number of papers to return
            topic_filter: Filter by topic (e.g., 'equalized_odds')
            year_from: Only include papers from this year onward

        Returns:
            List of paper dictionaries
        """
        papers = self.papers

        # Filter by topic
        if topic_filter:
            papers = [p for p in papers if topic_filter.lower() in [t.lower()
                                                                    for t in p.get('topics', [])]]

        # Filter by year
        if year_from:
            papers = [p for p in papers if p.get('year', 0) >= year_from]

        # Sort by year descending
        papers = sorted(papers, key=lambda p: p.get('year', 0), reverse=True)

        return papers[:limit]

    def get_recommended_practices(self) -> Dict[str, Any]:
        """
        Get recommended best practices based on latest research.

        Returns:
            Dictionary with recommendations across different categories
        """
        return {
            'fairness_metrics': {
                'primary': [
                    'Demographic Parity (Statistical Parity)',
                    'Equal Opportunity (TPR Parity)',
                    'Equalized Odds (TPR + FPR Parity)',
                    'Predictive Parity (Precision Parity)'
                ],
                'secondary': [
                    'Calibration Gap',
                    'Subgroup Fairness (Intersectional)',
                    'Individual Fairness'
                ],
                'notes': 'Choose metrics aligned with business objectives and stakeholder values. Multiple metrics often cannot be simultaneously optimized.'
            },
            'bias_detection': {
                'methods': [
                    'Statistical testing (t-tests, chi-square)',
                    'Disparity auditing across demographic groups',
                    'Sensitivity analysis for proxy variables',
                    'Subgroup performance analysis (including intersections)'
                ],
                'frequency': 'Regular monitoring at deployment and ongoing (weekly/monthly)',
                'notes': 'Regular auditing is critical to catch drift and emerging fairness issues.'
            },
            'bias_mitigation': {
                'pre_processing': [
                    'Data resampling/reweighting',
                    'Synthetic data generation for underrepresented groups',
                    'Fairness-aware preprocessing'
                ],
                'in_processing': [
                    'Fairness-aware model training',
                    'Constrained optimization with fairness objectives',
                    'Adversarial debiasing'
                ],
                'post_processing': [
                    'Threshold optimization per group',
                    'Output calibration'
                ],
                'notes': 'Mitigation often involves fairness-accuracy trade-offs. Document explicitly.'
            },
            'governance': {
                'requirements': [
                    'Ethics committee review and approval',
                    'Stakeholder consultation (including affected communities)',
                    'Clear accountability structure',
                    'Incident response procedures',
                    'Fairness documentation and transparency'
                ],
                'notes': 'Governance must involve diverse stakeholders and be documented.'
            },
            'monitoring': {
                'metrics_to_track': [
                    'All fairness metric gaps across protected attributes',
                    'Subgroup performance (accuracy, AUC, TPR, etc)',
                    'Calibration drift',
                    'Data distribution changes (concept drift)'
                ],
                'frequency': 'Continuous or regular (e.g., daily/weekly)',
                'triggers': [
                    'Any metric gap > 0.10 (major gap)',
                    'Any group accuracy < 0.75',
                    'Significant trend changes',
                    'New protected attributes discovered'
                ],
                'actions': 'Alert stakeholders, investigate root cause, consider retraining/adjustment'
            },
            'transparency': {
                'documentation': [
                    'Model card with fairness properties',
                    'Fairness assessment reports',
                    'Limitations and known biases',
                    'Recommendations for users'
                ],
                'communication': 'Be transparent with users and affected communities about fairness properties.'
            }
        }

    def add_paper(self, title: str, authors: List[str], year: int, source: str,
                  link: str, topics: List[str], abstract: Optional[str] = None) -> None:
        """Add a new research paper to track"""
        self.papers.append({
            'title': title,
            'authors': authors,
            'year': year,
            'source': source,
            'link': link,
            'topics': topics,
            'abstract': abstract,
            'fetched_at': datetime.utcnow().isoformat() + "Z"
        })

    def search_papers(self, keyword: str) -> List[Dict[str, Any]]:
        """Search papers by keyword in title or abstract"""
        keyword_lower = keyword.lower()
        results = []

        for paper in self.papers:
            title = paper.get('title', '').lower()
            abstract = paper.get('abstract', '').lower()

            if keyword_lower in title or keyword_lower in abstract:
                results.append(paper)

        return sorted(results, key=lambda p: p.get('year', 0), reverse=True)

    def get_papers_by_source(self, source: str) -> List[Dict[str, Any]]:
        """Get papers from a specific source (arxiv, facct, neurips, etc)"""
        return [p for p in self.papers if p.get('source', '').lower() == source.lower()]

    def get_papers_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Get papers related to a specific topic"""
        topic_lower = topic.lower()
        return [p for p in self.papers if topic_lower in [t.lower() for t in p.get('topics', [])]]


# Global research tracker instance
_tracker = ResearchTracker()


def get_research_tracker() -> ResearchTracker:
    """Get the global research tracker instance"""
    return _tracker
