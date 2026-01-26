"""
Pydantic models for Atlas AI
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# Incident Models
class Incident(BaseModel):
    """Incident log entry"""
    incident_id: str
    timestamp: str
    source_system: str
    event_type: str
    severity: int
    asset_id: str
    location: str
    message: str
    raw_value: Optional[float] = None
    unit: Optional[str] = None
    operator: str
    correlation_id: Optional[str] = None
    root_cause_hint: Optional[str] = None


class IncidentChain(BaseModel):
    """Correlated incident chain"""
    chain_id: str
    incidents: List[Incident]
    root_cause: str
    confidence: float
    timeline_summary: str
    affected_assets: List[str]
    severity_max: int


class TimelineRequest(BaseModel):
    """Request to analyze incident timeline"""
    incidents: List[Incident]
    correlation_window_seconds: Optional[int] = 300
    detect_patterns: Optional[bool] = True


class TimelineResponse(BaseModel):
    """Timeline analysis response"""
    chains: List[IncidentChain]
    isolated_incidents: List[Incident]
    total_incidents: int
    analysis_summary: str


# Document Models  
class DocumentMetadata(BaseModel):
    """Document metadata"""
    document_id: str
    filename: str
    chunk_count: int
    uploaded_at: Optional[datetime] = None


class QueryRequest(BaseModel):
    """SOP query request"""
    question: str
    top_k: Optional[int] = 3
    include_sources: Optional[bool] = True


class SourceCitation(BaseModel):
    """Source citation"""
    index: int
    document: str
    document_id: str
    excerpt: str


class QueryResponse(BaseModel):
    """Query response with sources"""
    answer: str
    confidence: str
    sources: Optional[List[SourceCitation]] = []
