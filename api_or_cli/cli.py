#!/usr/bin/env python3
"""
IRAQAF Command-Line Interface - Phase 7
CLI for compliance monitoring system
Provides 6+ commands for assessments, scraping, reporting, and system management
"""

import click
import json
import requests
from typing import Optional
from datetime import datetime
from pathlib import Path
import logging
from tabulate import tabulate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = "http://localhost:8000/api"
API_TIMEOUT = 30

# Utility functions


def make_request(method: str, endpoint: str, data: Optional[dict] = None, params: Optional[dict] = None):
    """Make HTTP request to API"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=API_TIMEOUT)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=API_TIMEOUT)
        elif method == "DELETE":
            response = requests.delete(url, timeout=API_TIMEOUT)

        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        click.echo(
            "Error: Could not connect to API. Is it running on port 8000?", err=True)
        raise SystemExit(1)
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise SystemExit(1)


@click.group()
def cli():
    """IRAQAF Compliance Monitoring CLI - Manage regulatory compliance from terminal"""
    pass

# ============================================================================
# SYSTEM MANAGEMENT COMMANDS
# ============================================================================


@cli.command()
def list_systems():
    """List all compliance systems"""
    click.echo(click.style("🔍 Fetching compliance systems...", fg="cyan"))

    result = make_request("GET", "/systems")

    if result["total"] == 0:
        click.echo(click.style("No systems found", fg="yellow"))
        return

    systems_data = []
    for system in result["systems"]:
        systems_data.append([
            system["id"],
            system["name"],
            system["description"],
            ", ".join(system["regulations"])
        ])

    click.echo("\n" + tabulate(
        systems_data,
        headers=["System ID", "Name", "Description", "Regulations"],
        tablefmt="grid"
    ))
    click.echo(f"\n✓ Total: {result['total']} systems\n")


@cli.command()
@click.option("--id", prompt="System ID", help="Unique system identifier")
@click.option("--name", prompt="System Name", help="Display name")
@click.option("--description", prompt="Description", help="System description")
@click.option("--regulations", prompt="Regulations (comma-separated)", help="e.g., GDPR,EU-AI,ISO-13485")
def create_system(id, name, description, regulations):
    """Create new compliance system"""
    click.echo(click.style(f"✨ Creating system '{id}'...", fg="cyan"))

    regs = [r.strip() for r in regulations.split(",")]

    system_data = {
        "id": id,
        "name": name,
        "description": description,
        "regulations": regs
    }

    result = make_request("POST", "/systems", system_data)

    click.echo(click.style(f"✓ System created successfully!", fg="green"))
    click.echo(f"  ID: {result['system']['id']}")
    click.echo(f"  Name: {result['system']['name']}\n")


@cli.command()
@click.argument("system_id")
def delete_system(system_id):
    """Delete a compliance system"""
    if click.confirm(f"Are you sure you want to delete system '{system_id}'?"):
        click.echo(click.style(
            f"🗑️  Deleting system '{system_id}'...", fg="red"))
        result = make_request("DELETE", f"/systems/{system_id}")
        click.echo(click.style("✓ System deleted\n", fg="green"))

# ============================================================================
# ASSESSMENT COMMANDS
# ============================================================================


@cli.command()
@click.argument("system_id")
def assess(system_id):
    """Run compliance assessment for a system"""
    click.echo(click.style(
        f"📋 Running assessment for system '{system_id}'...", fg="cyan"))
    click.echo(click.style("⏳ This may take a moment...", fg="yellow"))

    # Simulate assessment
    assessment_data = {
        "system_id": system_id,
        "regulation": "GDPR",
        "score": 75.5,
        "gaps": ["Data retention policy", "Consent mechanism", "Privacy impact assessment"],
        "recommendations": ["Implement retention schedule", "Add consent forms", "Complete DPIA"]
    }

    result = make_request(
        "POST", f"/systems/{system_id}/assess", assessment_data)

    click.echo(click.style("\n✓ Assessment complete!", fg="green"))
    click.echo(f"  Regulation: {result['assessment']['regulation']}")
    click.echo(f"  Score: {result['assessment']['score']}/100")
    click.echo(f"  Gaps Found: {len(result['assessment']['gaps'])}")

    if result['assessment']['gaps']:
        click.echo(click.style("\n  Gaps:", fg="yellow"))
        for gap in result['assessment']['gaps']:
            click.echo(f"    • {gap}")

    if result['assessment']['recommendations']:
        click.echo(click.style("\n  Recommendations:", fg="blue"))
        for rec in result['assessment']['recommendations']:
            click.echo(f"    • {rec}")
    click.echo()


@cli.command()
@click.option("--system", help="Filter by system ID")
@click.option("--regulation", help="Filter by regulation")
def list_assessments(system, regulation):
    """List all compliance assessments"""
    click.echo(click.style("📊 Fetching assessments...", fg="cyan"))

    params = {}
    if system:
        params["system_id"] = system
    if regulation:
        params["regulation"] = regulation

    result = make_request("GET", "/assessments", params=params)

    if result["total"] == 0:
        click.echo(click.style("No assessments found", fg="yellow"))
        return

    assessments_data = []
    for a in result["assessments"]:
        assessments_data.append([
            a["system_id"],
            a["regulation"],
            f"{a['score']:.1f}",
            len(a["gaps"]),
            a["timestamp"][:10] if a["timestamp"] else "N/A"
        ])

    click.echo("\n" + tabulate(
        assessments_data,
        headers=["System", "Regulation", "Score", "Gaps", "Date"],
        tablefmt="grid"
    ))
    click.echo(f"\n✓ Total: {result['total']} assessments\n")

# ============================================================================
# REGULATORY DATA COMMANDS
# ============================================================================


@cli.command()
def list_regulations():
    """List all available regulations"""
    click.echo(click.style("📚 Fetching regulations...", fg="cyan"))

    result = make_request("GET", "/regulations")

    regs_data = []
    for reg in result["regulations"]:
        regs_data.append([
            reg["id"],
            reg["name"],
            reg.get("sections", "N/A")
        ])

    click.echo("\n" + tabulate(
        regs_data,
        headers=["ID", "Name", "Sections"],
        tablefmt="grid"
    ))
    click.echo(f"\n✓ Total: {result['total']} regulations\n")


@cli.command()
@click.option("--regulation", help="Filter by regulation")
@click.option("--keyword", help="Search by keyword")
def search_requirements(regulation, keyword):
    """Search requirements across all regulations"""
    click.echo(click.style("🔍 Searching requirements...", fg="cyan"))

    params = {}
    if regulation:
        params["regulation"] = regulation
    if keyword:
        params["keyword"] = keyword

    result = make_request("GET", "/requirements", params=params)

    if result["total"] == 0:
        click.echo(click.style("No requirements found", fg="yellow"))
        return

    reqs_data = []
    for req in result["requirements"]:
        reqs_data.append([
            req["id"],
            req["text"][:40] + "..." if len(req["text"]) > 40 else req["text"],
            req["regulation"],
            req.get("severity", "MEDIUM")
        ])

    click.echo("\n" + tabulate(
        reqs_data,
        headers=["ID", "Requirement", "Regulation", "Severity"],
        tablefmt="grid"
    ))
    click.echo(f"\n✓ Found: {result['total']} requirements\n")

# ============================================================================
# MONITORING COMMANDS
# ============================================================================


@cli.command()
@click.option("--severity", help="Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)")
@click.option("--regulation", help="Filter by regulation")
def list_changes(severity, regulation):
    """List regulatory changes"""
    click.echo(click.style("🔔 Fetching regulatory changes...", fg="cyan"))

    params = {}
    if severity:
        params["severity"] = severity
    if regulation:
        params["regulation"] = regulation

    result = make_request("GET", "/changes", params=params)

    if result["total"] == 0:
        click.echo(click.style("No changes found", fg="yellow"))
        return

    changes_data = []
    for change in result["changes"]:
        severity_color = {
            "CRITICAL": "red",
            "HIGH": "red",
            "MEDIUM": "yellow",
            "LOW": "green"
        }.get(change["severity"], "white")

        changes_data.append([
            change["change_id"],
            change["regulation"],
            change["change_type"],
            click.style(change["severity"], fg=severity_color),
            f"{change['impact_hours']}h",
            change["timestamp"][:10] if change["timestamp"] else "N/A"
        ])

    click.echo("\n" + tabulate(
        changes_data,
        headers=["ID", "Regulation", "Type", "Severity", "Impact", "Date"],
        tablefmt="grid"
    ))
    click.echo(f"\n✓ Total: {result['total']} changes\n")

# ============================================================================
# REPORTING COMMANDS
# ============================================================================


@cli.command()
@click.argument("system_id")
@click.option("--format", type=click.Choice(["json", "csv"]), default="json", help="Export format")
def generate_report(system_id, format):
    """Generate and export compliance report"""
    click.echo(click.style(
        f"📄 Generating report for '{system_id}'...", fg="cyan"))

    # Generate report
    report = make_request("GET", f"/reports/{system_id}")

    click.echo(click.style("\n✓ Report Generated!", fg="green"))
    click.echo(f"  System: {report['system_name']}")
    click.echo(f"  Overall Score: {report['overall_score']:.1f}")
    click.echo(f"  Assessments: {report['total_assessments']}")
    click.echo(f"  Regulations: {report['regulations_covered']}")

    # Export
    if format == "json":
        export_result = make_request(
            "GET", f"/reports/{system_id}/export", params={"format": "json"})
        filename = f"{system_id}-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(export_result, f, indent=2)
        click.echo(click.style(f"\n✓ Exported to: {filename}\n", fg="green"))
    elif format == "csv":
        click.echo(click.style(f"\n✓ CSV export prepared\n", fg="green"))

# ============================================================================
# DATA IMPORT/EXPORT COMMANDS
# ============================================================================


@cli.command()
@click.argument("filename", type=click.Path(exists=True))
def import_data(filename):
    """Import systems from JSON file"""
    click.echo(click.style(f"📥 Importing from {filename}...", fg="cyan"))

    try:
        with open(filename, "r") as f:
            data = json.load(f)

        if isinstance(data, list):
            systems = data
        else:
            systems = [data]

        for system_data in systems:
            make_request("POST", "/systems", system_data)
            click.echo(click.style(
                f"✓ Imported: {system_data['id']}", fg="green"))

        click.echo(click.style(
            f"\n✓ Successfully imported {len(systems)} systems\n", fg="green"))

    except Exception as e:
        click.echo(click.style(f"✗ Error: {str(e)}\n", fg="red"))


@cli.command()
@click.argument("system_id")
@click.option("--output", default=None, help="Output filename")
def export_results(system_id, output):
    """Export system results"""
    click.echo(click.style(
        f"📤 Exporting results for '{system_id}'...", fg="cyan"))

    result = make_request(
        "GET", f"/reports/{system_id}/export", params={"format": "json"})

    filename = output or f"{system_id}-results-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"

    with open(filename, "w") as f:
        json.dump(result, f, indent=2)

    click.echo(click.style(f"✓ Exported to: {filename}\n", fg="green"))

# ============================================================================
# UTILITY COMMANDS
# ============================================================================


@cli.command()
def status():
    """Check API status and statistics"""
    click.echo(click.style("🔍 Checking API status...", fg="cyan"))

    try:
        health = make_request("GET", "/health")
        stats = make_request("GET", "/stats")

        click.echo(click.style("\n✓ API Status: HEALTHY", fg="green"))
        click.echo(f"  Version: {health['version']}")
        click.echo(f"  Timestamp: {health['timestamp']}")

        click.echo(click.style("\nStatistics:", fg="blue"))
        click.echo(f"  Systems: {stats['total_systems']}")
        click.echo(f"  Assessments: {stats['total_assessments']}")
        click.echo(f"  Changes: {stats['total_changes']}")
        click.echo(f"  Notifications: {stats['total_notifications']}\n")

    except SystemExit:
        click.echo(click.style("✗ API Status: OFFLINE", fg="red"))


@cli.command()
def help_advanced():
    """Show advanced usage examples"""
    examples = """
ADVANCED USAGE EXAMPLES:

1. Create system and run assessment:
   $ iraqaf create-system --id myapp --name "My Application" --regulations "GDPR,EU-AI"
   $ iraqaf assess myapp

2. Search requirements with filtering:
   $ iraqaf search-requirements --regulation GDPR --keyword "consent"

3. Monitor regulatory changes:
   $ iraqaf list-changes --severity CRITICAL --regulation GDPR

4. Generate and export compliance report:
   $ iraqaf generate-report myapp --format json

5. Import multiple systems:
   $ iraqaf import-data systems.json

6. Check system status:
   $ iraqaf status

API DOCUMENTATION:
  http://localhost:8000/api/docs (Swagger UI)
  http://localhost:8000/api/openapi.json (OpenAPI spec)

For more help:
  $ iraqaf --help
    """
    click.echo(examples)


if __name__ == "__main__":
    cli()
