"""
IRAQAF Configuration Module
Centralized configuration for all components
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "db"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Database configuration
DATABASE_URL = f"sqlite:///{DB_DIR}/iraqaf.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Web scraping configuration
SCRAPER_CONFIG = {
    "timeout": 30,
    "retries": 3,
    "backoff_factor": 1.5,
    "user_agent": "IRAQAF-Compliance-Bot/1.0",
    "headers": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
}

# NLP configuration
NLP_CONFIG = {
    "model": "en_core_web_sm",
    "tfidf_max_features": 1000,
    "semantic_similarity_threshold": 0.7,
    "chunk_size": 512,
    "overlap": 50,
}

# Regulatory sources
REGULATORY_SOURCES = {
    "EU_AI_ACT": {
        "url": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
        "parser": "html",
        "update_frequency": "weekly",
    },
    "GDPR": {
        "url": "https://gdpr-info.eu/",
        "parser": "html",
        "update_frequency": "monthly",
    },
    "ISO_13485": {
        "url": "https://www.iso.org/standard/59752.html",
        "parser": "pdf",
        "update_frequency": "monthly",
    },
    "IEC_62304": {
        "url": "https://www.iec.ch/standard/62304",
        "parser": "pdf",
        "update_frequency": "monthly",
    },
    "FDA": {
        "url": "https://www.fda.gov/medical-devices/",
        "parser": "html",
        "update_frequency": "weekly",
    },
}

# Compliance module configuration
COMPLIANCE_MODULES = [
    "eu_ai_act",
    "gdpr",
    "iso_13485",
    "iec_62304",
    "fda",
]

# Change monitoring configuration
MONITOR_CONFIG = {
    "check_interval": 86400,  # 24 hours in seconds
    "notification_methods": ["email", "log"],
    "email_smtp": os.getenv("SMTP_SERVER", "localhost"),
    "email_port": int(os.getenv("SMTP_PORT", "587")),
    "email_from": os.getenv("SMTP_FROM", "iraqaf@compliance.local"),
}

# API configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": os.getenv("DEBUG", "False") == "True",
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "iraqaf.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": "INFO",
        }
    },
}
