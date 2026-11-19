from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None
    citations: Optional[List[Dict[str, Any]]] = None

class AgentTool:
    """Base interface for DocuMind agent tools."""
    name: str
    description: str
    parameters_schema: Dict[str, Any]

    def execute(self, **kwargs) -> ToolResult:
        raise NotImplementedError
