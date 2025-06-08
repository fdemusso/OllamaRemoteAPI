"""
API REST per Ollama - Modulo principale dell'applicazione.

Questo modulo implementa l'API REST per interfacciarsi con Ollama,
fornendo endpoint per la generazione di testo, chat, gestione modelli
e operazioni di controllo.

Autore: API Ollama Team
Versione: 1.0.0
"""

import logging
import subprocess
from typing import Dict, Any, Optional
import sys
import os
import time
from collections import defaultdict, deque

# Aggiungi la cartella parent al path per importare config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
from dotenv import load_dotenv

# Importa configurazione e utilities
from config.settings import config
from src.utils import (
    get_local_ip, validate_json_payload, log_request_info,
    create_success_response, create_error_response,
    validate_model_name, format_file_size, health_check_ollama
)

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# === CONFIGURAZIONE LOGGING ===
def setup_logging():
    """Configura il sistema di logging dell'applicazione."""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format=config.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            *([logging.FileHandler(config.LOG_FILE)] if config.LOG_FILE else [])
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

# === INIZIALIZZAZIONE FLASK ===
app = Flask(__name__)

# Configurazione CORS
CORS(app, 
     origins=config.get_cors_origins_list(),
     methods=config.CORS_METHODS.split(','))

# Rate limiting storage (in produzione si userebbe Redis)
rate_limit_storage = defaultdict(lambda: deque())

# === MIDDLEWARE DI SICUREZZA ===
@app.before_request
def security_middleware():
    """
    Middleware di sicurezza applicato a tutte le richieste.
    
    Controlla l'autenticazione API key, gli IP consentiti e il rate limiting se configurati.
    """
    # Salta il controllo per l'endpoint di health check
    if request.path == '/health':
        return
    
    # Rate limiting (se abilitato)
    if config.RATE_LIMIT_ENABLED:
        client_ip = request.remote_addr
        current_time = time.time()
        
        # Pulisci le richieste più vecchie di 60 secondi
        request_times = rate_limit_storage[client_ip]
        while request_times and current_time - request_times[0] > 60:
            request_times.popleft()
        
        # Controlla se ha superato il limite
        if len(request_times) >= config.RATE_LIMIT_PER_MINUTE:
            logger.warning(f"Rate limit superato per IP: {client_ip}")
            return jsonify(create_error_response(
                f"Rate limit superato: massimo {config.RATE_LIMIT_PER_MINUTE} richieste per minuto",
                "RATE_LIMIT_EXCEEDED"
            )), 429
        
        # Aggiungi la richiesta corrente
        request_times.append(current_time)
    
    # Controllo IP consentiti (se configurato)
    allowed_ips = config.get_allowed_ips_list()
    if allowed_ips and request.remote_addr not in allowed_ips:
        logger.warning(f"Accesso negato per IP: {request.remote_addr}")
        return jsonify(create_error_response(
            "Accesso negato: IP non autorizzato",
            "UNAUTHORIZED_IP"
        )), 403
    
    # Controllo API key (se configurata)
    if config.API_KEY:
        provided_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if provided_key != config.API_KEY:
            logger.warning(f"API key non valida da IP: {request.remote_addr}")
            return jsonify(create_error_response(
                "API key mancante o non valida",
                "INVALID_API_KEY"
            )), 401


# === ENDPOINT HEALTH CHECK ===
@app.route('/health', methods=['GET'])
@log_request_info
def health_check():
    """
    Endpoint per verificare lo stato dell'API e dei servizi.
    
    Returns:
        JSON: Stato dell'API, informazioni del server e endpoint disponibili
    """
    local_ip = get_local_ip()
    ollama_status = health_check_ollama(config.OLLAMA_BASE_URL)
    
    health_info = {
        "status": "ok",
        "message": "API Ollama funzionante",
        "version": "1.0.0",
        "local_ip": local_ip,
        "server_url": f"http://{local_ip}:{config.PORT}",
        "ollama_status": "online" if ollama_status else "offline",
        "ollama_url": config.OLLAMA_BASE_URL,
        "configuration": {
            "debug": config.DEBUG,
            "api_key_required": bool(config.API_KEY),
            "ip_filtering": bool(config.get_allowed_ips_list()),
            "rate_limiting": {
                "enabled": config.RATE_LIMIT_ENABLED,
                "requests_per_minute": config.RATE_LIMIT_PER_MINUTE if config.RATE_LIMIT_ENABLED else None
            },
            "cors_origins": config.CORS_ORIGINS,
            "log_level": config.LOG_LEVEL
        },
        "endpoints": {
            "health": f"GET http://{local_ip}:{config.PORT}/health",
            "generate": f"POST http://{local_ip}:{config.PORT}/generate",
            "chat": f"POST http://{local_ip}:{config.PORT}/chat",
            "list": f"GET http://{local_ip}:{config.PORT}/list",
            "ps": f"GET http://{local_ip}:{config.PORT}/ps",
            "stop": f"POST http://{local_ip}:{config.PORT}/stop",
            "pull": f"POST http://{local_ip}:{config.PORT}/pull"
        }
    }
    
    return jsonify(health_info)


