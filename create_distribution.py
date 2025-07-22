#!/usr/bin/env python3
"""
Script per creare un pacchetto di distribuzione dell'applicazione Misure-mq
Crea un file ZIP pronto per la distribuzione
"""

import os
import zipfile
import shutil
from datetime import datetime
from pathlib import Path

def create_distribution_package():
    """Crea un pacchetto ZIP per la distribuzione"""
    
    # Verifica che l'eseguibile esista
    exe_path = Path('dist/Misure-mq.exe')
    if not exe_path.exists():
        print("❌ Eseguibile non trovato. Esegui prima il build con build_app.py")
        return False
    
    # Nome del pacchetto con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"Misure-mq_v2.0_{timestamp}.zip"
    
    print(f"📦 Creazione pacchetto di distribuzione: {package_name}")
    
    try:
        with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Aggiungi l'eseguibile
            zipf.write('dist/Misure-mq.exe', 'Misure-mq.exe')
            print("✅ Aggiunto: Misure-mq.exe")
            
            # Aggiungi l'installer
            zipf.write('dist/installer.bat', 'installer.bat')
            print("✅ Aggiunto: installer.bat")
            
            # Aggiungi il README per l'utente finale
            user_readme = """# Misure-mq v2.0 - Applicazione Desktop

## 🚀 Installazione Rapida

1. **Estrai tutti i file** da questo archivio in una cartella
2. **Fai clic destro** su `installer.bat`
3. **Seleziona "Esegui come amministratore"**
4. **Segui le istruzioni** sullo schermo

## 📋 Cosa fa l'installer

- Crea una cartella `Misure-mq` sul desktop
- Copia l'applicazione nella cartella
- Crea un collegamento sul desktop
- L'applicazione è pronta all'uso!

## 🎯 Utilizzo

Dopo l'installazione, troverai:
- **Collegamento sul desktop**: Fai doppio clic per avviare
- **Cartella applicazione**: `%USERPROFILE%\\Desktop\\Misure-mq`

## ✨ Nuove Funzionalità v2.0

- **Calcolo elementi lineari**: Gestione completa di elementi a metro lineare
- **Export/Import dati**: Backup e ripristino di materiali, bordi ed elementi lineari
- **Interfaccia migliorata**: Nuovi manager e dialog per una migliore esperienza utente

## 🔧 Requisiti di Sistema

- Windows 7/8/10/11 (64-bit)
- Nessuna installazione aggiuntiva richiesta
- Tutti i componenti sono inclusi nell'eseguibile

## 🆘 Supporto

In caso di problemi:
1. Assicurati di eseguire l'installer come amministratore
2. Verifica di avere spazio sufficiente sul disco
3. Controlla che l'antivirus non blocchi l'applicazione

## 📝 Note

- L'applicazione è completamente standalone
- Non richiede connessione internet per funzionare
- Tutti i dati sono salvati localmente nel database SQLite incluso

---
**Versione**: 2.0  
**Data**: """ + datetime.now().strftime("%d/%m/%Y") + """  
**Sviluppatore**: JackoPeru
"""
            
            zipf.writestr('README.txt', user_readme)
            print("✅ Aggiunto: README.txt")
            
            # Aggiungi un file di versione
            version_info = f"""Misure-mq Desktop Application
Versione: 2.0
Build: {timestamp}
Piattaforma: Windows 64-bit
Dimensione eseguibile: {exe_path.stat().st_size / (1024*1024):.1f} MB

Funzionalità incluse:
- Calcolo preventivi tradizionali
- Gestione elementi lineari
- Export/Import dati JSON
- Interfaccia utente migliorata
- Database SQLite integrato

Dipendenze incluse:
- Python runtime
- Tkinter GUI
- SQLite database
- OpenPyXL (Excel)
- ReportLab (PDF)
- Requests (HTTP)
"""
            
            zipf.writestr('VERSION.txt', version_info)
            print("✅ Aggiunto: VERSION.txt")
        
        # Statistiche del pacchetto
        package_size = Path(package_name).stat().st_size / (1024*1024)
        print(f"\n🎉 Pacchetto creato con successo!")
        print(f"📁 Nome file: {package_name}")
        print(f"📏 Dimensione: {package_size:.1f} MB")
        print(f"📍 Percorso: {Path(package_name).absolute()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nella creazione del pacchetto: {e}")
        return False

def create_github_release_assets():
    """Crea gli asset per una release GitHub"""
    
    print("\n🐙 Preparazione asset per GitHub Release...")
    
    # Crea una cartella per gli asset
    assets_dir = Path('github_release_assets')
    if assets_dir.exists():
        shutil.rmtree(assets_dir)
    assets_dir.mkdir()
    
    try:
        # Copia l'eseguibile
        shutil.copy2('dist/Misure-mq.exe', assets_dir / 'Misure-mq.exe')
        
        # Crea un ZIP solo con l'eseguibile per download diretto
        with zipfile.ZipFile(assets_dir / 'Misure-mq-executable.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write('dist/Misure-mq.exe', 'Misure-mq.exe')
        
        # Crea il pacchetto completo
        timestamp = datetime.now().strftime("%Y%m%d")
        complete_package = assets_dir / f'Misure-mq-complete-v2.0.zip'
        
        with zipfile.ZipFile(complete_package, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write('dist/Misure-mq.exe', 'Misure-mq.exe')
            zipf.write('dist/installer.bat', 'installer.bat')
            
            # README per GitHub
            github_readme = """# Misure-mq v2.0 - Desktop Application

## Download Options

- **Misure-mq.exe**: Direct executable download
- **Misure-mq-complete-v2.0.zip**: Complete package with installer

## Installation

### Option 1: Direct Run
1. Download `Misure-mq.exe`
2. Run directly (no installation required)

### Option 2: Full Installation
1. Download `Misure-mq-complete-v2.0.zip`
2. Extract all files
3. Run `installer.bat` as administrator

## New Features in v2.0

- Linear elements calculation mode
- Complete linear elements manager
- JSON export/import for materials and edges
- Improved user interface
- Enhanced quote management

## System Requirements

- Windows 7/8/10/11 (64-bit)
- No additional software required
- Standalone executable

## Technical Details

- Built with PyInstaller
- Includes Python runtime
- SQLite database included
- All dependencies bundled

---
For more information, visit: https://github.com/JackoPeru/Misure-mq
"""
            
            zipf.writestr('README.md', github_readme)
        
        print("✅ Asset GitHub creati:")
        for asset in assets_dir.iterdir():
            size_mb = asset.stat().st_size / (1024*1024)
            print(f"  - {asset.name} ({size_mb:.1f} MB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nella creazione degli asset GitHub: {e}")
        return False

def main():
    """Funzione principale"""
    print("📦 Misure-mq Distribution Packager")
    print("=" * 40)
    
    # Verifica che il build sia stato fatto
    if not Path('dist/Misure-mq.exe').exists():
        print("❌ Eseguibile non trovato. Esegui prima:")
        print("   python build_app.py")
        return False
    
    # Crea il pacchetto di distribuzione
    if not create_distribution_package():
        return False
    
    # Crea gli asset per GitHub
    if not create_github_release_assets():
        return False
    
    print("\n🎉 Tutti i pacchetti sono stati creati con successo!")
    print("\nFile pronti per la distribuzione:")
    print("- Misure-mq_v2.0_*.zip (pacchetto utente finale)")
    print("- github_release_assets/ (asset per GitHub Release)")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)