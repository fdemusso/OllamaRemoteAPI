import requests
import json
import sys
import argparse

def test_health(base_url):
    """Test dell'endpoint health"""
    print("🔍 Test Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        if result.get('local_ip'):
            print(f"🌐 IP del server: {result['local_ip']}")
        print()
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore connessione: {e}")
        return False

def test_list_models(base_url):
    """Test dell'endpoint list"""
    print("🔍 Test Lista Modelli...")
    try:
        response = requests.get(f"{base_url}/list", timeout=30)
        print(f"Status: {response.status_code}")
        result = response.json()
        if response.status_code == 200:
            # Nuova struttura: data.models
            data = result.get('data', {})
            models = data.get('models', [])
            print(f"Modelli trovati: {len(models)}")
            for model in models[:3]:  # Mostra solo i primi 3
                name = model.get('name', 'Unknown')
                size = model.get('size_formatted', 'N/A')
                print(f"  - {name} ({size})")
        else:
            print(f"Errore: {result}")
        print()
        return response.status_code == 200, models
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore connessione: {e}")
        return False, []

def test_ps(base_url):
    """Test dell'endpoint ps"""
    print("🔍 Test Status Processi...")
    try:
        response = requests.get(f"{base_url}/ps", timeout=10)
        print(f"Status: {response.status_code}")
        result = response.json()
        if response.status_code == 200:
            # Nuova struttura: data.processes
            data = result.get('data', {})
            processes = data.get('processes', [])
            total = data.get('total_processes', 0)
            print(f"Processi attivi: {total}")
            if processes:
                for proc in processes[:3]:  # Mostra solo i primi 3
                    name = proc.get('name', 'N/A')
                    proc_id = proc.get('id', 'N/A')
                    print(f"  - {name} (ID: {proc_id})")
            else:
                print("  Nessun processo in esecuzione")
        else:
            print(f"Errore: {result}")
        print()
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore connessione: {e}")
        return False

def test_generate(base_url, model_name):
    """Test dell'endpoint generate"""
    print(f"🔍 Test Generazione con modello {model_name}...")
    
    data = {
        "model": model_name,
        "prompt": "Scrivi solo 'Test remoto riuscito!' come risposta"
    }
    
    try:
        response = requests.post(f"{base_url}/generate", 
                               headers={"Content-Type": "application/json"},
                               data=json.dumps(data),
                               timeout=60)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                data = result.get('data', {})
                print(f"Modello: {data.get('model')}")
                print(f"Risposta: {data.get('response', '')[:100]}...")
                print("✅ Test generazione completato con successo")
                return True
            else:
                print(f"❌ Errore API: {result}")
        else:
            result = response.json()
            print(f"❌ Errore HTTP: {result}")
        print()
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore connessione: {e}")
        return False

def test_connectivity(ip_address, port=5000):
    """Test di connettività di base"""
    print(f"🔌 Test connettività a {ip_address}:{port}")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip_address, port))
        sock.close()
        if result == 0:
            print("✅ Connessione TCP riuscita")
            return True
        else:
            print(f"❌ Connessione TCP fallita (codice: {result})")
            return False
    except Exception as e:
        print(f"❌ Errore test connettività: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test API Ollama da remoto')
    parser.add_argument('ip', nargs='?', default='localhost', 
                       help='Indirizzo IP del server (default: localhost)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Porta del server (default: 5000)')
    parser.add_argument('--skip-generate', action='store_true',
                       help='Salta il test di generazione (più veloce)')
    
    args = parser.parse_args()
    
    base_url = f"http://{args.ip}:{args.port}"
    
    print("🚀 Test API Ollama da rete locale")
    print(f"🎯 Target: {base_url}")
    print("="*50)
    
    # Test connettività di base
    if not test_connectivity(args.ip, args.port):
        print("\n❌ Test di connettività fallito. Verifica:")
        print("1. Che il server sia avviato")
        print("2. Che l'IP sia corretto")
        print("3. Che non ci siano firewall che bloccano la porta 5000")
        print("4. Che il computer sia sulla stessa rete")
        return
    
    try:
        # Test di base
        if not test_health(base_url):
            print("❌ Health check fallito!")
            return
        
        print("✅ API raggiungibile!")
        
        # Test lista modelli
        list_success, models = test_list_models(base_url)
        
        # Test status processi
        test_ps(base_url)
        
        # Test generazione se richiesto e ci sono modelli
        if not args.skip_generate and list_success and models:
            first_model = models[0]['name']
            print(f"📋 Uso il modello {first_model} per il test di generazione")
            test_generate(base_url, first_model)
        elif not models:
            print("⚠️  Nessun modello disponibile per il test di generazione")
        elif args.skip_generate:
            print("⏭️  Test di generazione saltato (--skip-generate)")
        
        print("✅ Test completati con successo!")
        print(f"\n🌐 L'API è accessibile da: {base_url}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrotti dall'utente")
    except Exception as e:
        print(f"\n❌ Errore durante i test: {e}")

if __name__ == "__main__":
    main() 