from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any, Union


class MessagePart(BaseModel):
    kind: str
    text: Optional[str] = None
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    file_url: Optional[str] = None

    @field_validator("data", mode="before")
    @classmethod
    def validate_data(cls, v):
        """Convert list data to dictionary"""
        if isinstance(v, list):
            if all(isinstance(item, dict) for item in v):
                merged = {}
                for item in v:
                    merged.update(item)
                return merged
        return v


class A2AMessage(BaseModel):
    role: str
    parts: List[MessagePart]
    messageId: Optional[str] = None
    taskId: Optional[str] = None


class MessageParams(BaseModel):
    message: A2AMessage
    configuration: Optional[Dict[str, Any]] = None


class ExecuteParams(BaseModel):
    contextId: Optional[str] = None
    taskId: Optional[str] = None
    messages: List[A2AMessage]


class A2ARequest(BaseModel):
    jsonrpc: str = "2.0"
    id: str
    method: str
    params: Dict[str, Any]


class TaskStatus(BaseModel):
    state: str
    timestamp: str
    message: Optional[A2AMessage] = None


class Artifact(BaseModel):
    artifactId: str
    name: str
    parts: List[MessagePart]


class TaskResult(BaseModel):
    id: str
    contextId: str
    status: TaskStatus
    artifacts: List[Artifact] = []
    history: List[A2AMessage] = []


class A2AResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: str
    result: Optional[TaskResult] = None
    error: Optional[Dict[str, Any]] = None
