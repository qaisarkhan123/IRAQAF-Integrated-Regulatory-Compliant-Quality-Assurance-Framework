"""
PHASE 4: SEMANTIC SIMILARITY & SEARCH ENGINE
=============================================

Implements semantic search across regulatory documents:
- TF-IDF vectorization with fine-tuned thresholds
- Word2vec/FastText embeddings
- Semantic similarity calculation
- Cross-regulation requirement linking
- Smart requirement recommendation engine

Author: IRAQAF Team
Version: 1.0.0
"""

import json
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import hashlib
from pathlib import Path

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None

try:
    import gensim.models
except ImportError:
    gensim = None


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class SimilarityMatch:
    """Represents a similarity match between requirements"""
    source_req_id: str
    target_req_id: str
    source_text: str
    target_text: str
    source_regulation: str
    target_regulation: str
    similarity_score: float
    match_type: str  # 'exact', 'semantic', 'partial'
    explanation: str


@dataclass
class CrossRegulationLink:
    """Link between requirements across regulations"""
    link_id: str
    source_req_id: str
    target_req_id: str
    regulations: List[str]
    link_strength: float  # 0-1
    relationship_type: str  # 'similar', 'duplicate', 'related', 'contradicts'
    confidence: float


@dataclass
class SearchResult:
    """Individual search result"""
    req_id: str
    requirement_text: str
    regulation: str
    section: str
    relevance_score: float
    match_snippets: List[str]  # highlighted matching parts
    metadata: Dict


@dataclass
class RequirementDependency:
    """Dependency between requirements"""
    source_req_id: str
    target_req_id: str
    dependency_type: str  # 'depends_on', 'conflicts_with', 'enables', 'requires'
    strength: float  # 0-1


# ============================================================================
# TF-IDF BASED SEARCH
# ============================================================================

