# Sample Data for Atlas AI

## Overview
This directory contains synthetic operational data for testing and demonstration purposes.

**Important:** All data in this repository is synthetic and generated for academic/demonstration purposes. No real utility data or proprietary information is included.

## Directory Structure

### `/sops/` - Standard Operating Procedures
Contains sample SOP documents for power utility operations:

- **SOP_Power_Outage_Response.pdf** - Emergency power outage response protocol
- **SOP_Power_Outage_Response_Expanded.pdf** - Detailed version
- **SOP_Transformer_Maintenance.pdf** - Transformer maintenance checklist
- **SOP_Transformer_Maintenance_Expanded.pdf** - Detailed version
- **SOP_Grid_Stability_Monitoring.pdf** - Grid stability monitoring procedures
- **SOP_Grid_Stability_Monitoring_Expanded.pdf** - Detailed version

**Usage:**
- These SOPs are ingested by the Ops Copilot module
- Used for RAG-based question answering
- Demonstrate SOP enforcement capabilities

**Total:** 6 PDF documents (~3 unique SOPs with expanded versions)

### `/incidents/` - Incident Logs
Will contain synthetic incident log data for timeline reconstruction and root cause analysis.

**Format:** JSON  
**Structure:**
```json
[
  {
    "id": "INC-2024-001",
    "timestamp": "2024-03-15T14:30:22Z",
    "source": "Substation_A_SCADA",
    "event_type": "transformer_overtemp",
    "severity": 3,
    "message": "Transformer T-401 temperature: 95°C",
    "asset_id": "T-401",
    "correlation_id": "CHAIN-001"
  }
]
```

**Status:** To be generated in Sprint 1 Week 2

### `/proposals/` - Consulting Templates (Optional)
Sample consulting proposal templates for stretch feature.

**Status:** Phase 2 / Optional

## Data Generation

### Who Generates What:
- **SOPs:** ChatGPT (with your domain customization) ✅ COMPLETE
- **Incident Logs:** DeepSeek (algorithm-focused design) → PENDING
- **Proposals:** ChatGPT (business writing) → OPTIONAL

## Next Steps

1. **Week 1:** Use existing SOPs for initial RAG development
2. **Week 2:** Generate incident logs with DeepSeek
3. **Week 3+:** Add edge cases and test data as needed

## Testing Use Cases

### Ops Copilot Test Queries:
- "What is the correct power outage response procedure?"
- "What safety precautions are required for transformer maintenance?"
- "How do I monitor grid stability?"
- "What are the emergency shutdown steps?"

### Incident Analyzer Test Scenarios:
- Single isolated incident
- Cascading failure chain (transformer → grid instability → outage)
- Recurring pattern detection
- Out-of-order log handling

## Data Privacy & Ethics

✅ All data is synthetic  
✅ No real infrastructure details  
✅ No proprietary information  
✅ Safe for public GitHub repository  
✅ Disclosed in main README  

---

**Last Updated:** January 26, 2026
