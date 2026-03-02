"""
SCADA and Grid Data Simulator for 330kV/132kV Substations

Simulates realistic utility operational data:
- SCADA telemetry (voltage, current, power flow)
- Protection relay events (fault records, COMTRADE-style data)
- PMU phasor measurements (C37.118 protocol simulation)
- Transformer monitoring (DGA, thermal, pressure)
- Weather correlation data

This provides realistic data sources for demonstrations without needing
actual grid connectivity.
"""

import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class AssetType(str, Enum):
    """Asset types in a 330/132kV substation"""
    TRANSFORMER = "Transformer"
    CIRCUIT_BREAKER = "Circuit Breaker"
    BUSBAR = "Busbar"
    LINE = "Transmission Line"
    GENERATOR = "Generator"


class FaultType(str, Enum):
    """Protection relay fault classifications"""
    PHASE_TO_GROUND = "Phase-to-Ground"
    PHASE_TO_PHASE = "Phase-to-Phase"
    THREE_PHASE = "Three-Phase Fault"
    OVERLOAD = "Thermal Overload"
    UNDERVOLTAGE = "Voltage Sag"
    OVERVOLTAGE = "Voltage Swell"


class Severity(str, Enum):
    """Incident severity levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class Asset:
    """Substation asset definition"""
    id: str
    name: str
    asset_type: AssetType
    rated_voltage_kv: Optional[float] = None
    rated_current_a: Optional[float] = None
    rated_mva: Optional[float] = None
    base_temperature_c: float = 75.0
    status: str = "Normal"


@dataclass
class SCADAMeasurement:
    """SCADA telemetry data point"""
    timestamp: str
    station_id: str
    asset_id: str
    measurements: Dict[str, float]
    alarms: List[str]
    status: str


@dataclass
class ProtectionEvent:
    """Protection relay event record (COMTRADE-style)"""
    timestamp: str
    relay_id: str
    asset_id: str
    fault_type: FaultType
    fault_current_ka: float
    fault_location_km: Optional[float]
    zone_operated: str
    trip_initiated: bool
    severity: Severity


@dataclass
class TransformerDGA:
    """Dissolved Gas Analysis (IEC 60599 standard)"""
    timestamp: str
    transformer_id: str
    h2_ppm: float  # Hydrogen
    ch4_ppm: float  # Methane
    c2h2_ppm: float  # Acetylene
    c2h4_ppm: float  # Ethylene
    c2h6_ppm: float  # Ethane
    co_ppm: float  # Carbon monoxide
    co2_ppm: float  # Carbon dioxide
    diagnosis: str
    confidence: float


@dataclass
class PMUMeasurement:
    """Phasor Measurement Unit data (C37.118 protocol)"""
    timestamp: str
    pmu_id: str
    frequency_hz: float
    df_dt: float  # Rate of change of frequency
    voltage_phasors: Dict[str, Dict[str, float]]  # Phase -> {magnitude, angle}
    current_phasors: Dict[str, Dict[str, float]]
    
    
class GridDataSimulator:
    """
    Realistic grid data simulator for 330kV/132kV substations
    
    Generates telemetry, events, and measurements that mimic actual
    utility monitoring systems (SCADA, protection, PMU, DGA).
    """
    
    def __init__(self, station_id: str = "330kV_Station_Alpha"):
        self.station_id = station_id
        self.assets = self._initialize_assets()
        self.base_frequency = 60.0  # Hz (North America) - change to 50.0 for Europe
        self.incident_probability = 0.02  # 2% chance per measurement cycle
        self.current_incidents: List[Dict] = []
        
    def _initialize_assets(self) -> Dict[str, Asset]:
        """Initialize typical 330/132kV substation assets"""
        return {
            "T-401": Asset(
                id="T-401",
                name="Main Power Transformer #1",
                asset_type=AssetType.TRANSFORMER,
                rated_voltage_kv=330.0,
                rated_mva=300.0,
                base_temperature_c=75.0
            ),
            "T-402": Asset(
                id="T-402",
                name="Main Power Transformer #2",
                asset_type=AssetType.TRANSFORMER,
                rated_voltage_kv=330.0,
                rated_mva=300.0,
                base_temperature_c=75.0
            ),
            "CB-101": Asset(
                id="CB-101",
                name="330kV Circuit Breaker #1",
                asset_type=AssetType.CIRCUIT_BREAKER,
                rated_voltage_kv=330.0,
                rated_current_a=4000.0
            ),
            "CB-102": Asset(
                id="CB-102",
                name="132kV Circuit Breaker #2",
                asset_type=AssetType.CIRCUIT_BREAKER,
                rated_voltage_kv=132.0,
                rated_current_a=2000.0
            ),
            "BUS-330": Asset(
                id="BUS-330",
                name="330kV Main Busbar",
                asset_type=AssetType.BUSBAR,
                rated_voltage_kv=330.0,
                rated_current_a=5000.0
            ),
            "BUS-132": Asset(
                id="BUS-132",
                name="132kV Distribution Bus",
                asset_type=AssetType.BUSBAR,
                rated_voltage_kv=132.0,
                rated_current_a=3000.0
            ),
            "LINE-304": Asset(
                id="LINE-304",
                name="330kV Transmission Line to Station B",
                asset_type=AssetType.LINE,
                rated_voltage_kv=330.0,
                rated_current_a=2500.0
            ),
        }
    
    def generate_scada_telemetry(self) -> SCADAMeasurement:
        """
        Generate realistic SCADA measurements
        
        Simulates typical SCADA systems (DNP3, Modbus, ICCP protocols)
        with voltage, current, power flow, and equipment status.
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Check if we should inject an incident
        inject_incident = random.random() < self.incident_probability
        
        measurements = {}
        alarms = []
        
        for asset_id, asset in self.assets.items():
            if asset.asset_type == AssetType.TRANSFORMER:
                # Transformer measurements
                base_temp = asset.base_temperature_c
                temp_variation = random.uniform(-3, 5)
                
                # Inject overheat incident
                if inject_incident and not self.current_incidents:
                    temp = base_temp + random.uniform(15, 30)
                    alarms.append(f"{asset_id}: High Temperature Alarm (>{base_temp + 10}°C)")
                    self._record_incident(asset_id, "Transformer Overheating", Severity.CRITICAL)
                else:
                    temp = base_temp + temp_variation
                
                measurements[asset_id] = {
                    "temperature_c": round(temp, 1),
                    "top_oil_temp_c": round(temp + random.uniform(5, 10), 1),
                    "load_percent": round(random.uniform(55, 95), 1),
                    "tap_position": random.randint(-8, 8),
                    "cooling_fans_running": random.randint(1, 3),
                    "oil_level_percent": round(random.uniform(85, 98), 1),
                }
                
                if temp > base_temp + 10:
                    alarms.append(f"{asset_id}: Temperature Warning")
                
            elif asset.asset_type == AssetType.CIRCUIT_BREAKER:
                # Circuit breaker status
                is_closed = random.random() > 0.1  # 90% closed
                measurements[asset_id] = {
                    "status": "CLOSED" if is_closed else "OPEN",
                    "current_a": round(random.uniform(800, 3500), 1) if is_closed else 0.0,
                    "operating_time_ms": round(random.uniform(15, 25), 1),
                    "operations_count": random.randint(150, 500),
                }
                
            elif asset.asset_type == AssetType.BUSBAR:
                # Busbar voltage measurements
                base_voltage = asset.rated_voltage_kv
                voltage_pu = random.uniform(0.95, 1.05)
                
                # Inject voltage sag incident
                if inject_incident and not self.current_incidents and random.random() < 0.3:
                    voltage_pu = random.uniform(0.75, 0.88)
                    alarms.append(f"{asset_id}: Undervoltage Detected ({voltage_pu:.2f} pu)")
                    self._record_incident(asset_id, "Voltage Instability", Severity.HIGH)
                
                measurements[asset_id] = {
                    "voltage_kv": round(base_voltage * voltage_pu, 2),
                    "voltage_pu": round(voltage_pu, 3),
                    "frequency_hz": round(self.base_frequency + random.uniform(-0.05, 0.05), 3),
                }
                
            elif asset.asset_type == AssetType.LINE:
                # Transmission line power flow
                measurements[asset_id] = {
                    "mw_flow": round(random.uniform(80, 250), 1),
                    "mvar_flow": round(random.uniform(-50, 50), 1),
                    "current_a": round(random.uniform(300, 2000), 1),
                    "line_loading_percent": round(random.uniform(35, 85), 1),
                }
        
        return SCADAMeasurement(
            timestamp=timestamp,
            station_id=self.station_id,
            asset_id="SCADA_MASTER",
            measurements=measurements,
            alarms=alarms,
            status="Alarm" if alarms else "Normal"
        )
    
    def generate_protection_event(self) -> Optional[ProtectionEvent]:
        """
        Generate protection relay event (fault record)
        
        Simulates SEL, GE, Siemens protection relays with COMTRADE-style
        fault records when abnormal conditions are detected.
        """
        if not self.current_incidents:
            return None
        
        # Generate event for active incident
        incident = self.current_incidents[0]
        asset_id = incident["asset_id"]
        
        fault_types = [FaultType.PHASE_TO_GROUND, FaultType.OVERLOAD]
        fault_type = random.choice(fault_types)
        
        return ProtectionEvent(
            timestamp=datetime.utcnow().isoformat(),
            relay_id=f"RELAY_{asset_id}",
            asset_id=asset_id,
            fault_type=fault_type,
            fault_current_ka=round(random.uniform(2.5, 8.5), 2),
            fault_location_km=round(random.uniform(5, 45), 1) if "LINE" in asset_id else None,
            zone_operated="Zone 1" if random.random() > 0.5 else "Zone 2",
            trip_initiated=True,
            severity=incident["severity"]
        )
    
    def generate_transformer_dga(self, transformer_id: str = "T-401") -> TransformerDGA:
        """
        Generate Dissolved Gas Analysis results
        
        Uses IEC 60599 standard ratios to diagnose transformer faults:
        - C₂H₂/C₂H₄ > 0.1: Arcing
        - CH₄/H₂ > 0.1: Overheating
        - C₂H₄/C₂H₆ > 1: Partial discharge
        """
        # Normal gas concentrations (ppm)
        h2 = random.uniform(50, 150)
        ch4 = random.uniform(20, 80)
        c2h2 = random.uniform(1, 10)
        c2h4 = random.uniform(10, 50)
        c2h6 = random.uniform(5, 30)
        co = random.uniform(300, 800)
        co2 = random.uniform(2000, 8000)
        
        # Check for active overheating incident
        if any(i["asset_id"] == transformer_id and "Overheat" in i["description"] 
               for i in self.current_incidents):
            # Inject thermal fault signature
            ch4 = random.uniform(150, 300)
            c2h4 = random.uniform(80, 150)
            h2 = random.uniform(200, 400)
        
        # Calculate IEC 60599 ratios
        ratio_c2h2_c2h4 = c2h2 / c2h4 if c2h4 > 0 else 0
        ratio_ch4_h2 = ch4 / h2 if h2 > 0 else 0
        ratio_c2h4_c2h6 = c2h4 / c2h6 if c2h6 > 0 else 0
        
        # Diagnosis based on ratios
        if ratio_c2h2_c2h4 > 0.1:
            diagnosis = "Electrical Arcing Detected"
            confidence = 0.95
        elif ratio_ch4_h2 > 0.1:
            diagnosis = "Thermal Overheating Detected"
            confidence = 0.88
        elif ratio_c2h4_c2h6 > 1:
            diagnosis = "Partial Discharge Activity"
            confidence = 0.82
        else:
            diagnosis = "Normal Operation"
            confidence = 0.75
        
        return TransformerDGA(
            timestamp=datetime.utcnow().isoformat(),
            transformer_id=transformer_id,
            h2_ppm=round(h2, 1),
            ch4_ppm=round(ch4, 1),
            c2h2_ppm=round(c2h2, 1),
            c2h4_ppm=round(c2h4, 1),
            c2h6_ppm=round(c2h6, 1),
            co_ppm=round(co, 1),
            co2_ppm=round(co2, 1),
            diagnosis=diagnosis,
            confidence=confidence
        )
    
    def generate_pmu_measurement(self) -> PMUMeasurement:
        """
        Generate PMU phasor measurement
        
        Simulates C37.118 protocol with synchronized phasor measurements
        (30-120 samples/second in real systems, here just snapshot).
        """
        freq = self.base_frequency + random.uniform(-0.02, 0.02)
        df_dt = random.uniform(-0.01, 0.01)
        
        # Three-phase voltage phasors (balanced system)
        v_magnitude = 330.0 * random.uniform(0.98, 1.02)
        voltage_phasors = {
            "Va": {"magnitude": round(v_magnitude, 2), "angle": 0.0},
            "Vb": {"magnitude": round(v_magnitude, 2), "angle": -120.0},
            "Vc": {"magnitude": round(v_magnitude, 2), "angle": 120.0}
        }
        
        # Three-phase current phasors
        i_magnitude = random.uniform(1000, 3000)
        current_angle = random.uniform(-30, 30)  # Power factor dependent
        current_phasors = {
            "Ia": {"magnitude": round(i_magnitude, 1), "angle": round(current_angle, 1)},
            "Ib": {"magnitude": round(i_magnitude, 1), "angle": round(current_angle - 120, 1)},
            "Ic": {"magnitude": round(i_magnitude, 1), "angle": round(current_angle + 120, 1)}
        }
        
        return PMUMeasurement(
            timestamp=datetime.utcnow().isoformat(),
            pmu_id=f"PMU_{self.station_id}",
            frequency_hz=round(freq, 3),
            df_dt=round(df_dt, 4),
            voltage_phasors=voltage_phasors,
            current_phasors=current_phasors
        )
    
    def get_active_incidents(self) -> List[Dict]:
        """Get currently active incidents"""
        return self.current_incidents.copy()
    
    def resolve_incident(self, asset_id: str):
        """Mark an incident as resolved"""
        self.current_incidents = [
            i for i in self.current_incidents 
            if i["asset_id"] != asset_id
        ]
    
    def _record_incident(self, asset_id: str, description: str, severity: Severity):
        """Internal: Record new incident"""
        incident = {
            "asset_id": asset_id,
            "description": description,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "Active"
        }
        self.current_incidents.append(incident)
    
    async def stream_telemetry(self, interval_seconds: int = 5):
        """
        Async generator for real-time telemetry streaming
        
        Usage:
            simulator = GridDataSimulator()
            async for data in simulator.stream_telemetry():
                process(data)
        """
        while True:
            yield self.generate_scada_telemetry()
            await asyncio.sleep(interval_seconds)


