import requests
import json

# URL base dell'API
BASE_URL = "http://localhost:5000"

def test_health():
    """Test dell'endpoint health"""
    print("🔍 Test Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Versione API: {result.get('version', 'N/A')}")
    print(f"Status Ollama: {result.get('ollama_status', 'N/A')}")
    print(f"IP Server: {result.get('local_ip', 'N/A')}")
    print()

def test_list_models():
    """Test dell'endpoint list"""
    print("🔍 Test Lista Modelli...")
    response = requests.get(f"{BASE_URL}/list")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        data = result.get('data', {})
        models = data.get('models', [])
        print(f"Modelli trovati: {data.get('total_count', 0)}")
        for model in models[:3]:  # Mostra solo i primi 3
            name = model.get('name', 'Unknown')
            size = model.get('size_formatted', 'N/A')
            print(f"  - {name} ({size})")
        return models
    else:
        print(f"Errore: {response.json()}")
        return []
    print()

def test_ps():
    """Test dell'endpoint ps"""
    print("🔍 Test Status Processi...")
    response = requests.get(f"{BASE_URL}/ps")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        data = result.get('data', {})
        processes = data.get('processes', [])
        print(f"Processi attivi: {data.get('total_processes', 0)}")
        if processes:
            for proc in processes:
                print(f"  - {proc.get('name', 'N/A')} (ID: {proc.get('id', 'N/A')})")
    else:
        print(f"Errore: {response.json()}")
    print()

def test_generate(model_name="llama2"):
    """Test dell'endpoint generate"""
    print(f"🔍 Test Generazione con modello {model_name}...")
    
    data = {
        "model": model_name,
        "prompt": "Scrivi solo 'Test riuscito!' come risposta"
    }
    
    response = requests.post(f"{BASE_URL}/generate", 
                           headers={"Content-Type": "application/json"},
                           data=json.dumps(data))
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            data = result.get('data', {})
            print(f"Modello: {data.get('model')}")
            print(f"Risposta: {data.get('response', '')[:200]}...")
            print("✅ Generazione completata con successo")
        else:
            print(f"❌ Errore API: {result}")
    else:
        print(f"❌ Errore HTTP: {response.json()}")
    print()

def test_chat(model_name="llama2"):
    """Test dell'endpoint chat"""
    print(f"🔍 Test Chat con modello {model_name}...")
    
    data = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": "Rispondi solo 'Ciao!' e nient'altro"}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/chat", 
                           headers={"Content-Type": "application/json"},
                           data=json.dumps(data))
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            data = result.get('data', {})
            print(f"Modello: {data.get('model')}")
            message = data.get('message', {})
            print(f"Risposta: {message.get('content', '')[:200]}...")
            print("✅ Chat completata con successo")
        else:
            print(f"❌ Errore API: {result}")
    else:
        print(f"❌ Errore HTTP: {response.json()}")
    print()

def test_pull(model_name="tinyllama"):
    """Test dell'endpoint pull (usa un modello piccolo per il test)"""
    print(f"🔍 Test Pull modello {model_name}...")
    
    data = {
        "model": model_name
    }
    
    response = requests.post(f"{BASE_URL}/pull", 
                           headers={"Content-Type": "application/json"},
                           data=json.dumps(data))
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_stop(model_name="llama2"):
    """Test dell'endpoint stop"""
    print(f"🔍 Test Stop modello {model_name}...")
    
    data = {
        "model": model_name
    }
    
    response = requests.post(f"{BASE_URL}/stop", 
                           headers={"Content-Type": "application/json"},
                           data=json.dumps(data))
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            print("✅ Modello fermato con successo")
        else:
            print(f"❌ Errore: {result}")
    else:
        print(f"❌ Errore HTTP: {response.json()}")
    print()

def main():
    """Esegue tutti i test"""
    print("🚀 Test API Ollama Riorganizzata\n")
    
    try:
        # Test di base
        test_health()
        models = test_list_models()
        test_ps()
        
        # Verifica se ci sono modelli disponibili
        if models:
            # Prendi il primo modello disponibile per i test
            first_model = models[0]['name']
            print(f"📋 Uso il modello {first_model} per i test di generazione\n")
            
            test_generate(first_model)
            test_chat(first_model)
            test_stop(first_model)
        else:
            print("⚠️  Nessun modello disponibile per i test di generazione")
        
        # Test pull (commentato perché può richiedere tempo)
        # test_pull("tinyllama")
        
        print("✅ Tutti i test completati!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Errore: Impossibile connettersi all'API.")
        print("Assicurati che l'API sia in esecuzione su http://localhost:5000")
    except Exception as e:
        print(f"❌ Errore durante i test: {e}")

if __name__ == "__main__":
    main() 