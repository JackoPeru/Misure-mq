#!/usr/bin/env python3
"""
Script per creare l'eseguibile dell'applicazione Misure-mq
Utilizza PyInstaller per generare un file .exe standalone
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Installa PyInstaller se non è presente"""
    try:
        import PyInstaller
        print("✅ PyInstaller già installato")
        return True
    except ImportError:
        print("📦 Installazione PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installato con successo")
            return True
        except subprocess.CalledProcessError:
            print("❌ Errore nell'installazione di PyInstaller")
            return False

def create_spec_file():
    """Crea il file .spec per PyInstaller con configurazioni personalizzate"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('preventivi.db', '.'),
        ('*.py', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'sqlite3',
        'openpyxl',
        'reportlab',
        'xlrd',
        'requests',
        'json',
        'os',
        'sys',
        'threading',
        'datetime',
        'decimal',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Misure-mq',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico' if os.path.exists('app_icon.ico') else None,
)
'''
    
    with open('Misure-mq.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ File .spec creato")

def create_icon():
    """Crea un'icona semplice per l'applicazione"""
    icon_content = '''<svg width="64" height="64" xmlns="http://www.w3.org/2000/svg">
  <rect width="64" height="64" fill="#2E86AB" rx="8"/>
  <text x="32" y="40" font-family="Arial, sans-serif" font-size="24" font-weight="bold" 
        text-anchor="middle" fill="white">M²</text>
  <rect x="8" y="8" width="48" height="8" fill="#A23B72" rx="2"/>
  <rect x="8" y="48" width="48" height="8" fill="#F18F01" rx="2"/>
</svg>'''
    
    with open('app_icon.svg', 'w', encoding='utf-8') as f:
        f.write(icon_content)
    
    print("✅ Icona SVG creata")

def build_executable():
    """Costruisce l'eseguibile usando PyInstaller"""
    print("🔨 Avvio build dell'eseguibile...")
    
    try:
        # Pulisce le directory precedenti
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        
        # Esegue PyInstaller
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name=Misure-mq',
            '--distpath=dist',
            '--workpath=build',
            '--specpath=.',
            'main.py'
        ]
        
        # Aggiunge l'icona se esiste
        if os.path.exists('app_icon.ico'):
            cmd.extend(['--icon=app_icon.ico'])
        
        # Aggiunge i file dati
        cmd.extend([
            '--add-data=preventivi.db;.',
            '--add-data=*.py;.',
        ])
        
        subprocess.check_call(cmd)
        print("✅ Build completato con successo!")
        
        # Verifica che l'eseguibile sia stato creato
        exe_path = Path('dist/Misure-mq.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Eseguibile creato: {exe_path}")
            print(f"📏 Dimensione: {size_mb:.1f} MB")
            return True
        else:
            print("❌ Eseguibile non trovato")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore durante il build: {e}")
        return False

def create_installer_script():
    """Crea uno script batch per l'installazione"""
    installer_content = '''@echo off
echo ========================================
echo    Misure-mq - Installer
echo ========================================
echo.

set "INSTALL_DIR=%USERPROFILE%\\Desktop\\Misure-mq"
set "SHORTCUT_PATH=%USERPROFILE%\\Desktop\\Misure-mq.lnk"

echo Creazione directory di installazione...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo Copia dell'eseguibile...
copy "Misure-mq.exe" "%INSTALL_DIR%\\" >nul

echo Creazione collegamento sul desktop...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\Misure-mq.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Applicazione per calcolo preventivi'; $Shortcut.Save()"

echo.
echo ✅ Installazione completata!
echo.
echo L'applicazione è stata installata in: %INSTALL_DIR%
echo È stato creato un collegamento sul desktop.
echo.
pause
'''
    
    with open('dist/installer.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print("✅ Script installer creato")

def main():
    """Funzione principale del builder"""
    print("🚀 Misure-mq Desktop App Builder")
    print("=" * 40)
    
    # Verifica che siamo nella directory corretta
    if not os.path.exists('main.py'):
        print("❌ File main.py non trovato. Assicurati di essere nella directory del progetto.")
        return False
    
    # Installa PyInstaller
    if not install_pyinstaller():
        return False
    
    # Crea l'icona
    create_icon()
    
    # Crea il file spec
    create_spec_file()
    
    # Costruisce l'eseguibile
    if not build_executable():
        return False
    
    # Crea l'installer
    create_installer_script()
    
    print("\n🎉 Build completato con successo!")
    print("\nFile generati:")
    print("- dist/Misure-mq.exe (eseguibile principale)")
    print("- dist/installer.bat (script di installazione)")
    print("\nPer distribuire l'applicazione:")
    print("1. Copia la cartella 'dist' sul computer di destinazione")
    print("2. Esegui 'installer.bat' come amministratore")
    print("3. L'applicazione sarà installata e pronta all'uso")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)