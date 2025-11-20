# Module 5: Complete Deployment Guide
## Continuous QA Automation & Monitoring System

**Version**: 1.0  
**Created**: 2025-11-20  
**Status**: ✅ PRODUCTION READY  

---

## 🎯 Overview

Module 5 is a two-layer continuous quality assurance system that monitors your entire IRAQAF ecosystem:

**Layer 1: Module 5 Hub (Port 8507)**
- Orchestrator that aggregates scores from all 5 existing hubs
- Computes system-level Continuous QA Score (CQS)
- Detects cross-hub anomalies and risks
- Provides unified quality control dashboard

**Layer 2: Module 5 Core (Port 8508)**
- Automation engine for deep monitoring
- Performance drift detection (PSI, KS, ECE)
- Fairness drift monitoring (demographic parity, equalized odds)
- Security & privacy anomaly detection
- Compliance drift tracking
- Intelligent alert system

---

## 🚀 Quick Start

### Option 1: Start All Dashboards at Once (Recommended)

```bash
python launch_all_dashboards.py
```

This starts:
- All 4 specialized hubs (L1, L2, L3, L4, Fairness)
- Module 5 Hub (orchestrator)
- Module 5 Core (automation engine)
- Main dashboard with navigation

### Option 2: Start Only Module 5

```bash
# Terminal 1: Start Module 5 Hub
python start_module5_hub.py

# Terminal 2: Start Module 5 Core
python start_module5_core.py
```

### Option 3: Start Individual Components

```bash
# Module 5 Hub - requires all 5 component hubs running
python start_module5_hub.py

# Module 5 Core - standalone, doesn't require other hubs
python start_module5_core.py

# Access
# Hub: http://localhost:8507
# Core: http://localhost:8508
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         Module 5: Continuous QA Automation                 │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Module 5 Hub │ │     Layer    │ │ Module 5     │
    │  (8507)      │ │   Division   │ │ Core (8508)  │
    │              │ │              │ │              │
    │ • Polls 5    │ │ • Hub polls  │ │ • Drift      │
    │   hubs       │ │ • Core polls │ │   detection  │
    │ • Aggregates │ │ • Blended    │ │ • Fairness   │
    │   CQS        │ │   CQS        │ │   monitoring │
    │ • Alerts     │ │              │ │ • Alerts     │
    └──────────────┘ └──────────────┘ └──────────────┘
            │                │                 │
    ┌───────┴────────┬───────┴────────┬────────┴────────┐
    │                │                │                 │
    ▼                ▼                ▼                 ▼
   L4 Hub          L2 Hub           L1 Hub           L3 Hubs
  (5000)          (8502)           (8504)        (8503, 8506)
  
   • AI Trans.    • Security       • Compliance    • Operations
   • Explain.     • Privacy        • Governance    • Fairness
   • Models       • Vulnerab.      • Regulatory    • Ethics
```

---

## 🔌 API Endpoints

### Module 5 Hub (Port 8507)

**System Overview**
```bash
GET /api/overview
# Returns: Complete system state, all hub data, alerts
```

**Continuous QA Score**
```bash
GET /api/cqs
# Returns: {
#   "overall_cqs": 87.5,
#   "timestamp": "2025-11-20T14:30:00",
#   "hub_scores": {...},
#   "trend": "stable"
# }
```

**Hub Status**
```bash
GET /api/hub-status
# Returns: Status of all 5 hubs (healthy/unhealthy, response time)
```

**Specific Hub Data**
```bash
GET /api/hub/l4          # L4 Explainability scores
GET /api/hub/l2          # L2 Security scores
GET /api/hub/l1          # L1 Compliance scores
GET /api/hub/l3_ops      # L3 Operations scores
GET /api/hub/l3_fairness # L3 Fairness scores
```

### Module 5 Core (Port 8508)

**Internal CQS**
```bash
GET /api/internal-cqs
# Returns: {
#   "overall_cqs": 78.5,
#   "categories": {
#     "performance": 85,
#     "fairness": 72,
#     "security_privacy": 88,
#     "compliance": 75,
#     "system_health": 78
#   }
# }
```

**Performance Drift**
```bash
GET /api/drift/performance
# Returns: {
#   "psi_input": 0.15,          # 0.0 = stable, >0.25 = significant drift
#   "ks_statistic": 0.12,       # 0.0 = identical, 1.0 = completely different
#   "ece_score": 0.08,          # 0.0 = perfect calibration
#   "trend": "stable"
# }
```