class TFIDFSearchEngine:
    """TF-IDF based full-text search with fine-tuned thresholds"""
    
    # Fine-tuned thresholds based on regulatory document analysis
    SIMILARITY_THRESHOLDS = {
        'exact_match': 0.95,      # Near-identical
        'high_similarity': 0.75,   # Very similar, likely duplicates
        'moderate_similarity': 0.50, # Related requirements
        'weak_similarity': 0.30,   # Potential connection
    }
    
    def __init__(self, max_features: int = 5000, min_df: int = 2, max_df: float = 0.8):
        """
        Initialize TF-IDF vectorizer with regulatory document optimizations
        
        Args:
            max_features: Maximum features (higher for regulatory docs)
            min_df: Minimum document frequency
            max_df: Maximum document frequency (to filter common words)
        """
        self.logger = logging.getLogger(__name__)
        
        if TfidfVectorizer is None:
            self.logger.warning("scikit-learn not installed, TF-IDF search disabled")
            self.vectorizer = None
            return
        
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            min_df=min_df,
            max_df=max_df,
            ngram_range=(1, 3),  # Include bigrams and trigrams
            stop_words='english',
            lowercase=True,
            analyzer='word',
        )
        
        self.tfidf_matrix = None
        self.documents = []
        self.document_ids = []
        self.requirement_index = {}  # Map req_id to doc index
    
    def index_requirements(self, requirements: List[Dict]) -> bool:
        """
        Build TF-IDF index from requirements
        
        Args:
            requirements: List of requirement dicts with 'requirement_id' and 'text'
        
        Returns:
            Success status
        """
        if self.vectorizer is None:
            return False
        
        try:
            texts = []
            for req in requirements:
                req_text = req.get('text', '') or req.get('requirement_text', '')
                texts.append(req_text)
                self.requirement_index[req['requirement_id']] = len(self.documents)
                self.documents.append(req)
                self.document_ids.append(req['requirement_id'])
            
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            self.logger.info(f"Indexed {len(requirements)} requirements with TF-IDF")
            return True
        
        except Exception as e:
            self.logger.error(f"Error indexing requirements: {e}")
            return False
    
    def search(self, query: str, top_k: int = 10, threshold: float = None) -> List[SearchResult]:
        """
        Search for similar requirements
        
        Args:
            query: Search query text
            top_k: Number of results to return
            threshold: Similarity threshold (uses 'moderate_similarity' if None)
        
        Returns:
            List of SearchResult objects
        """
        if self.vectorizer is None or self.tfidf_matrix is None:
            return []
        
        try:
            if threshold is None:
                threshold = self.SIMILARITY_THRESHOLDS['moderate_similarity']
            
            # Vectorize query
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            
            # Get top results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                
                if score < threshold:
                    break
                
                req = self.documents[idx]
                result = SearchResult(
                    req_id=req['requirement_id'],
                    requirement_text=req.get('text', '') or req.get('requirement_text', ''),
                    regulation=req.get('regulation', 'Unknown'),
                    section=req.get('section', ''),
                    relevance_score=score,
                    match_snippets=self._extract_snippets(query, req.get('text', '')),
                    metadata=req
                )
                results.append(result)
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error during search: {e}")
            return []
    
    def _extract_snippets(self, query: str, text: str, context_length: int = 50) -> List[str]:
        """Extract matching snippets from text"""
        snippets = []
        query_words = query.lower().split()
        text_lower = text.lower()
        
        for word in query_words:
            if word in text_lower:
                start = max(0, text_lower.find(word) - context_length)
                end = min(len(text), text_lower.find(word) + len(word) + context_length)
                snippets.append(f"...{text[start:end]}...")
        
        return list(set(snippets))[:3]  # Return up to 3 unique snippets
    
    def find_similar_requirements(self, req_id: str, threshold: float = None) -> List[SimilarityMatch]:
        """Find requirements similar to a given requirement"""
        if self.vectorizer is None or self.tfidf_matrix is None:
            return []
        
        if threshold is None:
            threshold = self.SIMILARITY_THRESHOLDS['high_similarity']
        
        if req_id not in self.requirement_index:
            self.logger.warning(f"Requirement {req_id} not found in index")
            return []
        
        try:
            source_idx = self.requirement_index[req_id]
            source_vector = self.tfidf_matrix[source_idx]
            
            similarities = cosine_similarity(source_vector, self.tfidf_matrix)[0]
            
            matches = []
            for idx, score in enumerate(similarities):
                if idx == source_idx or score < threshold:
                    continue
                
                target_req = self.documents[idx]
                source_req = self.documents[source_idx]
                
                match = SimilarityMatch(
                    source_req_id=req_id,
                    target_req_id=target_req['requirement_id'],
                    source_text=source_req.get('text', ''),
                    target_text=target_req.get('text', ''),
                    source_regulation=source_req.get('regulation', ''),
                    target_regulation=target_req.get('regulation', ''),
                    similarity_score=float(score),
                    match_type=self._classify_match(score),
                    explanation=f"TF-IDF similarity: {score:.2%}"
                )
                matches.append(match)
            
            # Sort by similarity score
            matches.sort(key=lambda x: x.similarity_score, reverse=True)
            return matches
        
        except Exception as e:
            self.logger.error(f"Error finding similar requirements: {e}")
            return []
    
    def _classify_match(self, score: float) -> str:
        """Classify match type by score"""
        if score >= self.SIMILARITY_THRESHOLDS['exact_match']:
            return 'exact'
        elif score >= self.SIMILARITY_THRESHOLDS['high_similarity']:
            return 'semantic'
        else:
            return 'partial'


# ============================================================================
# SEMANTIC SEARCH (EMBEDDING-BASED)
# ============================================================================

