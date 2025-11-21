#!/usr/bin/env python3
import sys
import os
sys.path.append('dashboard')

try:
    print("Testing research tracker import...")
    from research_tracker import get_research_tracker
    
    print("Getting research tracker instance...")
    tracker = get_research_tracker()
    print(f"SUCCESS: Tracker type: {type(tracker)}")
    
    print("Testing get_latest_research method...")
    papers = tracker.get_latest_research(limit=3)
    print(f"SUCCESS: Found {len(papers)} papers")
    
    if papers:
        print("Sample paper:")
        print(f"  Title: {papers[0].get('title', 'N/A')}")
        print(f"  Authors: {papers[0].get('authors', 'N/A')}")
    
    print("SUCCESS: Research tracker is working!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
