import os
import shutil
import zipfile
import requests
import subprocess
import sys

# --- CONFIGURAZIONE --- #
# L'URL da cui scaricare il file ZIP dell'aggiornamento.
# Dovrai ospitare i tuoi aggiornamenti da qualche parte (es. GitHub Releases, un tuo server)
# e mettere qui il link diretto al file ZIP.
UPDATE_ZIP_URL = "https://github.com/JackoPeru/Misure-mq.zip" # <--- MODIFICA QUESTO

# Nome del file ZIP scaricato
DOWNLOADED_ZIP_FILE = "Misure-mq.zip"

# Directory temporanea per estrarre i file dell'aggiornamento
TEMP_UPDATE_DIR = "temp_update_files"

# File che indicano la versione corrente (opzionale, ma utile)
# Potresti avere un file version.txt nel tuo progetto e nello ZIP di aggiornamento
# per confrontare le versioni prima di aggiornare.
# CURRENT_VERSION_FILE = "version.txt"

# File e directory da escludere dalla sovrascrittura (es. database, configurazioni utente)
EXCLUDE_FROM_OVERWRITE = ["preventivi.db", ".venv", "updater.py", DOWNLOADED_ZIP_FILE, TEMP_UPDATE_DIR, "__pycache__"]
# --- FINE CONFIGURAZIONE --- #

def get_script_directory():
    """Restituisce la directory in cui si trova lo script updater.py."""
    return os.path.dirname(os.path.realpath(__file__))

