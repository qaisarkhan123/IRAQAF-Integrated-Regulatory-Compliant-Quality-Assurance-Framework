# Module 5: Continuous QA Automation & Monitoring - Integration Guide

## Overview

**Module 5** is the 6th hub in the IRAQAF system that acts as a **unified quality assurance control tower**. It:

- 🔗 **Integrates** all 5 existing hubs (L4, L2, L1, L3 Operations, L3 Fairness)
- 📊 **Aggregates** metrics from all hubs into a single Continuous QA Score (CQS)
- 🎯 **Detects** cross-hub anomalies and risks
- ⚠️ **Alerts** on critical issues across the entire compliance ecosystem
- 🔍 **Monitors** hub health and responsiveness

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Module 5 Hub (Port 8507)                  │
│           Continuous QA Automation & Monitoring             │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────────┬────────────┐
        │            │            │              │            │
        ▼            ▼            ▼              ▼            ▼
    ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
    │   L4   │  │   L2   │  │   L1   │  │ L3-OPS │  │L3-FAIR │
    │Explain │  │Security│  │Regul.  │  │        │  │ness    │
    │Port5000│  │Port8502│  │Port8504│  │Port8503│  │Port8506│
    └────────┘  └────────┘  └────────┘  └────────┘  └────────┘
```

## Hub Clients

Each hub is accessed via a **hub client** that provides:

- Health checking
- Metric fetching with error handling
- Response time tracking
- Automatic retry logic

### Hub Clients

| Hub | Client | Port | Metrics |
|-----|--------|------|---------|
| L4 Explainability | `L4ExplainabilityClient` | 5000 | SHAP/LIME/GradCAM, Feature Importance, Transparency Score |
| L2 Security | `L2SecurityClient` | 8502 | SAI Score, Vulnerability Count, PII Detection, Encryption Status |
| L1 Regulations | `L1RegulationsClient` | 8504 | GDPR/EU AI Act/ISO/IEC/FDA Compliance Scores, Gaps |
| L3 Operations | `L3OperationsClient` | 8503 | System Health, Uptime, Response Time, Throughput |
| L3 Fairness | `L3FairnessClient` | 8506 | Demographic Parity, Equalized Odds, Bias Detection |

## Continuous QA Score (CQS)

The **CQS** is a weighted aggregate of all 5 hubs:

```
CQS = (L4 × 20%) + (L2 × 25%) + (L1 × 25%) + (L3-OPS × 15%) + (L3-FAIRNESS × 15%)

Range: 0.0 - 1.0 (displayed as 0% - 100%)
```

### Weighting Rationale
- **L2 Security (25%)** - Most critical for compliance
- **L1 Regulations (25%)** - Direct regulatory requirements
- **L4 Explainability (20%)** - Model transparency & trust
- **L3 Operations (15%)** - System stability
- **L3 Fairness (15%)** - Ethical compliance

## Data Flow

```
Poll Cycle (every 30 seconds):
├── Poll L4: Get transparency_score → normalized 0-1
├── Poll L2: Get sai_score → normalized 0-1
├── Poll L1: Get overall_score → normalized 0-1
├── Poll L3-OPS: Get system_health_score → normalized 0-1
├── Poll L3-FAIRNESS: Get overall_fairness_score → normalized 0-1
│
├── Calculate weighted CQS
├── Detect anomalies (if any score < threshold)
├── Generate alerts
└── Store snapshot & serve via API
```

## Running Module 5

### Start Module 5 Hub

```bash
python start_module5_hub.py
```

This will:
- Start Flask on port 8507
- Begin polling all 5 hubs
- Open the dashboard at http://localhost:8507

### Access Dashboard

- **URL**: http://localhost:8507
- **Features**:
  - Live CQS display (large gauge)
  - Individual hub scores
  - Hub status table
  - Active alerts
  - Auto-refresh every 30 seconds

### API Endpoints

#### Get Overview
```bash
curl http://localhost:8507/api/overview
```
Returns: Complete system state including CQS, all hub data, alerts

#### Get Current CQS
```bash
curl http://localhost:8507/api/cqs
```
Returns: `ContinuousQAScore` object

#### Get Hub Statuses
```bash
curl http://localhost:8507/api/hub-status
```
Returns: Array of `HubStatus` objects

#### Get Specific Hub Data
```bash
curl http://localhost:8507/api/hub/l4
curl http://localhost:8507/api/hub/l2
curl http://localhost:8507/api/hub/l1
curl http://localhost:8507/api/hub/l3_ops
curl http://localhost:8507/api/hub/l3_fairness
```

## Module Structure

```
module5/
├── __init__.py
├── hub_clients/
│   ├── __init__.py
│   ├── base_client.py           # Base HTTP client
│   ├── l4_explainability_client.py
│   ├── l2_security_client.py
│   ├── l1_regulations_client.py
│   ├── l3_operations_client.py
│   └── l3_fairness_client.py
│
└── orchestrator/
    ├── __init__.py
    └── orchestrator.py          # Main polling & aggregation logic

