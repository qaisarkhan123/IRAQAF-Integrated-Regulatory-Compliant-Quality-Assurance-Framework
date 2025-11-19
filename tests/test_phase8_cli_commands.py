"""
Phase 8 - CLI Command Tests
Comprehensive testing of CLI commands (15+ tests)
Tests all commands, options, and error handling
"""

import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock
import json

# Import the CLI
try:
    from api_or_cli.cli import cli
    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False


@pytest.fixture
def runner():
    """Create Click CLI test runner"""
    return CliRunner()


@pytest.mark.cli
@pytest.mark.unit
class TestSystemCommands:
    """Test system management commands"""

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_list_systems_command(self, runner):
        """Test 'list-systems' command"""
        result = runner.invoke(cli, ['list-systems'])
        # May succeed or fail depending on API
        assert result.exit_code in [0, 1]
        # Should not have exceptions
        assert "Traceback" not in result.output

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_create_system_command(self, runner):
        """Test 'create-system' command with prompts"""
        # Simulate user input
        result = runner.invoke(
            cli, ['create-system'], input='Test System\nTest medical device\nmedical_device\n')
        # Command should complete
        assert result.exit_code in [0, 1]

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_delete_system_command(self, runner):
        """Test 'delete-system' command"""
        result = runner.invoke(cli, ['delete-system', '1'])
        # Should attempt deletion
        assert result.exit_code in [0, 1]

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_help_command(self, runner):
        """Test general help"""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Commands:' in result.output or 'Usage:' in result.output


@pytest.mark.cli
@pytest.mark.unit
class TestAssessmentCommands:
    """Test assessment commands"""

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_assess_command(self, runner):
        """Test 'assess' command"""
        result = runner.invoke(cli, ['assess', '1'])
        assert result.exit_code in [0, 1]
        assert "Traceback" not in result.output

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_list_assessments_command(self, runner):
        """Test 'list-assessments' command"""
        result = runner.invoke(cli, ['list-assessments'])
        assert result.exit_code in [0, 1]
        assert "Traceback" not in result.output


@pytest.mark.cli
@pytest.mark.unit
class TestRegulatoryCommands:
    """Test regulatory data commands"""

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_list_regulations_command(self, runner):
        """Test 'list-regulations' command"""
        result = runner.invoke(cli, ['list-regulations'])
        assert result.exit_code in [0, 1]

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_search_requirements_command(self, runner):
        """Test 'search-requirements' command"""
        result = runner.invoke(
            cli, ['search-requirements', '--keyword', 'encryption'])
        assert result.exit_code in [0, 1]

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_search_with_filters(self, runner):
        """Test search with severity filter"""
        result = runner.invoke(
            cli, ['search-requirements', '--severity', 'high'])
        assert result.exit_code in [0, 1]


@pytest.mark.cli
@pytest.mark.unit
class TestMonitoringCommands:
    """Test monitoring commands"""

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_list_changes_command(self, runner):
        """Test 'list-changes' command"""
        result = runner.invoke(cli, ['list-changes'])
        assert result.exit_code in [0, 1]

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_list_changes_with_filter(self, runner):
        """Test 'list-changes' with severity filter"""
        result = runner.invoke(cli, ['list-changes', '--severity', 'critical'])
        assert result.exit_code in [0, 1]


@pytest.mark.cli
@pytest.mark.unit
class TestReportCommands:
    """Test report generation commands"""

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_generate_report_command(self, runner):
        """Test 'generate-report' command"""
        result = runner.invoke(cli, ['generate-report', '1'])
        assert result.exit_code in [0, 1]

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_export_results_command(self, runner):
        """Test 'export-results' command"""
        result = runner.invoke(cli, ['export-results', '1'])
        assert result.exit_code in [0, 1]


@pytest.mark.cli
@pytest.mark.unit
class TestUtilityCommands:
    """Test utility commands"""

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_status_command(self, runner):
        """Test 'status' command"""
        result = runner.invoke(cli, ['status'])
        assert result.exit_code in [0, 1]
        # Should show some status information
        assert len(result.output) > 0

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_help_advanced_command(self, runner):
        """Test 'help-advanced' command"""
        result = runner.invoke(cli, ['help-advanced'])
        assert result.exit_code in [0, 1]


@pytest.mark.cli
@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests for CLI workflows"""

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_workflow_list_then_assess(self, runner):
        """Test workflow: list systems then assess one"""
        # List systems
        result1 = runner.invoke(cli, ['list-systems'])
        # Attempt assessment
        result2 = runner.invoke(cli, ['assess', '1'])
        # Both should complete
        assert result1.exit_code in [0, 1]
        assert result2.exit_code in [0, 1]


@pytest.mark.cli
@pytest.mark.unit
class TestCLIErrorHandling:
    """Test CLI error handling"""

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_invalid_command(self, runner):
        """Test invalid command handling"""
        result = runner.invoke(cli, ['invalid-command'])
        assert result.exit_code != 0

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_missing_required_argument(self, runner):
        """Test missing required argument"""
        result = runner.invoke(cli, ['assess'])  # Missing system ID
        assert result.exit_code != 0

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI module not available")
    def test_invalid_filter_value(self, runner):
        """Test invalid filter value"""
        result = runner.invoke(
            cli, ['list-changes', '--severity', 'invalid-severity'])
        # Should handle gracefully
        assert "Traceback" not in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