# ==================== UTILITY FUNCTIONS ====================

def simulate_historical_incidents(days_back: int = 30) -> List[Dict]:
    """
    Generate historical incident data for analytics
    
    Returns list of incidents over the past N days for
    trending analysis, ML training, or dashboard visualization.
    """
    incidents = []
    simulator = GridDataSimulator()
    
    for day in range(days_back):
        # 1-3 incidents per day
        num_incidents = random.randint(1, 3)
        
        for _ in range(num_incidents):
            timestamp = datetime.utcnow() - timedelta(days=day, hours=random.randint(0, 23))
            asset = random.choice(list(simulator.assets.values()))
            
            incident_types = [
                ("Transformer Overheating", Severity.CRITICAL),
                ("Voltage Instability", Severity.HIGH),
                ("Circuit Breaker Failure", Severity.CRITICAL),
                ("Load Imbalance", Severity.MEDIUM),
                ("Minor Alarm", Severity.LOW),
            ]
            
            description, severity = random.choice(incident_types)
            
            incidents.append({
                "id": f"INC-{len(incidents):04d}",
                "timestamp": timestamp.isoformat(),
                "asset_id": asset.id,
                "asset_name": asset.name,
                "description": description,
                "severity": severity.value,
                "status": random.choice(["Resolved", "Investigating", "Active"]),
                "duration_minutes": random.randint(15, 480),
                "customers_affected": random.randint(0, 5000) if severity in [Severity.CRITICAL, Severity.HIGH] else 0
            })
    
    return sorted(incidents, key=lambda x: x["timestamp"], reverse=True)


