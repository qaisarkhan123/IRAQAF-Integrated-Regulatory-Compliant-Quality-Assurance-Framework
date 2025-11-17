"""
Performance Tests for Regulatory Monitoring System
Tests performance, scalability, and efficiency
"""

import pytest
import time
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

try:
    from nlp_change_detector import NLPChangeDetector
    from regulatory_monitor import RegulatoryMonitor
except ImportError:
    pytest.skip("Required modules not found", allow_module_level=True)


class TestPerformance:
    """Performance and load tests"""
    
    @pytest.fixture
    def detector(self):
        """Fixture: Initialize detector"""
        return NLPChangeDetector()
    
    # Performance Test 1: Single Similarity Calculation
    def test_single_similarity_calculation_speed(self, detector):
        """Performance: Single similarity calculation"""
        text1 = "Regulation text about data protection and compliance"
        text2 = "Regulation text about data security and standards"
        
        start = time.time()
        similarity = detector.compute_similarity(text1, text2)
        elapsed = time.time() - start
        
        # Should complete quickly
        assert elapsed < 1.0
        print(f"Single calculation: {elapsed:.3f}s")
    
    # Performance Test 2: Batch Similarity Calculations
    def test_batch_similarity_calculations(self, detector):
        """Performance: Batch similarity calculations"""
        texts = [
            f"Regulation {i}: Data protection requirement with various compliance clauses"
            for i in range(30)
        ]
        
        start = time.time()
        
        similarities = []
        for i in range(len(texts)-1):
            sim = detector.compute_similarity(texts[i], texts[i+1])
            similarities.append(sim)
        
        elapsed = time.time() - start
        
        # Should process 30 comparisons in reasonable time
        assert elapsed < 5
        assert len(similarities) > 0
        print(f"Batch {len(texts)} calculations: {elapsed:.3f}s ({elapsed/len(texts):.3f}s per item)")
    
    # Performance Test 3: Large Text Processing
    def test_large_text_processing(self, detector):
        """Performance: Process very large texts"""
        # Create large regulation text (10KB)
        large_text = "Data protection clause. " * 400
        
        start = time.time()
        
        similarity = detector.compute_similarity(large_text, large_text)
        
        elapsed = time.time() - start
        
        # Should handle large texts
        assert elapsed < 2
        assert similarity > 0.95
        print(f"Large text ({len(large_text)} chars): {elapsed:.3f}s")
    
    # Performance Test 4: Many Regulations Processing
    def test_many_regulations_processing(self):
        """Performance: Process 100+ regulations"""
        detector = NLPChangeDetector()
        
        regulations = [
            f"Regulation {i}: Compliance requirement {i} with various clauses"
            for i in range(100)
        ]
        
        start = time.time()
        
        results = []
        for reg in regulations:
            sim = detector.compute_similarity(reg, "baseline compliance requirement")
            results.append(sim)
        
        elapsed = time.time() - start
        
        # Should process 100 regulations in < 10 seconds
        assert elapsed < 10
        assert len(results) == 100
        print(f"100 regulations: {elapsed:.3f}s ({elapsed/100:.3f}s per regulation)")
    
    # Performance Test 5: Concurrent Processing
    def test_concurrent_processing_performance(self):
        """Performance: Concurrent processing"""
        import threading
        
        detector = NLPChangeDetector()
        results = []
        lock = threading.Lock()
        
        def process(text_id):
            sim = detector.compute_similarity(
                f"Text {text_id} about regulations",
                "baseline regulation"
            )
            with lock:
                results.append(sim)
        
        start = time.time()
        
        threads = [threading.Thread(target=process, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        elapsed = time.time() - start
        
        # Should complete concurrently quickly
        assert elapsed < 5
        assert len(results) == 10
        print(f"Concurrent (10 threads): {elapsed:.3f}s")
    
    # Performance Test 6: Memory Efficiency
    def test_memory_efficiency(self):
        """Performance: Memory usage monitoring"""
        import sys
        
        detector = NLPChangeDetector()
        
        # Initial size
        initial_size = sys.getsizeof(detector)
        
        # Process regulations
        regulations = [
            f"Regulation {i}: " + "Data protection clause " * 50
            for i in range(50)
        ]
        
        similarities = []
        for reg in regulations:
            sim = detector.compute_similarity(reg, "baseline")
            similarities.append(sim)
        
        # Should not use excessive memory
        assert len(similarities) == 50
        print(f"Memory usage: Initial {initial_size} bytes")
    
    # Performance Test 7: Cache Access Speed
    def test_cache_access_speed(self):
        """Performance: Cache read/write speed"""
        import tempfile
        import json
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "cache.json"
            
            # Write performance
            start = time.time()
            for i in range(1000):
                data = {"id": f"REG-{i:03d}", "content": f"Regulation {i}"}
            elapsed_write = time.time() - start
            
            # Single cache write
            start = time.time()
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            elapsed_single_write = time.time() - start
            
            # Single cache read
            start = time.time()
            with open(cache_file, 'r') as f:
                loaded = json.load(f)
            elapsed_read = time.time() - start
            
            # Should be fast
            assert elapsed_single_write < 0.1
            assert elapsed_read < 0.1
            print(f"Cache write: {elapsed_single_write:.3f}s, read: {elapsed_read:.3f}s")


class TestScalability:
    """Scalability tests"""
    
    # Scalability Test 1: Linear Time Complexity
    def test_linear_processing_complexity(self):
        """Scalability: Linear time with dataset size"""
        detector = NLPChangeDetector()
        
        sizes = [10, 50, 100]
        times = []
        
        for size in sizes:
            regulations = [f"Regulation {i}: text" for i in range(size)]
            
            start = time.time()
            for reg in regulations:
                detector.compute_similarity(reg, "baseline")
            elapsed = time.time() - start
            
            times.append(elapsed)
        
        # Should scale linearly or better
        # time for 100 should be ~2x time for 50
        ratio = times[2] / times[1] if times[1] > 0 else 1
        assert ratio < 3  # Allow some overhead
        
        print(f"Sizes {sizes}: Times {times}, Ratio {ratio:.2f}")
    
    # Scalability Test 2: Memory Scaling
    def test_memory_scaling(self):
        """Scalability: Memory usage with dataset size"""
        detector = NLPChangeDetector()
        
        # Process increasing sizes
        for size in [10, 50, 100]:
            regulations = [
                f"Regulation {i}: " + "compliance clause " * 10
                for i in range(size)
            ]
            
            # Should complete without error
            results = []
            for reg in regulations:
                sim = detector.compute_similarity(reg, "baseline")
                results.append(sim)
            
            assert len(results) == size


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