**Fairness Metrics**
```bash
GET /api/drift/fairness
# Returns: {
#   "demographic_parity_gap": 5.2,
#   "equalized_odds_gap": 8.1,
#   "fairness_score": 85,
#   "bias_detected": false
# }
```

**Security Anomalies**
```bash
GET /api/security/anomalies
# Returns: {
#   "adversarial_vulnerability_score": 0.15,
#   "model_integrity_status": "verified",
#   "access_anomalies": 0
# }
```

**Compliance Drift**
```bash
GET /api/compliance/drift
# Returns: {
#   "gdpr_compliance": 92,
#   "eu_ai_act_alignment": 88,
#   "drift_detected": false
# }
```

**Active Alerts**
```bash
GET /api/alerts
# Returns: {
#   "total_active": 3,
#   "by_severity": {
#     "CRITICAL": 0,
#     "WARNING": 2,
#     "INFO": 1
#   },
#   "active_alerts": [...]
# }
```

---

## 📈 CQS Formulas

### System-Level CQS (Hub)
```
CQS = (L4 × 20%) + (L2 × 25%) + (L1 × 25%) + (L3-OPS × 15%) + (L3-FAIR × 15%)

Range: 0% - 100%
Updated: Every 30 seconds
```

### Internal CQS (Core)
```
Internal CQS = (Performance × 30%) + (Fairness × 25%) + (Security/Privacy × 25%) 
             + (Compliance × 20%)

Where:
  Performance    = AUC, accuracy, calibration, drift metrics
  Fairness       = Demographic parity, equalized odds
  Security/Privacy = Adversarial robustness, model integrity
  Compliance     = GDPR, EU AI Act, regulatory alignment
```

### Global CQS (Hub + Core)
```
Global CQS = (System-Level CQS × 60%) + (Internal CQS × 40%)

Emphasizes hub reliability (cross-hub view) while incorporating
Core's automation intelligence (deep monitoring view)
```

---

## ⚙️ Configuration

### Module 5 Hub (`module5_hub_enhanced.py`)

```python
# Hub polling interval
POLLING_INTERVAL = 30  # seconds

# Hub timeout
HUB_TIMEOUT = 5  # seconds per hub poll

# Alert thresholds
ALERT_THRESHOLDS = {
    'L2_SECURITY': 0.70,        # Alert if < 70%
    'L1_COMPLIANCE': 0.75,      # Alert if < 75%
    'L3_OPERATIONS': 0.80,      # Alert if < 80%
    'L3_FAIRNESS': 0.70,        # Alert if < 70%
}
```

### Module 5 Core (`module5_core.py`)

```python
# Drift detection thresholds
PSI_THRESHOLD = 0.25          # Significant input drift
KS_THRESHOLD = 0.15           # Significant distribution change
ECE_THRESHOLD = 0.15          # Calibration degradation

# Fairness thresholds
DEMOGRAPHIC_PARITY_GAP = 0.10  # 10% difference
EQUALIZED_ODDS_GAP = 0.15      # 15% difference

# Alert intervals
DRIFT_CHECK_INTERVAL = 3600    # seconds (1 hour)
FAIRNESS_CHECK_INTERVAL = 86400 # seconds (1 day)
```

---

## 📋 Feature Checklist

### ✅ Module 5 Hub (Complete)
- [x] Polls all 5 hubs every 30 seconds
- [x] Computes system-level CQS
- [x] Detects cross-hub anomalies
- [x] Generates unified alerts
- [x] Tracks hub health and response times
- [x] Beautiful dashboard UI
- [x] REST API for integration
- [x] Background polling thread

### ✅ Module 5 Core (Complete)
- [x] Real-time metrics collection
- [x] Performance drift detection (PSI, KS, ECE)
- [x] Input/output drift monitoring
- [x] Concept drift detection
- [x] Fairness drift trends
- [x] Security anomaly detection
- [x] Compliance drift monitoring
- [x] Intelligent alert routing
- [x] Internal CQS calculation
- [x] Beautiful dashboard
- [x] REST API

### 🟢 Integration (Ready)
- [x] Module 5 Core client for Hub
- [x] Hub polls Core metrics
- [x] Blended CQS formula
- [x] Unified alert system
- [x] Master launcher script

---

## 🔍 Monitoring Guide