def analyze_causal_chain(incidents: List[Dict]) -> Dict[str, Any]:
    """
    Analyze incident correlation to find causal chains
    
    Simulates root cause analysis by correlating incidents
    that occurred close in time and affect related assets.
    """
    if not incidents:
        return {"root_cause": None, "chain": [], "confidence": 0.0}
    
    # Sort by timestamp
    sorted_incidents = sorted(incidents, key=lambda x: x["timestamp"])
    
    # Build causal chain (simplified heuristic)
    chain = []
    root = sorted_incidents[0]
    
    chain.append({
        "incident": root["description"],
        "asset": root["asset_id"],
        "role": "Root Cause",
        "timestamp": root["timestamp"]
    })
    
    for inc in sorted_incidents[1:]:
        time_diff = (datetime.fromisoformat(inc["timestamp"]) - 
                     datetime.fromisoformat(root["timestamp"])).total_seconds() / 60
        
        if time_diff < 15:  # Within 15 minutes
            chain.append({
                "incident": inc["description"],
                "asset": inc["asset_id"],
                "role": "Cascade Effect",
                "timestamp": inc["timestamp"]
            })
    
    confidence = min(0.95, 0.70 + (len(chain) - 1) * 0.1)
    
    return {
        "root_cause": root["description"],
        "root_asset": root["asset_id"],
        "chain": chain,
        "confidence": round(confidence, 2),
        "affected_assets": len(set(c["asset"] for c in chain))
    }


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Initialize simulator
    sim = GridDataSimulator(station_id="330kV_Station_Alpha")
    
    print("=" * 80)
    print("SCADA/Grid Data Simulator - 330kV/132kV Substation")
    print("=" * 80)
    
    # Generate SCADA telemetry
    print("\n1. SCADA TELEMETRY:")
    scada_data = sim.generate_scada_telemetry()
    print(f"Timestamp: {scada_data.timestamp}")
    print(f"Station: {scada_data.station_id}")
    print(f"Status: {scada_data.status}")
    print(f"Alarms: {scada_data.alarms if scada_data.alarms else 'None'}")
    print("\nAsset Measurements:")
    for asset_id, measurements in scada_data.measurements.items():
        print(f"  {asset_id}: {measurements}")
    
    # Generate protection event (if incident active)
    print("\n2. PROTECTION RELAY EVENT:")
    protection_event = sim.generate_protection_event()
    if protection_event:
        print(f"Relay: {protection_event.relay_id}")
        print(f"Fault Type: {protection_event.fault_type}")
        print(f"Fault Current: {protection_event.fault_current_ka} kA")
        print(f"Zone Operated: {protection_event.zone_operated}")
        print(f"Trip Initiated: {protection_event.trip_initiated}")
    else:
        print("No protection events (normal operation)")
    
    # Generate DGA analysis
    print("\n3. TRANSFORMER DGA (Dissolved Gas Analysis):")
    dga = sim.generate_transformer_dga("T-401")
    print(f"Transformer: {dga.transformer_id}")
    print(f"H₂: {dga.h2_ppm} ppm | CH₄: {dga.ch4_ppm} ppm | C₂H₂: {dga.c2h2_ppm} ppm")
    print(f"Diagnosis: {dga.diagnosis}")
    print(f"Confidence: {dga.confidence * 100:.1f}%")
    
    # Generate PMU measurement
    print("\n4. PMU PHASOR MEASUREMENT:")
    pmu = sim.generate_pmu_measurement()
    print(f"PMU ID: {pmu.pmu_id}")
    print(f"Frequency: {pmu.frequency_hz} Hz (df/dt: {pmu.df_dt} Hz/s)")
    print(f"Voltage Phasors: {pmu.voltage_phasors}")
    
    # Historical incidents
    print("\n5. HISTORICAL INCIDENT ANALYSIS (Last 7 Days):")
    historical = simulate_historical_incidents(days_back=7)
    print(f"Total Incidents: {len(historical)}")
    print("\nRecent Incidents:")
    for inc in historical[:5]:
        print(f"  [{inc['severity']}] {inc['timestamp'][:19]} - {inc['asset_id']}: {inc['description']}")
    
    # Causal chain analysis
    print("\n6. CAUSAL CHAIN ANALYSIS:")
    recent_incidents = [i for i in historical if i["status"] == "Active"][:3]
    if recent_incidents:
        analysis = analyze_causal_chain(recent_incidents)
        print(f"Root Cause: {analysis['root_cause']}")
        print(f"Confidence: {analysis['confidence'] * 100:.0f}%")
        print("Causal Chain:")
        for step in analysis["chain"]:
            print(f"  → {step['role']}: {step['incident']} ({step['asset']})")
    else:
        print("No active incident chains")
    
    print("\n" + "=" * 80)
    print("Simulator ready for integration with UI/API")
    print("=" * 80)
