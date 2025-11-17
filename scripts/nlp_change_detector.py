#!/usr/bin/env python
"""
NLP-Based Regulatory Change Detector
Uses semantic similarity to detect meaningful changes in regulations
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import re

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
except ImportError:
    print("Install required packages: pip install scikit-learn numpy")
    raise

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class NLPChangeDetector:
    """Detect semantic changes in regulatory documents"""
    
    def __init__(self, similarity_threshold: float = 0.75):
        """
        Args:
            similarity_threshold: Cosine similarity threshold for detecting changes (0-1)
                                 Lower = more sensitive to changes
        """
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
    def extract_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
        
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts"""
        try:
            # Ensure we have both texts
            if not text1 or not text2:
                return 0.0
                
            # Create TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
            return float(similarity)
        except Exception as e:
            logger.warning(f"Similarity computation error: {e}")
            return 0.5
            
    def detect_clause_changes(self, old_text: str, new_text: str) -> Dict[str, any]:
        """Detect changes at clause/sentence level"""
        old_sentences = self.extract_sentences(old_text)
        new_sentences = self.extract_sentences(new_text)
        
        changes = {
            'total_old_clauses': len(old_sentences),
            'total_new_clauses': len(new_sentences),
            'added_clauses': [],
            'removed_clauses': [],
            'modified_clauses': [],
            'similarity_score': 0.0
        }
        
        # Compute overall similarity
        if old_sentences and new_sentences:
            old_text_clean = ' '.join(old_sentences)
            new_text_clean = ' '.join(new_sentences)
            changes['similarity_score'] = self.compute_similarity(old_text_clean, new_text_clean)
        
        # Find clause-level changes
        matched_new = set()
        
        for old_clause in old_sentences:
            best_match = None
            best_score = 0.0
            best_idx = -1
            
            for idx, new_clause in enumerate(new_sentences):
                if idx in matched_new:
                    continue
                    
                score = self.compute_similarity(old_clause, new_clause)
                if score > best_score:
                    best_score = score
                    best_match = new_clause
                    best_idx = idx
            
            if best_score < self.similarity_threshold:
                # Clause was removed or significantly changed
                changes['removed_clauses'].append({
                    'text': old_clause[:100],
                    'confidence': 1.0 - best_score
                })
            elif best_score < 0.95:
                # Clause was modified
                changes['modified_clauses'].append({
                    'old_text': old_clause[:100],
                    'new_text': best_match[:100],
                    'similarity': best_score
                })
                matched_new.add(best_idx)
            else:
                matched_new.add(best_idx)
        
        # Find added clauses
        for idx, new_clause in enumerate(new_sentences):
            if idx not in matched_new:
                changes['added_clauses'].append({
                    'text': new_clause[:100]
                })
        
        return changes
        
    def extract_key_topics(self, text: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """Extract key topics from text"""
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        
        # Calculate word frequencies
        word_freq = {}
        for word in words:
            # Filter out common words
            if len(word) > 4 and word not in {'article', 'section', 'clause', 'shall'}:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return sorted_words[:top_n]
        
    def classify_severity(self, changes: Dict) -> str:
        """Classify change severity: critical, high, medium, low"""
        added = len(changes.get('added_clauses', []))
        removed = len(changes.get('removed_clauses', []))
        modified_clauses = changes.get('modified_clauses', [])
        similarity = changes.get('similarity_score', 1.0)
        
        # Count significant changes
        significant_changes = added + removed + len([m for m in modified_clauses if m.get('similarity', 1.0) < 0.8])
        
        if similarity < 0.5 or significant_changes > 5:
            return 'CRITICAL'
        elif similarity < 0.7 or significant_changes > 3:
            return 'HIGH'
        elif similarity < 0.85 or significant_changes > 1:
            return 'MEDIUM'
        else:
            return 'LOW'
            
    def generate_summary(self, regulation: Dict, changes: Dict) -> str:
        """Generate human-readable summary of changes"""
        severity = self.classify_severity(changes)
        
        summary = f"""
🔍 REGULATORY CHANGE DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Regulation: {regulation.get('title', 'Unknown')}
📅 Date: {regulation.get('date', 'Unknown')}
🏷️  Severity: {severity}
📊 Similarity: {changes.get('similarity_score', 0):.1%}

📈 CHANGE SUMMARY:
  • New clauses: {len(changes.get('added_clauses', []))}
  • Removed clauses: {len(changes.get('removed_clauses', []))}
  • Modified clauses: {len(changes.get('modified_clauses', []))}

{self._format_changes(changes)}

🎯 ACTION REQUIRED: Review regulation and update IRAQAF trace_map.yaml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return summary
        
    def _format_changes(self, changes: Dict) -> str:
        """Format changes for display"""
        output = []
        
        if changes.get('added_clauses'):
            output.append("➕ NEW CLAUSES:")
            for clause in changes['added_clauses'][:3]:
                output.append(f"   • {clause['text']}")
        
        if changes.get('removed_clauses'):
            output.append("➖ REMOVED CLAUSES:")
            for clause in changes['removed_clauses'][:3]:
                output.append(f"   • {clause['text']}")
        
        if changes.get('modified_clauses'):
            output.append("🔄 MODIFIED CLAUSES:")
            for clause in changes['modified_clauses'][:3]:
                similarity = clause.get('similarity', 0)
                output.append(f"   • {clause['old_text']} → {clause['new_text']} ({similarity:.0%})")
        
        return '\n'.join(output)


class ChangeTracker:
    """Track historical changes to regulations"""
    
    def __init__(self, history_file: str = 'regulatory_data/change_history.json'):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(exist_ok=True)
        
    def load_history(self) -> Dict[str, List[Dict]]:
        """Load change history"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {}
        
    def save_change(self, regulation_id: str, change_data: Dict) -> None:
        """Save a detected change"""
        history = self.load_history()
        
        if regulation_id not in history:
            history[regulation_id] = []
        
        history[regulation_id].append({
            'timestamp': datetime.now().isoformat(),
            **change_data
        })
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
            
        logger.info(f"Change saved for {regulation_id}")
        
    def get_regulation_timeline(self, regulation_id: str) -> List[Dict]:
        """Get change history for a regulation"""
        history = self.load_history()
        return history.get(regulation_id, [])


def main():
    """Example usage"""
    detector = NLPChangeDetector(similarity_threshold=0.75)
    tracker = ChangeTracker()
    
    # Example: Compare old and new GDPR text
    old_text = """
    Article 4: Definitions. Personal data means any information relating to an identified 
    or identifiable natural person. Processing means any operation performed on personal data. 
    Data controller means the person who determines the purposes and means of processing.
    """
    
    new_text = """
    Article 4: Definitions. Personal data means any information relating to an identified 
    or identifiable natural person, including biometric data. Processing means any operation 
    performed on personal data, including automated decision-making. Data controller means 
    the person who determines the purposes and means of processing, including third parties.
    """
    
    logger.info("Analyzing regulatory changes...")
    changes = detector.detect_clause_changes(old_text, new_text)
    
    regulation = {
        'title': 'GDPR Article 4 Update',
        'date': datetime.now().isoformat()
    }
    
    summary = detector.generate_summary(regulation, changes)
    logger.info(summary)
    
    # Extract key topics
    topics = detector.extract_key_topics(new_text)
    logger.info(f"Key topics: {topics}")
    
    # Save to history
    tracker.save_change('GDPR-Article-4', changes)
    
    # Show timeline
    timeline = tracker.get_regulation_timeline('GDPR-Article-4')
    logger.info(f"Regulation has {len(timeline)} tracked changes")


if __name__ == '__main__':
    main()
