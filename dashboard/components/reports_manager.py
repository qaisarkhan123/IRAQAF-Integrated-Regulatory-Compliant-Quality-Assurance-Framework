"""
IRAQAF Reports Manager Component
Handles report loading, searching, and display functionality
"""

import streamlit as st
import json
import glob
import os
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Module names mapping
NAMES = {
    "L1": "🏛️ Governance & Regulations",
    "L2": "🔐 Privacy & Security",
    "L3": "⚖️ Fairness & Ethics", 
    "L4": "🔍 Explainability & Transparency",
    "L5": "⚙️ Operations & Monitoring",
    "AGG": "📊 Aggregate Analysis"
}

def get_reports_path() -> Path:
    """Get reports directory path"""
    # Try to find project root
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent  # Go up from dashboard/components/
    return project_root / "reports"

def get_report_files(pattern: str = "*.json") -> List[str]:
    """Get report files from reports directory"""
    reports_dir = get_reports_path()
    if not reports_dir.exists():
        return []
    return sorted(glob.glob(str(reports_dir / pattern)))

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def load_all_reports_cached(file_list: tuple) -> Dict[str, Any]:
    """
    Load all reports with caching and optimizations.
    
    Args:
        file_list: Tuple of file paths (must be tuple for hashing)
        
    Returns:
        Dict mapping module names to their latest reports
    """
    latest_by_module = {k: None for k in ["L1", "L2", "L3", "L4", "L5", "AGG"]}
    seen_mtime = {k: -1 for k in latest_by_module.keys()}
    errors = []
    
    # Sort files by modification time (newest first)
    try:
        sorted_files = sorted(
            file_list, 
            key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, 
            reverse=True
        )
    except Exception:
        sorted_files = list(file_list)
    
    modules_found = set()
    
    for f in sorted_files:
        # Early exit if all modules found
        if len(modules_found) == 6:
            break
            
        try:
            # Quick check: skip if file is too old
            if not os.path.exists(f):
                continue
                
            mtime = os.path.getmtime(f)
            
            # Read file with size limit
            file_size = os.path.getsize(f)
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                logger.warning(f"Skipping large file: {f} ({file_size / 1024 / 1024:.1f}MB)")
                continue
                
            with open(f, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
                
            # Handle both single report and list of reports
            for rec in (raw if isinstance(raw, list) else [raw]):
                if not isinstance(rec, dict):
                    continue
                    
                mod = str(rec.get("module", "")).upper()
                if mod in latest_by_module and mtime >= seen_mtime[mod]:
                    latest_by_module[mod] = rec
                    seen_mtime[mod] = mtime
                    modules_found.add(mod)
                    
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {f}: {e}")
            errors.append({
                "file": os.path.basename(f),
                "error": "Invalid JSON format",
                "type": "JSONDecodeError"
            })
        except Exception as e:
            logger.error(f"Failed to load {f}: {e}")
            errors.append({
                "file": os.path.basename(f),
                "error": str(e)[:100],
                "type": type(e).__name__
            })
    
    # Attach metadata
    latest_by_module["_errors"] = errors
    latest_by_module["_load_time"] = datetime.now().isoformat()
    
    return latest_by_module

def render_search_interface():
    """Render the global search interface"""
    st.markdown("---")
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        search_query = st.text_input(
            "🔍 Search across all modules",
            placeholder="Search for metrics, clauses, or evidence...",
            key="global_search",
            help="Press Ctrl+K to focus"
        )
    
    with search_col2:
        search_in = st.multiselect(
            "Search in",
            ["Modules", "Evidence", "Reports"],
            default=["Modules"],
            key="search_scope"
        )
    
    return search_query, search_in

def perform_search(search_query: str, search_in: List[str], latest_reports: Dict[str, Any] = None) -> List[Dict[str, str]]:
    """Perform search across modules, hubs, and evidence"""
    results = []
    
    if not search_query:
        return results
    
    # Search in modules (if reports are available)
    if "Modules" in search_in and latest_reports:
        for mid, rep in latest_reports.items():
            if rep and mid not in ["_errors", "_load_time"] and search_query.lower() in str(rep).lower():
                results.append({
                    "Type": "Module",
                    "Location": NAMES.get(mid, mid),
                    "Match": f"Found in {mid} report",
                    "Score": "High"
                })
    
    # Search in hub names and descriptions
    if "Hubs" in search_in:
        hub_info = {
            "L1 Regulations & Governance": "Compliance requirements foundation, GDPR, EU AI Act",
            "L2 Privacy & Security": "Privacy/security requirements, data protection, encryption",
            "L3 Fairness & Ethics": "Fairness evaluation, bias detection, ethical AI",
            "L4 Explainability & Transparency": "AI transparency, explainability, interpretability",
            "SOQM": "System operations, QA monitoring, performance tracking",
            "UQO": "Unified QA orchestration, cross-hub aggregation",
            "CAE": "Continuous assurance, drift detection, automation"
        }
        
        for hub_name, description in hub_info.items():
            if (search_query.lower() in hub_name.lower() or 
                search_query.lower() in description.lower()):
                results.append({
                    "Type": "Hub",
                    "Location": hub_name,
                    "Match": f"Hub matches '{search_query}'",
                    "Score": "High"
                })
    
    # Search in reports (file names)
    if "Reports" in search_in:
        files = get_report_files("*.json")
        for f in files:
            if search_query.lower() in os.path.basename(f).lower():
                results.append({
                    "Type": "Report File",
                    "Location": os.path.basename(f),
                    "Match": f"Filename contains '{search_query}'",
                    "Score": "Medium"
                })
    
    # Search in common terms
    if "Evidence" in search_in:
        evidence_terms = {
            "compliance": "Regulatory compliance documentation",
            "security": "Security policies and procedures", 
            "privacy": "Privacy impact assessments",
            "fairness": "Bias testing and fairness evaluations",
            "explainability": "Model interpretability documentation",
            "monitoring": "System monitoring and alerting"
        }
        
        for term, description in evidence_terms.items():
            if search_query.lower() in term or search_query.lower() in description.lower():
                results.append({
                    "Type": "Evidence Category",
                    "Location": term.title(),
                    "Match": description,
                    "Score": "Medium"
                })
    
    return results

def render_reports_overview(latest_reports: Dict[str, Any]):
    """Render overview of loaded reports"""
    st.markdown("### 📊 Reports Overview")
    
    # Count loaded modules
    loaded_modules = [
        mid for mid, rep in latest_reports.items() 
        if rep is not None and mid not in ["_errors", "_load_time"]
    ]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Loaded Modules", len(loaded_modules), help="Successfully loaded report modules")
    
    with col2:
        errors = latest_reports.get("_errors", [])
        st.metric("Load Errors", len(errors), delta=f"-{len(errors)}" if errors else None)
    
    with col3:
        load_time = latest_reports.get("_load_time")
        if load_time:
            load_dt = datetime.fromisoformat(load_time)
            time_ago = (datetime.now() - load_dt).total_seconds()
            st.metric("Last Refresh", f"{time_ago:.0f}s ago")
    
    with col4:
        if st.button("🔄 Refresh Reports", help="Reload all reports from disk"):
            st.cache_data.clear()
            st.rerun()

def render_module_cards(latest_reports: Dict[str, Any]):
    """Render cards for each loaded module"""
    st.markdown("### 📋 Module Reports")
    
    # Create grid layout
    cols = st.columns(2)
    
    for i, (mid, rep) in enumerate(latest_reports.items()):
        if mid in ["_errors", "_load_time"]:
            continue
            
        col = cols[i % 2]
        
        with col:
            if rep is None:
                # Module not loaded
                st.markdown(f"""
                    <div style="
                        border: 1px solid #E5E7EB;
                        border-radius: 8px;
                        padding: 16px;
                        margin-bottom: 12px;
                        background: #F9FAFB;
                        opacity: 0.7;
                    ">
                        <div style="display: flex; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 1.2em; margin-right: 8px;">❌</span>
                            <strong>{NAMES.get(mid, mid)}</strong>
                        </div>
                        <div style="font-size: 0.9em; color: #6B7280;">
                            No report available
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Module loaded successfully
                score = rep.get("overall_score", 0)
                timestamp = rep.get("timestamp", "Unknown")
                
                # Determine status color
                if score >= 80:
                    status_color = "🟢"
                    bg_color = "#F0FDF4"
                elif score >= 60:
                    status_color = "🟡"
                    bg_color = "#FFFBEB"
                else:
                    status_color = "🔴"
                    bg_color = "#FEF2F2"
                
                st.markdown(f"""
                    <div style="
                        border: 1px solid #E5E7EB;
                        border-radius: 8px;
                        padding: 16px;
                        margin-bottom: 12px;
                        background: {bg_color};
                    ">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                            <strong>{NAMES.get(mid, mid)}</strong>
                            <span>{status_color} {score:.1f}%</span>
                        </div>
                        <div style="font-size: 0.9em; color: #6B7280;">
                            Last updated: {timestamp}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Show expandable details
                with st.expander(f"📄 {mid} Details", expanded=False):
                    if isinstance(rep, dict):
                        # Show key metrics
                        metrics = {k: v for k, v in rep.items() if k not in ['timestamp', 'module']}
                        st.json(metrics)
                    else:
                        st.write(rep)

def render_reports_manager():
    """Main function to render the complete reports management interface"""
    
    # Load reports
    files = get_report_files("*.json")
    
    if not files:
        # Instead of just showing an error, provide hub-based reporting
        st.info("📊 **Hub-Based Reporting Active**")
        st.markdown("""
        The IRAQAF system is running in **hub-based mode**. Instead of CLI-generated reports, 
        you can access real-time data directly from each hub:
        """)
        
        # Show hub-based reporting options
        render_hub_based_reports()
        return None
    
    # Load all reports with caching
    with st.spinner("Loading reports..."):
        latest_reports = load_all_reports_cached(tuple(files))
    
    # Show load errors if any
    errors = latest_reports.get("_errors", [])
    if errors:
        with st.expander("⚠️ Load Errors", expanded=False):
            error_df = pd.DataFrame(errors)
            st.dataframe(error_df, use_container_width=True)
    
    # Reports overview
    render_reports_overview(latest_reports)
    
    # Search interface
    search_query, search_in = render_search_interface()
    
    # Show search results
    if search_query:
        st.markdown(f"### 🔍 Search Results for '{search_query}'")
        results = perform_search(search_query, search_in, latest_reports)
        
        if results:
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True)
        else:
            st.info("No results found. Try different keywords.")
    
    st.markdown("---")
    
    # Module cards
    render_module_cards(latest_reports)
    
    return latest_reports

def render_hub_based_reports():
    """Render hub-based reporting when traditional reports aren't available"""
    
    st.markdown("### 🎯 Live Hub Data")
    
    # Hub endpoints for data collection
    hub_endpoints = {
        'L1 Regulations & Governance': {
            'url': 'http://localhost:8504/api/summary',
            'port': '8504',
            'icon': '⚖️'
        },
        'L2 Privacy & Security': {
            'url': 'http://localhost:8502/api/metrics', 
            'port': '8502',
            'icon': '🔐'
        },
        'L3 Fairness & Ethics': {
            'url': 'http://localhost:8506/api/summary',
            'port': '8506', 
            'icon': '⚖️'
        },
        'L4 Explainability & Transparency': {
            'url': 'http://localhost:5000/api/explainability-metrics',
            'port': '5000',
            'icon': '🔍'
        },
        'SOQM': {
            'url': 'http://localhost:8503/api/status',
            'port': '8503',
            'icon': '⚙️'
        },
        'UQO': {
            'url': 'http://localhost:8507/api/qa-overview', 
            'port': '8507',
            'icon': '📊'
        },
        'CAE': {
            'url': 'http://localhost:8508/api/internal-cqs',
            'port': '8508',
            'icon': '🤖'
        }
    }
    
    # Create columns for hub data
    col1, col2 = st.columns(2)
    
    for i, (hub_name, hub_info) in enumerate(hub_endpoints.items()):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            with st.expander(f"{hub_info['icon']} {hub_name}", expanded=False):
                try:
                    import requests
                    response = requests.get(hub_info['url'], timeout=3)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Display key metrics
                        if isinstance(data, dict):
                            # Show important metrics
                            for key, value in list(data.items())[:5]:  # Show first 5 items
                                if isinstance(value, (int, float)):
                                    st.metric(key.replace('_', ' ').title(), f"{value:.1f}" if isinstance(value, float) else str(value))
                                elif isinstance(value, str) and len(value) < 50:
                                    st.text(f"{key}: {value}")
                            
                            # Show raw data in expandable section
                            with st.expander("📄 Raw Data", expanded=False):
                                st.json(data)
                        else:
                            st.write(data)
                        
                        st.success(f"✅ Connected to port {hub_info['port']}")
                    else:
                        st.error(f"❌ HTTP {response.status_code}")
                        
                except requests.exceptions.ConnectionError:
                    st.warning(f"⚠️ Hub offline (port {hub_info['port']})")
                    st.markdown(f"**Start the hub:** `python dashboard/{hub_name.lower().replace(' ', '_')}_hub.py`")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)[:50]}...")
    
    st.markdown("---")
    
    # Quick actions for hub management
    st.markdown("### ⚡ Hub Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh All Data", help="Refresh data from all hubs"):
            st.cache_data.clear()
            st.success("Cache cleared! Data will refresh on next load.")
    
    with col2:
        if st.button("📊 Generate Summary Report", help="Create a summary from all hubs"):
            # Collect data from all hubs
            summary_data = {}
            for hub_name, hub_info in hub_endpoints.items():
                try:
                    import requests
                    response = requests.get(hub_info['url'], timeout=2)
                    if response.status_code == 200:
                        summary_data[hub_name] = response.json()
                except:
                    summary_data[hub_name] = {"status": "offline"}
            
            # Display summary
            st.json(summary_data)
    
    with col3:
        if st.button("📖 Hub Documentation", help="View hub documentation"):
            st.markdown("""
            **Hub Documentation:**
            - [📖 Comprehensive Guide](./IRAQAF_HUBS_COMPREHENSIVE_GUIDE.md)
            - Each hub provides REST API endpoints for data access
            - Use the sidebar navigation to access individual hub dashboards
            """)
    
    # Alternative report generation
    st.markdown("---")
    st.markdown("### 📝 Alternative Report Generation")
    
    st.info("""
    **💡 Tip:** If you need traditional JSON reports, you can:
    
    1. **Use Hub APIs directly** - Each hub exposes REST endpoints
    2. **Export hub data** - Use the "Generate Summary Report" button above  
    3. **Set up CLI reporting** - Create a `reports/` directory and configure CLI tools
    4. **Custom integration** - Build your own reporting using the hub APIs
    
    **Current hub status is shown above** - all data is available in real-time!
    """)
    
    return summary_data if 'summary_data' in locals() else {}
