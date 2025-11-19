"""
NLP Pipeline module for IRAQAF
Handles document ingestion, text processing, and semantic analysis
"""

import logging
from typing import List, Dict, Tuple
import spacy
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import NLP_CONFIG

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Processes documents through the NLP pipeline
    Handles PDF, DOCX, TXT, and HTML extraction
    """

    def __init__(self):
        """Initialize NLP models and utilities"""
        try:
            self.nlp = spacy.load(NLP_CONFIG["model"])
        except OSError:
            logger.warning(f"Model {NLP_CONFIG['model']} not found. Downloading...")
            import subprocess
            subprocess.run([
                "python", "-m", "spacy", "download", NLP_CONFIG["model"]
            ])
            self.nlp = spacy.load(NLP_CONFIG["model"])

        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=NLP_CONFIG["tfidf_max_features"],
            stop_words="english"
        )

    def extract_text(self, file_path: str, file_type: str) -> str:
        """
        Extract text from various document formats
        
        Args:
            file_path: Path to the document
            file_type: Type of document (pdf, docx, txt, html)
            
        Returns:
            Extracted text
        """
        text = ""

        try:
            if file_type.lower() == "pdf":
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"

            elif file_type.lower() == "docx":
                from docx import Document
                doc = Document(file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"

            elif file_type.lower() == "txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

            elif file_type.lower() == "html":
                from bs4 import BeautifulSoup
                with open(file_path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")
                    text = soup.get_text()

            logger.info(f"Extracted {len(text)} characters from {file_path}")
            return text

        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ""

    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Split text into overlapping chunks for processing
        
        Args:
            text: Input text
            chunk_size: Size of each chunk (tokens)
            overlap: Overlap between chunks (tokens)
            
        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or NLP_CONFIG["chunk_size"]
        overlap = overlap or NLP_CONFIG["overlap"]

        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            doc = self.nlp(sentence)
            sentence_length = len(doc)

            if current_length + sentence_length > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                # Keep last few sentences for overlap
                current_chunk = current_chunk[-2:] if len(current_chunk) > 2 else current_chunk
                current_length = sum(len(self.nlp(s)) for s in current_chunk)

            current_chunk.append(sentence)
            current_length += sentence_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks

    def extract_entities(self, text: str) -> Dict:
        """
        Extract named entities, requirements, and key terms
        """
        doc = self.nlp(text)
        entities = {
            "PERSON": [],
            "ORG": [],
            "PRODUCT": [],
            "REQUIREMENT": [],
        }

        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)

        # Extract requirement-like phrases
        for token in doc:
            if token.dep_ == "nsubj" and token.head.pos_ == "VERB":
                requirement_phrase = " ".join([t.text for t in token.subtree])
                entities["REQUIREMENT"].append(requirement_phrase)

        logger.info(f"Extracted {sum(len(v) for v in entities.values())} entities")
        return entities

    def compute_semantic_similarity(
        self,
        documents: List[str],
        query: str = None
    ) -> np.ndarray:
        """
        Compute semantic similarity between documents using TF-IDF
        """
        try:
            if query:
                documents = [query] + documents
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
                return similarity[0]
            else:
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
                similarity = cosine_similarity(tfidf_matrix)
                return similarity

        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            return np.array([])

    def find_relevant_clauses(
        self,
        documents: List[Dict],
        requirement: str,
        threshold: float = None
    ) -> List[Tuple[Dict, float]]:
        """
        Find document clauses relevant to a requirement
        """
        threshold = threshold or NLP_CONFIG["semantic_similarity_threshold"]
        doc_texts = [d.get("content", "") for d in documents]

        similarities = self.compute_semantic_similarity(doc_texts, requirement)
        results = []

        for i, score in enumerate(similarities):
            if score >= threshold:
                results.append((documents[i], float(score)))

        results.sort(key=lambda x: x[1], reverse=True)
        logger.info(f"Found {len(results)} relevant clauses for requirement")
        return results
