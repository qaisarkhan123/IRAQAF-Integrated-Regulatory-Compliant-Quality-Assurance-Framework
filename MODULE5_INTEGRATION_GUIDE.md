# Module 5: Continuous QA Automation & Monitoring
## Part 1: Module 5 Hub – System QA Orchestrator & Integration Guide

### Document Purpose

This guide describes **Module 5 Hub**, which is one layer of the two-layer **Module 5: Continuous QA Automation & Monitoring** system:

- **Module 5 Hub** (this document) – Orchestrator that aggregates scores across all 5 existing hubs into a system-level Continuous QA Score (CQS)
- **Module 5 Core** (separate spec) – Internal engine implementing performance monitoring, drift detection, security/privacy checks, compliance drift, alerts, and reporting

### Module 5 Hub Overview

**Module 5 Hub** is the 6th hub in the IRAQAF system that acts as a **unified quality assurance control tower**. It:

- 🔗 **Integrates** all 5 existing hubs (L4, L2, L1, L3 Operations, L3 Fairness)
- 📊 **Aggregates** their scores into a single system-level Continuous QA Score (CQS)
- 🎯 **Detects** cross-hub anomalies and risks
- ⚠️ **Alerts** on critical issues across the entire compliance ecosystem
- 🔍 **Monitors** hub health and responsiveness
- 🔄 **Provides** normalized metrics that feed into Module 5 Core for deeper analysis

## Architecture: Two-Layer Module 5 System

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                                  │
│                              Module 5: Continuous QA Automation & Monitoring                                   │
│                                                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  Module 5 Hub (Port 8507) – System-Level Orchestrator                                                  │  │
│  │  ──────────────────────────────────────────────────────────────────────────────────────────────────────  │  │
│  │  • Polls 5 hubs + Module 5 Core metrics                                                               │  │
│  │  • Computes System-Level CQS (weighted hub average)                                                   │  │
│  │  • Cross-hub anomaly detection                                                                        │  │
│  │  • Serves REST API + Dashboard                                                                        │  │
│  │  • Feeds normalized metrics to Module 5 Core                                                          │  │
│  └────────────────────────────────┬──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                                                          │
│        ┌───────────────────────────┼──────────────────┬──────────────────┬──────────────────┬─────────────┐   │
│        │                           │                  │                  │                  │             │   │
│        ▼                           ▼                  ▼                  ▼                  ▼             ▼   │
│    ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐                                            │
│    │   L4   │  │   L2   │  │   L1   │  │ L3-OPS │  │L3-FAIR │                                            │
│    │Explain │  │Security│  │Regul.  │  │        │  │ness    │                                            │
│    │Port5000│  │Port8502│  │Port8504│  │Port8503│  │Port8506│                                            │
│    └────────┘  └────────┘  └────────┘  └────────┘  └────────┘                                            │
│                                                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  Module 5 Core – Continuous QA Automation Engine                                                       │  │
│  │  ──────────────────────────────────────────────────────────────────────────────────────────────────────  │  │
│  │  Component 1: Real-Time Metrics Collection Pipeline                                                   │  │
│  │  Component 2: Performance Drift Detection (PSI, KS, ECE)                                              │  │
│  │  Component 3: Fairness Drift Monitoring (demographic parity)                                         │  │
│  │  Component 4: Security & Privacy Anomaly Detection                                                    │  │
│  │  Component 5: Compliance Drift Detector                                                               │  │
│  │  Component 6: Intelligent Multi-Level Alert System                                                    │  │
│  │  Component 7: Automated QA Dashboard & Reporting Engine                                              │  │
│  │  ──────────────────────────────────────────────────────────────────────────────────────────────────────  │  │
│  │  Output: Internal CQS (category-weighted), detailed alerts,                                           │  │
│  │  reports, recommendations                                                                             │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Design Principle

