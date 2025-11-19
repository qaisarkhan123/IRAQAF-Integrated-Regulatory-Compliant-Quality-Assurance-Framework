# 🎛️ L3 Operations Control Center - Quick Reference Card

## One-Line Starters

```bash
# Start L3 Hub Only
python launch_l3_operations_hub.py

# Start All 4 Dashboards  
.\START_ALL_DASHBOARDS.ps1

# Direct Python
python dashboard/l3_operations_control_center.py
```

---

## Access Points

| Hub | Port | URL | Purpose |
|-----|------|-----|---------|
| **L1** | 8504 | http://localhost:8504 | Regulations & Governance |
| **L2** | 8502 | http://localhost:8502 | Privacy & Security |
| **L3** | 8503 | http://localhost:8503 | Operations (ALL PHASES) |
| **L4** | 5000 | http://localhost:5000 | Model Explainability |

---

## Dashboard Overview

### Header
- 🎛️ System name and version
- ✅ Live status indicators
- ⏰ Real-time clock

### 4 Key Metrics
```
🧪 Tests:           105+
📈 Coverage:        89%
🔌 Endpoints:       19+
📋 Requirements:    105
```

### 8 Phase Cards
Each with expandable details:
1. 🏗️ Architecture
2. 🗄️ Database
3. 🕷️ Scrapers
4. 🧠 NLP
5. ⚖️ Compliance
6. 👁️ Monitoring
7. 🔌 APIs
8. 🧪 Testing

### API Endpoints
All 19+ grouped by resource type

### Coverage Visualization
Module-by-module code coverage bars

---

## API Reference

```
GET /api/status              Full system status
GET /api/phase/1             Phase 1 details
GET /api/phase/2             Phase 2 details
GET /api/phase/3             Phase 3 details
GET /api/phase/4             Phase 4 details
GET /api/phase/5             Phase 5 details
GET /api/phase/6             Phase 6 details
GET /api/phase/7             Phase 7 details
GET /api/phase/8             Phase 8 details
GET /api/health              Health check
```

---

## Dashboard Features At a Glance

| Feature | Status |
|---------|--------|
| Real-time Monitoring | ✅ |
| All 8 Phases Visible | ✅ |
| API Documentation | ✅ |
| Coverage Tracking | ✅ |
| Status Indicators | ✅ |
| Responsive UI | ✅ |
| Dark Theme | ✅ |
| Performance Optimized | ✅ |

---

## Phase Integration

### Phase 1: Architecture
- Module overview
- System structure
- Core components

### Phase 2: Database
- Schema display
- Operations list
- Connection info

### Phase 3: Scrapers
- 5 sources listed
- Status per scraper
- Last run times

### Phase 4: NLP
- Capabilities shown
- Metrics displayed
- Performance data

### Phase 5: Compliance
- Scoring metrics
- Gap analysis
- Assessment times

### Phase 6: Monitoring
- Recent changes feed
- Alert count
- Drift status

### Phase 7: APIs/CLI
- 19+ endpoints
- 12+ commands
- Rate limits

### Phase 8: Testing
- 105+ tests
- 98.1% pass rate
- 89% coverage

---

## Browser Navigation

| Element | Action |
|---------|--------|
| Phase Cards | Click to expand/collapse |
| Metrics | View in real-time |
| Endpoints | Scroll to see all |
| Coverage Bars | Hover for details |
| Status Indicators | Always live |

---

## Troubleshooting

### Port Already in Use
```bash
# Find PID on port 8503
netstat -ano | findstr ":8503"

# Kill process
taskkill /PID <PID> /F
```

### Dashboard Won't Load
- Check URL: http://localhost:8503
- Check server is running
- Clear browser cache
- Try different browser

### API Not Responding
- Verify port 8503 is open
- Check firewall settings
- Restart dashboard
- Review server logs

---

## Performance Profile

| Metric | Value |
|--------|-------|
| Response Time | <100ms |
| Concurrent Users | 100+ |
| Memory | ~50MB |
| CPU (idle) | <1% |
| Dashboard Load | 2-3s |

---

## Files Reference

```
Main Files:
  dashboard/l3_operations_control_center.py
  L3_OPERATIONS_CONTROL_CENTER_GUIDE.md
  launch_l3_operations_hub.py
  L3_LAUNCH_SUMMARY.md

Phase Files:
  db/operations.py
  scrapers/base_scraper.py
  nlp_pipeline/nlp.py
  compliance/scorer.py
  monitoring/change_detector.py
  api_or_cli/api.py
  api_or_cli/cli.py
  tests/test_phase8_*.py

Launchers:
  START_ALL_DASHBOARDS.ps1
  START_ALL_DASHBOARDS.py
  launch_l3_operations_hub.py
```

---

## Integration Map

```
L3 Operations (8503)
├── L1 Regulations (8504)
│   └─ Details: GDPR, EU AI Act, ISO
├── L2 Security (8502)
│   └─ Details: 11 modules, SAI score
└── L4 Explainability (5000)
    └─ Details: SHAP, LIME, GradCAM
```

---

## Next Steps

1. **Start Dashboard**
   ```bash
   python launch_l3_operations_hub.py
   ```

2. **Open in Browser**
   ```
   http://localhost:8503
   ```

3. **Explore Phases**
   - Click each card to see details
   - Review metrics
   - Check API endpoints

4. **Use APIs**
   ```bash
   curl http://localhost:8503/api/status
   ```

5. **Switch Between Hubs**
   - L1 for regulations
   - L2 for security
   - L3 for operations (you are here)
   - L4 for model insights

---

## Git Status

```
Commit:  2b3d228
Branch:  main
Status:  Pushed to GitHub ✅
Message: feat: Add L3 Operations Control Center
```

---

## Contact & Support

- Main Guide: `L3_OPERATIONS_CONTROL_CENTER_GUIDE.md`
- Code: `dashboard/l3_operations_control_center.py`
- Launcher: `launch_l3_operations_hub.py`

---

**L3 Operations Control Center v1.0**  
*All 8 IRAQAF Phases Integrated*  
*Production-Ready Dashboard*

✨ Your operational cockpit is ready!
