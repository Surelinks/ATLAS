# ATLAS AI - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard Module](#dashboard-module)
3. [Operations Copilot](#operations-copilot)
4. [Incident Analyzer](#incident-analyzer)
5. [System Analytics](#system-analytics)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### System Requirements
- **Backend**: Python 3.10+
- **Frontend**: Modern web browser (Chrome, Firefox, Edge)
- **Network**: Backend on port 8000, Frontend on port 8501

### First Time Setup

1. **Start the Backend Server**
   ```bash
   cd backend
   python -m uvicorn app.main:app --port 8000 --reload
   ```

2. **Start the Frontend**
   ```bash
   streamlit run ui/app.py --server.port 8501
   ```

3. **Access the Application**
   - Open browser to: `http://localhost:8501`
   - Verify "System Status" shows green indicators in sidebar

---

## Dashboard Module

### Purpose
Real-time SCADA monitoring for 330kV/132kV substation operations.

### Features

#### 1. SCADA Metrics
- **Grid Frequency**: Normal range 59.95-60.05 Hz
- **Power Flow**: MW through transmission lines
- **Transformer Load**: Percentage of rated capacity
- **Busbar Voltage**: Per-unit voltage (0.95-1.05 pu acceptable)

**Status Indicators:**
- 🟢 Green = Normal operation
- 🟡 Yellow = Warning (approaching limits)
- 🔴 Red = Critical (out of limits)

#### 2. Asset Telemetry
View live measurements organized by:
- **Transformers**: Temperature, load, cooling status
- **Circuit Breakers**: Position, trip counts
- **Busbars**: Voltage levels, phase balance

#### 3. Incident Log
- Recent alarm history
- Severity classification (Critical/High/Medium/Low)
- Asset-specific alerts

### How to Use
1. Select "Dashboard" from sidebar
2. Monitor metric cards for anomalies
3. Check "Active Alarms" section if red indicators appear
4. Review asset telemetry tabs for detailed readings

---

## Operations Copilot

### Purpose
RAG-powered assistant for operational procedure queries.

### Step-by-Step Guide

#### Uploading SOPs

1. Click "Operations Copilot" in sidebar
2. Navigate to **left column** ("Upload Documents")
3. Click "Browse files" button
4. Select PDF or TXT documents:
   - Standard Operating Procedures
   - Emergency response guides
   - Maintenance manuals
5. Click "Process Document"
6. Wait for "Document indexed successfully" confirmation

**Supported Formats:**
- ✅ PDF (.pdf)
- ✅ Text (.txt)
- ❌ Word (.docx) - not supported
- ❌ Images - not supported

#### Asking Questions

1. Go to **center column** ("Chat Interface")
2. Type your question in the input box
3. Press Enter or click "Send"
4. AI responds with answer + source citations

**Example Questions:**
- "What are the steps for grid stability restoration?"
- "How do I handle transformer overheating?"
- "What is the power outage response procedure?"
- "What are the safety requirements for maintenance?"

#### Understanding Responses

**Answer Section:**
- AI-generated response based on your documents
- Cites specific SOPs and page numbers

**Retrieved Context** (right column):
- Shows source documents used
- Relevance score (0-1, higher = more relevant)
- Text snippets from documents

### Tips for Best Results
✅ **Do:**
- Upload comprehensive SOPs before asking questions
- Ask specific, detailed questions
- Reference equipment by standard IDs (T-401, CB-101, etc.)

❌ **Don't:**
- Ask questions before uploading documents
- Use vague or overly broad questions
- Expect answers outside your uploaded content

---

## Incident Analyzer

### Purpose
AI-powered root cause analysis and event correlation.

### Features

#### 1. Search & Filter
- **Search Bar**: Find incidents by description or asset ID
- **Severity Filter**: Show only Critical/High/Medium/Low
- **Export**: Download incident data as CSV

#### 2. Timeline Analysis
- **Visual Timeline**: Events plotted by time and severity
- **Interactive Chart**: Zoom, pan, reset view
- **Pagination**: Navigate through incidents (15 per page)

**How to Read Timeline:**
- X-axis = Time
- Y-axis = Severity (Low → Critical)
- Color = Severity level
- Hover = Incident details

#### 3. Root Cause Detection
- Identifies primary fault source
- Shows causal chain (cascading failures)
- Confidence level (0-100%)
- Affected asset count

**Example Output:**
```
✓ Primary Cause: Transformer Overload
✓ Root Asset: T-401
✓ Confidence: 92% (High)
✓ Affected Assets: 3 components

Causal Chain:
1. ROOT: T-401 overload at 08:15:00
2. CASCADE: CB-101 tripped at 08:15:23
3. CASCADE: BUS-330 voltage drop at 08:15:45
```

#### 4. DGA Diagnostics
Dissolved Gas Analysis for transformer health.

**Gas Concentrations:**
- H₂ (Hydrogen): < 100 ppm normal
- CH₄ (Methane): < 120 ppm normal
- C₂H₂ (Acetylene): < 5 ppm normal (fault indicator)
- C₂H₄ (Ethylene): < 50 ppm normal
- C₂H₆ (Ethane): < 65 ppm normal

**Fault Types Detected:**
- ⚡ Electrical Arcing (high C₂H₂)
- 🔥 Thermal Fault (high CH₄, C₂H₄)
- ❌ Normal Aging (balanced gases)
- 🔌 Partial Discharge (high H₂, low others)

### How to Use
1. Select "Incident Analyzer" from sidebar
2. Use search/filter to find specific incidents
3. View timeline to identify event clusters
4. Check Root Cause tab for AI analysis
5. Review DGA for transformer-specific faults
6. Export data for reporting

---

## System Analytics

### Purpose
Long-term trend analysis and performance metrics.

### Modules

#### 1. Incident Trends Chart
- Line graph showing incidents over time
- Color-coded by severity
- Selectable time range (7/30/90 days)
- Interactive zoom and pan

**How to Use:**
- Click legend to show/hide severity levels
- Drag to zoom into specific date range
- Double-click to reset zoom
- Click download icon to save as PNG

#### 2. Severity Distribution
- Pie chart showing incident breakdown
- Percentage of each severity level
- Quick health indicator

**Interpretation:**
- High % Critical = System stress
- Mostly Low/Medium = Normal operations
- Trend increasing = Investigate root causes

#### 3. Top Affected Assets
- Bar chart of assets with most incidents
- Identifies problematic equipment
- Focus maintenance efforts

**Action Items:**
- Assets with >10 incidents/month = inspect
- Repeated failures = consider replacement
- Cluster analysis = common mode failures

#### 4. Export Analytics
- Click "Export Analytics" to download CSV
- Includes all data for selected time range
- Use for management reports

### How to Use
1. Select "System Analytics" from sidebar
2. Choose time range (7/30/90 days)
3. Review trend charts for patterns
4. Identify high-incident assets
5. Export data for offline analysis

---

## Keyboard Shortcuts

Speed up your workflow with keyboard commands:

| Shortcut | Action |
|----------|--------|
| `Ctrl + K` | Focus search bar |
| `Ctrl + U` | Quick upload document |
| `Ctrl + Enter` | Send chat message |
| `Ctrl + E` | Export current view |
| `Esc` | Clear filters |

**Tips:**
- Shortcuts work when input fields are not focused
- Use `Tab` to navigate between elements
- Press `?` to show shortcut help

---

## Theme Settings

### Switch Themes
1. Open sidebar
2. Find "⚙️ Settings" section
3. Click:
   - 🌙 Dark (default)
   - ☀️ Light (high contrast)

**Theme persists during session**

---

## Troubleshooting

### Backend Connection Issues

**Symptom:** Red "API Server" status in sidebar

**Solutions:**
1. Check backend is running:
   ```bash
   cd backend
   python -m uvicorn app.main:app --port 8000
   ```
2. Verify port 8000 not in use:
   ```bash
   netstat -ano | findstr :8000
   ```
3. Check firewall allows localhost:8000

---

### Document Upload Fails

**Symptom:** "Upload failed" error

**Solutions:**
1. Check file format (only PDF/TXT supported)
2. Verify file size < 25MB
3. Ensure backend /api/v1/ops-copilot/upload endpoint accessible
4. Check browser console for detailed error

---

### No Chat Response

**Symptom:** Spinning loader, no answer

**Solutions:**
1. Verify documents are uploaded first
2. Check question is clear and specific
3. Ensure LLM API key configured (GROQ_API_KEY in .env)
4. Review backend logs for errors

---

### SCADA Data Not Updating

**Symptom:** Static metrics, no changes

**Solution:**
- SCADA simulator generates data on page load
- Click "Dashboard" again to refresh
- Check simulator is initialized (sidebar shows "SCADA Feed: Connected")

---

### Charts Not Displaying

**Symptom:** Blank space where chart should be

**Solutions:**
1. Ensure historical incidents exist (7+ days of data)
2. Check browser JavaScript is enabled
3. Try refreshing page (Ctrl+R)
4. Check browser console for Plotly errors

---

## Getting Help

**Documentation:**
- API Docs: `/docs/API_DOCUMENTATION.md`
- Demo Guide: `/DEMO_GUIDE.md`
- Architecture: `/README.md`

**Common Issues:**
- Check backend terminal for error logs
- Review browser console (F12) for frontend errors
- Verify environment variables in `.env` file

**Support:**
- Check GitHub Issues
- Review PROJECT_AUDIT.md for known limitations
