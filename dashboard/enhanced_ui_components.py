"""
Enhanced Dashboard UI Components
Provides advanced visualization and interaction components for the regulatory dashboard.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from enum import Enum


class ThemeMode(Enum):
    """UI theme modes."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class MetricStatus(Enum):
    """Status indicators for metrics."""
    EXCELLENT = ("excellent", "#00AA44")
    GOOD = ("good", "#4CAF50")
    WARNING = ("warning", "#FFC107")
    CRITICAL = ("critical", "#F44336")
    UNKNOWN = ("unknown", "#9E9E9E")


def setup_theme(mode: str = "light"):
    """Configure Streamlit theme."""
    if mode == "dark":
        st.set_page_config(
            page_title="Regulatory Compliance Dashboard",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        # Dark theme colors
        primary_color = "#1f77b4"
        background_color = "#0e1117"
        secondary_background_color = "#161b22"
        text_color = "#c9d1d9"
    else:
        st.set_page_config(
            page_title="Regulatory Compliance Dashboard",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        primary_color = "#1f77b4"
        background_color = "#ffffff"
        secondary_background_color = "#f0f2f6"
        text_color = "#262730"
    
    return {
        "primary_color": primary_color,
        "background_color": background_color,
        "secondary_background_color": secondary_background_color,
        "text_color": text_color
    }


def render_metric_card(title: str,
                      value: Any,
                      unit: str = "",
                      status: str = "unknown",
                      trend: Optional[str] = None,
                      metric_id: str = "") -> None:
    """Render an enhanced metric card with status indicator."""
    status_enum = MetricStatus[status.upper()] if status.upper() in MetricStatus.__members__ else MetricStatus.UNKNOWN
    status_name, status_color = status_enum.value
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**{title}**")
        st.markdown(f"<h2 style='color: {status_color}; margin: 0;'>{value}{unit}</h2>",
                   unsafe_allow_html=True)
        
        if trend:
            trend_symbol = "📈" if "up" in trend.lower() or "improv" in trend.lower() else "📉"
            st.caption(f"{trend_symbol} {trend}")
    
    with col2:
        # Status indicator circle
        st.markdown(
            f"<div style='width: 50px; height: 50px; background-color: {status_color}; "
            f"border-radius: 50%; display: flex; align-items: center; justify-content: center; "
            f"color: white; font-weight: bold;'>{status_name[0].upper()}</div>",
            unsafe_allow_html=True
        )


def render_compliance_gauge(value: float,
                          min_val: float = 0,
                          max_val: float = 100,
                          title: str = "Compliance Score",
                          threshold: float = 80.0) -> None:
    """Render an interactive compliance gauge chart."""
    
    # Determine color based on threshold
    if value >= threshold:
        gauge_color = ["#00AA44"]
    elif value >= threshold * 0.8:
        gauge_color = ["#FFC107"]
    else:
        gauge_color = ["#F44336"]
    
    fig = go.Figure(data=[go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": title},
        delta={"reference": threshold, "suffix": "% vs Target"},
        gauge={
            "axis": {"range": [min_val, max_val]},
            "bar": {"color": gauge_color[0]},
            "steps": [
                {"range": [min_val, threshold * 0.5], "color": "#FFCCCC"},
                {"range": [threshold * 0.5, threshold * 0.8], "color": "#FFFFCC"},
                {"range": [threshold * 0.8, max_val], "color": "#CCFFCC"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": threshold
            }
        }
    )])
    
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, width="stretch")


def render_regulatory_timeline(events: List[Dict[str, Any]], 
                             height: int = 500) -> None:
    """Render an interactive regulatory timeline visualization."""
    
    if not events:
        st.info("No events to display")
        return
    
    # Convert to dataframe
    df = pd.DataFrame(events)
    
    if "timestamp" not in df.columns:
        st.error("Events must have 'timestamp' field")
        return
    
    # Sort by timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    
    # Create timeline chart
    fig = go.Figure()
    
    # Color map for impact levels
    color_map = {
        "critical": "#F44336",
        "high": "#FF9800",
        "medium": "#FFC107",
        "low": "#4CAF50",
    }
    
    for idx, row in df.iterrows():
        impact = row.get("impact_level", "medium").lower()
        color = color_map.get(impact, "#9E9E9E")
        
        fig.add_trace(go.Scatter(
            x=[row["timestamp"]],
            y=[idx],
            mode="markers+text",
            marker=dict(size=15, color=color),
            text=[row.get("regulation_name", "Event")],
            textposition="top center",
            hovertemplate=f"<b>{row.get('regulation_name', 'Event')}</b><br>" +
                         f"Impact: {impact}<br>" +
                         f"Date: {row['timestamp'].strftime('%Y-%m-%d %H:%M')}<extra></extra>",
            showlegend=False
        ))
    
    fig.update_layout(
        title="Regulatory Events Timeline",
        xaxis_title="Date",
        height=height,
        showlegend=False,
        hovermode="closest",
        yaxis=dict(visible=False)
    )
    
    st.plotly_chart(fig, width="stretch")


def render_compliance_trend_chart(trends: List[Dict[str, Any]],
                                 metric_name: str = "") -> None:
    """Render compliance trend over time."""
    
    if not trends:
        st.info("No trend data available")
        return
    
    df = pd.DataFrame(trends)
    
    if "timestamp" not in df.columns or "compliance_score" not in df.columns:
        st.error("Trends must have 'timestamp' and 'compliance_score' fields")
        return
    
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    
    fig = go.Figure()
    
    # Add main line
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["compliance_score"],
        mode="lines+markers",
        name="Compliance Score",
        line=dict(color="#1f77b4", width=2),
        marker=dict(size=6)
    ))
    
    # Add forecast if available
    if "forecast_7d" in df.columns:
        last_date = df["timestamp"].max()
        future_date = last_date + timedelta(days=7)
        
        fig.add_trace(go.Scatter(
            x=[last_date, future_date],
            y=[df["compliance_score"].iloc[-1], df["forecast_7d"].iloc[-1]],
            mode="lines",
            name="7-Day Forecast",
            line=dict(color="#FF9800", width=2, dash="dash"),
            marker=dict(size=6)
        ))
    
    # Add threshold line
    fig.add_hline(
        y=80,
        line_dash="dash",
        line_color="red",
        annotation_text="Threshold (80%)",
        annotation_position="right"
    )
    
    fig.update_layout(
        title=f"Compliance Trend{(' - ' + metric_name) if metric_name else ''}",
        xaxis_title="Date",
        yaxis_title="Compliance Score (%)",
        height=400,
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, width="stretch")


