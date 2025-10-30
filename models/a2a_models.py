#!/usr/bin/python3
"""Agent model module"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class Message(BaseModel):
    """class representing a message in the conversation"""

    kind: str
    text: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    file_url: Optional[str] = None

class A2AMessage(BaseModel):
    """class representing a message in the A2A conversation"""

    role: str
    parts: List[Message]
    messageId: Optional[str] = None
    taskId: Optional[str] = None

class MessageParams(BaseModel):
    """class representing parameters for message processing"""

    message: A2AMessage
    configuration: Optional[Dict[str, Any]] = None

class ExecuteParams(BaseModel):
    """class representing parameters for executing a task"""

    contextId: Optional[str] = None
    taskId: Optional[str] = None
    message: List[A2AMessage]

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
    parts: List[Message]

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