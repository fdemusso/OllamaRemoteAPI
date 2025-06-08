# Ollama API

A professional REST API to interface with Ollama and local language models.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API
python app.py
```

The API will be available at:
- **Local**: `http://localhost:5000`
- **Local Network**: `http://[YOUR_MACHINE_IP]:5000`

## 📡 Main Endpoints

- `GET /health` - API status
- `POST /generate` - Text generation
- `POST /chat` - Chat conversations
- `GET /list` - List models
- `POST /pull` - Download models
- `POST /stop` - Stop models
- `GET /ps` - Process status

## 🔧 Configuration

Create a `.env` file in the project root to customize the configuration:

```env
# Server Configuration
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=True

# Ollama Configuration
OLLAMA_HOST=localhost
OLLAMA_PORT=11434

# Security Configuration (optional)
API_KEY=your_secret_api_key
ALLOWED_IPS=192.168.1.100,192.168.1.101

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/api.log
```

## 📚 Documentation

- [**Complete Documentation**](docs/README.md) - Detailed guide
- [**Test Examples**](tests/) - Test scripts and examples
- [**Utility Scripts**](scripts/) - Startup and configuration scripts

## 🏗️ Project Structure

```
IA_API/
├── src/                 # Source code
│   ├── api.py          # Main API
│   ├── utils.py        # Utilities
│   └── __init__.py     # Package init
├── config/             # Configuration
│   └── settings.py     # Settings
├── tests/              # Tests
│   ├── test_api.py     # Local tests
│   └── test_remote_api.py  # Network tests
├── scripts/            # Scripts
│   └── start_api.bat   # Windows startup
├── docs/               # Documentation
│   └── README.md       # Detailed docs
├── app.py              # Entry point
├── requirements.txt    # Dependencies
└── .env.example        # Configuration example
```

## 🔒 Security

The API supports:
- **API Key Authentication** (optional)
- **IP Filtering** (optional)
- **Configurable CORS**
- **Input Validation**
- **Rate Limiting** (configurable)

## 📋 Prerequisites

- Python 3.7+
- Ollama installed and running
- Ollama models downloaded (`ollama pull <model_name>`)

## 🤝 Contributions

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is released under the MIT license. See the LICENSE file for details.

---

**Developed with ❤️ for the Ollama community** 