def render_risk_heat_map(data: Dict[str, Dict[str, float]],
                        title: str = "Risk Assessment Matrix") -> None:
    """Render a risk assessment heat map."""
    
    # Convert data to matrix format
    systems = list(data.keys())
    regulations = set()
    
    for sys_data in data.values():
        regulations.update(sys_data.keys())
    
    regulations = sorted(list(regulations))
    
    # Build matrix
    matrix = []
    for regulation in regulations:
        row = [data.get(system, {}).get(regulation, 0) for system in systems]
        matrix.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=systems,
        y=regulations,
        colorscale="RdYlGn_r",
        text=np.array(matrix),
        texttemplate="%{text:.1f}",
        textfont={"size": 12},
        colorbar=dict(title="Risk Score")
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Systems",
        yaxis_title="Regulations",
        height=max(400, len(regulations) * 30),
        hovermode="closest"
    )
    
    st.plotly_chart(fig, width="stretch")


def render_alert_panel(alerts: List[Dict[str, Any]]) -> None:
    """Render alert notification panel."""
    
    if not alerts:
        st.success("✓ No active alerts")
        return
    
    # Group by risk level
    risk_levels = ["critical", "high", "medium", "low"]
    
    for risk_level in risk_levels:
        level_alerts = [a for a in alerts if a.get("risk_level", "").lower() == risk_level]
        
        if not level_alerts:
            continue
        
        color_map = {
            "critical": "#F44336",
            "high": "#FF9800",
            "medium": "#FFC107",
            "low": "#4CAF50"
        }
        
        color = color_map.get(risk_level, "#9E9E9E")
        
        with st.container():
            st.markdown(f"### <span style='color: {color};'>⚠ {risk_level.upper()}</span>", 
                       unsafe_allow_html=True)
            
            for alert in level_alerts:
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**{alert.get('alert_type', 'Alert')}**: {alert.get('message', '')}")
                    st.caption(f"Affected: {alert.get('affected_regulation', 'N/A')}")
                    st.caption(f"Action: {alert.get('recommended_action', 'N/A')}")
                
                with col2:
                    if st.button("Acknowledge", key=f"ack_{alert.get('alert_id', '')}"):
                        st.success("Alert acknowledged")


