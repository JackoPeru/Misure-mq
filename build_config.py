# Configurazione per PyInstaller
# Questo file contiene le impostazioni per la creazione dell'eseguibile

# File da includere nel build
include_files = [
    'preventivi.db',
    'database.py',
    'utils.py',
    'materials_manager.py',
    'edges_manager.py',
    'linear_elements_manager.py',
    'edge_editor_dialog.py',
    'linear_quote_dialog.py',
]

# Moduli nascosti da includere
hidden_imports = [
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
    'urllib.request',
    'urllib.parse',
    'zipfile',
    'tempfile',
    'shutil',
]

# Configurazioni dell'eseguibile
app_config = {
    'name': 'Misure-mq',
    'version': '2.0',
    'description': 'Applicazione per calcolo preventivi con elementi lineari',
    'author': 'JackoPeru',
    'console': False,  # Nasconde la console
    'onefile': True,   # Crea un singolo file eseguibile
    'upx': True,       # Compressione UPX per ridurre dimensioni
}

# Percorsi di esclusione (per ridurre dimensioni)
excludes = [
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'PIL',
    'cv2',
    'tensorflow',
    'torch',
]