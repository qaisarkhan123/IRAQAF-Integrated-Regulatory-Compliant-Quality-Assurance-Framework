

from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash, make_response
import logging
import sys
import os
from pathlib import Path
import requests
import time
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.utils
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import scipy.stats as stats
import pickle
import hashlib
import re
from difflib import SequenceMatcher
from collections import defaultdict
import uuid
import secrets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'iraqaf_enhanced_auth_secret_key_2024'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Global configuration
app.config.update({
    'TEMPLATES_AUTO_RELOAD': True,
    'SEND_FILE_MAX_AGE_DEFAULT': 0,
    'JSON_SORT_KEYS': False
})

def setup_paths():
    """Setup project paths for imports"""
    try:
        current_dir = Path(__file__).parent if '__file__' in globals() else Path.cwd()
        project_root = current_dir.parent if current_dir.name == 'dashboard' else current_dir
        
        paths_to_add = [str(project_root), str(current_dir)]
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
        
        return project_root, current_dir
    except Exception as e:
        logger.error(f"Path setup failed: {e}")
        return Path.cwd(), Path.cwd()

# Setup paths
project_root, dashboard_dir = setup_paths()

# Import authentication system
try:
    from flask_auth_enhanced import (
        FlaskAuthenticationManager, 
        login_required, 
        permission_required, 
        admin_required,
        TwoFactorAuth
    )
    auth_manager = FlaskAuthenticationManager()
    logger.info("Enhanced authentication system loaded successfully")
except ImportError as e:
    logger.error(f"Failed to load authentication system: {e}")
    auth_manager = None

# ============================================================================
# SESSION MANAGEMENT (Authentication Removed)

# ============================================================================

def get_user_preferences():
    """Get user preferences from session with defaults"""
    return session.get('user_preferences', {
        'theme': 'light',
        'layout': 'wide',
        'auto_refresh': False,
        'refresh_interval': 30
    })

def save_user_preferences(preferences):
    """Save user preferences to session"""
    session['user_preferences'] = preferences
    session.permanent = True

@app.after_request
def after_request(response):
    """Add cache control headers to prevent caching issues"""
    # Only apply no-cache to dynamic content, not static resources
    if request.endpoint in ['dashboard', 'api_dashboard_data', 'api_live_data']:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Special headers for login page to prevent password manager interference
    if request.endpoint == 'login':
        response.headers['Content-Security-Policy'] = "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; connect-src 'self'; default-src 'self'"
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Permissions-Policy'] = 'password-managers=()'
    
    return response

# ============================================================================
# DATA FETCHING & PROCESSING
# ============================================================================

def fetch_live_hub_data():
    """Fetch live data from all hub APIs"""
    hub_endpoints = {
        'uqo': 'http://localhost:8507/api/qa-overview',
        'l1_crs': 'http://localhost:8504/api/crs',
        'l2_sai': 'http://localhost:8502/api/metrics',
        'l3_fairness': 'http://localhost:8506/api/fi',
        'l4_transparency': 'http://localhost:5000/api/transparency-score',
        'soqm_status': 'http://localhost:8503/api/status',
        'cae_alerts': 'http://localhost:8508/api/alerts'
    }
    
    live_data = {}
    response_times = {}
    
    for hub_name, url in hub_endpoints.items():
        try:
            start_time = time.time()
            response = requests.get(url, timeout=3)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                live_data[hub_name] = response.json()
                response_times[hub_name] = response_time
            else:
                live_data[hub_name] = {'error': f'HTTP {response.status_code}'}
                response_times[hub_name] = None
        except Exception as e:
            live_data[hub_name] = {'error': str(e)}
            response_times[hub_name] = None
    
    return live_data, response_times

