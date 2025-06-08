# API Ollama

Un'API REST professionale per interfacciarsi con Ollama e i modelli di linguaggio locali.

## 🚀 Avvio Rapido

```bash
# Installa le dipendenze
pip install -r requirements.txt

# Avvia l'API
python app.py
```

L'API sarà disponibile su:
- **Locale**: `http://localhost:5000`
- **Rete locale**: `http://[IP_TUA_MACCHINA]:5000`

## 📡 Endpoint Principali

- `GET /health` - Stato dell'API
- `POST /generate` - Generazione testo
- `POST /chat` - Conversazioni chat
- `GET /list` - Lista modelli
- `POST /pull` - Scarica modelli
- `POST /stop` - Ferma modelli
- `GET /ps` - Status processi

## 🔧 Configurazione

Crea un file `.env` nella root del progetto per personalizzare la configurazione:

```env
# Configurazione Server
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=True

# Configurazione Ollama
OLLAMA_HOST=localhost
OLLAMA_PORT=11434

# Configurazione Sicurezza (opzionale)
API_KEY=your_secret_api_key
ALLOWED_IPS=192.168.1.100,192.168.1.101

# Configurazione Logging
LOG_LEVEL=INFO
LOG_FILE=logs/api.log
```

## 📚 Documentazione

- [**Documentazione Completa**](docs/README.md) - Guida dettagliata
- [**Esempi di Test**](tests/) - Script di test e esempi
- [**Script di Utilità**](scripts/) - Script di avvio e configurazione

## 🏗️ Struttura del Progetto

```
IA_API/
├── src/                 # Codice sorgente
│   ├── api.py          # API principale
│   ├── utils.py        # Utilities
│   └── __init__.py     # Package init
├── config/             # Configurazione
│   └── settings.py     # Impostazioni
├── tests/              # Test
│   ├── test_api.py     # Test locali
│   └── test_remote_api.py  # Test rete
├── scripts/            # Script
│   └── start_api.bat   # Avvio Windows
├── docs/               # Documentazione
│   └── README.md       # Docs dettagliate
├── app.py              # Entry point
├── requirements.txt    # Dipendenze
└── .env.example        # Esempio configurazione
```

## 🔒 Sicurezza

L'API supporta:
- **Autenticazione API Key** (opzionale)
- **Filtraggio IP** (opzionale)
- **CORS configurabile**
- **Validazione input**
- **Rate limiting** (configurabile)

## 📋 Prerequisiti

- Python 3.7+
- Ollama installato e in esecuzione
- Modelli Ollama scaricati (`ollama pull <model_name>`)

## 🤝 Contributi

Benvenuti contributi! Per favore:
1. Fork del repository
2. Crea un branch per la tua feature
3. Commit delle modifiche
4. Push al branch
5. Apri una Pull Request

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file LICENSE per i dettagli.

---

**Developed with ❤️ for the Ollama community** 