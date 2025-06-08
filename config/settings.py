"""
Configurazione dell'applicazione API Ollama.

Questo modulo gestisce tutte le impostazioni di configurazione
utilizzando variabili d'ambiente con valori di fallback appropriati.
"""

import os
from typing import Optional


class Config:
    """
    Classe di configurazione principale per l'API Ollama.
    
    Utilizza variabili d'ambiente per la configurazione, con valori
    di default appropriati per lo sviluppo locale.
    """
    
    # === CONFIGURAZIONE SERVER ===
    HOST: str = os.getenv('API_HOST', '0.0.0.0')
    PORT: int = int(os.getenv('API_PORT', '5000'))
    DEBUG: bool = os.getenv('API_DEBUG', 'True').lower() == 'true'
    
    # === CONFIGURAZIONE OLLAMA ===
    OLLAMA_HOST: str = os.getenv('OLLAMA_HOST', 'localhost')
    OLLAMA_PORT: int = int(os.getenv('OLLAMA_PORT', '11434'))
    OLLAMA_BASE_URL: str = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
    OLLAMA_TIMEOUT: int = int(os.getenv('OLLAMA_TIMEOUT', '3600'))  # Timeout specifico per Ollama
    
    # === CONFIGURAZIONE LOGGING ===
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = os.getenv('LOG_FORMAT', 
                               '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_FILE: Optional[str] = os.getenv('LOG_FILE')  # None = solo console
    
    # === CONFIGURAZIONE CORS ===
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')
    CORS_METHODS: str = os.getenv('CORS_METHODS', 'GET,POST,PUT,DELETE,OPTIONS')
    
    # === CONFIGURAZIONE TIMEOUTS ===
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '60'))  # secondi
    GENERATE_TIMEOUT: int = int(os.getenv('GENERATE_TIMEOUT', '300'))  # secondi
    
    # === CONFIGURAZIONE SICUREZZA ===
    API_KEY: Optional[str] = os.getenv('API_KEY')  # Chiave API opzionale
    ALLOWED_IPS: Optional[str] = os.getenv('ALLOWED_IPS')  # IPs consentiti (CSV)
    
    # === CONFIGURAZIONE RATE LIMITING ===
    RATE_LIMIT_ENABLED: bool = os.getenv('RATE_LIMITING', 'False').lower() == 'true'  # Correzione nome variabile
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    @classmethod
    def validate(cls) -> bool:
        """
        Valida la configurazione e restituisce True se tutto è corretto.
        
        Returns:
            bool: True se la configurazione è valida, False altrimenti
        """
        try:
            # Verifica che le porte siano valide
            if not (1 <= cls.PORT <= 65535):
                print(f"Errore: Porta API non valida: {cls.PORT}")
                return False
                
            if not (1 <= cls.OLLAMA_PORT <= 65535):
                print(f"Errore: Porta Ollama non valida: {cls.OLLAMA_PORT}")
                return False
            
            # Verifica che i timeout siano positivi
            if cls.REQUEST_TIMEOUT <= 0:
                print(f"Errore: Timeout richiesta non valido: {cls.REQUEST_TIMEOUT}")
                return False
                
            if cls.GENERATE_TIMEOUT <= 0:
                print(f"Errore: Timeout generazione non valido: {cls.GENERATE_TIMEOUT}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Errore durante la validazione della configurazione: {e}")
            return False
    
    @classmethod
    def get_allowed_ips_list(cls) -> list:
        """
        Restituisce la lista degli IPs consentiti.
        
        Returns:
            list: Lista degli IPs consentiti, vuota se non specificati
        """
        if cls.ALLOWED_IPS:
            return [ip.strip() for ip in cls.ALLOWED_IPS.split(',')]
        return []
    
    @classmethod
    def get_cors_origins_list(cls) -> list:
        """
        Restituisce la lista delle origini CORS consentite.
        
        Returns:
            list: Lista delle origini CORS, ['*'] se non specificate
        """
        if cls.CORS_ORIGINS == '*':
            return ['*']
        return [origin.strip() for origin in cls.CORS_ORIGINS.split(',')]
    
    @classmethod
    def print_config(cls):
        """Stampa la configurazione attuale (nascondendo dati sensibili)."""
        print("=== CONFIGURAZIONE API OLLAMA ===")
        print(f"Server: {cls.HOST}:{cls.PORT}")
        print(f"Debug: {cls.DEBUG}")
        print(f"Ollama: {cls.OLLAMA_BASE_URL}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print(f"CORS Origins: {cls.CORS_ORIGINS}")
        print(f"API Key: {'*** CONFIGURATA ***' if cls.API_KEY else 'Non configurata'}")
        print(f"Rate Limiting: {cls.RATE_LIMIT_ENABLED}")
        if cls.RATE_LIMIT_ENABLED:
            print(f"Rate Limit: {cls.RATE_LIMIT_PER_MINUTE} req/min")
        print("=" * 35)


# Istanza globale della configurazione
config = Config()

# Valida la configurazione all'importazione
if not config.validate():
    raise ValueError("Configurazione non valida! Controlla le variabili d'ambiente.") 