**Module 5 Hub** is a **meta-layer**: it orchestrates the 5 existing hubs + Module 5 Core.

- **Inputs**: Hub scores (normalized 0–1) + Module 5 Core metrics (performance, drift, security, fairness, compliance)
- **Output**: System-level CQS, cross-hub alerts, health status
- **Role**: Provide a unified "pulse" of the entire IRAQAF system

**Module 5 Core** is the **automation engine**: it implements all continuous QA logic.

- **Inputs**: Real-time prediction logs, model inputs/outputs, access patterns, compliance requirements
- **Output**: Detailed metrics, drift alerts, security flags, compliance gaps, PDF/HTML reports
- **Role**: Implement 24/7 monitoring and automation logic

## Hub Clients (Module 5 Hub Layer)

| Hub | Client | Port | Metrics | Weight in CQS |
|-----|--------|------|---------|---------------|\n| L4 Explainability | `L4ExplainabilityClient` | 5000 | SHAP/LIME/GradCAM, Feature Importance, Transparency Score | 20% |
| L2 Security | `L2SecurityClient` | 8502 | SAI Score, Vulnerability Count, PII Detection, Encryption Status | 25% |
| L1 Regulations | `L1RegulationsClient` | 8504 | GDPR/EU AI Act/ISO/IEC/FDA Compliance Scores, Gaps | 25% |
| L3 Operations | `L3OperationsClient` | 8503 | System Health, Uptime, Response Time, Throughput | 15% |
| L3 Fairness & Ethics | `L3FairnessClient` | 8506 | Demographic Parity, Equalized Odds, Bias Detection | 15% |

**Note**: L3 Fairness & Ethics hub runs on **port 8506** (Module 3 Fairness moved from 8505).

## Continuous QA Score (CQS) – Hub-Level Aggregation

### System-Level CQS (Module 5 Hub)

The **System-Level CQS** is a weighted aggregate of all 5 hub scores:

```
System-Level CQS = (L4 × 20%) + (L2 × 25%) + (L1 × 25%) + (L3-OPS × 15%) + (L3-FAIRNESS × 15%)

Range: 0.0 - 1.0 (displayed as 0% - 100%)
```

#### Weighting Rationale
- **L2 Security (25%)** - Most critical for regulatory compliance and breach prevention
- **L1 Regulations (25%)** - Direct alignment with regulatory requirements
- **L4 Explainability (20%)** - Model transparency & trust foundations
- **L3 Operations (15%)** - System stability and availability
- **L3 Fairness (15%)** - Ethical compliance and bias prevention

### Internal CQS (Module 5 Core – Separate Spec)

**Module 5 Core** defines a separate **Internal CQS** that weights its own monitoring categories:

```
Internal CQS = (0.30 × Performance) + (0.20 × Fairness) + (0.15 × Security/Privacy) 
             + (0.20 × Compliance) + (0.15 × System Health)

Where:
  • Performance     = AUC, accuracy, calibration, no-drift score
  • Fairness        = demographic parity, equalized odds, fairness drift
  • Security/Privacy= privacy breach score, access anomalies, model integrity
  • Compliance      = GDPR/EU AI Act/ISO score, compliance drift detected
  • System Health   = uptime, response time, error rates
```

**Relationship**: Module 5 Hub polls both hub-level scores and Module 5 Core's internal CQS, exposing both via `/api/cqs` (system-level) and `/api/module5-core/cqs` (internal).

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

## Running Module 5 Hub

### Prerequisites

All 5 hubs must be running:

```bash
# Terminal 1: L4 Explainability Hub (port 5000)
python dashboard/hub_explainability_app.py

# Terminal 2: L2 Privacy & Security Hub (port 8502)
python dashboard/privacy_security_hub.py

# Terminal 3: L1 Regulations & Governance Hub (port 8504)
python dashboard/l1_regulations_governance_hub.py

# Terminal 4: L3 Operations & Control Hub (port 8503)
python dashboard/l3_operations_control_center.py

# Terminal 5: L3 Fairness & Ethics Hub (port 8506)
python start_fairness_hub.py
```

