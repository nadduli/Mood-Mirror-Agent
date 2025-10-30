# Mood Mirror A2A Agent

An AI agent that analyzes emotional tone and provides empathetic responses using the A2A protocol.

## Features

- 🤖 **A2A Protocol Compliant** - Works with any A2A platform
- 🎭 **Emotional Analysis** - Detects mood from text
- ❤️ **Empathetic Responses** - Context-aware replies
- 📊 **Mood Artifacts** - Returns structured mood data
- 🚀 **FastAPI Powered** - High performance async API

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

2. Run the agent:
    ```bash
    python main.py
    ```
3. Test the endpoint:
    ```bash
curl -X POST http://localhost:8000/a2a/moodmirror \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{
          "kind": "text",
          "text": "I feel amazing today!"
        }]
      }
    }
  }'
    ```
