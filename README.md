# Customer Support Chatbot - Computer Products

A prototype customer support chatbot for computer products (monitors, printers, keyboards, etc.) that integrates with an MCP (Model Context Protocol) server for enhanced support capabilities.

## Features

- **Console-based interface** - Simple command-line interaction
- **MCP Server Integration** - Connects to external support tools via MCP protocol
- **Built-in Product Knowledge** - Troubleshooting guides for common computer product issues
- **Conversation History** - Track and review chat sessions
- **Offline Mode** - Works even when MCP server is unavailable

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/customer-support-chatbot.git
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment (optional):
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

Run the chatbot from the project root:

```bash
python src/main.py
```

### Available Commands

- Type your question or describe your issue
- `history` - View conversation history
- `clear` - Clear conversation history  
- `tools` - Show available support tools
- `quit` or `exit` - Exit the chatbot

## Example Interactions

```
You: My monitor has no display
Bot: I can help you with monitors issues. For no display issues: Check power cable, video cable connections, and try different input source

You: My printer is jamming
Bot: I can help you with printers issues. For paper jam issues: Turn off printer, remove paper carefully, check for torn pieces
```

## Architecture

- `main.py` - Console interface and main application entry point
- `chatbot.py` - Core chatbot logic with product knowledge
- `mcp_client.py` - MCP protocol client for server communication
- `schemas.py` - Data structures and type definitions

## MCP Server Integration

The chatbot connects to: `MCP_SERVER_URL` in the environment variables.

If the MCP server is unavailable, the chatbot runs in offline mode with built-in product knowledge.