### Start Module 5 Hub

```bash
python start_module5_hub.py
```

This will:
- Start Flask on port 8507
- Begin polling all 5 hubs every 30 seconds
- Begin polling Module 5 Core (when deployed)
- Compute and expose system-level CQS
- Serve dashboard at http://localhost:8507

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

## Module 5 Hub Structure

```
module5/
├── __init__.py
├── hub_clients/
│   ├── __init__.py
│   ├── base_client.py                    # Base HTTP client
│   ├── l4_explainability_client.py       # L4 connector
│   ├── l2_security_client.py             # L2 connector
│   ├── l1_regulations_client.py          # L1 connector
│   ├── l3_operations_client.py           # L3 Operations connector
│   └── l3_fairness_client.py             # L3 Fairness connector
│
└── orchestrator/
    ├── __init__.py
    └── orchestrator.py                   # Polling & hub aggregation

module5_hub.py                   # Flask Hub application (port 8507)
start_module5_hub.py             # Launcher script
```

**Note**: Module 5 Core components are deployed separately and expose their metrics via REST API that Module 5 Hub polls.

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

## Thresholds – Module 5 Hub Level

These are **hub-level thresholds** used by Module 5 Hub for alerting:

| Metric | Threshold | Alert Type |
|--------|-----------|-------------|
| L2 Security Hub Score | < 70% | Warning |
| L1 Compliance Hub Score | < 75% | Warning |
| L3 Operations Hub Score | < 80% | Warning |
| L3 Fairness Hub Score | < 70% | Warning |
| Any Hub Unresponsive | N/A | Critical |
| System-Level CQS | < 65% | Warning |

### Granular Thresholds – Module 5 Core Level

Module 5 Core implements **much more granular thresholds** for internal monitoring:

| Category | Metric | Threshold | Action |
|----------|--------|-----------|--------|
| **Performance** | AUC Drop (1 week) | PSI > 0.1 | Warning → Investigate |
| | Accuracy Drop | > 5% from baseline | Critical → Alert squad |
| | Calibration (ECE) | > 0.15 | Warning → Recalibrate |
| **Fairness** | Demographic Parity Gap | > 10% | Warning |
| | Equalized Odds Gap | > 15% | Critical |
| | Fairness Drift (weekly) | > 20% from baseline | Critical → Review model |
| **Security/Privacy** | Access Anomaly Score | > 3σ | Critical → Investigate |
| | Model Integrity Check | Hash mismatch | Critical → Incident |
| | PII Exposure Risk | Detected in outputs | Critical → Remediate |
| **Compliance** | GDPR Compliance Gap | > 5% from target | Warning → Review |
| | Regulatory Change Impact | Breaking change | Critical → Assess |
| | Audit Log Gap | > 1 hour missing | Warning → Check logs |

**Design**: Hub-level alerts are surfaced in Module 5 Hub dashboard; granular core alerts are sent to Module 5 Core alert routing system.

## Integration Points

### With Main Dashboard (IRAQAF Portal)

Add button to main dashboard sidebar to link to Module 5 Hub:

```python
if st.sidebar.button("📊 Module 5 QA Monitor"):
    st.switch_page("page_8507")  # Navigate to Module 5 Hub
```

### With Module 5 Core

Module 5 Hub pulls metrics from Module 5 Core (once deployed):

```python
# In orchestrator.poll_all_hubs():
core_metrics = self.core_client.get_internal_cqs()      # Internal CQS + categories
core_alerts = self.core_client.get_active_alerts()      # All Core alerts
core_drift = self.core_client.get_drift_summary()       # Performance/fairness/compliance drift
```

### For External Systems

**REST API** is fully available at `http://localhost:8507/api/*`

