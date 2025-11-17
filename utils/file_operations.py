"""
File: utils/file_operations.py
Centralized file operations with error handling
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def load_json(path: str) -> dict:
    """
    Load JSON file safely with comprehensive error handling.
    
    Args:
        path: Path to JSON file
        
    Returns:
        Dictionary from JSON file, or empty dict on error
    """
    try:
        file_path = Path(path)
        
        if not file_path.exists():
            logger.warning(f"File not found: {path}")
            return {}
        
        with open(file_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            
        if not isinstance(data, dict):
            logger.warning(f"JSON in {path} is not a dictionary, got {type(data)}")
            return {}
            
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        return {}
        
    except PermissionError:
        logger.error(f"Permission denied reading {path}")
        return {}
        
    except Exception as e:
        logger.error(f"Unexpected error loading {path}: {e}", exc_info=True)
        return {}


def save_json(data: dict, path: str, indent: int = 2) -> bool:
    """
    Save dictionary to JSON file safely.
    
    Args:
        data: Dictionary to save
        path: Target file path
        indent: JSON indentation (default: 2)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        temp_path = file_path.with_suffix('.tmp')
        
        with open(temp_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=indent)
        
        temp_path.replace(file_path)
        
        logger.info(f"Saved JSON to {path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save JSON to {path}: {e}", exc_info=True)
        return False