module5_hub.py                   # Flask application (port 8507)
start_module5_hub.py             # Launcher script
```

## Error Handling

If a hub is unreachable:
- Hub marked as `is_healthy: false`
- Error message captured
- That hub's score defaults to 0
- Alert added to CQS
- Critical issue count incremented
- Polling continues for other hubs

## Alerts

Alerts are generated when:

- **Hub Unreachable**: Any hub fails to respond
- **Low L2 Security**: SAI score < 70%
- **Low L1 Compliance**: Compliance score < 75%
- **Low L3 Operations**: System health < 80%
- **Low L3 Fairness**: Fairness score < 70%

## Thresholds

| Metric | Threshold | Alert Type |
|--------|-----------|-----------|
| L2 Security | < 70% | Warning |
| L1 Compliance | < 75% | Warning |
| L3 Operations | < 80% | Warning |
| L3 Fairness | < 70% | Warning |
| Hub Unresponsive | N/A | Critical |

## Integration Points

### With Main Dashboard

Add button to main dashboard sidebar:
```python
if st.sidebar.button("📊 Module 5 QA Monitor"):
    st.switch_page("page_8507")  # Navigate to Module 5
```

### For Other Systems

**REST API** is fully available at http://localhost:8507/api/*

Can be integrated with:
- External compliance dashboards
- Alert systems
- Audit logging
- Automated remediation workflows

## Development

### Adding a New Hub Client

1. Create `new_hub_client.py` in `module5/hub_clients/`
2. Extend `BaseHubClient`
3. Implement hub-specific methods
4. Add to `module5/hub_clients/__init__.py`
5. Create snapshot dataclass
6. Update orchestrator to poll new hub
7. Update CQS weighting formula

## Troubleshooting

### Hub Not Found
```
ConnectionError: Hub unreachable
```
- Check hub is running on correct port
- Verify firewall allows connection
- Test with: `curl http://localhost:{port}`

### Module Import Error
```
ModuleNotFoundError: No module named 'module5'
```
- Ensure you're in project root directory
- Run: `python start_module5_hub.py` from project root

### No Data in Dashboard
- Wait 30 seconds for first poll cycle
- Check browser console for errors
- Verify all 5 hubs are accessible via curl

## Next Steps

- [ ] Add Module 5 button to main dashboard (port 8501)
- [ ] Create email alert integration for critical issues
- [ ] Build historical trend charts (CQS over time)
- [ ] Add automated remediation recommendations
- [ ] Create detailed audit logs for compliance

---

**Status**: ✅ Module 5 Ready for Deployment

**Created**: 2025-11-20
**Version**: 1.0
**Ports**: 8507 (Module 5), Integrates: 5000, 8502, 8504, 8503, 8506
