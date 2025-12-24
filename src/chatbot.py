""" Customer Support Chatbot for computer products """

import os
from typing import List, Dict, Any, Optional
from schemas import Message, MessageRole
from mcp_client import MCPClient

class CustomerSupportChatbot:
    """Customer Support Chatbot for computer products"""

    def __init__(self, mcp_server_url: str):
        self.mcp_client = MCPClient(mcp_server_url)
        self.conversation_history: List[Message] = []
        self.product_knowledge = {
            "monitors": {
                "common_issues": ["no display", "flickering", "dead pixels", "color issues"],
                "troubleshooting": {
                    "no display": "Check power cable, video cable connections, and try different input source",
                    "flickering": "Check refresh rate settings and cable connections",
                    "dead pixels": "Try pixel fixing software or contact warranty support",
                    "color issues": "Calibrate display settings or check color profile"
                }
            },
            "printers": {
                "common_issues": ["paper jam", "poor print quality", "connectivity", "ink/toner"],
                "troubleshooting": {
                    "paper jam": "Turn off printer, remove paper carefully, check for torn pieces",
                    "poor print quality": "Clean print heads, check ink/toner levels, use correct paper type",
                    "connectivity": "Check USB/network connections, restart printer and computer",
                    "ink/toner": "Replace cartridges, ensure they're properly installed"
                }
            },
            "keyboards": {
                "common_issues": ["keys not working", "connectivity", "sticky keys", "backlighting"],
                "troubleshooting": {
                    "keys not working": "Clean keyboard, check connections, try different USB port",
                    "connectivity": "Check wireless receiver, replace batteries, re-pair device",
                    "sticky keys": "Clean with compressed air and isopropyl alcohol",
                    "backlighting": "Check software settings, function key combinations"
                }
            }
        }
        
    def initialize(self) -> bool:
        """Initialize the MCP client connection"""
        return self.mcp_client.initialize()
    
    def get_available_tools(self) -> List[str]:
        """Get list of available MCP tools"""
        tools = self.mcp_client.get_available_tools()
        return [tool.name for tool in tools]
    
    def _find_product_info(self, user_input: str) -> Dict[str, Any]:
        """Find relevant product information based on user input"""
        user_lower = user_input.lower()
        
        for product_type, info in self.product_knowledge.items():
            if product_type in user_lower or any(issue in user_lower for issue in info["common_issues"]):
                return {
                    "product_type": product_type,
                    "relevant_issues": [issue for issue in info["common_issues"] if issue in user_lower],
                    "troubleshooting": info["troubleshooting"]
                }
        
        return {}
    
    def _generate_response(self, user_input: str) -> str:
        """Generate a response based on user input and available tools"""
        user_lower = user_input.lower()
        
        # Check if user is asking about available products
        if any(keyword in user_lower for keyword in ["what products", "what do you have", "list products", "available products", "products do you"]):
            return self._handle_product_query()
        
        # Check for product-specific knowledge first
        product_info = self._find_product_info(user_input)
        
        if product_info:
            response = f"I can help you with {product_info['product_type']} issues. "
            
            if product_info['relevant_issues']:
                issue = product_info['relevant_issues'][0]
                troubleshooting = product_info['troubleshooting'].get(issue, "")
                response += f"For {issue} issues: {troubleshooting}"
            else:
                response += f"Common issues include: {', '.join(product_info['troubleshooting'].keys())}. "
                response += "Could you describe your specific problem?"
        else:
            # Try to use MCP tools if available
            tools = self.get_available_tools()
            if tools:
                response = f"I have access to these support tools: {', '.join(tools)}. "
                response += "Could you provide more details about your computer product issue?"
            else:
                response = "I'm here to help with computer product support (monitors, printers, keyboards, etc.). "
                response += "Could you describe the issue you're experiencing?"
        
        return response
    
    def _handle_product_query(self) -> str:
        """Handle queries about available products using MCP tools"""
        try:
            # Try to get product list from MCP server
            result = self.mcp_client.call_tool("list_products", {})
            if result and "content" in result:
                return f"Here are our available products:\n{result['content']}"
            elif result:
                # Handle different response formats
                products_data = str(result)
                return f"Here are our available products:\n{products_data}"
        except Exception as e:
            print(f"Error fetching products: {e}")
        
        # Fallback to general product categories
        return ("We offer a wide range of computer products including:\n"
                "• Monitors (LCD, LED, Gaming, 4K displays)\n"
                "• Printers (Inkjet, Laser, All-in-one)\n"
                "• Keyboards (Mechanical, Wireless, Gaming)\n"
                "• And many other computer accessories\n\n"
                "What specific product are you looking for or having issues with?")
    
    def _use_mcp_tool(self, tool_name: str, user_input: str) -> Optional[str]:
        """Try to use an MCP tool to process the user's query"""
        try:
            # Simple argument extraction - in a real implementation, this would be more sophisticated
            result = self.mcp_client.call_tool(tool_name, {"query": user_input})
            if result and "content" in result:
                return result["content"]
        except Exception as e:
            print(f"Error using MCP tool {tool_name}: {e}")
        return None
    
    def chat(self, user_input: str) -> str:
        """Main chat interface"""
        # Add user message to history
        self.conversation_history.append(Message(MessageRole.USER, user_input))
        
        # Generate response
        response = self._generate_response(user_input)
        
        # Try to enhance response with MCP tools
        tools = self.get_available_tools()
        if tools and any(keyword in user_input.lower() for keyword in ["help", "support", "problem", "issue"]):
            for tool in tools[:1]:  # Try first available tool
                tool_response = self._use_mcp_tool(tool, user_input)
                if tool_response:
                    response += f"\n\nAdditional information: {tool_response}"
                    break
        
        # Add assistant response to history
        self.conversation_history.append(Message(MessageRole.ASSISTANT, response))
        
        return response
    
    def get_conversation_history(self) -> List[Message]:
        """Get the conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
