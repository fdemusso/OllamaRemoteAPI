# Ollama API - Detailed Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [API Endpoints](#api-endpoints)
5. [Security](#security)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

## Overview

This API provides a REST interface to interact with Ollama and local language models. It allows you to:
- Generate text using various models
- Manage chat conversations
- Control Ollama processes
- Download and manage models

## Installation

1. Clone the repository:
```bash
git clone https://github.com/fdemusso/OllamaRemoteAPI.git
cd IA_API
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create configuration file:
```bash
cp .env.example .env
```

4. Start the API:
```bash
python app.py
```

## Configuration

### Environment Variables

Create a `.env` file with the following settings:

```env
# Server Configuration
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=True

# Ollama Configuration
OLLAMA_HOST=localhost
OLLAMA_PORT=11434

# Security (optional)
API_KEY=your_secret_key
ALLOWED_IPS=192.168.1.100,192.168.1.101

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/api.log
```

## API Endpoints

### Health Check
```http
GET /health
```
Returns API status and configuration.

### Text Generation
```http
POST /generate
Content-Type: application/json

{
    "model": "gemma3:12b",
    "prompt": "Your prompt here",
    "stream": false
}
```

### Chat
```http
POST /chat
Content-Type: application/json

{
    "model": "gemma3:12b",
    "messages": [
        {"role": "user", "content": "Hello!"}
    ]
}
```

### Model Management
```http
GET /list
POST /pull
POST /stop
GET /ps
```

## Security

### API Key Authentication
Add the API key to requests:
```http
X-API-Key: your_secret_key
```

### IP Filtering
Configure allowed IPs in `.env`:
```env
ALLOWED_IPS=192.168.1.100,192.168.1.101
```

## Examples

### Python
```python
import requests

API_URL = "http://localhost:5000"
API_KEY = "your_secret_key"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Generate text
response = requests.post(
    f"{API_URL}/generate",
    headers=headers,
    json={
        "model": "gemma3:12b",
        "prompt": "Hello, how are you?"
    }
)
print(response.json())
```

### JavaScript
```javascript
const API_URL = "http://localhost:5000";
const API_KEY = "your_secret_key";

async function generateText() {
    const response = await fetch(`${API_URL}/generate`, {
        method: "POST",
        headers: {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            model: "gemma3:12b",
            prompt: "Hello, how are you?"
        })
    });
    const data = await response.json();
    console.log(data);
}
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if Ollama is running
   - Verify port configuration
   - Check firewall settings

2. **Model Not Found**
   - Ensure model is downloaded: `ollama pull <model_name>`
   - Check model name spelling

3. **Authentication Failed**
   - Verify API key configuration
   - Check IP restrictions

### Logs

Check the logs in `logs/api.log` for detailed error information.

---

For more help, open an issue on GitHub or contact the maintainers. 