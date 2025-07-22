# Misure-mq Desktop App Builder

Questo documento spiega come creare un eseguibile desktop dell'applicazione Misure-mq.

## 🚀 Avvio Rapido

### Metodo 1: Script Automatico (Raccomandato)
```bash
# Esegui il file batch
build.bat
```

### Metodo 2: Script Python
```bash
# Esegui direttamente lo script Python
python build_app.py
```

## 📋 Prerequisiti

- Python 3.7 o superiore
- Tutte le dipendenze dell'applicazione installate
- Connessione internet (per installare PyInstaller se necessario)

## 🔧 Processo di Build

Il builder esegue automaticamente i seguenti passaggi:

1. **Verifica Dipendenze**: Controlla e installa PyInstaller se necessario
2. **Creazione Icona**: Genera un'icona SVG per l'applicazione
3. **Configurazione Build**: Crea il file `.spec` con le impostazioni ottimali
4. **Compilazione**: Utilizza PyInstaller per creare l'eseguibile
5. **Packaging**: Genera l'installer per la distribuzione

## 📦 Output del Build

Dopo il completamento, troverai nella cartella `dist/`:

- **Misure-mq.exe**: Eseguibile principale dell'applicazione
- **installer.bat**: Script di installazione per gli utenti finali

## 🎯 Distribuzione

Per distribuire l'applicazione:

1. Comprimi la cartella `dist/` in un file ZIP
2. Condividi il file ZIP con gli utenti
3. Gli utenti dovranno:
   - Estrarre il contenuto
   - Eseguire `installer.bat` come amministratore
   - L'applicazione sarà installata sul desktop

## ⚙️ Configurazioni Avanzate

### Personalizzazione Icona
- Sostituisci `app_icon.ico` con la tua icona personalizzata
- Formati supportati: ICO, PNG (convertito automaticamente)

### Modifica Configurazioni Build
Modifica il file `Misure-mq.spec` per:
- Aggiungere/rimuovere dipendenze
- Modificare le impostazioni dell'eseguibile
- Personalizzare i file inclusi

### Ottimizzazioni
- **UPX Compression**: Abilitata per ridurre le dimensioni
- **One-File**: Tutto incluso in un singolo eseguibile
- **Windowed**: Nasconde la console per un'esperienza desktop pulita

## 🐛 Risoluzione Problemi

### Errore "Module not found"
- Aggiungi il modulo mancante in `hiddenimports` nel file `.spec`
- Verifica che tutte le dipendenze siano installate

### Eseguibile troppo grande
- Rimuovi dipendenze non necessarie
- Considera l'uso di un ambiente virtuale pulito

### Errori di runtime
- Testa l'eseguibile su un sistema pulito
- Verifica che tutti i file dati siano inclusi correttamente

## 📊 Dimensioni Tipiche

- **Eseguibile base**: ~50-80 MB
- **Con tutte le dipendenze**: ~100-150 MB
- **Compresso (ZIP)**: ~30-50 MB

## 🔄 Aggiornamenti

Per creare una nuova versione:

1. Aggiorna il codice sorgente
2. Modifica la versione in `main.py` se necessario
3. Riesegui il build
4. Distribuisci la nuova versione

## 📝 Note Tecniche

- **Compatibilità**: Windows 7/8/10/11 (64-bit)
- **Framework**: Tkinter (incluso in Python)
- **Database**: SQLite (incluso)
- **Dipendenze**: Tutte incluse nell'eseguibile

## 🆘 Supporto

In caso di problemi:
1. Verifica i log di build nella console
2. Controlla che tutti i file sorgente siano presenti
3. Assicurati di avere i permessi di scrittura nella directory