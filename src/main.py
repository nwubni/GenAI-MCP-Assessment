#!/usr/bin/env python3
"""
Customer Support Chatbot - Console Interface
A prototype chatbot for computer product support using MCP server integration.
"""

import os
from chatbot import CustomerSupportChatbot

def print_welcome():
    """Print welcome message and instructions"""
    print("=" * 60)
    print("🖥️  COMPUTER PRODUCTS CUSTOMER SUPPORT CHATBOT")
    print("=" * 60)
    print("Welcome! I'm here to help with your computer product issues.")
    print("I can assist with monitors, printers, keyboards, and more.")
    print("\nCommands:")
    print("  - Type your question or describe your issue")
    print("  - 'history' - View conversation history")
    print("  - 'clear' - Clear conversation history")
    print("  - 'tools' - Show available support tools")
    print("  - 'quit' or 'exit' - Exit the chatbot")
    print("-" * 60)

def print_history(chatbot):
    """Print conversation history"""
    history = chatbot.get_conversation_history()
    if not history:
        print("No conversation history yet.")
        return
    
    print("\n📋 Conversation History:")
    print("-" * 40)
    for i, message in enumerate(history, 1):
        role = "You" if message.role.value == "user" else "Bot"
        print(f"{i}. {role}: {message.content}")
    print("-" * 40)

def main():
    """Main application entry point"""
    # Get MCP server URL from environment or use default
    mcp_server_url = os.getenv("MCP_SERVER_URL", "https://vipfapwm3x.us-east-1.awsapprunner.com/mcp")
    
    print_welcome()
    
    # Initialize chatbot
    print("🔄 Initializing connection to support system...")
    chatbot = CustomerSupportChatbot(mcp_server_url)
    
    if not chatbot.initialize():
        print("⚠️  Warning: Could not connect to MCP server. Running in offline mode.")
        print("Some advanced features may not be available.")
    else:
        print("✅ Connected to support system successfully!")
        tools = chatbot.get_available_tools()
        if tools:
            print(f"📋 Available tools: {', '.join(tools)}")
    
    print("\nHow can I help you today? (Type 'quit' to exit)")
    
    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
                
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for using Customer Support! Have a great day!")
                break
            
            if user_input.lower() == 'history':
                print_history(chatbot)
                continue
            
            if user_input.lower() == 'clear':
                chatbot.clear_history()
                print("✅ Conversation history cleared.")
                continue
            
            if user_input.lower() == 'tools':
                tools = chatbot.get_available_tools()
                if tools:
                    print(f"🛠️  Available tools: {', '.join(tools)}")
                else:
                    print("🛠️  No external tools available (offline mode)")
                continue
            
            # Get chatbot response
            print("Bot: ", end="", flush=True)
            response = chatbot.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()