"""
Data loading service for IRAQAF dashboard.
Handles all report loading and caching logic.
"""

import os
import json
import logging
import streamlit as st
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DataLoadError(Exception):
    """Error loading data files"""
    pass


class DataLoader:
    """Manages loading and caching of IRAQAF reports."""
    
    def __init__(self, reports_dir: Path, cache_ttl: int = 300):
        self.reports_dir = reports_dir
        self.cache_ttl = cache_ttl
    
    @st.cache_data(ttl=300, show_spinner=False, max_entries=50)
    def load_all_reports(_self, file_list: tuple, force_reload: bool = False) -> Dict:
        """Load all reports with caching."""
        latest_by_module = {k: None for k in ["L1", "L2", "L3", "L4", "L5", "AGG"]}
        seen_mtime = {k: -1 for k in latest_by_module.keys()}
        errors = []
        
        sorted_files = sorted(file_list, key=lambda f: os.path.getmtime(f), reverse=True)
        modules_found = set()
        
        for f in sorted_files:
            if len(modules_found) == 6:
                break
            
            try:
                mtime = os.path.getmtime(f)
                file_size = os.path.getsize(f)
                
                if file_size > 10 * 1024 * 1024:
                    logger.warning(f"Skipping large file: {f}")
                    continue
                
                with open(f, "r", encoding="utf-8") as fh:
                    raw = json.load(fh)
                
                for rec in (raw if isinstance(raw, list) else [raw]):
                    if not isinstance(rec, dict):
                        continue
                    
                    mod = str(rec.get("module", "")).upper()
                    if mod in latest_by_module and mtime >= seen_mtime[mod]:
                        latest_by_module[mod] = rec
                        seen_mtime[mod] = mtime
                        modules_found.add(mod)
            
            except Exception as e:
                logger.error(f"Failed to load {f}: {e}")
                errors.append({
                    "file": os.path.basename(f),
                    "error": str(e)[:100],
                    "type": type(e).__name__
                })
        
        latest_by_module["_errors"] = errors
        latest_by_module["_load_time"] = datetime.now().isoformat()
        latest_by_module["_modules_found"] = len(modules_found)
        
        return latest_by_module
    
    def load_latest(self, module_id: str) -> Optional[Dict]:
        """Load the latest report for a specific module."""
        pattern = f"{module_id}-*.json"
        files = sorted(self.reports_dir.glob(pattern), 
                      key=lambda p: p.stat().st_mtime, 
                      reverse=True)
        
        if not files:
            return None
        
        try:
            with open(files[0], "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as e:
            logger.error(f"Failed to load {files[0]}: {e}")
            return None