def render_compliance_summary_table(data: List[Dict[str, Any]]) -> None:
    """Render a compliance summary table with formatting."""
    
    if not data:
        st.info("No compliance data available")
        return
    
    df = pd.DataFrame(data)
    
    # Format percentage columns
    percentage_cols = [col for col in df.columns if "score" in col.lower() or "%" in col]
    for col in percentage_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"{x:.1f}%" if isinstance(x, (int, float)) else x)
    
    st.dataframe(df, width="stretch")


def render_system_impact_card(system_name: str,
                             impact_score: float,
                             affected_regulations: List[str],
                             remediation_items: int) -> None:
    """Render a system impact assessment card."""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Impact Score", f"{impact_score:.1f}/10")
    
    with col2:
        st.metric("Affected Regulations", len(affected_regulations))
    
    with col3:
        st.metric("Remediation Items", remediation_items)
    
    with st.expander("View Details"):
        st.write("**Affected Regulations:**")
        for reg in affected_regulations:
            st.write(f"- {reg}")


def render_deployment_progress(phases: Dict[str, float]) -> None:
    """Render deployment progress visualization."""
    
    data = []
    for phase_name, completion in phases.items():
        data.append({
            "Phase": phase_name,
            "Completed": completion,
            "Remaining": 100 - completion
        })
    
    df = pd.DataFrame(data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df["Phase"],
        y=df["Completed"],
        name="Completed",
        marker_color="#4CAF50"
    ))
    
    fig.add_trace(go.Bar(
        x=df["Phase"],
        y=df["Remaining"],
        name="Remaining",
        marker_color="#E0E0E0"
    ))
    
    fig.update_layout(
        barmode="stack",
        title="Deployment Progress by Phase",
        xaxis_title="Phase",
        yaxis_title="Progress (%)",
        height=400,
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, width="stretch")


def render_regulatory_framework_matrix(frameworks: Dict[str, Dict[str, str]]) -> None:
    """Render regulatory framework compatibility matrix."""
    
    framework_names = list(frameworks.keys())
    dimensions = set()
    
    for framework_data in frameworks.values():
        dimensions.update(framework_data.keys())
    
    dimensions = sorted(list(dimensions))
    
    # Create status matrix
    status_symbols = {
        "compliant": "✓",
        "partial": "◐",
        "non_compliant": "✗",
        "unknown": "?"
    }
    
    rows = []
    for dimension in dimensions:
        row = {"Dimension": dimension}
        for framework in framework_names:
            status = frameworks[framework].get(dimension, "unknown")
            row[framework] = status_symbols.get(status, "?")
        rows.append(row)
    
    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch")


def render_quick_action_panel() -> Optional[str]:
    """Render a quick action selection panel."""
    
    st.markdown("### Quick Actions")
    
    action_cols = st.columns(4)
    
    actions = [
        ("📋", "View Alerts", "view_alerts"),
        ("📊", "Generate Report", "generate_report"),
        ("🔍", "Run Audit", "run_audit"),
        ("⚙️", "Configure", "configure")
    ]
    
    selected_action = None
    
    for idx, (icon, label, action_key) in enumerate(actions):
        with action_cols[idx]:
            if st.button(f"{icon}\n{label}", key=f"action_{action_key}"):
                selected_action = action_key
    
    return selected_action