### Real-Time Monitoring
```bash
# Check system CQS every 5 seconds
watch -n 5 'curl -s http://localhost:8507/api/cqs | jq ".overall_cqs"'

# Check core internal CQS
watch -n 5 'curl -s http://localhost:8508/api/internal-cqs | jq ".overall_cqs"'

# Monitor drift status
curl http://localhost:8508/api/drift/performance

# Check active alerts
curl http://localhost:8508/api/alerts
```

### Alert Types & Actions

| Alert Type | Source | Severity | Typical Cause | Action |
|---|---|---|---|---|
| Hub Unreachable | Hub | CRITICAL | Hub crashed | Restart hub |
| Low Security Score | Hub | WARNING | Security issues | Review L2 hub |
| Input Drift Detected | Core | WARNING | Distribution change | Retrain model |
| Fairness Drift | Core | WARNING | Bias emerging | Review fairness |
| Compliance Gap | Core | CRITICAL | Regulatory violation | Escalate |
| Adversarial Vulnerability | Core | WARNING | Model robustness issue | Harden model |

---

## 🐛 Troubleshooting

### Module 5 Hub Not Starting

```bash
# Check Python environment
python --version

# Check Flask installed
pip install flask -q

# Verify port 8507 is available
netstat -ano | findstr ":8507"

# Run with verbose output
python start_module5_hub.py
```

### Module 5 Core Not Starting

```bash
# Check dependencies
pip install flask numpy requests -q

# Run directly
python start_module5_core.py

# Check port 8508
netstat -ano | findstr ":8508"
```

### Hubs Not Connecting

```bash
# Verify all 5 hubs are running
curl http://localhost:5000/api/transparency-score
curl http://localhost:8502/api/sai
curl http://localhost:8504/api/score
curl http://localhost:8503/api/health
curl http://localhost:8506/api/fairness-score

# Check Hub can reach Core
curl http://localhost:8508/api/internal-cqs
```

### High CQS Variance

**Issue**: System CQS fluctuating significantly  
**Cause**: Hub polling timing or network latency  
**Solution**: 
- Increase polling interval to 60 seconds
- Check network stability
- Verify hub endpoints respond consistently

---

## 📁 File Structure

```
iraqaf_starter_kit/
├── module5/
│   ├── __init__.py
│   ├── hub_clients/
│   │   ├── __init__.py
│   │   ├── base_client.py
│   │   ├── l4_explainability_client.py
│   │   ├── l2_security_client.py
│   │   ├── l1_regulations_client.py
│   │   ├── l3_operations_client.py
│   │   ├── l3_fairness_client.py
│   │   └── module5_core_client.py (NEW)
│   └── orchestrator/
│       ├── __init__.py
│       └── orchestrator.py
│
├── module5_core.py                    (Automation engine)
├── module5_hub_enhanced.py            (Hub orchestrator)
├── start_module5_hub.py              (Hub launcher)
├── start_module5_core.py             (Core launcher - NEW)
├── launch_all_dashboards.py          (Master launcher - NEW)
│
├── dashboard/
│   ├── app.py                        (Main portal)
│   ├── hub_explainability_app.py     (L4)
│   ├── privacy_security_hub.py       (L2)
│   ├── l1_regulations_governance_hub.py (L1)
│   ├── l3_operations_control_center.py (L3)
│   └── fairness_ethics_hub.py        (Fairness)
│
└── MODULE5_INTEGRATION_GUIDE.md       (This document)
```

---

## 🎯 Next Steps

1. **Deploy Module 5 Hub**
   ```bash
   python start_module5_hub.py
   # Access: http://localhost:8507
   ```

2. **Deploy Module 5 Core**
   ```bash
   python start_module5_core.py
   # Access: http://localhost:8508
   ```

3. **Verify Integration**
   ```bash
   curl http://localhost:8507/api/cqs
   curl http://localhost:8508/api/internal-cqs
   ```

4. **Add to Main Dashboard**
   - Module 5 Hub button added to sidebar
   - Navigation links available

5. **Monitor System**
   - Watch CQS trends
   - Review active alerts
   - Adjust thresholds as needed

---

## 📞 Support

For issues with:
- **Module 5 Hub**: Check `module5_hub_enhanced.py` error logs
- **Module 5 Core**: Check `module5_core.py` error logs
- **Integration**: Verify both services are running and accessible
- **Dashboards**: Check individual hub log files

---

**Status**: 🟢 **PRODUCTION READY**

Module 5 is fully implemented and tested. Deploy both Hub and Core for complete continuous QA automation.