def get_hub_health_status():
    """Get comprehensive hub health status"""
    hubs_info = [
        ("L1 Regulations & Governance", 8504, "⚖️"),
        ("L2 Privacy & Security", 8502, "🔐"),
        ("L3 Fairness & Ethics", 8506, "⚖️"),
        ("L4 Explainability & Transparency", 5000, "🔍"),
        ("System Operations & QA Monitor (SOQM)", 8503, "⚙️"),
        ("Unified QA Orchestrator (UQO)", 8507, "📊"),
        ("Continuous Assurance Engine (CAE)", 8508, "🤖")
    ]
    
    # Define correct health endpoints for each hub
    health_endpoints = {
        "L1 Regulations & Governance": "/",
        "L2 Privacy & Security": "/",
        "L3 Fairness & Ethics": "/health",
        "L4 Explainability & Transparency": "/health",
        "System Operations & QA Monitor (SOQM)": "/api/health",
        "Unified QA Orchestrator (UQO)": "/health",
        "Continuous Assurance Engine (CAE)": "/api/health"
    }
    
    health_status = {}
    
    for name, port, icon in hubs_info:
        try:
            start_time = time.time()
            endpoint = health_endpoints.get(name, "/health")
            response = requests.get(f"http://localhost:{port}{endpoint}", timeout=5)
            
            response_time = (time.time() - start_time) * 1000
            online = response.status_code == 200
            
            health_status[name] = {
                'online': online,
                'response_time': response_time,
                'port': port,
                'icon': icon,
                'status_code': response.status_code
            }
        except Exception as e:
            health_status[name] = {
                'online': False,
                'response_time': None,
                'port': port,
                'icon': icon,
                'error': str(e)
            }
    
    return health_status

def get_system_alerts(live_data, health_status):
    """Generate system alerts based on hub data and health status"""
    alerts = []
    current_time = datetime.now()
    
    # Check for offline hubs
    for hub_name, status in health_status.items():
        if not status['online']:
            alerts.append({
                'id': f"hub_offline_{hub_name.lower().replace(' ', '_')}",
                'type': 'System',
                'severity': 'critical',
                'title': f'{hub_name} Hub Offline',
                'message': f'The {hub_name} hub is not responding. This may affect related functionality.',
                'source': 'System Monitor',
                'timestamp': current_time,
                'action_required': True,
                'icon': '🔴'
            })
    
    # Check for slow response times
    for hub_name, status in health_status.items():
        if status['online'] and status.get('response_time', 0) > 2000:  # > 2 seconds
            alerts.append({
                'id': f"slow_response_{hub_name.lower().replace(' ', '_')}",
                'type': 'Performance',
                'severity': 'warning',
                'title': f'{hub_name} Slow Response',
                'message': f'Response time is {status["response_time"]:.0f}ms (threshold: 2000ms)',
                'source': 'Performance Monitor',
                'timestamp': current_time,
                'action_required': False,
                'icon': '⚠️'
            })
    
    # Check for low scores
    if 'l1_crs' in live_data and 'error' not in live_data['l1_crs']:
        crs = live_data['l1_crs'].get('crs', 100)
        if crs < 70:
            alerts.append({
                'id': 'low_crs_score',
                'type': 'Compliance',
                'severity': 'warning',
                'title': 'Low Compliance Score',
                'message': f'CRS score is {crs:.1f}% (threshold: 70%)',
                'source': 'L1 Regulations Hub',
                'timestamp': current_time,
                'action_required': True,
                'icon': '⚖️'
            })
    
    return alerts

def get_alert_summary(alerts):
    """Get alert summary statistics"""
    summary = {
        'total': len(alerts),
        'critical': len([a for a in alerts if a['severity'] == 'critical']),
        'warning': len([a for a in alerts if a['severity'] == 'warning']),
        'info': len([a for a in alerts if a['severity'] == 'info'])
    }
    return summary

# ============================================================================
# CHART GENERATION FUNCTIONS
# ============================================================================

