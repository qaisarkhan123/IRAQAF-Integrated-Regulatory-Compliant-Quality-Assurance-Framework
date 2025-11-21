"""
WebSocket Handler for Real-time Dashboard Updates
Provides real-time data streaming for IRAQAF dashboards
"""

import json
import logging
import asyncio
import threading
import time
from datetime import datetime
from typing import Dict, List, Set, Any, Optional
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections and real-time updates"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
        self.connected_clients: Set[str] = set()
        self.client_rooms: Dict[str, str] = {}
        self.update_thread = None
        self.running = False
        
        # Hub URLs for data collection
        self.hub_urls = {
            "l1": "http://localhost:8504/api/crs",
            "l2": "http://localhost:8502/api/sai",
            "l3_fairness": "http://localhost:8506/api/summary",
            "l4": "http://localhost:5000/api/transparency-score",
            "soqm": "http://localhost:8503/api/status",
            "cae": "http://localhost:8508/api/internal-cqs"
        }
        
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            client_id = self._get_client_id()
            self.connected_clients.add(client_id)
            logger.info(f"Client connected: {client_id}")
            
            # Send initial data
            initial_data = self._collect_current_data()
            emit('initial_data', initial_data)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            client_id = self._get_client_id()
            self.connected_clients.discard(client_id)
            if client_id in self.client_rooms:
                del self.client_rooms[client_id]
            logger.info(f"Client disconnected: {client_id}")
        
        @self.socketio.on('join_dashboard')
        def handle_join_dashboard(data):
            client_id = self._get_client_id()
            dashboard_type = data.get('dashboard', 'main')
            room = f"dashboard_{dashboard_type}"
            
            join_room(room)
            self.client_rooms[client_id] = room
            logger.info(f"Client {client_id} joined {room}")
            
            # Send dashboard-specific data
            dashboard_data = self._get_dashboard_data(dashboard_type)
            emit('dashboard_data', dashboard_data)
        
        @self.socketio.on('request_update')
        def handle_request_update():
            """Handle manual update requests"""
            client_id = self._get_client_id()
            logger.info(f"Manual update requested by {client_id}")
            
            current_data = self._collect_current_data()
            emit('data_update', current_data)
        
        @self.socketio.on('subscribe_alerts')
        def handle_subscribe_alerts():
            """Subscribe to alert notifications"""
            client_id = self._get_client_id()
            join_room('alerts')
            logger.info(f"Client {client_id} subscribed to alerts")
    
    def _get_client_id(self) -> str:
        """Get unique client identifier"""
        from flask import request
        return request.sid
    
    def _collect_current_data(self) -> Dict[str, Any]:
        """Collect current data from all hubs"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "hubs": {},
            "summary": {}
        }
        
        # Collect data from each hub
        for hub_name, url in self.hub_urls.items():
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    hub_data = response.json()
                    data["hubs"][hub_name] = {
                        "status": "online",
                        "data": hub_data,
                        "response_time": response.elapsed.total_seconds() * 1000
                    }
                else:
                    data["hubs"][hub_name] = {
                        "status": "error",
                        "error": f"HTTP {response.status_code}",
                        "response_time": None
                    }
            except Exception as e:
                data["hubs"][hub_name] = {
                    "status": "offline",
                    "error": str(e),
                    "response_time": None
                }
        
        # Calculate summary metrics
        data["summary"] = self._calculate_summary(data["hubs"])
        
        return data
    
    def _calculate_summary(self, hub_data: Dict) -> Dict[str, Any]:
        """Calculate summary metrics from hub data"""
        online_hubs = sum(1 for hub in hub_data.values() if hub["status"] == "online")
        total_hubs = len(hub_data)
        
        # Extract key metrics
        cqs = None
        if "uqo" in hub_data and hub_data["uqo"]["status"] == "online":
            cqs_data = hub_data["uqo"]["data"]
            if isinstance(cqs_data, dict) and "cqs" in cqs_data:
                cqs = cqs_data["cqs"]
        
        # Calculate average response time
        response_times = [hub["response_time"] for hub in hub_data.values() 
                         if hub["response_time"] is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else None
        
        return {
            "system_health": (online_hubs / total_hubs) * 100,
            "online_hubs": online_hubs,
            "total_hubs": total_hubs,
            "cqs": cqs,
            "avg_response_time": avg_response_time,
            "last_update": datetime.now().isoformat()
        }
    
    def _get_dashboard_data(self, dashboard_type: str) -> Dict[str, Any]:
        """Get specific data for dashboard type"""
        current_data = self._collect_current_data()
        
        if dashboard_type == "main":
            return current_data
        elif dashboard_type == "alerts":
            return self._get_alerts_data()
        elif dashboard_type == "trends":
            return self._get_trends_data()
        else:
            return current_data
    
    def _get_alerts_data(self) -> Dict[str, Any]:
        """Get current alerts data"""
        try:
            # Try to get alerts from UQO
            response = requests.get("http://localhost:8507/api/alerts", timeout=3)
            if response.status_code == 200:
                return {
                    "alerts": response.json(),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
        
        return {
            "alerts": [],
            "error": "Could not fetch alerts",
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_trends_data(self) -> Dict[str, Any]:
        """Get trends data"""
        try:
            # Try to get historical data from UQO
            response = requests.get("http://localhost:8507/api/qa-history", timeout=3)
            if response.status_code == 200:
                return {
                    "trends": response.json(),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error fetching trends: {e}")
        
        return {
            "trends": [],
            "error": "Could not fetch trends",
            "timestamp": datetime.now().isoformat()
        }
    
    def start_background_updates(self, interval: int = 30):
        """Start background thread for periodic updates"""
        if self.running:
            return
        
        self.running = True
        
        def update_loop():
            while self.running:
                try:
                    if self.connected_clients:
                        # Collect fresh data
                        current_data = self._collect_current_data()
                        
                        # Broadcast to all connected clients
                        self.socketio.emit('data_update', current_data)
                        
                        # Check for alerts and broadcast if any
                        alerts_data = self._get_alerts_data()
                        if alerts_data.get("alerts"):
                            self.socketio.emit('alert_update', alerts_data, room='alerts')
                        
                        logger.debug(f"Broadcasted update to {len(self.connected_clients)} clients")
                    
                    time.sleep(interval)
                
                except Exception as e:
                    logger.error(f"Error in update loop: {e}")
                    time.sleep(interval)
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
        logger.info(f"Started background updates with {interval}s interval")
    
    def stop_background_updates(self):
        """Stop background updates"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
        logger.info("Stopped background updates")
    
    def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Broadcast alert to subscribed clients"""
        self.socketio.emit('new_alert', alert_data, room='alerts')
        logger.info(f"Broadcasted alert: {alert_data.get('title', 'Unknown')}")
    
    def broadcast_system_event(self, event_type: str, event_data: Dict[str, Any]):
        """Broadcast system events to all clients"""
        event_message = {
            "type": event_type,
            "data": event_data,
            "timestamp": datetime.now().isoformat()
        }
        self.socketio.emit('system_event', event_message)
        logger.info(f"Broadcasted system event: {event_type}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            "connected_clients": len(self.connected_clients),
            "active_rooms": len(set(self.client_rooms.values())),
            "update_thread_running": self.running,
            "timestamp": datetime.now().isoformat()
        }


class ExportManager:
    """Manages data export functionality"""
    
    def __init__(self):
        self.export_formats = ["json", "csv", "pdf", "excel"]
        self.exports_dir = "exports"
        self._ensure_exports_dir()
    
    def _ensure_exports_dir(self):
        """Ensure exports directory exists"""
        import os
        os.makedirs(self.exports_dir, exist_ok=True)
    
    def export_data(self, data: Dict[str, Any], format_type: str, 
                   filename: Optional[str] = None) -> str:
        """Export data in specified format"""
        if format_type not in self.export_formats:
            raise ValueError(f"Unsupported format: {format_type}")
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"iraqaf_export_{timestamp}.{format_type}"
        
        filepath = f"{self.exports_dir}/{filename}"
        
        if format_type == "json":
            return self._export_json(data, filepath)
        elif format_type == "csv":
            return self._export_csv(data, filepath)
        elif format_type == "pdf":
            return self._export_pdf(data, filepath)
        elif format_type == "excel":
            return self._export_excel(data, filepath)
    
    def _export_json(self, data: Dict[str, Any], filepath: str) -> str:
        """Export data as JSON"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return filepath
    
    def _export_csv(self, data: Dict[str, Any], filepath: str) -> str:
        """Export data as CSV"""
        import pandas as pd
        
        # Flatten data for CSV export
        flattened_data = self._flatten_dict(data)
        df = pd.DataFrame([flattened_data])
        df.to_csv(filepath, index=False)
        return filepath
    
    def _export_pdf(self, data: Dict[str, Any], filepath: str) -> str:
        """Export data as PDF report"""
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        doc = SimpleDocTemplate(filepath)
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        story.append(Paragraph("IRAQAF Data Export", styles['Title']))
        story.append(Spacer(1, 12))
        
        # Add timestamp
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Add data summary
        if "summary" in data:
            story.append(Paragraph("Summary", styles['Heading2']))
            for key, value in data["summary"].items():
                story.append(Paragraph(f"{key}: {value}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        doc.build(story)
        return filepath
    
    def _export_excel(self, data: Dict[str, Any], filepath: str) -> str:
        """Export data as Excel file"""
        import pandas as pd
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            if "summary" in data:
                summary_df = pd.DataFrame([data["summary"]])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Hub data sheets
            if "hubs" in data:
                for hub_name, hub_data in data["hubs"].items():
                    if hub_data.get("status") == "online" and "data" in hub_data:
                        hub_df = pd.DataFrame([hub_data["data"]])
                        sheet_name = f"{hub_name.upper()}_Data"[:31]  # Excel sheet name limit
                        hub_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return filepath
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)


# Global instances
websocket_manager = None
export_manager = ExportManager()

def initialize_websocket(app: Flask) -> WebSocketManager:
    """Initialize WebSocket manager"""
    global websocket_manager
    websocket_manager = WebSocketManager(app)
    return websocket_manager

def get_websocket_manager() -> Optional[WebSocketManager]:
    """Get WebSocket manager instance"""
    return websocket_manager

def get_export_manager() -> ExportManager:
    """Get export manager instance"""
    return export_manager

if __name__ == "__main__":
    # Test the WebSocket and export functionality
    from flask import Flask
    
    app = Flask(__name__)
    ws_manager = initialize_websocket(app)
    
    print("WebSocket manager initialized")
    print("Starting background updates...")
    ws_manager.start_background_updates(interval=10)
    
    # Test export functionality
    test_data = {
        "summary": {"cqs": 85.2, "online_hubs": 6, "total_hubs": 7},
        "timestamp": datetime.now().isoformat()
    }
    
    export_mgr = get_export_manager()
    json_file = export_mgr.export_data(test_data, "json")
    print(f"Test export created: {json_file}")
    
    # Run the app
    ws_manager.socketio.run(app, debug=True, port=5001)
