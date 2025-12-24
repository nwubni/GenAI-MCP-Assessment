""" Customer Support Chatbot for computer products """

import os
from typing import List, Dict, Any, Optional
from schemas import Message, MessageRole
from mcp_client import MCPClient
from openai import OpenAI

class CustomerSupportChatbot:
    """Customer Support Chatbot for computer products"""

    def __init__(self, mcp_server_url: str):
        self.mcp_client = MCPClient(mcp_server_url)
        self.conversation_history: List[Message] = []
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=api_key) if api_key else None
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
                "common_issues": ["paper jam", "jamming", "poor print quality", "connectivity", "ink/toner", "printer"],
                "troubleshooting": {
                    "paper jam": "Turn off printer, remove paper carefully, check for torn pieces",
                    "jamming": "Turn off printer, remove paper carefully, check for torn pieces",
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
        
        # Check if user is asking about available products or pricing
        if any(keyword in user_lower for keyword in ["what products", "what do you have", "list products", "available products", "products do you"]):
            return self._handle_product_query()
        
        # Check for product search queries
        if any(keyword in user_lower for keyword in ["search", "find", "show me", "do you have", "looking for"]) and any(product in user_lower for product in ["monitor", "printer", "keyboard", "mouse", "gaming", "wireless"]):
            return self._handle_product_search(user_input)
        
        # Check for pricing queries
        if any(keyword in user_lower for keyword in ["how much", "price", "cost", "expensive", "cheap"]):
            return self._handle_pricing_query(user_input)
        
        # Check for specific product ID queries (e.g., "Tell me about MON-0001")
        if any(keyword in user_lower for keyword in ["tell me about", "details", "info", "information"]) and any(id_pattern in user_input for id_pattern in ["MON-", "PRI-", "ACC-", "NET-"]):
            return self._handle_product_details(user_input)
        
        # Check for customer authentication queries
        if any(keyword in user_lower for keyword in ["login", "sign in", "authenticate", "verify", "my account", "customer"]) and ("@" in user_input or "pin" in user_lower):
            return self._handle_customer_auth(user_input)
        
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
            print(f"DEBUG: MCP result = {result}")  # Debug line
            
            if result:
                # Handle different response formats
                if isinstance(result, dict):
                    if "content" in result:
                        return f"Here are our available products:\n{result['content']}"
                    elif "result" in result and "content" in result["result"]:
                        return f"Here are our available products:\n{result['result']['content']}"
                    else:
                        # Try to extract any string data
                        for key, value in result.items():
                            if isinstance(value, str) and len(value) > 100:  # Likely product data
                                return f"Here are our available products:\n{value}"
                
                # Fallback to string representation
                products_data = str(result)
                if len(products_data) > 100:  # Has substantial content
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
    
    def _extract_search_terms_with_ai(self, user_input: str) -> List[str]:
        """Use OpenAI to extract search terms from natural language query"""
        if not self.openai_client:
            # Fallback to basic keyword extraction
            user_lower = user_input.lower()
            terms = []
            keywords = ["monitor", "gaming", "keyboard", "wireless", "printer", "mouse", "webcam", "headset", "router", "switch", "modem", "hub", "docking", "cable", "kvm"]
            for keyword in keywords:
                if keyword in user_lower:
                    terms.append(keyword)
            return terms
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract product search terms from user queries. Return only relevant product categories and attributes as a comma-separated list. Focus on: monitors, printers, keyboards, mice, gaming, wireless, mechanical, laser, inkjet, 4K, LED, etc."},
                    {"role": "user", "content": f"Extract search terms from: '{user_input}'"}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            ai_terms = response.choices[0].message.content.strip()
            return [term.strip() for term in ai_terms.split(",") if term.strip()]
            
        except Exception as e:
            print(f"AI extraction error: {e}")
            # Fallback to basic extraction
            user_lower = user_input.lower()
            terms = []
            keywords = ["monitor", "gaming", "keyboard", "wireless", "printer", "mouse"]
            for keyword in keywords:
                if keyword in user_lower:
                    terms.append(keyword)
            return terms

    def _handle_product_search(self, user_input: str) -> str:
        """Handle product search queries using search_products MCP tool with AI enhancement"""
        try:
            # Use AI to extract search terms
            search_terms = self._extract_search_terms_with_ai(user_input)
            
            # Try different search strategies
            search_queries = []
            if search_terms:
                search_queries.append(" ".join(search_terms))  # Combined terms
                search_queries.extend(search_terms[:3])  # Individual terms (max 3)
            search_queries.append(user_input.lower())  # Original query as fallback
            
            for search_query in search_queries:
                result = self.mcp_client.call_tool("search_products", {"query": search_query})
                print(f"DEBUG: Search query='{search_query}', result = {result}")
                
                if result and isinstance(result, dict):
                    if "content" in result and result["content"]:
                        content = result["content"]
                        if isinstance(content, list) and len(content) > 0:
                            text_content = content[0].get("text", "") if isinstance(content[0], dict) else str(content[0])
                            if "No products found" not in text_content and len(text_content) > 20:
                                return f"Found these products matching your search:\n{text_content}"
                    
        except Exception as e:
            print(f"Error searching products: {e}")
        
        return "I can help you search for products. Try asking about monitors, printers, keyboards, or other computer accessories. You can also ask 'What products do you have?' to see our full catalog."
    
    def _handle_pricing_query(self, user_input: str) -> str:
        """Handle pricing queries using search_products MCP tool"""
        try:
            # Extract product type from pricing query
            search_query = user_input.lower()
            result = self.mcp_client.call_tool("search_products", {"query": search_query})
            print(f"DEBUG: Pricing result = {result}")
            
            if result:
                if isinstance(result, dict):
                    for key, value in result.items():
                        if isinstance(value, str) and "price" in value.lower():
                            return f"Here are the pricing details:\n{value}"
                
                products_data = str(result)
                if "price" in products_data.lower() and len(products_data) > 50:
                    return f"Here are the pricing details:\n{products_data}"
                    
        except Exception as e:
            print(f"Error getting pricing: {e}")
        
        return "I can help you with pricing information. Please specify which product you're interested in (monitors, printers, keyboards, etc.)."
    
    def _handle_product_details(self, user_input: str) -> str:
        """Handle specific product detail queries using get_product MCP tool"""
        try:
            # Extract product ID from user input
            import re
            product_id_match = re.search(r'(MON-\d+|PRI-\d+|ACC-\d+|NET-\d+)', user_input)
            if product_id_match:
                product_id = product_id_match.group(1)
                result = self.mcp_client.call_tool("get_product", {"product_id": product_id})
                print(f"DEBUG: Product details result = {result}")
                
                if result:
                    if isinstance(result, dict):
                        for _, value in result.items():
                            if isinstance(value, str) and len(value) > 20:
                                return f"Product Details:\n{value}"
                    
                    product_data = str(result)
                    if len(product_data) > 20:
                        return f"Product Details:\n{product_data}"
                        
        except Exception as e:
            print(f"Error getting product details: {e}")
        
        return "I can provide detailed information about specific products. Please provide a product ID (like MON-0001, PRI-0101, etc.)."
    
    def _handle_customer_auth(self, user_input: str) -> str:
        """Handle customer authentication using verify_customer_pin MCP tool"""
        try:
            # Extract email and PIN from user input
            import re
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', user_input)
            pin_match = re.search(r'\b(\d{4})\b', user_input)
            
            if email_match and pin_match:
                email = email_match.group(1)
                pin = pin_match.group(1)
                
                # Verify customer PIN
                result = self.mcp_client.call_tool("verify_customer_pin", {"email": email, "pin": pin})
                print(f"DEBUG: Customer auth result = {result}")
                
                if result and isinstance(result, dict):
                    # Check if verification was successful
                    if "content" in result:
                        content = result["content"]
                        if isinstance(content, list) and len(content) > 0:
                            text_content = content[0].get("text", "") if isinstance(content[0], dict) else str(content[0])
                            if "verified" in text_content.lower() or "success" in text_content.lower():
                                # Get customer information
                                customer_info = self.mcp_client.call_tool("get_customer", {"email": email})
                                if customer_info:
                                    return f"Welcome back! Authentication successful.\n{text_content}"
                                return f"Authentication successful! Welcome back.\n{text_content}"
                            else:
                                return f"Authentication failed. Please check your email and PIN.\n{text_content}"
                
                return "Authentication failed. Please check your email and PIN and try again."
            else:
                return "Please provide your email address and 4-digit PIN for authentication. Example: 'Login with donaldgarcia@example.net PIN 7912'"
                
        except Exception as e:
            print(f"Error with customer authentication: {e}")
        
        return "I can help you authenticate with your customer account. Please provide your email and 4-digit PIN."
    
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
