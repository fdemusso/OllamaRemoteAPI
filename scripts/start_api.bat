@echo off
echo ========================================
echo   API Ollama - Avvio con Rete Locale
echo ========================================
echo.

REM Verifica se Python è installato
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python non trovato. Installare Python prima di continuare.
    pause
    exit /b 1
)

REM Verifica se Ollama è installato
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama non trovato. Installare Ollama prima di continuare.
    pause
    exit /b 1
)

echo [OK] Python e Ollama trovati
echo.

REM Installa dipendenze se necessario
echo [SETUP] Installazione dipendenze...
pip install -r requirements.txt

echo.
echo [FIREWALL] Configurazione Firewall (richiede privilegi amministratore)
echo Questo permettera l'accesso alla porta 5000 da altri computer della rete.
echo.

REM Aggiunge regola firewall per la porta 5000 (richiede admin)
netsh advfirewall firewall show rule name="Ollama API" >nul 2>&1
if errorlevel 1 (
    echo Aggiunta regola firewall...
    netsh advfirewall firewall add rule name="Ollama API" dir=in action=allow protocol=TCP localport=5000
    if errorlevel 1 (
        echo [WARNING] Impossibile aggiungere regola firewall. Eseguire come amministratore per l'accesso da rete locale.
    ) else (
        echo [OK] Regola firewall aggiunta con successo
    )
) else (
    echo [OK] Regola firewall gia esistente
)

echo.
echo [START] Avvio API Ollama...
echo.
echo [INFO] Consigli:
echo    - L'API sara accessibile da altri computer della rete
echo    - Usa Ctrl+C per fermare il server
echo    - Controlla l'IP mostrato all'avvio per l'accesso remoto
echo.
echo ========================================
echo.

REM Avvia l'API
python app.py

echo.
echo [STOP] API fermata
pause 