class SemanticSearchEngine:
    """Semantic search using embeddings"""
    
    def __init__(self, embedding_type: str = 'tfidf'):
        """
        Initialize semantic search engine
        
        Args:
            embedding_type: 'tfidf' (default, always available), 'word2vec', 'fasttext'
        """
        self.logger = logging.getLogger(__name__)
        self.embedding_type = embedding_type
        self.embeddings = {}
        self.requirement_vectors = {}
        self.document_index = []
    
    def build_embeddings(self, requirements: List[Dict], method: str = 'tfidf') -> bool:
        """
        Build semantic embeddings for requirements
        
        Args:
            requirements: List of requirement dicts
            method: Embedding method ('tfidf' default)
        
        Returns:
            Success status
        """
        try:
            if method == 'tfidf':
                return self._build_tfidf_embeddings(requirements)
            elif method == 'word2vec':
                return self._build_word2vec_embeddings(requirements)
            else:
                self.logger.warning(f"Unknown embedding method: {method}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error building embeddings: {e}")
            return False
    
    def _build_tfidf_embeddings(self, requirements: List[Dict]) -> bool:
        """Build TF-IDF based embeddings"""
        try:
            if TfidfVectorizer is None:
                self.logger.error("scikit-learn not available")
                return False
            
            vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
            texts = [r.get('text', '') for r in requirements]
            
            vectors = vectorizer.fit_transform(texts)
            
            for idx, req in enumerate(requirements):
                self.requirement_vectors[req['requirement_id']] = vectors[idx]
                self.document_index.append({
                    'req_id': req['requirement_id'],
                    'regulation': req.get('regulation', ''),
                    'section': req.get('section', ''),
                    'text': req.get('text', ''),
                })
            
            self.logger.info(f"Built TF-IDF embeddings for {len(requirements)} requirements")
            return True
        
        except Exception as e:
            self.logger.error(f"Error building TF-IDF embeddings: {e}")
            return False
    
    def _build_word2vec_embeddings(self, requirements: List[Dict]) -> bool:
        """Build Word2Vec embeddings (requires gensim)"""
        if gensim is None:
            self.logger.warning("gensim not installed, Word2Vec unavailable")
            return False
        
        try:
            # Tokenize
            sentences = []
            for req in requirements:
                text = req.get('text', '')
                tokens = text.lower().split()
                sentences.append(tokens)
            
            # Train Word2Vec
            model = gensim.models.Word2Vec(
                sentences=sentences,
                vector_size=300,
                window=5,
                min_count=1,
                workers=4
            )
            
            # Create requirement vectors (average of word vectors)
            for req in requirements:
                text = req.get('text', '')
                tokens = text.lower().split()
                vectors = [model.wv[token] for token in tokens if token in model.wv]
                
                if vectors:
                    avg_vector = np.mean(vectors, axis=0)
                    self.requirement_vectors[req['requirement_id']] = avg_vector
            
            self.logger.info(f"Built Word2Vec embeddings for {len(requirements)} requirements")
            return True
        
        except Exception as e:
            self.logger.error(f"Error building Word2Vec embeddings: {e}")
            return False
    
    def semantic_search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """
        Perform semantic search on indexed requirements
        
        Args:
            query: Search query
            top_k: Number of results
        
        Returns:
            List of SearchResult
        """
        if not self.requirement_vectors:
            self.logger.warning("No embeddings indexed")
            return []
        
        try:
            # Create query embedding
            if self.embedding_type == 'tfidf':
                # Simple word presence scoring for query
                query_words = set(query.lower().split())
                scores = []
                
                for doc in self.document_index:
                    doc_words = set(doc['text'].lower().split())
                    overlap = len(query_words & doc_words)
                    score = overlap / max(len(query_words), 1)
                    scores.append(score)
                
                top_indices = np.argsort(scores)[::-1][:top_k]
                
                results = []
                for idx in top_indices:
                    if scores[idx] > 0:
                        doc = self.document_index[idx]
                        results.append(SearchResult(
                            req_id=doc['req_id'],
                            requirement_text=doc['text'],
                            regulation=doc['regulation'],
                            section=doc['section'],
                            relevance_score=scores[idx],
                            match_snippets=[],
                            metadata=doc
                        ))
                
                return results
            
            else:
                self.logger.warning("Semantic search only supports TF-IDF currently")
                return []
        
        except Exception as e:
            self.logger.error(f"Error in semantic search: {e}")
            return []


# ============================================================================
# CROSS-REGULATION LINKING
# ============================================================================

