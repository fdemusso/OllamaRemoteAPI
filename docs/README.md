# API Ollama

Un'API REST per interfacciarsi con Ollama e i modelli di linguaggio locali.

## Installazione

1. Assicurati di avere Ollama installato e in esecuzione sul tuo sistema
2. Installa le dipendenze Python:

```bash
pip install -r requirements.txt
```

## Avvio

### Avvio Semplice (solo locale)
```bash
python app.py
```

### Avvio con Accesso da Rete Locale (Windows)
```bash
# Eseguire come Amministratore per configurare automaticamente il firewall
start_api.bat
```

### Avvio Manuale con Rete Locale
```bash
python app.py
```

L'API sarà disponibile:
- **Localmente**: `http://localhost:5000`
- **Da rete locale**: `http://[IP_DELLA_MACCHINA]:5000` (mostrato all'avvio)

## Test da Rete Locale

Per testare l'API da un altro computer nella rete locale:

```bash
# Test locale
python test_api.py

# Test da computer remoto (sostituire con l'IP del server)
python test_remote_api.py 192.168.1.100

# Test veloce senza generazione
python test_remote_api.py 192.168.1.100 --skip-generate
```

## Endpoints

### 1. Health Check
- **GET** `/health`
- Verifica lo stato dell'API

```bash
curl http://localhost:5000/health
```

### 2. Generazione Risposta
- **POST** `/generate`
- Genera una risposta usando un modello specifico

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "prompt": "Ciao, come stai?"
  }'
```

### 3. Chat
- **POST** `/chat`
- Conversazione con il modello usando il formato chat

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "messages": [
      {"role": "user", "content": "Ciao, come stai?"}
    ]
  }'
```

### 4. Lista Modelli
- **GET** `/list`
- Ottiene la lista dei modelli disponibili

```bash
curl http://localhost:5000/list
```

### 5. Status Processi
- **GET** `/ps`
- Mostra i processi Ollama in esecuzione

```bash
curl http://localhost:5000/ps
```

### 6. Ferma Modello
- **POST** `/stop`
- Ferma un modello specifico

```bash
curl -X POST http://localhost:5000/stop \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2"
  }'
```

### 7. Scarica Modello
- **POST** `/pull`
- Scarica un nuovo modello

```bash
curl -X POST http://localhost:5000/pull \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2"
  }'
```

## Formati di Risposta

Tutte le risposte sono in formato JSON con la struttura:

```json
{
  "status": "success|error",
  "data": "...",
  "error": "messaggio di errore (se presente)"
}
```

## Prerequisiti

- Python 3.7+
- Ollama installato e configurato
- I modelli desiderati scaricati tramite `ollama pull <model_name>`

## Risoluzione Problemi Rete Locale

Se l'API non è accessibile da altri computer:

1. **Verifica Firewall Windows**:
   ```bash
   # Aggiungi regola manualmente (come Amministratore)
   netsh advfirewall firewall add rule name="Ollama API" dir=in action=allow protocol=TCP localport=5000
   ```

2. **Verifica IP del Server**:
   - Esegui `ipconfig` sul server per trovare l'IP locale
   - Usa l'endpoint `/health` per vedere l'IP rilevato automaticamente

3. **Test Connettività**:
   ```bash
   # Dal computer client, testa la porta
   telnet [IP_SERVER] 5000
   ```

4. **Controlla Configurazione di Rete**:
   - Assicurati che entrambi i computer siano sulla stessa rete
   - Disabilita temporaneamente firewall/antivirus per test
   - Verifica che non ci siano proxy o VPN attive

## Note

- L'API supporta CORS per l'uso da applicazioni web
- I log sono configurati per tracciare le operazioni
- Gli errori sono gestiti e restituiti in formato JSON strutturato
- Il server è configurato per `host='0.0.0.0'` per accesso da rete locale
- L'IP locale viene rilevato automaticamente e mostrato all'avvio 