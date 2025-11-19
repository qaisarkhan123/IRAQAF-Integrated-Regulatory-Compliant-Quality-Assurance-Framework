# PHASE 8 - API REFERENCE DOCUMENTATION
## Complete REST API Reference for IRAQAF Platform

**API Version**: 1.0.0 | **Framework**: FastAPI | **Port**: 8000
**Base URL**: `http://localhost:8000/api` or `https://your-domain.com/api`

---

## TABLE OF CONTENTS

1. [Authentication](#authentication)
2. [Response Format](#response-format)
3. [Error Handling](#error-handling)
4. [Endpoints Overview](#endpoints-overview)
5. [Systems Endpoints](#systems-endpoints)
6. [Assessments Endpoints](#assessments-endpoints)
7. [Regulatory Data](#regulatory-data)
8. [Changes & Monitoring](#changes--monitoring)
9. [Notifications](#notifications)
10. [Reports](#reports)
11. [Health & Statistics](#health--statistics)
12. [Rate Limiting](#rate-limiting)

---

## AUTHENTICATION

### Bearer Token (Recommended)

```bash
# Include authorization header
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/systems
```

### API Key Alternative

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/api/systems
```

### No Authentication (Development)

Current version supports unauthenticated requests. Production deployment requires:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.get("/api/protected")
async def protected_endpoint(credentials = Depends(security)):
    return {"message": "Protected endpoint"}
```

---

## RESPONSE FORMAT

### Successful Response (200 OK)

```json
{
  "data": {...},
  "status": "success",
  "timestamp": "2024-01-15T10:30:00Z",
  "message": "Operation completed successfully"
}
```

### Error Response (4xx/5xx)

```json
{
  "error": {
    "code": "SYSTEM_NOT_FOUND",
    "message": "System with ID 999 not found",
    "details": "The requested system does not exist in the database",
    "status_code": 404
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Pagination Response

```json
{
  "data": [...],
  "pagination": {
    "total": 100,
    "page": 1,
    "per_page": 20,
    "total_pages": 5
  },
  "status": "success"
}
```

---

## ERROR HANDLING

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created |
| 204 | No Content | Resource deleted |
| 400 | Bad Request | Invalid JSON |
| 401 | Unauthorized | Missing authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Response Examples

**404 Not Found**:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "System not found",
    "status_code": 404
  }
}
```

**422 Validation Error**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "name",
        "error": "Field required"
      }
    ],
    "status_code": 422
  }
}
```

---

## ENDPOINTS OVERVIEW

### Available Endpoints (10+)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/systems` | GET | List all systems |
| `/systems` | POST | Create new system |
| `/systems/{id}` | GET | Get system details |
| `/systems/{id}` | PUT | Update system |
| `/systems/{id}` | DELETE | Delete system |
| `/systems/{id}/assess` | POST | Run assessment |
| `/systems/{id}/assessment` | GET | Get latest assessment |
| `/assessments` | GET | List assessments |
| `/regulations` | GET | List regulations |
| `/regulations/{id}` | GET | Get regulation details |
| `/requirements` | GET | Search requirements |
| `/changes` | GET | List regulatory changes |
| `/changes/detect` | POST | Detect new changes |
| `/notifications` | GET | List notifications |
| `/notifications/send` | POST | Send notification |
| `/reports/{id}` | GET | Generate report |
| `/reports/{id}/export` | GET | Export report (JSON/CSV) |
| `/health` | GET | Health check |
| `/stats` | GET | System statistics |

---

## SYSTEMS ENDPOINTS

### GET /api/systems

List all systems with optional filtering.

**Request**:
```bash
curl http://localhost:8000/api/systems?page=1&per_page=20
```

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number |
| per_page | integer | No | 20 | Items per page |
| domain | string | No | - | Filter by domain |
| status | string | No | - | Filter by status |

**Response (200)**:
```json
{
  "data": [
    {
      "id": 1,
      "name": "Medical Device System",
      "description": "AI-powered diagnostic device",
      "domain": "medical_device",
      "regulations": ["EU-AI-Act", "GDPR", "FDA"],
      "status": "active",
      "created_at": "2024-01-10T08:00:00Z",
      "last_assessment": "2024-01-15T10:00:00Z"
    }
  ],
  "pagination": {
    "total": 5,
    "page": 1,
    "per_page": 20,
    "total_pages": 1
  },
  "status": "success"
}
```

### POST /api/systems

Create a new system.

**Request**:
```bash
curl -X POST http://localhost:8000/api/systems \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Medical Device",
    "description": "Advanced diagnostic system",
    "domain": "medical_device",
    "regulations": ["EU-AI-Act", "GDPR"]
  }'
```

**Request Body**:
```json
{
  "name": "string (required)",
  "description": "string (required)",
  "domain": "string (required)",
  "regulations": ["string (optional)"],
  "metadata": {"key": "value (optional)"}
}
```

**Response (200)**:
```json
{
  "data": {
    "id": 6,
    "name": "New Medical Device",
    "description": "Advanced diagnostic system",
    "domain": "medical_device",
    "regulations": ["EU-AI-Act", "GDPR"],
    "status": "created",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "status": "success"
}
```

### GET /api/systems/{id}

Get detailed information about a specific system.

**Request**:
```bash
curl http://localhost:8000/api/systems/1
```

**Response (200)**:
```json
{
  "data": {
    "id": 1,
    "name": "Medical Device System",
    "description": "AI-powered diagnostic device",
    "domain": "medical_device",
    "regulations": ["EU-AI-Act", "GDPR", "FDA"],
    "status": "active",
    "created_at": "2024-01-10T08:00:00Z",
    "last_assessment": "2024-01-15T10:00:00Z",
    "metadata": {}
  },
  "status": "success"
}
```

**Response (404)**:
```json
{
  "error": {
    "code": "SYSTEM_NOT_FOUND",
    "message": "System with ID 99 not found",
    "status_code": 404
  }
}
```

### PUT /api/systems/{id}

Update an existing system.

**Request**:
```bash
curl -X PUT http://localhost:8000/api/systems/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "status": "inactive"
  }'
```

**Response (200)**:
```json
{
  "data": {
    "id": 1,
    "name": "Updated Name",
    "description": "...",
    "status": "inactive",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "status": "success"
}
```

### DELETE /api/systems/{id}

Delete a system.

**Request**:
```bash
curl -X DELETE http://localhost:8000/api/systems/1
```

**Response (204)**: No content

**Response (404)**:
```json
{
  "error": {
    "code": "SYSTEM_NOT_FOUND",
    "message": "System not found",
    "status_code": 404
  }
}
```

---

## ASSESSMENTS ENDPOINTS

### POST /api/systems/{id}/assess

Run a compliance assessment for a system.

**Request**:
```bash
curl -X POST http://localhost:8000/api/systems/1/assess
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| regulations | string[] | Specific regulations to assess (optional) |

**Response (200)**:
```json
{
  "data": {
    "id": 101,
    "system_id": 1,
    "compliance_score": 78.5,
    "status": "partial_compliance",
    "requirements_met": 65,
    "requirements_total": 82,
    "assessment_date": "2024-01-15T10:30:00Z",
    "assessor": "automated",
    "module_scores": {
      "EU-AI-Act": 75.0,
      "GDPR": 82.0,
      "FDA": 71.0
    }
  },
  "status": "success"
}
```

### GET /api/systems/{id}/assessment

Get the latest assessment for a system.

**Request**:
```bash
curl http://localhost:8000/api/systems/1/assessment
```

**Response (200)**:
```json
{
  "data": {
    "id": 101,
    "system_id": 1,
    "compliance_score": 78.5,
    "requirements_met": 65,
    "requirements_total": 82,
    "assessment_date": "2024-01-15T10:30:00Z",
    "status": "partial_compliance"
  },
  "status": "success"
}
```

### GET /api/assessments

List all assessments.

**Request**:
```bash
curl http://localhost:8000/api/assessments?system_id=1
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| system_id | integer | Filter by system (optional) |
| status | string | Filter by status (optional) |

**Response (200)**:
```json
{
  "data": [
    {
      "id": 101,
      "system_id": 1,
      "compliance_score": 78.5,
      "status": "partial_compliance",
      "assessment_date": "2024-01-15T10:30:00Z"
    }
  ],
  "status": "success"
}
```

---

## REGULATORY DATA

### GET /api/regulations

List all regulatory frameworks.

**Request**:
```bash
curl http://localhost:8000/api/regulations
```

**Response (200)**:
```json
{
  "data": [
    {
      "id": 1,
      "name": "EU Artificial Intelligence Act",
      "acronym": "EU-AI-Act",
      "jurisdiction": "EU",
      "sections": 99,
      "requirements": 156,
      "last_updated": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "General Data Protection Regulation",
      "acronym": "GDPR",
      "jurisdiction": "EU",
      "sections": 99,
      "requirements": 105,
      "last_updated": "2023-12-20T00:00:00Z"
    }
  ],
  "status": "success"
}
```

### GET /api/regulations/{id}

Get detailed regulation information.

**Request**:
```bash
curl http://localhost:8000/api/regulations/1
```

**Response (200)**:
```json
{
  "data": {
    "id": 1,
    "name": "EU Artificial Intelligence Act",
    "acronym": "EU-AI-Act",
    "jurisdiction": "EU",
    "sections": [
      {
        "number": 41,
        "title": "Prohibited AI Practices",
        "content": "...",
        "requirements": 5
      }
    ],
    "requirements": [
      {
        "id": "EU-AI-41-1",
        "text": "The use of AI systems for...",
        "severity": "critical"
      }
    ]
  },
  "status": "success"
}
```

### GET /api/requirements

Search requirements across all regulations.

**Request**:
```bash
curl http://localhost:8000/api/requirements?q=encryption
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| q | string | Search query (keyword) |
| regulation | string | Filter by regulation |
| severity | string | Filter by severity |

**Response (200)**:
```json
{
  "data": [
    {
      "id": "REQ-001",
      "text": "Implement end-to-end encryption",
      "regulation": "GDPR",
      "severity": "high",
      "confidence": 0.95
    }
  ],
  "status": "success"
}
```

---

## CHANGES & MONITORING

### GET /api/changes

List detected regulatory changes.

**Request**:
```bash
curl http://localhost:8000/api/changes?severity=critical
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| severity | string | Filter by severity |
| regulation | string | Filter by regulation |

**Response (200)**:
```json
{
  "data": [
    {
      "id": 1,
      "regulation": "EU-AI-Act",
      "change_type": "modification",
      "severity": "critical",
      "old_content": "...",
      "new_content": "...",
      "detection_date": "2024-01-15T08:00:00Z",
      "affected_systems": 3
    }
  ],
  "status": "success"
}
```

### POST /api/changes/detect

Manually trigger regulatory change detection.

**Request**:
```bash
curl -X POST http://localhost:8000/api/changes/detect
```

**Response (200)**:
```json
{
  "data": {
    "scan_timestamp": "2024-01-15T10:30:00Z",
    "changes_detected": 3,
    "new_requirements": 2,
    "modified_sections": 1,
    "regulations_scanned": 5
  },
  "status": "success"
}
```

---

## NOTIFICATIONS

### GET /api/notifications

List system notifications.

**Request**:
```bash
curl http://localhost:8000/api/notifications?unread=true
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| unread | boolean | Show only unread (optional) |

**Response (200)**:
```json
{
  "data": [
    {
      "id": 1,
      "type": "regulatory_change",
      "severity": "high",
      "title": "Critical: EU AI Act Modified",
      "message": "Section 41 has been updated",
      "read": false,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "status": "success"
}
```

### POST /api/notifications/send

Send a notification.

**Request**:
```bash
curl -X POST http://localhost:8000/api/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "type": "alert",
    "title": "Test Alert",
    "message": "This is a test notification",
    "recipients": ["admin@company.com"],
    "channels": ["email", "dashboard"]
  }'
```

**Response (200)**:
```json
{
  "data": {
    "id": 1,
    "status": "sent",
    "recipients_count": 1,
    "sent_at": "2024-01-15T10:30:00Z"
  },
  "status": "success"
}
```

---

## REPORTS

### GET /api/reports/{system_id}

Generate a compliance report.

**Request**:
```bash
curl http://localhost:8000/api/reports/1
```

**Response (200)**:
```json
{
  "data": {
    "report_id": "RPT-001",
    "system_id": 1,
    "generated_at": "2024-01-15T10:30:00Z",
    "overall_score": 78.5,
    "compliance_status": "partial_compliance",
    "module_scores": {...},
    "gaps": [...],
    "recommendations": [...]
  },
  "status": "success"
}
```

### GET /api/reports/{system_id}/export

Export report in various formats.

**Request**:
```bash
# JSON format
curl http://localhost:8000/api/reports/1/export?format=json > report.json

# CSV format
curl http://localhost:8000/api/reports/1/export?format=csv > report.csv

# PDF format (if supported)
curl http://localhost:8000/api/reports/1/export?format=pdf > report.pdf
```

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| format | string | json | Export format (json, csv, pdf) |
| include_details | boolean | true | Include detailed analysis |

**Response (200)**: File download or JSON

---

## HEALTH & STATISTICS

### GET /api/health

Health check endpoint.

**Request**:
```bash
curl http://localhost:8000/api/health
```

**Response (200)**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime_seconds": 3600,
  "database": "connected",
  "services": {
    "api": "running",
    "scheduler": "running",
    "notifications": "operational"
  }
}
```

### GET /api/stats

Get system statistics.

**Request**:
```bash
curl http://localhost:8000/api/stats
```

**Response (200)**:
```json
{
  "data": {
    "total_systems": 5,
    "total_assessments": 23,
    "average_compliance_score": 76.3,
    "critical_findings": 3,
    "last_change_detection": "2024-01-15T08:00:00Z",
    "api_calls_today": 234
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "success"
}
```

---

## RATE LIMITING

Rate limits prevent abuse and ensure fair resource usage.

### Limits

- **Unauthenticated**: 100 requests/hour per IP
- **Authenticated**: 1,000 requests/hour per user
- **Admin**: Unlimited

### Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1705339800
```

### When Limited (429 Too Many Requests)

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Try again after 3600 seconds",
    "retry_after": 3600,
    "status_code": 429
  }
}
```

---

## EXAMPLES

### Python Example

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# List systems
response = requests.get(f"{BASE_URL}/systems")
systems = response.json()
print(json.dumps(systems, indent=2))

# Create system
system_data = {
    "name": "New System",
    "description": "Test system",
    "domain": "medical_device"
}
response = requests.post(
    f"{BASE_URL}/systems",
    json=system_data
)
new_system = response.json()
print(f"Created system ID: {new_system['data']['id']}")

# Run assessment
system_id = new_system['data']['id']
response = requests.post(f"{BASE_URL}/systems/{system_id}/assess")
assessment = response.json()
print(f"Compliance Score: {assessment['data']['compliance_score']}")
```

### JavaScript Example

```javascript
const BASE_URL = "http://localhost:8000/api";

// List systems
async function listSystems() {
  const response = await fetch(`${BASE_URL}/systems`);
  const data = await response.json();
  console.log(data);
}

// Create system
async function createSystem() {
  const response = await fetch(`${BASE_URL}/systems`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: "New System",
      description: "Test",
      domain: "medical_device"
    })
  });
  const data = await response.json();
  return data.data.id;
}

listSystems();
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/api/health

# List systems
curl http://localhost:8000/api/systems | jq

# Create system
curl -X POST http://localhost:8000/api/systems \
  -H "Content-Type: application/json" \
  -d '{
    "name":"My System",
    "description":"Test",
    "domain":"medical_device"
  }' | jq

# Get system
curl http://localhost:8000/api/systems/1 | jq

# Run assessment
curl -X POST http://localhost:8000/api/systems/1/assess | jq

# Generate report
curl http://localhost:8000/api/reports/1 | jq
```

---

## INTERACTIVE API DOCUMENTATION

Access Swagger UI for interactive API exploration:

```
http://localhost:8000/api/docs
```

Or ReDoc alternative documentation:

```
http://localhost:8000/api/redoc
```

---

**API Version**: 1.0.0  
**Last Updated**: January 2024  
**Status**: ✅ Production Ready