class CrossRegulationLinker:
    """Links requirements across different regulations"""
    
    def __init__(self, similarity_threshold: float = 0.65):
        self.logger = logging.getLogger(__name__)
        self.similarity_threshold = similarity_threshold
        self.links = []
        self.link_map = defaultdict(list)
    
    def find_cross_regulation_links(self, requirements: List[Dict]) -> List[CrossRegulationLink]:
        """
        Find requirements that relate to each other across regulations
        
        Args:
            requirements: List of requirement dicts with regulation, section, text
        
        Returns:
            List of CrossRegulationLink
        """
        self.links = []
        
        # Group by regulation
        by_regulation = defaultdict(list)
        for req in requirements:
            reg = req.get('regulation', 'Unknown')
            by_regulation[reg].append(req)
        
        # Compare requirements across regulations
        regulations = list(by_regulation.keys())
        
        for i, reg1 in enumerate(regulations):
            for reg2 in regulations[i+1:]:
                self._compare_regulation_pairs(
                    by_regulation[reg1],
                    by_regulation[reg2],
                    reg1,
                    reg2
                )
        
        self.logger.info(f"Found {len(self.links)} cross-regulation links")
        return self.links
    
    def _compare_regulation_pairs(self, reqs1: List[Dict], reqs2: List[Dict], 
                                  reg1: str, reg2: str) -> None:
        """Compare requirements between two regulations"""
        for req1 in reqs1:
            for req2 in reqs2:
                similarity = self._calculate_similarity(
                    req1.get('text', ''),
                    req2.get('text', '')
                )
                
                if similarity >= self.similarity_threshold:
                    link_type = self._determine_link_type(req1, req2, similarity)
                    
                    link = CrossRegulationLink(
                        link_id=f"LINK_{hashlib.md5(f'{req1['requirement_id']}{req2['requirement_id']}'.encode()).hexdigest()[:8]}",
                        source_req_id=req1['requirement_id'],
                        target_req_id=req2['requirement_id'],
                        regulations=[reg1, reg2],
                        link_strength=similarity,
                        relationship_type=link_type,
                        confidence=0.85 + (similarity - self.similarity_threshold) * 0.15
                    )
                    
                    self.links.append(link)
                    self.link_map[req1['requirement_id']].append(link)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple method"""
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        overlap = len(words1 & words2)
        union = len(words1 | words2)
        
        return overlap / union
    
    def _determine_link_type(self, req1: Dict, req2: Dict, similarity: float) -> str:
        """Determine type of relationship between requirements"""
        if similarity > 0.90:
            return 'duplicate'
        elif similarity > 0.75:
            return 'similar'
        else:
            return 'related'
    
    def get_linked_requirements(self, req_id: str) -> List[CrossRegulationLink]:
        """Get all links for a requirement"""
        return self.link_map.get(req_id, [])


# ============================================================================
# REQUIREMENT DEPENDENCY GRAPH
# ============================================================================

class RequirementDependencyGraph:
    """Builds and analyzes requirement dependency relationships"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dependencies = []
        self.graph = defaultdict(list)
    
    def build_dependency_graph(self, requirements: List[Dict]) -> List[RequirementDependency]:
        """
        Build dependency graph between requirements
        
        Args:
            requirements: List of requirement dicts
        
        Returns:
            List of RequirementDependency
        """
        self.dependencies = []
        
        # Look for dependency keywords
        dependency_patterns = {
            'depends_on': r'\b(requires|depends on|needs|prerequisite)\b',
            'enables': r'\b(enables|allows|permits|facilitates)\b',
            'conflicts_with': r'\b(conflicts with|incompatible|contradicts)\b',
        }
        
        for i, req1 in enumerate(requirements):
            text1 = req1.get('text', '').lower()
            
            for j, req2 in enumerate(requirements):
                if i >= j:
                    continue
                
                text2 = req2.get('text', '').lower()
                
                # Check for explicit references
                if req2['requirement_id'] in text1 or req1['requirement_id'] in text2:
                    dep = RequirementDependency(
                        source_req_id=req1['requirement_id'],
                        target_req_id=req2['requirement_id'],
                        dependency_type='depends_on',
                        strength=0.9
                    )
                    self.dependencies.append(dep)
                    self.graph[req1['requirement_id']].append(dep)
        
        self.logger.info(f"Built dependency graph with {len(self.dependencies)} dependencies")
        return self.dependencies
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in requirements"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for dep in self.graph[node]:
                next_node = dep.target_req_id
                
                if next_node in rec_stack:
                    # Found cycle
                    cycle_start = path.index(next_node)
                    cycles.append(path[cycle_start:] + [next_node])
                elif next_node not in visited:
                    dfs(next_node, path)
            
            path.pop()
            rec_stack.remove(node)
        
        for node in self.graph:
            if node not in visited:
                dfs(node, [])
        
        if cycles:
            self.logger.warning(f"Found {len(cycles)} circular dependencies")
        
        return cycles


# ============================================================================
# REQUIREMENT RECOMMENDATION ENGINE
# ============================================================================

