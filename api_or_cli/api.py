"""
IRAQAF REST API Layer - Phase 7
FastAPI-based REST API for compliance monitoring system
Provides 10+ endpoints for system management, assessments, regulations, and monitoring
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="IRAQAF Compliance API",
    description="Real-time regulatory compliance monitoring API",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Data Models
class System(BaseModel):
    """Compliance System model"""
    id: str
    name: str
    description: str
    regulations: List[str]
    created_at: str = None
    updated_at: str = None

class Assessment(BaseModel):
    """Compliance Assessment model"""
    system_id: str
    regulation: str
    score: float
    gaps: List[str]
    recommendations: List[str]
    timestamp: str = None

class Change(BaseModel):
    """Regulatory Change model"""
    change_id: str
    regulation: str
    change_type: str
    severity: str
    description: str
    impact_hours: float
    timestamp: str = None

class Notification(BaseModel):
    """Notification model"""
    id: str
    system_id: str
    change_id: str
    message: str
    channel: str
    status: str
    created_at: str = None

# Mock data storage (in production, use actual database)
systems_db: Dict[str, System] = {}
assessments_db: List[Assessment] = []
changes_db: List[Change] = []
notifications_db: List[Notification] = []
requirements_db: List[Dict] = []

# Authentication
def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    """Verify API token"""
    token = credentials.credentials
    if token != "your-secret-api-key":  # In production, use proper token validation
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token

# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

@app.get("/api/systems", tags=["Systems"])
async def list_systems():
    """List all compliance systems"""
    logger.info("GET /api/systems - Listing all systems")
    return {
        "total": len(systems_db),
        "systems": list(systems_db.values())
    }

@app.post("/api/systems", tags=["Systems"])
async def create_system(system: System):
    """Create a new compliance system"""
    logger.info(f"POST /api/systems - Creating system: {system.id}")
    if system.id in systems_db:
        raise HTTPException(status_code=400, detail="System already exists")
    
    system.created_at = datetime.now().isoformat()
    system.updated_at = datetime.now().isoformat()
    systems_db[system.id] = system
    
    return {
        "status": "success",
        "message": f"System {system.id} created",
        "system": system
    }

@app.get("/api/systems/{system_id}", tags=["Systems"])
async def get_system(system_id: str):
    """Get specific system details"""
    logger.info(f"GET /api/systems/{system_id}")
    if system_id not in systems_db:
        raise HTTPException(status_code=404, detail="System not found")
    return systems_db[system_id]

@app.put("/api/systems/{system_id}", tags=["Systems"])
async def update_system(system_id: str, system: System):
    """Update system"""
    logger.info(f"PUT /api/systems/{system_id}")
    if system_id not in systems_db:
        raise HTTPException(status_code=404, detail="System not found")
    
    system.updated_at = datetime.now().isoformat()
    systems_db[system_id] = system
    return {"status": "success", "system": system}

@app.delete("/api/systems/{system_id}", tags=["Systems"])
async def delete_system(system_id: str):
    """Delete system"""
    logger.info(f"DELETE /api/systems/{system_id}")
    if system_id not in systems_db:
        raise HTTPException(status_code=404, detail="System not found")
    
    del systems_db[system_id]
    return {"status": "success", "message": f"System {system_id} deleted"}

# ============================================================================
# ASSESSMENT ENDPOINTS
# ============================================================================

@app.get("/api/systems/{system_id}/assessment", tags=["Assessments"])
async def get_assessment(system_id: str):
    """Get compliance assessment for system"""
    logger.info(f"GET /api/systems/{system_id}/assessment")
    if system_id not in systems_db:
        raise HTTPException(status_code=404, detail="System not found")
    
    system_assessments = [a for a in assessments_db if a.system_id == system_id]
    return {
        "system_id": system_id,
        "total_assessments": len(system_assessments),
        "assessments": system_assessments
    }

@app.post("/api/systems/{system_id}/assess", tags=["Assessments"])
async def run_assessment(system_id: str, assessment: Assessment):
    """Run compliance assessment for system"""
    logger.info(f"POST /api/systems/{system_id}/assess")
    if system_id not in systems_db:
        raise HTTPException(status_code=404, detail="System not found")
    
    assessment.system_id = system_id
    assessment.timestamp = datetime.now().isoformat()
    assessments_db.append(assessment)
    
    return {
        "status": "success",
        "message": "Assessment completed",
        "assessment": assessment
    }

@app.get("/api/assessments", tags=["Assessments"])
async def list_assessments(
    system_id: Optional[str] = Query(None),
    regulation: Optional[str] = Query(None)
):
    """List all assessments with optional filters"""
    logger.info("GET /api/assessments")
    
    results = assessments_db
    if system_id:
        results = [a for a in results if a.system_id == system_id]
    if regulation:
        results = [a for a in results if a.regulation == regulation]
    
    return {
        "total": len(results),
        "assessments": results
    }

# ============================================================================
# REGULATION ENDPOINTS
# ============================================================================

@app.get("/api/regulations", tags=["Regulations"])
async def list_regulations():
    """List all available regulations"""
    logger.info("GET /api/regulations")
    regulations = [
        {"id": "GDPR", "name": "GDPR", "sections": 99},
        {"id": "EU-AI", "name": "EU AI Act", "sections": 71},
        {"id": "ISO-13485", "name": "ISO 13485", "sections": 150},
        {"id": "IEC-62304", "name": "IEC 62304", "sections": 130},
        {"id": "FDA", "name": "FDA Guidelines", "sections": 200},
    ]
    return {
        "total": len(regulations),
        "regulations": regulations
    }

@app.get("/api/regulations/{regulation_id}", tags=["Regulations"])
async def get_regulation(regulation_id: str):
    """Get regulation details"""
    logger.info(f"GET /api/regulations/{regulation_id}")
    
    regs = {
        "GDPR": {"id": "GDPR", "name": "General Data Protection Regulation", "articles": 99},
        "EU-AI": {"id": "EU-AI", "name": "EU AI Act", "chapters": 8},
        "ISO-13485": {"id": "ISO-13485", "name": "Medical Device QMS", "clauses": 150},
        "IEC-62304": {"id": "IEC-62304", "name": "Medical Device SW Lifecycle", "clauses": 130},
        "FDA": {"id": "FDA", "name": "FDA Guidelines", "sections": 200},
    }
    
    if regulation_id not in regs:
        raise HTTPException(status_code=404, detail="Regulation not found")
    
    return regs[regulation_id]

# ============================================================================
# REQUIREMENT ENDPOINTS
# ============================================================================

@app.get("/api/requirements", tags=["Requirements"])
async def search_requirements(
    regulation: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None)
):
    """Search requirements"""
    logger.info(f"GET /api/requirements - regulation={regulation}, keyword={keyword}")
    
    # Mock requirements database
    mock_requirements = [
        {"id": "GDPR-1", "text": "Data subject rights", "regulation": "GDPR", "severity": "HIGH"},
        {"id": "GDPR-2", "text": "Consent management", "regulation": "GDPR", "severity": "HIGH"},
        {"id": "EU-AI-1", "text": "Risk assessment", "regulation": "EU-AI", "severity": "CRITICAL"},
        {"id": "EU-AI-2", "text": "Transparency", "regulation": "EU-AI", "severity": "HIGH"},
    ]
    
    results = mock_requirements
    if regulation:
        results = [r for r in results if r["regulation"] == regulation]
    if keyword:
        keyword_lower = keyword.lower()
        results = [r for r in results if keyword_lower in r["text"].lower()]
    
    return {
        "total": len(results),
        "requirements": results
    }

@app.get("/api/requirements/{requirement_id}", tags=["Requirements"])
async def get_requirement(requirement_id: str):
    """Get specific requirement details"""
    logger.info(f"GET /api/requirements/{requirement_id}")
    
    mock_requirements = {
        "GDPR-1": {"id": "GDPR-1", "text": "Data subject rights", "regulation": "GDPR"},
        "EU-AI-1": {"id": "EU-AI-1", "text": "Risk assessment", "regulation": "EU-AI"},
    }
    
    if requirement_id not in mock_requirements:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    return mock_requirements[requirement_id]

# ============================================================================
# CHANGE MONITORING ENDPOINTS
# ============================================================================

@app.get("/api/changes", tags=["Monitoring"])
async def list_changes(
    severity: Optional[str] = Query(None),
    regulation: Optional[str] = Query(None)
):
    """List regulatory changes"""
    logger.info("GET /api/changes")
    
    results = changes_db
    if severity:
        results = [c for c in results if c.severity == severity]
    if regulation:
        results = [c for c in results if c.regulation == regulation]
    
    return {
        "total": len(results),
        "changes": results
    }

@app.post("/api/changes/detect", tags=["Monitoring"])
async def detect_changes(regulation: str):
    """Detect new changes in regulation"""
    logger.info(f"POST /api/changes/detect - regulation={regulation}")
    
    new_change = Change(
        change_id=f"CHG-{len(changes_db)+1}",
        regulation=regulation,
        change_type="NEW_REQUIREMENT",
        severity="HIGH",
        description=f"New requirement detected in {regulation}",
        impact_hours=40.0,
        timestamp=datetime.now().isoformat()
    )
    
    changes_db.append(new_change)
    
    return {
        "status": "success",
        "change": new_change
    }

# ============================================================================
# NOTIFICATION ENDPOINTS
# ============================================================================

@app.get("/api/notifications", tags=["Notifications"])
async def list_notifications(
    system_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """List notifications"""
    logger.info("GET /api/notifications")
    
    results = notifications_db
    if system_id:
        results = [n for n in results if n.system_id == system_id]
    if status:
        results = [n for n in results if n.status == status]
    
    return {
        "total": len(results),
        "notifications": results
    }

@app.post("/api/notifications/send", tags=["Notifications"])
async def send_notification(notification: Notification):
    """Send notification"""
    logger.info(f"POST /api/notifications/send - {notification.id}")
    
    notification.created_at = datetime.now().isoformat()
    notification.status = "sent"
    notifications_db.append(notification)
    
    return {
        "status": "success",
        "notification": notification
    }

# ============================================================================
# REPORTING ENDPOINTS
# ============================================================================

@app.get("/api/reports/{system_id}", tags=["Reports"])
async def generate_report(system_id: str):
    """Generate compliance report"""
    logger.info(f"GET /api/reports/{system_id}")
    
    if system_id not in systems_db:
        raise HTTPException(status_code=404, detail="System not found")
    
    system = systems_db[system_id]
    system_assessments = [a for a in assessments_db if a.system_id == system_id]
    
    # Calculate metrics
    total_score = 0
    if system_assessments:
        total_score = sum(a.score for a in system_assessments) / len(system_assessments)
    
    return {
        "system_id": system_id,
        "system_name": system.name,
        "total_assessments": len(system_assessments),
        "overall_score": total_score,
        "regulations_covered": len(system.regulations),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/reports/{system_id}/export", tags=["Reports"])
async def export_report(system_id: str, format: str = Query("json")):
    """Export report in different formats"""
    logger.info(f"GET /api/reports/{system_id}/export - format={format}")
    
    if system_id not in systems_db:
        raise HTTPException(status_code=404, detail="System not found")
    
    system = systems_db[system_id]
    
    report_data = {
        "system": system.dict(),
        "assessments": [a.dict() for a in assessments_db if a.system_id == system_id],
        "exported_at": datetime.now().isoformat()
    }
    
    if format == "json":
        return report_data
    elif format == "csv":
        return {"status": "CSV export prepared", "file": f"{system_id}-report.csv"}
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

# ============================================================================
# HEALTH & ADMIN ENDPOINTS
# ============================================================================

@app.get("/api/health", tags=["Health"])
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/stats", tags=["Admin"])
async def get_stats():
    """Get API statistics"""
    logger.info("GET /api/stats")
    
    return {
        "total_systems": len(systems_db),
        "total_assessments": len(assessments_db),
        "total_changes": len(changes_db),
        "total_notifications": len(notifications_db),
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/api/admin/reset", tags=["Admin"])
async def reset_data():
    """Reset all data (admin only)"""
    logger.info("DELETE /api/admin/reset - Resetting database")
    
    global systems_db, assessments_db, changes_db, notifications_db
    systems_db.clear()
    assessments_db.clear()
    changes_db.clear()
    notifications_db.clear()
    
    return {"status": "success", "message": "All data reset"}

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "name": "IRAQAF Compliance API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "openapi": "/api/openapi.json"
    }

@app.get("/api", tags=["Root"])
async def api_root():
    """API documentation"""
    return {
        "title": "IRAQAF Compliance Monitoring API",
        "version": "1.0.0",
        "endpoints": {
            "systems": [
                "GET /api/systems - List all systems",
                "POST /api/systems - Create system",
                "GET /api/systems/{id} - Get system",
                "PUT /api/systems/{id} - Update system",
                "DELETE /api/systems/{id} - Delete system",
            ],
            "assessments": [
                "GET /api/systems/{id}/assessment - Get assessment",
                "POST /api/systems/{id}/assess - Run assessment",
                "GET /api/assessments - List assessments",
            ],
            "regulations": [
                "GET /api/regulations - List regulations",
                "GET /api/regulations/{id} - Get regulation",
            ],
            "requirements": [
                "GET /api/requirements - Search requirements",
                "GET /api/requirements/{id} - Get requirement",
            ],
            "monitoring": [
                "GET /api/changes - List changes",
                "POST /api/changes/detect - Detect changes",
            ],
            "notifications": [
                "GET /api/notifications - List notifications",
                "POST /api/notifications/send - Send notification",
            ],
            "reports": [
                "GET /api/reports/{id} - Generate report",
                "GET /api/reports/{id}/export - Export report",
            ]
        },
        "documentation": "/api/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
