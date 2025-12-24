"""Schemas for MCP client"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

class MessageRole(Enum):
    """Message role enum"""
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class MCPRequest:
    """MCP request dataclass"""
    jsonrpc: str = "2.0"
    id: Union[str, int] = 1
    method: str = ""
    params: Optional[Dict[str, Any]] = None

@dataclass
class MCPResponse:
    """MCP response dataclass"""
    jsonrpc: str
    id: Union[str, int]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

@dataclass
class Tool:
    """Tool dataclass"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

@dataclass
class Message:
    """Message dataclass"""
    role: MessageRole
    content: str

@dataclass
class ChatRequest:
    """Chat request dataclass"""

    messages: List[Message]
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None