# === ENDPOINT GENERAZIONE TESTO ===
@app.route('/generate', methods=['POST'])
@log_request_info
@validate_json_payload(['model', 'prompt'])
def generate_response():
    """
    Endpoint per generare testo utilizzando un modello specifico.
    
    Payload JSON richiesto:
    {
        "model": "nome_modello",
        "prompt": "testo_del_prompt",
        "stream": false (opzionale),
        "options": {} (opzionale)
    }
    
    Returns:
        JSON: Risposta generata dal modello con metadati
    """
    try:
        data = request.get_json()
        
        model = data.get('model')
        prompt = data.get('prompt')
        stream = data.get('stream', False)
        options = data.get('options', {})
        
        # Validazione del nome del modello
        if not validate_model_name(model):
            return jsonify(create_error_response(
                "Nome del modello non valido",
                "INVALID_MODEL_NAME"
            )), 400
        
        logger.info(f"Generazione testo con modello: {model}")
        
        # Chiamata a Ollama con timeout configurato
        response = ollama.generate(
            model=model,
            prompt=prompt,
            stream=stream,
            options={**options, 'timeout': config.OLLAMA_TIMEOUT}
        )
        
        # Formatta la risposta
        result = {
            "model": model,
            "response": response['response'],
            "done": response.get('done', True),
            "context": response.get('context'),
            "total_duration": response.get('total_duration'),
            "load_duration": response.get('load_duration'),
            "prompt_eval_count": response.get('prompt_eval_count'),
            "prompt_eval_duration": response.get('prompt_eval_duration'),
            "eval_count": response.get('eval_count'),
            "eval_duration": response.get('eval_duration')
        }
        
        return jsonify(create_success_response(result, "Testo generato con successo"))
        
    except ollama.ResponseError as e:
        error_msg = f"Errore del modello Ollama: {str(e)}"
        logger.error(error_msg)
        return jsonify(create_error_response(error_msg, "OLLAMA_ERROR")), 500
    except Exception as e:
        error_msg = f"Errore interno durante la generazione: {str(e)}"
        logger.error(error_msg)
        return jsonify(create_error_response(error_msg, "INTERNAL_ERROR")), 500


# === ENDPOINT CHAT ===
@app.route('/chat', methods=['POST'])
@log_request_info
@validate_json_payload(['model', 'messages'])
def chat():
    """
    Endpoint per conversazioni chat con un modello.
    
    Payload JSON richiesto:
    {
        "model": "nome_modello",
        "messages": [
            {"role": "user", "content": "messaggio"},
            {"role": "assistant", "content": "risposta"}
        ],
        "stream": false (opzionale),
        "options": {} (opzionale)
    }
    
    Returns:
        JSON: Risposta del modello in formato chat
    """
    try:
        data = request.get_json()
        
        model = data.get('model')
        messages = data.get('messages')
        stream = data.get('stream', False)
        options = data.get('options', {})
        
        # Validazione del nome del modello
        if not validate_model_name(model):
            return jsonify(create_error_response(
                "Nome del modello non valido",
                "INVALID_MODEL_NAME"
            )), 400
        
        # Validazione formato messaggi
        if not isinstance(messages, list) or not messages:
            return jsonify(create_error_response(
                "I messaggi devono essere una lista non vuota",
                "INVALID_MESSAGES_FORMAT"
            )), 400
        
        logger.info(f"Chat con modello: {model}, messaggi: {len(messages)}")
        
        # Chiamata chat a Ollama
        response = ollama.chat(
            model=model,
            messages=messages,
            stream=stream,
            options={**options, 'timeout': config.OLLAMA_TIMEOUT}
        )
        
        # Formatta la risposta
        result = {
            "model": model,
            "message": response['message'],
            "done": response.get('done', True),
            "total_duration": response.get('total_duration'),
            "load_duration": response.get('load_duration'),
            "prompt_eval_count": response.get('prompt_eval_count'),
            "prompt_eval_duration": response.get('prompt_eval_duration'),
            "eval_count": response.get('eval_count'),
            "eval_duration": response.get('eval_duration')
        }
        
        return jsonify(create_success_response(result, "Chat completata con successo"))
        
    except ollama.ResponseError as e:
        error_msg = f"Errore del modello Ollama: {str(e)}"
        logger.error(error_msg)
        return jsonify(create_error_response(error_msg, "OLLAMA_ERROR")), 500
    except Exception as e:
        error_msg = f"Errore interno durante la chat: {str(e)}"
        logger.error(error_msg)
        return jsonify(create_error_response(error_msg, "INTERNAL_ERROR")), 500