Can be integrated with:
- External compliance dashboards
- SIEM/alert aggregation systems
- Audit logging platforms
- Automated remediation workflows
- Stakeholder reporting systems

**Example**: Pull CQS every minute for automated SLA tracking:

```bash
curl http://localhost:8507/api/cqs | jq '.overall_cqs'
```

## Development

### Adding a New Hub Client to Module 5 Hub

1. Create `new_hub_client.py` in `module5/hub_clients/`
2. Extend `BaseHubClient`
3. Implement hub-specific metric methods
4. Add to `module5/hub_clients/__init__.py`
5. Create snapshot dataclass
6. Update orchestrator.py to poll new hub
7. Update CQS weighting formula if adding to system-level CQS
8. Add endpoint `/api/hub/{new_hub_name}` to Flask app

### Adding Module 5 Core Integration

When Module 5 Core is deployed:

1. Create `module5_core_client.py` in `module5/hub_clients/`
2. Implement methods:
   - `get_internal_cqs()` – Core's category-weighted CQS
   - `get_active_alerts()` – All drift/security/compliance alerts
   - `get_drift_summary()` – Performance, fairness, compliance drift
   - `get_reports()` – Automated QA reports
3. Update orchestrator to poll Core every 30s
4. Expose Core metrics via `/api/module5-core/*` endpoints
5. Optionally blend Core CQS into system-level CQS (e.g., 40% hub avg, 60% core internal)

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

### Phase 1: Module 5 Hub (This Document) – IN PROGRESS ✅

- [x] Deploy Module 5 Hub (port 8507) with 5 hub integration
- [x] Implement hub client pool + orchestrator
- [x] Expose REST API + dashboard
- [ ] Add Module 5 Hub button to main dashboard sidebar (port 8501)
- [ ] Create email alert integration for critical hub-level issues
- [ ] Build historical trend charts for system-level CQS

### Phase 2: Module 5 Core – NOT YET STARTED

- [ ] Design/implement real-time metrics collection pipeline
- [ ] Build drift detection algorithms (PSI, KS, concept drift)
- [ ] Implement fairness drift monitor (weekly subgroup analysis)
- [ ] Implement security & privacy anomaly detector
- [ ] Implement compliance drift monitor (regulatory change detection)
- [ ] Build intelligent multi-level alert system
- [ ] Build automated QA reporting engine (PDF/HTML)
- [ ] Deploy Module 5 Core on dedicated port (e.g., 8508 or internal only)

### Phase 3: Full Integration

- [ ] Module 5 Hub polls Module 5 Core metrics
- [ ] Blend hub-level CQS + core-level CQS for unified score
- [ ] Expose all metrics in unified dashboard
- [ ] Create automated remediation recommendation engine
- [ ] Build audit logging for full compliance traceability

---

**Module 5 Hub Status**: ✅ **Ready for Deployment** (as system orchestrator)

**Module 5 Core Status**: 🔜 **Not Yet Implemented** (see separate Module 5 Core Specification)

**Created**: 2025-11-20
**Last Updated**: 2025-11-20  
**Version**: 1.1 (restructured as Hub-only specification)  
**Ports**:  
- Module 5 Hub: 8507
- Integrates: 5000, 8502, 8504, 8503, 8506
- Module 5 Core: TBD (8508 or internal)

---

## Related Documentation

- **MODULE 5: Continuous QA Automation & Monitoring – SYSTEM-LEVEL REQUIREMENTS** (comprehensive spec for Module 5 Core)
- **L4_EXPLAINABILITY_HUB_GUIDE.md** (port 5000)
- **L2_SECURITY_HUB_GUIDE.md** (port 8502)
- **L1_REGULATIONS_HUB_GUIDE.md** (port 8504)
- **L3_OPERATIONS_HUB_GUIDE.md** (port 8503)
- **L3_FAIRNESS_HUB_GUIDE.md** (port 8506)
