
"""MCP client"""

import json
import requests
from typing import Dict, Any, List, Optional
from schemas import MCPRequest, MCPResponse, Tool

class MCPClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.tools: List[Tool] = []
        
    def _make_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> MCPResponse:
        """Make an MCP request to the server"""
        request = MCPRequest(method=method, params=params)
        
        try:
            response = self.session.post(
                self.server_url,
                json={
                    "jsonrpc": request.jsonrpc,
                    "id": request.id,
                    "method": request.method,
                    "params": request.params
                },
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return MCPResponse(
                jsonrpc=data.get("jsonrpc", "2.0"),
                id=data.get("id", 1),
                result=data.get("result"),
                error=data.get("error")
            )
        except requests.exceptions.RequestException as e:
            return MCPResponse(
                jsonrpc="2.0",
                id=1,
                error={"code": -1, "message": f"Request failed: {str(e)}"}
            )
        except json.JSONDecodeError as e:
            return MCPResponse(
                jsonrpc="2.0", 
                id=1,
                error={"code": -2, "message": f"Invalid JSON response: {str(e)}"}
            )
    
    def initialize(self) -> bool:
        """Initialize connection with the MCP server"""
        response = self._make_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "customer-support-chatbot",
                "version": "1.0.0"
            }
        })
        
        if response.error:
            print(f"Failed to initialize: {response.error}")
            return False
            
        # Get available tools
        tools_response = self._make_request("tools/list")
        if tools_response.result and "tools" in tools_response.result:
            self.tools = [
                Tool(
                    name=tool["name"],
                    description=tool["description"],
                    inputSchema=tool["inputSchema"]
                )
                for tool in tools_response.result["tools"]
            ]
        
        return True
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a specific tool on the MCP server"""
        response = self._make_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if response.error:
            print(f"Tool call failed: {response.error}")
            return None
            
        return response.result
    
    def get_available_tools(self) -> List[Tool]:
        """Get list of available tools"""
        return self.tools