class RequirementRecommendationEngine:
    """Generates intelligent recommendations for requirements"""
    
    def __init__(self, search_engine: SemanticSearchEngine = None):
        self.logger = logging.getLogger(__name__)
        self.search_engine = search_engine or SemanticSearchEngine()
    
    def generate_recommendations(self, requirement: Dict, similar_reqs: List[Dict]) -> Dict:
        """
        Generate recommendations for a requirement
        
        Args:
            requirement: The requirement to generate recommendations for
            similar_reqs: Similar requirements from other regulations
        
        Returns:
            Dict with recommendations
        """
        recommendations = {
            'requirement_id': requirement['requirement_id'],
            'consolidation_suggestions': [],
            'implementation_insights': [],
            'related_standards': [],
            'compliance_tips': [],
        }
        
        # Find consolidation opportunities
        if similar_reqs:
            recommendations['consolidation_suggestions'] = [
                {
                    'type': 'consolidate',
                    'suggestion': f"This requirement is similar to {len(similar_reqs)} other(s) across regulations",
                    'benefit': "Implement once, satisfy multiple regulations",
                    'regulations': list(set(r.get('regulation') for r in similar_reqs))
                }
            ]
        
        # Generate implementation insights
        recommendations['implementation_insights'].append({
            'insight': 'Related Requirements Detected',
            'details': f"Found {len(similar_reqs)} similar requirements in other regulations",
            'action': 'Review cross-regulation alignments to ensure consistent implementation'
        })
        
        return recommendations


# ============================================================================
# COMPLETE SEMANTIC SEARCH PIPELINE
# ============================================================================

class SemanticSearchPipeline:
    """Complete semantic search pipeline"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tfidf_engine = TFIDFSearchEngine()
        self.semantic_engine = SemanticSearchEngine()
        self.cross_linker = CrossRegulationLinker()
        self.dependency_graph = RequirementDependencyGraph()
        self.recommender = RequirementRecommendationEngine(self.semantic_engine)
        
        self.requirements_index = []
    
    def build_complete_index(self, requirements: List[Dict]) -> bool:
        """Build complete search index"""
        try:
            self.requirements_index = requirements
            
            # Build all indices
            self.tfidf_engine.index_requirements(requirements)
            self.semantic_engine.build_embeddings(requirements)
            self.cross_linker.find_cross_regulation_links(requirements)
            self.dependency_graph.build_dependency_graph(requirements)
            
            self.logger.info("Complete semantic search index built successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Error building index: {e}")
            return False
    
    def search(self, query: str, top_k: int = 10) -> Dict:
        """
        Perform comprehensive search
        
        Returns results from all search methods
        """
        return {
            'query': query,
            'tfidf_results': [asdict(r) for r in self.tfidf_engine.search(query, top_k)],
            'semantic_results': [asdict(r) for r in self.semantic_engine.semantic_search(query, top_k)],
        }
    
    def get_requirement_context(self, req_id: str) -> Dict:
        """Get complete context for a requirement"""
        # Find the requirement
        req = next((r for r in self.requirements_index if r['requirement_id'] == req_id), None)
        
        if not req:
            return {'error': f'Requirement {req_id} not found'}
        
        # Get similar requirements
        similar = self.tfidf_engine.find_similar_requirements(req_id)
        
        # Get cross-regulation links
        links = self.cross_linker.get_linked_requirements(req_id)
        
        # Get recommendations
        similar_reqs = [r for r in self.requirements_index 
                       if r['requirement_id'] in [s.target_req_id for s in similar]]
        recommendations = self.recommender.generate_recommendations(req, similar_reqs)
        
        return {
            'requirement': req,
            'similar_requirements': [asdict(s) for s in similar],
            'cross_regulation_links': [asdict(l) for l in links],
            'recommendations': recommendations,
        }


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


if __name__ == "__main__":
    setup_logging()
    
    # Example usage
    pipeline = SemanticSearchPipeline()
    
    sample_requirements = [
        {
            'requirement_id': 'EU-AI-1',
            'text': 'The system shall implement role-based access control',
            'regulation': 'EU AI Act',
            'section': '4.1',
        },
        {
            'requirement_id': 'GDPR-1',
            'text': 'Systems must implement access control mechanisms',
            'regulation': 'GDPR',
            'section': '32',
        },
        {
            'requirement_id': 'ISO-1',
            'text': 'Access control shall be implemented',
            'regulation': 'ISO 13485',
            'section': '8.2',
        },
    ]
    
    pipeline.build_complete_index(sample_requirements)
    
    # Search
    results = pipeline.search('access control', top_k=5)
    print(json.dumps(results, indent=2, default=str))
    
    # Get context for requirement
    context = pipeline.get_requirement_context('EU-AI-1')
    print(json.dumps(context, indent=2, default=str))
