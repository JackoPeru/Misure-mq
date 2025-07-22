# Nuove Funzionalità Aggiunte

## 1. Modalità Calcolo Metri Lineari

### Descrizione
È stata aggiunta una nuova modalità per il calcolo di elementi lineari come battiscopa, cornici, profili, ecc., dove non è necessario calcolare i metri quadri.

### Come utilizzare:
1. **Gestione Elementi Lineari**: Vai su `Gestione > Elementi Lineari...` per creare e gestire i tipi di elementi lineari disponibili
2. **Aggiunta al Preventivo**: Usa il pulsante `📏 Aggiungi Elemento Lineare` nella schermata principale per aggiungere elementi lineari al preventivo
3. **Calcolo Automatico**: Il sistema calcola automaticamente il costo totale basato su: Quantità × Lunghezza (ml) × Prezzo per metro lineare

### Caratteristiche:
- Gestione separata degli elementi lineari nel database
- Calcolo automatico del costo totale
- Integrazione completa con il sistema di preventivi esistente
- Possibilità di aggiungere note per ogni elemento

## 2. Esportazione e Importazione Dati

### Descrizione
È stata aggiunta la funzionalità per esportare e importare tutti i dati di materiali, bordi ed elementi lineari per facilitare gli aggiornamenti dell'applicazione.

### Come utilizzare:
1. **Esportazione**: Vai su `Gestione > Esporta Dati (Materiali e Bordi)...` per salvare tutti i dati in un file JSON
2. **Importazione**: Vai su `Gestione > Importa Dati (Materiali e Bordi)...` per caricare i dati da un file JSON precedentemente esportato

### Caratteristiche:
- Backup completo di tutti i materiali e tipi di bordo
- Formato JSON leggibile e modificabile
- Gestione automatica dei duplicati durante l'importazione
- Rapporto dettagliato di elementi importati e saltati
- Include data di esportazione per tracciabilità

## 3. Miglioramenti all'Interfaccia

### Nuovi Elementi UI:
- Pulsante `📏 Aggiungi Elemento Lineare` nella schermata principale
- Menu `Elementi Lineari...` nella sezione Gestione
- Finestra dedicata per la gestione degli elementi lineari
- Dialog per l'aggiunta di elementi lineari ai preventivi

### Integrazione:
- Gli elementi lineari appaiono nella tabella del preventivo con indicazione "LINEAR" nella colonna larghezza
- Calcolo automatico dei totali che include sia elementi quadrati che lineari
- Esportazione PDF che include tutti i tipi di elementi

## Note Tecniche

### Database:
- Gli elementi lineari sono memorizzati nella tabella `edges` con prefisso "LINEAR_" nel campo `edge_type`
- Compatibilità completa con la struttura database esistente
- Nessuna modifica breaking alle funzionalità esistenti

### File Aggiunti:
- `linear_elements_manager.py`: Gestione elementi lineari
- `linear_quote_dialog.py`: Dialog per aggiunta elementi ai preventivi
- Modifiche a `main.py`, `utils.py` per integrazione completa

### Compatibilità:
- Tutte le funzionalità esistenti rimangono invariate
- I preventivi esistenti continuano a funzionare normalmente
- L'esportazione/importazione è retrocompatibile