# === ENDPOINT LISTA MODELLI ===
@app.route('/list', methods=['GET'])
@log_request_info
def list_models():
    """
    Endpoint per ottenere la lista dei modelli disponibili.
    
    Returns:
        JSON: Lista dei modelli con informazioni dettagliate
    """
    try:
        logger.info("Recupero lista modelli")
        
        # Ottieni la lista dei modelli da Ollama
        models_response = ollama.list()
        models = models_response.get('models', [])
        
        # Arricchisci le informazioni sui modelli
        enriched_models = []
        for model in models:
            enriched_model = {
                "name": model.get('name'),
                "model": model.get('model'),
                "size": model.get('size', 0),
                "size_formatted": format_file_size(model.get('size', 0)),
                "digest": model.get('digest'),
                "modified_at": model.get('modified_at'),
                "details": model.get('details', {})
            }
            enriched_models.append(enriched_model)
        
        result = {
            "models": enriched_models,
            "total_count": len(enriched_models)
        }
        
        return jsonify(create_success_response(result, "Lista modelli ottenuta con successo"))
        
    except Exception as e:
        error_msg = f"Errore nel recuperare la lista dei modelli: {str(e)}"
        logger.error(error_msg)
        return jsonify(create_error_response(error_msg, "LIST_MODELS_ERROR")), 500


# === ENDPOINT STATUS PROCESSI ===
@app.route('/ps', methods=['GET'])
@log_request_info
def process_status():
    """
    Endpoint per vedere i processi Ollama in esecuzione.
    
    Returns:
        JSON: Lista dei processi attivi con informazioni dettagliate
    """
    try:
        logger.info("Recupero status processi Ollama")
        
        # Esegui il comando ollama ps
        result = subprocess.run(['ollama', 'ps'], 
                              capture_output=True, 
                              text=True, 
                              check=True,
                              timeout=10)
        
        # Processa l'output
        output_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
        processes = []
        
        # Salta la riga di header se presente
        for line in output_lines[1:] if len(output_lines) > 1 else []:
            if line.strip():
                parts = line.split()
                if len(parts) >= 4:
                    processes.append({
                        "name": parts[0],
                        "id": parts[1],
                        "size": parts[2],
                        "processor": parts[3],
                        "until": " ".join(parts[4:]) if len(parts) > 4 else ""
                    })
        
        result_data = {
            "raw_output": result.stdout,
            "processes": processes,
            "total_processes": len(processes)
        }
        
        return jsonify(create_success_response(result_data, "Status processi ottenuto con successo"))
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Errore comando ollama ps: {str(e)}"
        logger.error(error_msg)
        return jsonify(create_error_response(error_msg, "OLLAMA_PS_ERROR")), 500
    except subprocess.TimeoutExpired:
        error_msg = "Timeout durante l'esecuzione di ollama ps"
        logger.error(error_msg)
        return jsonify(create_error_response(error_msg, "OLLAMA_PS_TIMEOUT")), 500
    except Exception as e:
        error_msg = f"Errore interno durante ollama ps: {str(e)}"
        logger.error(error_msg)
        return jsonify(create_error_response(error_msg, "INTERNAL_ERROR")), 500


