from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.policy import PolicyType, PolicyStatus


class PolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    policy_type: PolicyType
    natural_language: Optional[str] = None
    dsl: Optional[str] = None
    priority: int = 100


class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    natural_language: Optional[str] = None
    dsl: Optional[str] = None
    status: Optional[PolicyStatus] = None
    priority: Optional[int] = None


class PolicyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    policy_type: PolicyType
    natural_language: Optional[str]
    dsl: Optional[str]
    status: PolicyStatus
    priority: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PolicyTranslateRequest(BaseModel):
    natural_language: str


class InsightResponse(BaseModel):
    title: str
    description: str
    severity: str
    category: str
    suggested_action: str
    impact: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    current_page: Optional[str] = "/"


class ChatResponse(BaseModel):
    role: str
    content: str
    tool_calls: List[Dict[str, Any]] = []
