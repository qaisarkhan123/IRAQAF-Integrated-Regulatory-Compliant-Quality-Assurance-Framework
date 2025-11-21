"""
Hub Service - Manages communication with all IRAQAF hubs
"""

import requests
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class HubInfo:
    """Information about a hub"""
    name: str
    port: int
    url: str
    icon: str
    description: str
    health_endpoint: str
    api_endpoints: Dict[str, str]

class HubService:
    """Service for managing hub communications"""
    
    def __init__(self):
        self.hubs = {
            'l1': HubInfo(
                name="L1 Regulations & Governance",
                port=8504,
                url="http://localhost:8504",
                icon="⚖️",
                description="Compliance requirements foundation",
                health_endpoint="/health",
                api_endpoints={
                    'summary': '/api/summary',
                    'crs': '/api/crs',
                    'frameworks': '/api/frameworks'
                }
            ),
            'l2': HubInfo(
                name="L2 Privacy & Security",
                port=8502,
                url="http://localhost:8502",
                icon="🔐",
                description="Privacy/security requirements",
                health_endpoint="/health",
                api_endpoints={
                    'metrics': '/api/metrics',
                    'sai': '/api/sai'
                }
            ),
            'l3_fairness': HubInfo(
                name="L3 Fairness & Ethics",
                port=8506,
                url="http://localhost:8506",
                icon="⚖️",
                description="Fairness evaluation & ethics",
                health_endpoint="/health",
                api_endpoints={
                    'summary': '/api/summary',
                    'fi': '/api/fi',
                    'eml': '/api/eml'
                }
            ),
            'l4': HubInfo(
                name="L4 Explainability & Transparency",
                port=5000,
                url="http://localhost:5000",
                icon="🔍",
                description="AI transparency & explainability",
                health_endpoint="/health",
                api_endpoints={
                    'metrics': '/api/explainability-metrics',
                    'transparency': '/api/transparency-score'
                }
            ),
            'soqm': HubInfo(
                name="System Operations & QA Monitor",
                port=8503,
                url="http://localhost:8503",
                icon="⚙️",
                description="System operations & QA monitoring",
                health_endpoint="/health",
                api_endpoints={
                    'status': '/api/status'
                }
            ),
            'uqo': HubInfo(
                name="Unified QA Orchestrator",
                port=8507,
                url="http://localhost:8507",
                icon="📊",
                description="Unified QA orchestration",
                health_endpoint="/health",
                api_endpoints={
                    'overview': '/api/qa-overview',
                    'cqs': '/api/unified-cqs'
                }
            ),
            'cae': HubInfo(
                name="Continuous Assurance Engine",
                port=8508,
                url="http://localhost:8508",
                icon="🤖",
                description="Continuous assurance engine",
                health_endpoint="/health",
                api_endpoints={
                    'cqs': '/api/internal-cqs',
                    'alerts': '/api/alerts'
                }
            )
        }
    
    def get_hub_info(self, hub_id: str) -> Optional[HubInfo]:
        """Get information about a specific hub"""
        return self.hubs.get(hub_id)
    
    def get_all_hubs(self) -> Dict[str, HubInfo]:
        """Get information about all hubs"""
        return self.hubs
    
    def check_hub_health(self, hub_id: str, timeout: int = 3) -> Dict[str, Any]:
        """
        Check if a hub is healthy
        
        Args:
            hub_id: Hub identifier
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with health status
        """
        hub = self.hubs.get(hub_id)
        if not hub:
            return {'online': False, 'error': 'Hub not found'}
        
        try:
            url = f"{hub.url}{hub.health_endpoint}"
            start_time = datetime.now()
            response = requests.get(url, timeout=timeout)
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return {
                'online': response.status_code == 200,
                'response_time_ms': response_time,
                'status_code': response.status_code,
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.Timeout:
            return {'online': False, 'error': 'Timeout'}
        except requests.exceptions.ConnectionError:
            return {'online': False, 'error': 'Connection refused'}
        except Exception as e:
            logger.error(f"Health check failed for {hub_id}: {e}")
            return {'online': False, 'error': str(e)}
    
    def check_all_hubs_health(self, timeout: int = 3) -> Dict[str, Dict[str, Any]]:
        """Check health of all hubs"""
        health_status = {}
        for hub_id in self.hubs.keys():
            health_status[hub_id] = self.check_hub_health(hub_id, timeout)
        return health_status
    
    def get_hub_data(self, hub_id: str, endpoint: str, timeout: int = 5) -> Dict[str, Any]:
        """
        Get data from a hub endpoint
        
        Args:
            hub_id: Hub identifier
            endpoint: Endpoint name (from hub's api_endpoints)
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with response data or error
        """
        hub = self.hubs.get(hub_id)
        if not hub:
            return {'error': 'Hub not found'}
        
        if endpoint not in hub.api_endpoints:
            return {'error': f'Endpoint {endpoint} not found for hub {hub_id}'}
        
        try:
            url = f"{hub.url}{hub.api_endpoints[endpoint]}"
            response = requests.get(url, timeout=timeout)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'HTTP {response.status_code}'}
                
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout'}
        except requests.exceptions.ConnectionError:
            return {'error': 'Connection failed'}
        except Exception as e:
            logger.error(f"Failed to get data from {hub_id}/{endpoint}: {e}")
            return {'error': str(e)}
    
    def get_all_hub_summaries(self, timeout: int = 5) -> Dict[str, Dict[str, Any]]:
        """Get summary data from all hubs"""
        summaries = {}
        
        # Define primary endpoints for each hub
        primary_endpoints = {
            'l1': 'summary',
            'l2': 'metrics', 
            'l3_fairness': 'summary',
            'l4': 'metrics',
            'soqm': 'status',
            'uqo': 'overview',
            'cae': 'cqs'
        }
        
        for hub_id, endpoint in primary_endpoints.items():
            summaries[hub_id] = self.get_hub_data(hub_id, endpoint, timeout)
        
        return summaries
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get complete system overview including health and data"""
        health = self.check_all_hubs_health()
        summaries = self.get_all_hub_summaries()
        
        # Calculate overall statistics
        online_count = sum(1 for status in health.values() if status.get('online', False))
        total_count = len(self.hubs)
        
        avg_response_time = None
        response_times = [
            status.get('response_time_ms') 
            for status in health.values() 
            if status.get('response_time_ms') is not None
        ]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'health': health,
            'summaries': summaries,
            'statistics': {
                'hubs_online': online_count,
                'hubs_total': total_count,
                'availability_percentage': (online_count / total_count) * 100,
                'average_response_time_ms': avg_response_time
            }
        }

# Global hub service instance
hub_service = HubService()
