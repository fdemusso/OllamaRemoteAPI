"""
Modulo utilities per l'API Ollama.

Contiene funzioni di supporto e utility comuni utilizzate
in tutta l'applicazione.
"""

import socket
import logging
from typing import Optional, Dict, Any
from functools import wraps
import time


def get_local_ip() -> str:
    """
    Ottiene l'indirizzo IP locale della macchina.
    
    Utilizza una connessione temporanea verso un server DNS pubblico
    per determinare l'IP locale utilizzato per le connessioni di rete.
    
    Returns:
        str: Indirizzo IP locale o 'localhost' in caso di errore
    """
    try:
        # Crea una connessione temporanea per ottenere l'IP locale
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception as e:
        logging.warning(f"Impossibile determinare l'IP locale: {e}")
        return "localhost"


def validate_json_payload(required_fields: list) -> callable:
    """
    Decorator per validare i payload JSON delle richieste.
    
    Args:
        required_fields (list): Lista dei campi richiesti nel JSON
        
    Returns:
        callable: Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request, jsonify
            
            # Verifica che ci sia un payload JSON
            if not request.is_json:
                return jsonify({
                    "error": "Content-Type deve essere application/json"
                }), 400
            
            data = request.get_json()
            if not data:
                return jsonify({
                    "error": "Payload JSON mancante o non valido"
                }), 400
            
            # Verifica i campi richiesti
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    "error": f"Campi mancanti: {', '.join(missing_fields)}"
                }), 400
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_request_info(func) -> callable:
    """
    Decorator per loggare informazioni sulle richieste HTTP.
    
    Args:
        func: Funzione da decorare
        
    Returns:
        callable: Funzione decorata
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request
        
        logger = logging.getLogger(__name__)
        start_time = time.time()
        
        # Log della richiesta in arrivo
        logger.info(f"[{request.method}] {request.path} - IP: {request.remote_addr}")
        
        try:
            # Esegui la funzione originale
            result = func(*args, **kwargs)
            
            # Log del tempo di esecuzione
            execution_time = time.time() - start_time
            logger.info(f"Richiesta completata in {execution_time:.3f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Errore durante la richiesta (dopo {execution_time:.3f}s): {e}")
            raise
    
    return wrapper


def create_success_response(data: Any, message: str = "Operazione completata") -> Dict[str, Any]:
    """
    Crea una risposta JSON di successo standardizzata.
    
    Args:
        data: Dati da includere nella risposta
        message: Messaggio di successo
        
    Returns:
        Dict[str, Any]: Dizionario con la risposta standardizzata
    """
    return {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": time.time()
    }


def create_error_response(error: str, code: str = "GENERIC_ERROR") -> Dict[str, Any]:
    """
    Crea una risposta JSON di errore standardizzata.
    
    Args:
        error: Messaggio di errore
        code: Codice di errore
        
    Returns:
        Dict[str, Any]: Dizionario con l'errore standardizzato
    """
    return {
        "status": "error",
        "error": error,
        "error_code": code,
        "timestamp": time.time()
    }


def validate_model_name(model_name: str) -> bool:
    """
    Valida il nome di un modello Ollama.
    
    Args:
        model_name: Nome del modello da validare
        
    Returns:
        bool: True se il nome è valido, False altrimenti
    """
    if not model_name or not isinstance(model_name, str):
        return False
    
    # Il nome non deve essere vuoto e non deve contenere caratteri pericolosi
    dangerous_chars = ['/', '\\', '..', '<', '>', '|', '&', ';']
    return len(model_name.strip()) > 0 and not any(char in model_name for char in dangerous_chars)


def safe_int_conversion(value: Any, default: int = 0) -> int:
    """
    Converte un valore in intero in modo sicuro.
    
    Args:
        value: Valore da convertire
        default: Valore di default se la conversione fallisce
        
    Returns:
        int: Valore convertito o default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def format_file_size(size_bytes: int) -> str:
    """
    Formatta una dimensione in bytes in formato leggibile.
    
    Args:
        size_bytes: Dimensione in bytes
        
    Returns:
        str: Dimensione formattata (es. "1.5 GB", "256 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    size_index = 0
    
    while size_bytes >= 1024 and size_index < len(size_names) - 1:
        size_bytes /= 1024.0
        size_index += 1
    
    return f"{size_bytes:.1f} {size_names[size_index]}"


def health_check_ollama(base_url: str, timeout: int = 5) -> bool:
    """
    Verifica se Ollama è raggiungibile.
    
    Args:
        base_url: URL base di Ollama
        timeout: Timeout in secondi
        
    Returns:
        bool: True se Ollama è raggiungibile, False altrimenti
    """
    try:
        import requests
        response = requests.get(f"{base_url}/api/tags", timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False 