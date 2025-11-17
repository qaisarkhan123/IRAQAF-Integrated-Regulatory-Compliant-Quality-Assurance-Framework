"""
Pytest configuration and shared fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add dashboard directory to Python path (one level up, then into dashboard)
dashboard_dir = Path(__file__).parent.parent / "dashboard"
sys.path.insert(0, str(dashboard_dir))

print(f"Added to path: {dashboard_dir}")  # Debug: verify path is correct


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory"""
    path = Path(__file__).parent / "test_data"
    path.mkdir(exist_ok=True)
    return path


@pytest.fixture
def mock_streamlit(monkeypatch):
    """Mock streamlit functions for testing"""

    class MockStreamlit:
        def __init__(self):
            self.session_state = {}
            self.errors = []
            self.warnings = []
            self.infos = []

        def error(self, msg):
            self.errors.append(msg)

        def warning(self, msg):
            self.warnings.append(msg)

        def info(self, msg):
            self.infos.append(msg)

        def cache_data(self, *args, **kwargs):
            """Mock cache decorator that does nothing"""
            def decorator(func):
                # Return the original function unwrapped
                return func
            return decorator

        def cache_resource(self, *args, **kwargs):
            """Mock cache decorator for resources"""
            def decorator(func):
                return func
            return decorator

    mock_st = MockStreamlit()

    # Try to patch streamlit in app module
    try:
        import app
        monkeypatch.setattr(app, "st", mock_st)
    except ImportError:
        pass  # app module not imported yet

    return mock_st