# === ENDPOINT STOP MODELLO ===
@app.route('/stop', methods=['POST'])
@log_request_info
@validate_json_payload(['model'])
def stop_model():
    """
    Endpoint per fermare un modello specifico.
    
    Payload JSON richiesto:
    {
        "model": "nome_modello"
    }
    
    Returns:
        JSON: Conferma dell'operazione di stop
    """
    try:
        data = request.get_json()
        model = data.get('model')
        
        # Validazione del nome del modello
        if not validate_model_name(model):
            return jsonify(create_error_response(
                "Nome del modello non valido",
                "INVALID_MODEL_NAME"
            )), 400
        
        logger.info(f"Fermando modello: {model}")
        
        # Esegui il comando ollama stop
        result = subprocess.run(['ollama', 'stop', model], 
                              capture_output=True, 
                              text=True, 
                              check=True,
                              timeout=30)
        
        result_data = {
            "model": model,
            "output": result.stdout,
            "command_success": True
        }
        
        return jsonify(create_success_response(result_data, f"Modello {model} fermato con successo"))
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Errore nel fermare il modello {model}: {str(e)}"
        logger.error(error_msg)
        return jsonify(create_error_response(error_msg, "OLLAMA_STOP_ERROR")), 500
    except subprocess.TimeoutExpired:
        error_msg = f"Timeout durante l'arresto del modello {model}"
        logger.error(error_msg)
        return jsonify(create_error_response(error_msg, "OLLAMA_STOP_TIMEOUT")), 500
    except Exception as e:
        error_msg = f"Errore interno durante l'arresto: {str(e)}"
        logger.error(error_msg)
        return jsonify(create_error_response(error_msg, "INTERNAL_ERROR")), 500


# === ENDPOINT PULL MODELLO ===
@app.route('/pull', methods=['POST'])
@log_request_info
@validate_json_payload(['model'])
def pull_model():
    """
    Endpoint per scaricare un nuovo modello.
    
    Payload JSON richiesto:
    {
        "model": "nome_modello"
    }
    
    Returns:
        JSON: Stato del download del modello
    """
    try:
        data = request.get_json()
        model = data.get('model')
        
        # Validazione del nome del modello
        if not validate_model_name(model):
            return jsonify(create_error_response(
                "Nome del modello non valido",
                "INVALID_MODEL_NAME"
            )), 400
        
        logger.info(f"Scaricando modello: {model}")
        
        # Usa la libreria ollama per il pull con timeout
        ollama.pull(model, timeout=config.OLLAMA_TIMEOUT)
        
        result_data = {
            "model": model,
            "download_success": True
        }
        
        return jsonify(create_success_response(result_data, f"Modello {model} scaricato con successo"))
        
    except ollama.ResponseError as e:
        error_msg = f"Errore nel scaricare il modello {model}: {str(e)}"
        logger.error(error_msg)
        return jsonify(create_error_response(error_msg, "OLLAMA_PULL_ERROR")), 500
    except Exception as e:
        error_msg = f"Errore interno durante il download: {str(e)}"
        logger.error(error_msg)
        return jsonify(create_error_response(error_msg, "INTERNAL_ERROR")), 500


# === GESTIONE ERRORI GLOBALI ===
@app.errorhandler(404)
def not_found(error):
    """Gestisce gli errori 404."""
    return jsonify(create_error_response(
        "Endpoint non trovato",
        "ENDPOINT_NOT_FOUND"
    )), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Gestisce gli errori 405."""
    return jsonify(create_error_response(
        "Metodo HTTP non consentito",
        "METHOD_NOT_ALLOWED"
    )), 405


@app.errorhandler(500)
def internal_server_error(error):
    """Gestisce gli errori 500."""
    logger.error(f"Errore interno del server: {error}")
    return jsonify(create_error_response(
        "Errore interno del server",
        "INTERNAL_SERVER_ERROR"
    )), 500


# === FUNZIONE PRINCIPALE ===
def create_app() -> Flask:
    """
    Factory function per creare l'app Flask.
    
    Returns:
        Flask: Istanza dell'applicazione configurata
    """
    return app


def main():
    """Funzione principale per avviare l'API."""
    # Mostra la configurazione all'avvio
    config.print_config()
    
    # Informazioni di avvio
    local_ip = get_local_ip()
    logger.info("=== AVVIO API OLLAMA ===")
    logger.info(f"Versione: 1.0.0")
    logger.info(f"Server locale: http://localhost:{config.PORT}")
    logger.info(f"Server rete: http://{local_ip}:{config.PORT}")
    logger.info(f"Health check: http://{local_ip}:{config.PORT}/health")
    logger.info("=========================")
    
    # Output per l'utente
    print("\n=== API Ollama avviata! ===")
    print(f"[LOCAL]  http://localhost:{config.PORT}")
    print(f"[REMOTE] http://{local_ip}:{config.PORT}")
    print(f"[TEST]   http://{local_ip}:{config.PORT}/health")
    print(f"[DOC]    Leggi il README.md per la documentazione completa\n")
    
    # Avvia l'applicazione
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )


if __name__ == '__main__':
    main() 