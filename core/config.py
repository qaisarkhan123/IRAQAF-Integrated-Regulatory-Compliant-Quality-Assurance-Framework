"""
Configuration management for IRAQAF dashboard.
Centralizes paths and settings.
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class EvidenceConfig:
    """Evidence handling configuration."""
    max_file_size_mb: int = 50
    max_files_per_upload: int = 10
    allowed_extensions: List[str] = field(default_factory=lambda: [
        'pdf', 'csv', 'png', 'jpg', 'txt', 'docx', 'xlsx'
    ])


@dataclass
class CacheConfig:
    """Cache configuration."""
    ttl_seconds: int = 300
    max_cache_size_mb: int = 500
    max_memory_mb: int = 500


@dataclass
class PerformanceConfig:
    """Performance monitoring configuration."""
    enable_monitoring: bool = True
    log_slow_operations: bool = True
    slow_operation_threshold_ms: int = 1000


@dataclass
class SecurityConfig:
    """Security configuration."""
    enable_rate_limiting: bool = True
    enable_input_validation: bool = True
    enable_audit_logging: bool = True


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    limits: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        'prometheus': {'max_calls': 60, 'window_seconds': 60},
        'file_upload': {'max_calls': 10, 'window_seconds': 60},
        'export': {'max_calls': 20, 'window_seconds': 60},
        'api_calls': {'max_calls': 100, 'window_seconds': 60},
    })


@dataclass
class PolicyConfig:
    """Policy thresholds configuration."""
    latency_slo: float = 1.0
    error_rate_threshold: float = 5.0
    refresh_interval_s: int = 60


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    max_file_size_mb: int = 10
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class UIConfig:
    """UI preferences configuration."""
    default_theme: str = "Auto"
    enable_animations: bool = True
    compact_mode: bool = False
    show_timestamps: bool = True
    decimal_places: int = 2


@dataclass
class ExportConfig:
    """Export settings configuration."""
    default_format: str = "json"
    include_metadata: bool = True
    compress_large_exports: bool = True
    max_export_size_mb: int = 100


@dataclass
class Config:
    """Central configuration for IRAQAF dashboard."""

    # Sub-configs
    evidence: EvidenceConfig
    cache: CacheConfig
    performance: PerformanceConfig
    security: SecurityConfig
    rate_limits: RateLimitConfig
    policies: PolicyConfig
    logging_config: LoggingConfig
    ui: UIConfig
    export: ExportConfig

    # Project structure
    project_root: Path
    dashboard_dir: Path
    reports_dir: Path
    configs_dir: Path
    logs_dir: Path
    evidence_dir: Path
    data_dir: Path
    temp_dir: Path

    # Evidence tracking
    index_path: Path

    # Logging
    log_file: Path
    audit_log_file: Path

    def __init__(self, config_file: str = "configs/dashboard.yaml"):
        # Detect project root
        self.dashboard_dir = Path(
            __file__).resolve().parent.parent / "dashboard"
        self.project_root = self.dashboard_dir.parent

        # Load from YAML if exists
        config_path = self.project_root / config_file
        yaml_config = {}

        if config_path.exists():
            try:
                with open(config_path) as f:
                    yaml_config = yaml.safe_load(f) or {}
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.warning(
                    f"Failed to load config from {config_path}: {e}. Using defaults.")
        else:
            logger.warning(
                f"Config file not found: {config_path}. Using defaults.")

        # Initialize sub-configs
        self.evidence = EvidenceConfig(**yaml_config.get('evidence', {}))
        self.cache = CacheConfig(**yaml_config.get('cache', {}))
        self.performance = PerformanceConfig(
            **yaml_config.get('performance', {}))
        self.security = SecurityConfig(**yaml_config.get('security', {}))
        self.rate_limits = RateLimitConfig(
            limits=yaml_config.get('rate_limits', {}))
        self.policies = PolicyConfig(**yaml_config.get('policies', {}))
        self.logging_config = LoggingConfig(**yaml_config.get('logging', {}))
        self.ui = UIConfig(**yaml_config.get('ui', {}))
        self.export = ExportConfig(**yaml_config.get('export', {}))

        # Standard directories (can be overridden by YAML)
        paths_config = yaml_config.get('paths', {})
        self.reports_dir = self.project_root / \
            paths_config.get('reports_dir', 'reports')
        self.configs_dir = self.project_root / \
            paths_config.get('configs_dir', 'configs')
        self.logs_dir = self.project_root / \
            paths_config.get('logs_dir', 'logs')
        self.data_dir = self.project_root / \
            paths_config.get('data_dir', 'data')
        self.evidence_dir = self.project_root / \
            paths_config.get('evidence_dir', 'evidence')
        self.temp_dir = self.project_root / \
            paths_config.get('temp_dir', 'temp')

        # Files
        self.index_path = self.configs_dir / "evidence_index.json"
        self.log_file = self.logs_dir / "dashboard.log"
        self.audit_log_file = self.logs_dir / "audit.log"

        # Create directories
        self._ensure_directories()

    def _ensure_directories(self):
        """Create all required directories."""
        for dir_path in [
            self.reports_dir,
            self.configs_dir,
            self.logs_dir,
            self.data_dir,
            self.evidence_dir,
            self.temp_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_report_path(self, module: str, timestamp: str = None) -> Path:
        """Get path for a module report."""
        if timestamp:
            filename = f"{module}-{timestamp}.json"
        else:
            filename = f"{module}-latest.json"
        return self.reports_dir / filename

    def get_evidence_path(self, module: str, filename: str) -> Path:
        """Get path for evidence file."""
        return self.evidence_dir / module / filename

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-notation key (e.g., 'evidence.max_file_size_mb')"""
        keys = key.split('.')
        value = self
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        return value

    def reload(self):
        """Reload configuration from file."""
        self.__init__()
        logger.info("Configuration reloaded")


# Global config instance
config = Config()