def download_update(url, download_path):
    """Scarica il file di aggiornamento dall'URL specificato."""
    print(f"Download dell'aggiornamento da {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Solleva un'eccezione per errori HTTP
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download completato.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Errore durante il download: {e}")
        return False

def extract_update(zip_path, extract_to_dir):
    """Estrae il file ZIP dell'aggiornamento."""
    print(f"Estrazione dell'aggiornamento in {extract_to_dir}...")
    try:
        os.makedirs(extract_to_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_dir)
        print("Estrazione completata.")
        return True
    except zipfile.BadZipFile:
        print("Errore: Il file scaricato non è un file ZIP valido.")
        return False
    except Exception as e:
        print(f"Errore durante l'estrazione: {e}")
        return False

def backup_existing_files(project_root, backup_dir_name="backup_old_version"):
    """Crea un backup dei file esistenti (esclusi quelli in EXCLUDE_FROM_OVERWRITE)."""
    backup_path = os.path.join(project_root, backup_dir_name)
    if os.path.exists(backup_path):
        print(f"Rimozione del backup precedente in {backup_path}...")
        shutil.rmtree(backup_path)
    os.makedirs(backup_path, exist_ok=True)
    print(f"Creazione del backup in {backup_path}...")
    
    copied_count = 0
    for item in os.listdir(project_root):
        source_item_path = os.path.join(project_root, item)
        if item in EXCLUDE_FROM_OVERWRITE or item == backup_dir_name:
            continue
        
        destination_item_path = os.path.join(backup_path, item)
        try:
            if os.path.isfile(source_item_path):
                shutil.copy2(source_item_path, destination_item_path)
                copied_count += 1
            elif os.path.isdir(source_item_path):
                shutil.copytree(source_item_path, destination_item_path, dirs_exist_ok=True)
                copied_count += 1
        except Exception as e:
            print(f"  Attenzione: Impossibile eseguire il backup di {item}: {e}")
    print(f"Backup di {copied_count} elementi completato.")

def apply_update(update_source_dir, project_root):
    """Applica i file aggiornati dalla directory sorgente alla root del progetto."""
    print("Applicazione dell'aggiornamento...")
    copied_count = 0
    updated_requirements = False

    for item_name in os.listdir(update_source_dir):
        source_item_path = os.path.join(update_source_dir, item_name)
        destination_item_path = os.path.join(project_root, item_name)

        if item_name in EXCLUDE_FROM_OVERWRITE:
            print(f"  Ignorato {item_name} (in lista di esclusione).")
            continue

        try:
            if os.path.isdir(source_item_path):
                # Rimuovi la directory di destinazione se esiste, poi copia
                if os.path.exists(destination_item_path):
                    print(f"  Rimozione directory esistente: {destination_item_path}")
                    shutil.rmtree(destination_item_path)
                shutil.copytree(source_item_path, destination_item_path)
                print(f"  Copiata directory: {item_name}")
            elif os.path.isfile(source_item_path):
                shutil.copy2(source_item_path, destination_item_path)
                print(f"  Copiato file: {item_name}")
            
            copied_count += 1
            if item_name == "requirements.txt":
                updated_requirements = True
        except Exception as e:
            print(f"  Errore durante la copia di {item_name}: {e}")
            
    print(f"Aggiornamento di {copied_count} elementi applicato.")
    return updated_requirements

def update_dependencies(project_root):
    """Esegue pip install -r requirements.txt."""
    print("Aggiornamento delle dipendenze...")
    requirements_path = os.path.join(project_root, "requirements.txt")
    if not os.path.exists(requirements_path):
        print("File requirements.txt non trovato. Salto aggiornamento dipendenze.")
        return

    try:
        # Trova l'eseguibile Python corretto (quello che esegue questo script)
        python_executable = sys.executable
        subprocess.check_call([python_executable, "-m", "pip", "install", "-r", requirements_path])
        print("Dipendenze aggiornate con successo.")
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'aggiornamento delle dipendenze: {e}")
    except FileNotFoundError:
        print("Errore: Comando 'pip' non trovato. Assicurati che Python e pip siano nel PATH.")

def cleanup(zip_file, temp_dir):
    """Pulisce i file temporanei."""
    print("Pulizia dei file temporanei...")
    if os.path.exists(zip_file):
        os.remove(zip_file)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    print("Pulizia completata.")

def main():
    project_root = get_script_directory()
    download_zip_target = os.path.join(project_root, DOWNLOADED_ZIP_FILE)
    temp_extract_target = os.path.join(project_root, TEMP_UPDATE_DIR)

    print("--- Inizio Procedura di Aggiornamento ---")

    # 1. (Opzionale) Chiedere conferma all'utente
    # confirm = input("Vuoi cercare e installare gli aggiornamenti? (s/n): ")
    # if confirm.lower() != 's':
    #     print("Aggiornamento annullato dall'utente.")
    #     return

    # 2. Scarica l'aggiornamento
    if not download_update(UPDATE_ZIP_URL, download_zip_target):
        print("Impossibile scaricare l'aggiornamento. Procedura interrotta.")
        cleanup(download_zip_target, temp_extract_target)
        return

    # 3. Estrai l'aggiornamento
    if not extract_update(download_zip_target, temp_extract_target):
        print("Impossibile estrarre l'aggiornamento. Procedura interrotta.")
        cleanup(download_zip_target, temp_extract_target)
        return

    # 4. Backup dei file esistenti (MOLTO IMPORTANTE)
    backup_existing_files(project_root)

    # 5. Applica l'aggiornamento
    # Assumiamo che lo ZIP contenga una struttura di file che rispecchia la root del progetto
    # Se lo ZIP contiene una cartella principale (es. 'my_app_v1.1'), dovrai modificare
    # update_source_dir per puntare a quella cartella interna.
    # Esempio: update_source_dir = os.path.join(temp_extract_target, 'nome_cartella_nello_zip')
    update_source_dir = temp_extract_target 
    requirements_updated = apply_update(update_source_dir, project_root)

    # 6. Aggiorna le dipendenze se requirements.txt è stato modificato
    if requirements_updated:
        update_dependencies(project_root)
    else:
        print("Nessun aggiornamento per requirements.txt rilevato.")

    # 7. Pulizia
    cleanup(download_zip_target, temp_extract_target)

    print("--- Procedura di Aggiornamento Completata ---")
    print("Si consiglia di riavviare l'applicazione.")

if __name__ == "__main__":
    main()