def create_hub_performance_chart(live_data, response_times):
    """Create interactive hub performance chart"""
    hub_names = []
    scores = []
    colors = []
    
    # Extract scores from live data
    if 'l1_crs' in live_data and 'error' not in live_data['l1_crs']:
        hub_names.append('L1 CRS')
        scores.append(live_data['l1_crs'].get('crs', 0))
        colors.append('#3B82F6')
    
    if 'l2_sai' in live_data and 'error' not in live_data['l2_sai']:
        hub_names.append('L2 SAI')
        scores.append(live_data['l2_sai'].get('sai', 0))
        colors.append('#10B981')
    
    if 'l3_fairness' in live_data and 'error' not in live_data['l3_fairness']:
        hub_names.append('L3 FI')
        scores.append(live_data['l3_fairness'].get('fairness_index', 0))
        colors.append('#F59E0B')
    
    if 'l4_transparency' in live_data and 'error' not in live_data['l4_transparency']:
        hub_names.append('L4 TS')
        scores.append(live_data['l4_transparency'].get('transparency_score', 0))
        colors.append('#8B5CF6')
    
    if not hub_names:
        # Fallback with mock data
        hub_names = ['L1 CRS', 'L2 SAI', 'L3 FI', 'L4 TS']
        scores = [75.2, 82.1, 68.9, 85.0]
        colors = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6']
    
    fig = go.Figure(data=[
        go.Bar(
            x=hub_names,
            y=scores,
            marker_color=colors,
            text=[f"{score:.1f}%" for score in scores],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Hub Performance Scores",
        xaxis_title="Hubs",
        yaxis_title="Score (%)",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig

def create_compliance_radar_chart(live_data):
    """Create compliance radar chart"""
    categories = ['Compliance', 'Security', 'Fairness', 'Transparency', 'Operations']
    
    # Extract values from live data or use defaults
    values = []
    if 'l1_crs' in live_data and 'error' not in live_data['l1_crs']:
        values.append(live_data['l1_crs'].get('crs', 75))
    else:
        values.append(75)
    
    if 'l2_sai' in live_data and 'error' not in live_data['l2_sai']:
        values.append(live_data['l2_sai'].get('sai', 82))
    else:
        values.append(82)
    
    if 'l3_fairness' in live_data and 'error' not in live_data['l3_fairness']:
        values.append(live_data['l3_fairness'].get('fairness_index', 69))
    else:
        values.append(69)
    
    if 'l4_transparency' in live_data and 'error' not in live_data['l4_transparency']:
        values.append(live_data['l4_transparency'].get('transparency_score', 85))
    else:
        values.append(85)
    
    # SOQM operations score (mock)
    values.append(78)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Current Performance',
        line_color='#3B82F6'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Compliance Radar Overview",
        height=400
    )
    
    return fig

def create_trend_chart():
    """Create quality trends chart"""
    # Generate mock historical data
    dates = pd.date_range(start='2024-10-01', end='2024-11-21', freq='D')
    
    np.random.seed(42)
    base_crs = 75 + np.random.normal(0, 5, len(dates)).cumsum() * 0.1
    base_sai = 80 + np.random.normal(0, 3, len(dates)).cumsum() * 0.1
    base_fi = 70 + np.random.normal(0, 4, len(dates)).cumsum() * 0.1
    base_ts = 85 + np.random.normal(0, 2, len(dates)).cumsum() * 0.1
    
    # Ensure values stay within reasonable bounds
    base_crs = np.clip(base_crs, 40, 95)
    base_sai = np.clip(base_sai, 50, 95)
    base_fi = np.clip(base_fi, 30, 95)
    base_ts = np.clip(base_ts, 60, 95)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=base_crs,
        mode='lines+markers',
        name='Compliance (CRS)',
        line=dict(color='#3B82F6', width=3),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=base_sai,
        mode='lines+markers',
        name='Security (SAI)',
        line=dict(color='#10B981', width=3),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=base_fi,
        mode='lines+markers',
        name='Fairness (FI)',
        line=dict(color='#F59E0B', width=3),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=base_ts,
        mode='lines+markers',
        name='Transparency (TS)',
        line=dict(color='#8B5CF6', width=3),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title="Quality Trends (Last 30 Days)",
        xaxis_title="Date",
        yaxis_title="Score (%)",
        height=500,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Enhanced login page with 2FA support"""
    if not auth_manager:
        flash('Authentication system not available', 'error')
        return redirect(url_for('dashboard'))
    
    # If user is already authenticated, redirect to dashboard
    if session.get('authenticated'):
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        two_fa_token = request.form.get('two_fa_token', '').strip()
        remember_me = 'remember_me' in request.form
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        # Attempt authentication
        success, result = auth_manager.authenticate(username, password, two_fa_token)
        
        if success:
            # Successful login
            user_data = result
            session['authenticated'] = True
            session['username'] = user_data['username']
            session['email'] = user_data['email']
            session['role'] = user_data['role']
            session['permissions'] = user_data['permissions']
            session['two_fa_enabled'] = user_data['two_fa_enabled']
            session['login_time'] = datetime.now().isoformat()
            session['session_id'] = secrets.token_hex(16)
            
            if remember_me:
                session.permanent = True
            
            flash(f'Welcome back, {username}!', 'success')
            # Add a small delay to ensure session is properly set
            response = make_response(redirect(url_for('dashboard')))
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        
        elif result and result.get('requires_2fa'):
            # 2FA required
            session['pending_username'] = username
            session['pending_password'] = password
            flash('Please enter your 2FA code', 'info')
            return render_template('login.html', requires_2fa=True)
        
        else:
            # Authentication failed
            flash('Invalid credentials or account locked', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    username = session.get('username', 'Unknown')
    
    # Log logout event
    if auth_manager and username != 'Unknown':
        auth_manager.audit_logger.log_event("LOGOUT", username)
    
    # Clear session
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/setup-2fa')
@login_required
def setup_2fa():
    """Setup 2FA for current user"""
    if not auth_manager:
        flash('Authentication system not available', 'error')
        return redirect(url_for('dashboard'))
    
    username = session.get('username')
    success, result = auth_manager.setup_2fa(username)
    
    if success:
        return render_template('setup_2fa.html', 
                             qr_code=result['qr_code'],
                             backup_codes=result['backup_codes'])
    else:
        flash('Failed to setup 2FA', 'error')
        return redirect(url_for('settings'))

@app.route('/enable-2fa', methods=['POST'])
@login_required
def enable_2fa():
    """Enable 2FA after verification"""
    if not auth_manager:
        flash('Authentication system not available', 'error')
        return redirect(url_for('dashboard'))
    
    username = session.get('username')
    token = request.form.get('verification_token', '').strip()
    
    if not token:
        flash('Please enter verification code', 'error')
        return redirect(url_for('setup_2fa'))
    
    success, message = auth_manager.enable_2fa(username, token)
    
    if success:
        session['two_fa_enabled'] = True
        flash('2FA enabled successfully!', 'success')
    else:
        flash(f'Failed to enable 2FA: {message}', 'error')
    
    return redirect(url_for('settings'))

@app.route('/create-user', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Create new user (admin only)"""
    if not auth_manager:
        flash('Authentication system not available', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        role = request.form.get('role', 'viewer')
        
        if not all([username, password, email]):
            flash('All fields are required', 'error')
            return render_template('create_user.html')
        
        success, message = auth_manager.create_user(username, password, email, role)
        
        if success:
            flash(f'User {username} created successfully', 'success')
            return redirect(url_for('manage_users'))
        else:
            flash(f'Failed to create user: {message}', 'error')
    
    return render_template('create_user.html')

@app.route('/manage-users')
@admin_required
def manage_users():
    """Manage users (admin only)"""
    if not auth_manager:
        flash('Authentication system not available', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all users (this would need to be implemented in auth_manager)
    # For now, just redirect to settings
    return redirect(url_for('settings'))

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/ping')
def ping():
    """Simple ping endpoint for performance testing"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/')
def root():
    """Root route - always redirect to login page"""
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page with optimized loading"""
    preferences = get_user_preferences()
    current_time = datetime.now()
    
    # Load data asynchronously or use cached/mock data for faster initial load
    # For immediate display, use mock data and load real data via AJAX
    mock_metrics = {
        'crs': 75.2,
        'sai': 82.1, 
        'fi': 68.9,
        'ts': 85.0,
        'cqs': 78.5
    }
    
    mock_health_status = {
        'L1 Regulations & Governance': {'online': True, 'response_time': 150, 'port': 8504, 'icon': '⚖️'},
        'L2 Privacy & Security': {'online': True, 'response_time': 120, 'port': 8502, 'icon': '🔐'},
        'L3 Fairness & Ethics': {'online': True, 'response_time': 180, 'port': 8506, 'icon': '⚖️'},
        'L4 Explainability & Transparency': {'online': True, 'response_time': 200, 'port': 5000, 'icon': '🔍'},
        'System Operations & QA Monitor (SOQM)': {'online': True, 'response_time': 160, 'port': 8503, 'icon': '⚙️'},
        'Unified QA Orchestrator (UQO)': {'online': True, 'response_time': 140, 'port': 8507, 'icon': '📊'},
        'Continuous Assurance Engine (CAE)': {'online': True, 'response_time': 170, 'port': 8508, 'icon': '🤖'}
    }
    
    mock_alerts = []  # Start with no alerts for fast loading
    mock_alert_summary = {'total': 0, 'critical': 0, 'warning': 0, 'info': 0}
    
    online_hubs = sum(1 for status in mock_health_status.values() if status['online'])
    total_hubs = len(mock_health_status)
    system_uptime = (online_hubs / total_hubs) * 100 if total_hubs > 0 else 0
    avg_response = 155  # Mock average
    
    return render_template('dashboard.html',
                         preferences=preferences,
                         health_status=mock_health_status,
                         metrics=mock_metrics,
                         alerts=mock_alerts,
                         alert_summary=mock_alert_summary,
                         online_hubs=online_hubs,
                         total_hubs=total_hubs,
                         system_uptime=system_uptime,
                         avg_response=avg_response,
                         username=session.get('username', 'User'),
                         user_role=session.get('role', 'viewer'),
                         user_permissions=session.get('permissions', []),
                         current_time=current_time,
                         fast_load=True,  # Flag to indicate this is fast load mode
                         cache_buster=int(time.time()))  # Add cache buster for CSS/JS

@app.route('/hub-overview')
@login_required
def hub_overview():
    """Hub overview page"""
    health_status = get_hub_health_status()
    return render_template('hub_overview.html', health_status=health_status)

@app.route('/charts')
@login_required
def charts():
    """Interactive charts page"""
    live_data, response_times = fetch_live_hub_data()
    
    # Generate charts
    perf_chart = create_hub_performance_chart(live_data, response_times)
    radar_chart = create_compliance_radar_chart(live_data)
    trend_chart = create_trend_chart()
    
    # Convert charts to JSON for frontend
    charts_json = {
        'performance': plotly.utils.PlotlyJSONEncoder().encode(perf_chart),
        'radar': plotly.utils.PlotlyJSONEncoder().encode(radar_chart),
        'trends': plotly.utils.PlotlyJSONEncoder().encode(trend_chart)
    }
    
    return render_template('charts.html', charts=charts_json)

@app.route('/alerts')
@login_required
def alerts_page():
    """Alerts management page"""
    live_data, _ = fetch_live_hub_data()
    health_status = get_hub_health_status()
    alerts = get_system_alerts(live_data, health_status)
    alert_summary = get_alert_summary(alerts)
    
    # Filter alerts based on query parameters
    severity_filter = request.args.get('severity', 'all')
    source_filter = request.args.get('source', 'all')
    
    filtered_alerts = alerts
    if severity_filter != 'all':
        filtered_alerts = [a for a in filtered_alerts if a['severity'] == severity_filter]
    if source_filter != 'all':
        filtered_alerts = [a for a in filtered_alerts if a['source'] == source_filter]
    
    # Get current time for display
    current_time = datetime.now()
    
    return render_template('alerts.html',
                         alerts=filtered_alerts,
                         alert_summary=alert_summary,
                         severity_filter=severity_filter,
                         source_filter=source_filter,
                         all_sources=list(set([a['source'] for a in alerts])),
                         current_time=current_time)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page"""
    if request.method == 'POST':
        preferences = {
            'theme': request.form.get('theme', 'light'),
            'layout': request.form.get('layout', 'wide'),
            'auto_refresh': 'auto_refresh' in request.form,
            'refresh_interval': int(request.form.get('refresh_interval', 30))
        }
        save_user_preferences(preferences)
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('settings'))
    
    preferences = get_user_preferences()
    current_time = datetime.now()
    return render_template('settings.html', preferences=preferences, current_time=current_time)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/live-data')
@login_required
def api_live_data():
    """API endpoint for live hub data"""
    live_data, response_times = fetch_live_hub_data()
    return jsonify({
        'data': live_data,
        'response_times': response_times,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/dashboard-data')
@login_required
def api_dashboard_data():
    """Fast API endpoint for dashboard data with real hub status"""
    try:
        # This will be called asynchronously after page load
        live_data, response_times = fetch_live_hub_data()
        health_status = get_hub_health_status()
        alerts = get_system_alerts(live_data, health_status)
        alert_summary = get_alert_summary(alerts)
        
        # Calculate summary metrics
        online_hubs = sum(1 for status in health_status.values() if status['online'])
        total_hubs = len(health_status)
        system_uptime = (online_hubs / total_hubs) * 100 if total_hubs > 0 else 0
        
        # Extract key metrics with proper error handling
        def safe_get_metric(data, key, default='N/A'):
            if key in data and 'error' not in data[key]:
                return data[key].get(key.split('_')[-1], default)
            return default
        
        metrics = {
            'crs': safe_get_metric(live_data, 'l1_crs', 75.2),
            'sai': safe_get_metric(live_data, 'l2_sai', 82.1),
            'fi': safe_get_metric(live_data, 'l3_fairness', 68.9),
            'ts': safe_get_metric(live_data, 'l4_transparency', 85.0),
            'cqs': safe_get_metric(live_data, 'uqo', 78.5)
        }
        
        # Calculate average response time
        valid_times = [t for t in response_times.values() if t is not None]
        avg_response = sum(valid_times) / len(valid_times) if valid_times else None
        
        return jsonify({
            'health_status': health_status,
            'metrics': metrics,
            'alerts': alerts,
            'alert_summary': alert_summary,
            'online_hubs': online_hubs,
            'total_hubs': total_hubs,
            'system_uptime': system_uptime,
            'avg_response': avg_response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        return jsonify({'error': 'Failed to fetch data'}), 500

@app.route('/api/health-status')
@login_required
def api_health_status():
    """API endpoint for hub health status"""
    health_status = get_hub_health_status()
    return jsonify({
        'health_status': health_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/alerts')
@login_required
def api_alerts():
    """API endpoint for system alerts"""
    live_data, _ = fetch_live_hub_data()
    health_status = get_hub_health_status()
    alerts = get_system_alerts(live_data, health_status)
    alert_summary = get_alert_summary(alerts)
    
    return jsonify({
        'alerts': alerts,
        'summary': alert_summary,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/charts/<chart_type>')
@login_required
def api_charts(chart_type):
    """API endpoint for chart data"""
    live_data, response_times = fetch_live_hub_data()
    
    if chart_type == 'performance':
        chart = create_hub_performance_chart(live_data, response_times)
    elif chart_type == 'radar':
        chart = create_compliance_radar_chart(live_data)
    elif chart_type == 'trends':
        chart = create_trend_chart()
    else:
        return jsonify({'error': 'Invalid chart type'}), 400
    
    return jsonify({
        'chart': plotly.utils.PlotlyJSONEncoder().encode(chart),
        'timestamp': datetime.now().isoformat()
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    print("="*60)
    print("IRAQAF Dashboard - Flask Version")
    print("="*60)
    print("URL: http://localhost:8510")
    print("Login: admin / admin")
    print("Features: All dashboard functionality converted to Flask")
    print("="*60)
    print("Starting server...")
    
    # Optimize for fast startup - no reloader, no debug, threaded
    app.run(host='0.0.0.0', port=8510, debug=False, threaded=True, use_reloader=False)
