import tkinter as tk
from tkinter import ttk, Menu, messagebox
import database
from materials_manager import MaterialsManager
from edges_manager import EdgesManager # Importa EdgesManager
import utils # Import the utils module
from edge_editor_dialog import EdgeEditorDialog # Importa la nuova finestra di dialogo

class App(tk.Tk):
    def __init__(self):
        print("App.__init__: Inizio")
        super().__init__()

        self.title("Preventivo Soglie Marmista")
        self.geometry("1000x700") # Increased size

        # Initialize database and tables
        database.create_tables()

        self._create_menu()
        self._create_ui()
        self._load_materials_to_combobox()
        print("App.__init__: Fine")

    def _create_menu(self):
        menubar = Menu(self)
        self.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Nuovo Preventivo", command=self.new_quote)
        file_menu.add_command(label="Apri Preventivo...", command=self.open_quote_from_json)
        file_menu.add_command(label="Salva Preventivo...", command=self.save_quote_to_json)
        file_menu.add_separator()
        file_menu.add_command(label="Esporta PDF...", command=self.export_quote_to_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.quit)

        gestione_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Gestione", menu=gestione_menu)
        gestione_menu.add_command(label="Materiali...", command=self.open_materials_manager)
        gestione_menu.add_command(label="Tipi di Bordo...", command=self.open_edges_manager) # Aggiungi menu per bordi
        # Updated command to call the new import function
        gestione_menu.add_command(label="Importa Materiali da Excel...", command=self.import_materials_from_excel_dialog)
        print("App._create_menu: Fine")

    def _create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        # --- Input Frame ---
        input_frame = ttk.LabelFrame(main_frame, text="Aggiungi Riga Preventivo", padding="10")
        input_frame.pack(fill="x", pady=10)
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        input_frame.columnconfigure(5, weight=1)
        input_frame.columnconfigure(7, weight=1)

        ttk.Label(input_frame, text="N. Soglie:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.num_soglie_var = tk.StringVar()
        self.num_soglie_entry = ttk.Entry(input_frame, textvariable=self.num_soglie_var, width=7)
        self.num_soglie_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Lunghezza (cm):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.lunghezza_var = tk.StringVar()
        self.lunghezza_entry = ttk.Entry(input_frame, textvariable=self.lunghezza_var, width=7)
        self.lunghezza_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Larghezza (cm):").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.larghezza_var = tk.StringVar()
        self.larghezza_entry = ttk.Entry(input_frame, textvariable=self.larghezza_var, width=7)
        self.larghezza_entry.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Materiale:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.material_var = tk.StringVar()
        self.material_combobox = ttk.Combobox(input_frame, textvariable=self.material_var, state="readonly", width=30)
        self.material_combobox.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        self.material_combobox.bind("<<ComboboxSelected>>", self.on_material_selected)

        ttk.Label(input_frame, text="Spessore (cm):").grid(row=1, column=4, padx=5, pady=5, sticky="w")
        self.spessore_var = tk.StringVar(value="N/A")
        self.spessore_label = ttk.Label(input_frame, textvariable=self.spessore_var, width=10)
        self.spessore_label.grid(row=1, column=5, padx=5, pady=5, sticky="ew")

        add_row_button = ttk.Button(input_frame, text="Aggiungi Riga", command=self.add_quote_row)
        add_row_button.grid(row=1, column=6, padx=10, pady=5, sticky="e")

        # --- Quote Table Frame ---
        quote_table_frame = ttk.LabelFrame(main_frame, text="Dettaglio Preventivo", padding="10")
        quote_table_frame.pack(fill="both", expand=True, pady=10)

        self.quote_tree = ttk.Treeview(quote_table_frame, columns=(
            "num", "lun", "lar", "materiale", "spessore", "mq", "prezzo_mq", "costo_lastra", "costo_bordi", "importo_riga", "id_riga"
        ), show="headings")
        
        self.quote_tree.heading("num", text="N.")
        self.quote_tree.heading("lun", text="L (cm)")
        self.quote_tree.heading("lar", text="W (cm)")
        self.quote_tree.heading("materiale", text="Materiale")
        self.quote_tree.heading("spessore", text="Spess. (cm)")
        self.quote_tree.heading("mq", text="m²")
        self.quote_tree.heading("prezzo_mq", text="€/m²")
        self.quote_tree.heading("costo_lastra", text="Lastra (€)")
        self.quote_tree.heading("costo_bordi", text="Bordi (€)")
        self.quote_tree.heading("importo_riga", text="Tot. Riga (€)")
        self.quote_tree.column("id_riga", width=0, stretch=tk.NO) # Hidden column for row ID

        self.quote_tree.column("num", width=40, anchor="center")
        self.quote_tree.column("lun", width=70, anchor="e")
        self.quote_tree.column("lar", width=70, anchor="e")
        self.quote_tree.column("materiale", width=150)
        self.quote_tree.column("spessore", width=80, anchor="e")
        self.quote_tree.column("mq", width=70, anchor="e")
        self.quote_tree.column("prezzo_mq", width=70, anchor="e")
        self.quote_tree.column("costo_lastra", width=80, anchor="e")
        self.quote_tree.column("costo_bordi", width=80, anchor="e")
        self.quote_tree.column("importo_riga", width=90, anchor="e")

        self.quote_tree.pack(side="left", fill="both", expand=True)
        # Aggiungi scrollbar
        scrollbar = ttk.Scrollbar(quote_table_frame, orient="vertical", command=self.quote_tree.yview)
        self.quote_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Aggiungi un listener per il doppio click sulla riga per aprire l'editor dei bordi
        self.quote_tree.bind("<Double-1>", self.open_edge_editor)

        # Frame per i pulsanti sotto la tabella del preventivo
        quote_buttons_frame = ttk.Frame(main_frame)
        quote_buttons_frame.pack(fill="x", pady=(0, 5))

        self.add_row_button = ttk.Button(quote_buttons_frame, text="➕ Aggiungi Riga", command=self.add_quote_row, style="Accent.TButton")
        self.add_row_button.pack(side="left", padx=5)

        self.delete_row_button = ttk.Button(quote_buttons_frame, text="➖ Elimina Riga", command=self.delete_quote_row)
        self.delete_row_button.pack(side="left", padx=5)

        self.edit_edges_button = ttk.Button(quote_buttons_frame, text="✂️ Gestisci Bordi Riga Selezionata", command=self.open_edge_editor)
        self.edit_edges_button.pack(side="left", padx=5)

        # Riepilogo
        summary_frame = ttk.LabelFrame(main_frame, text="Riepilogo", padding="10")
        summary_frame.pack(fill="x", pady=10)

        ttk.Label(summary_frame, text="Totale m²:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.total_mq_var = tk.StringVar(value="0.0000")
        ttk.Label(summary_frame, textvariable=self.total_mq_var, font=("Helvetica", 10, "bold")).grid(row=0, column=1, padx=5, pady=2, sticky="e")

        ttk.Label(summary_frame, text="Totale Costo Lastre (€):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.total_slabs_eur_var = tk.StringVar(value="0.00")
        ttk.Label(summary_frame, textvariable=self.total_slabs_eur_var, font=("Helvetica", 10, "bold")).grid(row=1, column=1, padx=5, pady=2, sticky="e")

        ttk.Label(summary_frame, text="Totale Costo Bordi (€):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.total_edges_eur_var = tk.StringVar(value="0.00")
        ttk.Label(summary_frame, textvariable=self.total_edges_eur_var, font=("Helvetica", 10, "bold")).grid(row=2, column=1, padx=5, pady=2, sticky="e")
        
        ttk.Label(summary_frame, text="Totale Importo (€):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.total_eur_var = tk.StringVar(value="0.00")
        ttk.Label(summary_frame, textvariable=self.total_eur_var, font=("Helvetica", 10, "bold")).grid(row=3, column=1, padx=5, pady=2, sticky="e")
        summary_frame.columnconfigure(1, weight=1)
        print("App._create_ui: Fine")

    def _load_materials_to_combobox(self):
        print("App._load_materials_to_combobox: Inizio")
        materials = database.get_all_materials()
        # Create a unique display name and map it to the material ID for direct lookup
        self.material_map = {}
        display_names = []
        for mat in materials:
            # Display name: "Name (Thickness cm, Supplier)" - Supplier can be None
            supplier_str = f", {mat['supplier']}" if mat['supplier'] else ""
            thickness_str = f"{mat['thickness'] if mat['thickness'] is not None else 'N/A'} cm"
            display_name = f"{mat['name']} ({thickness_str}{supplier_str})"
            display_names.append(display_name)
            # Use the unique display name as key, store the full material record
            self.material_map[display_name] = mat 

        self.material_combobox['values'] = sorted(display_names)
        if display_names:
            self.material_combobox.current(0)
            self.on_material_selected(None) # Trigger update for the first material
        else:
            self.material_var.set("")
            self.spessore_var.set("N/A")
            # self.prezzo_mq_var.set("N/A") # Add a var for price display if needed
        print("App._load_materials_to_combobox: Fine")

    def on_material_selected(self, event):
        selected_display_name = self.material_var.get()
        if selected_display_name in self.material_map:
            material = self.material_map[selected_display_name]
            thickness = material['thickness']
            self.spessore_var.set(str(thickness) if thickness is not None else "N/A")
            # Optionally, display price per sqm if you have a label for it
            # self.prezzo_mq_var.set(f"{material['price_per_sqm']:.2f}".replace('.', ','))
        else:
            self.spessore_var.set("N/A")
            # self.prezzo_mq_var.set("N/A")

    def open_materials_manager(self):
        manager_window = MaterialsManager(self)
        # Aspetta che la finestra di gestione materiali sia chiusa
        manager_window.wait_window()
        # Ricarica i materiali nel combobox principale e nell'editor dei bordi se aperto
        self._load_materials_to_combobox()
        # Potrebbe essere necessario aggiornare anche l'editor dei bordi se è aperto
        # e dipende dai materiali (es. per bordi specifici per materiale)

    def open_edges_manager(self):
        """Apre la finestra di gestione dei tipi di bordo."""
        edges_manager_window = EdgesManager(self)
        edges_manager_window.wait_window() # Aspetta che la finestra sia chiusa
        # Qui potresti voler ricaricare i dati dei bordi se qualche altra parte dell'UI dipende da essi
        # Ad esempio, se l'EdgeEditorDialog è aperto, potrebbe aver bisogno di un refresh.
        # Per ora, non facciamo nulla al ritorno, ma è un punto da considerare.
        # Se l'EdgeEditorDialog ricarica i tipi di bordo ogni volta che si apre, non serve altro qui.

        self.wait_window(edges_manager_window)
    # I tipi di bordo vengono ricaricati da EdgeEditorDialog se necessario, o qui se la logica cambia.
    # Per ora, EdgeEditorDialog gestisce il proprio caricamento.
    # Se la finestra EdgesManager modifica i dati, EdgeEditorDialog dovrebbe ricaricarli alla prossima apertura.

    def add_quote_row(self):
        # Validation
        try:
            num_soglie = int(self.num_soglie_var.get())
            if num_soglie <= 0: raise ValueError("Numero soglie deve essere positivo")
        except ValueError:
            messagebox.showerror("Errore Input", "Numero soglie non valido (intero positivo).", parent=self)
            return

        try:
            # Allow comma as decimal separator for input, convert to dot for float()
            lunghezza_cm = float(self.lunghezza_var.get().replace(',', '.'))
            if lunghezza_cm <= 0: raise ValueError("Lunghezza deve essere positiva")
        except ValueError:
            messagebox.showerror("Errore Input", "Lunghezza non valida (es. 120.5 o 120,5).", parent=self)
            return

        try:
            larghezza_cm = float(self.larghezza_var.get().replace(',', '.'))
            if larghezza_cm <= 0: raise ValueError("Larghezza deve essere positiva")
        except ValueError:
            messagebox.showerror("Errore Input", "Larghezza non valida (es. 30.0 o 30,0).", parent=self)
            return

        selected_material_display_name = self.material_var.get()
        if not selected_material_display_name or selected_material_display_name not in self.material_map:
            messagebox.showerror("Errore Selezione", "Selezionare un materiale valido.", parent=self)
            return
        
        material_data = self.material_map[selected_material_display_name]
        material_name = material_data['name']
        thickness = material_data['thickness']
        price_per_sqm = material_data['price_per_sqm']

        # Calcoli
        num_soglie_val = int(self.num_soglie_var.get())
        lunghezza_m = lunghezza_cm / 100
        larghezza_m = larghezza_cm / 100
        mq_singola = lunghezza_m * larghezza_m
        mq_totali_riga = num_soglie_val * mq_singola
        costo_lastra_riga = mq_totali_riga * price_per_sqm
        costo_bordi_riga = 0.0 # Placeholder, sarà calcolato da EdgeEditorDialog
        importo_totale_riga = costo_lastra_riga + costo_bordi_riga

        # Genera un ID univoco per la riga per poterla modificare/eliminare e associare i bordi
        row_id = f"row_{len(self.quote_tree.get_children())}_{material_name.replace(' ','_')}"

        # Aggiungi alla Treeview
        self.quote_tree.insert("", "end", iid=row_id, values=(
            num_soglie_val, 
            f"{lunghezza_cm:.1f}", 
            f"{larghezza_cm:.1f}", 
            material_name, 
            str(thickness) if thickness is not None else "N/A", 
            f"{mq_totali_riga:.4f}", 
            f"{price_per_sqm:.2f}",
            f"{costo_lastra_riga:.2f}",
            f"{costo_bordi_riga:.2f}",
            f"{importo_totale_riga:.2f}",
            row_id # Store row_id itself for easy access
        ))

        # Store edge data associated with this row_id (inizialmente vuoto)
        if not hasattr(self, 'edge_details_map'):
            self.edge_details_map = {}
        self.edge_details_map[row_id] = {
            'front': {'active': False, 'type': '', 'length_cm': lunghezza_cm, 'price_lm': 0, 'cost': 0},
            'back': {'active': False, 'type': '', 'length_cm': lunghezza_cm, 'price_lm': 0, 'cost': 0},
            'left': {'active': False, 'type': '', 'length_cm': larghezza_cm, 'price_lm': 0, 'cost': 0},
            'right': {'active': False, 'type': '', 'length_cm': larghezza_cm, 'price_lm': 0, 'cost': 0},
            'total_edge_cost': 0.0
        }

        self.update_summary()

        # Dopo aver aggiunto la riga, chiedi se l'utente vuole definire i bordi
        if messagebox.askyesno("Gestione Bordi", "Vuoi definire i bordi per la riga appena aggiunta?", parent=self):
            # Passiamo l'ID della riga appena creata a open_edge_editor
            self.open_edge_editor(from_add_row=True, row_id_to_edit=row_id)
        
        self.clear_input_fields()

    def clear_input_fields(self):
        self.num_soglie_var.set("")
        self.lunghezza_var.set("")
        self.larghezza_var.set("")
        # Non resettare il materiale selezionato, potrebbe essere utile per righe successive

    def delete_quote_row(self):
        selected_items = self.quote_tree.selection()
        if not selected_items:
            messagebox.showwarning("Nessuna Selezione", "Selezionare una riga da eliminare.", parent=self)
            return
        
        for item_iid in selected_items:
            if hasattr(self, 'edge_details_map') and item_iid in self.edge_details_map:
                del self.edge_details_map[item_iid]
            self.quote_tree.delete(item_iid)
        self.update_summary()

    def update_summary(self):
        total_mq = 0.0
        total_slabs_eur = 0.0
        total_edges_eur = 0.0
        total_eur = 0.0

        for row_iid in self.quote_tree.get_children():
            values = self.quote_tree.item(row_iid, 'values')
            try:
                total_mq += float(values[5])
                total_slabs_eur += float(values[7])
                total_edges_eur += float(values[8]) # Costo bordi dalla colonna
                total_eur += float(values[9])     # Importo totale riga dalla colonna
            except (IndexError, ValueError) as e:
                print(f"Errore nel calcolo del sommario per la riga {row_iid}: {values} - {e}")
                continue
        
        self.total_mq_var.set(f"{total_mq:.4f}")
        self.total_slabs_eur_var.set(f"{total_slabs_eur:.2f}")
        self.total_edges_eur_var.set(f"{total_edges_eur:.2f}")
        self.total_eur_var.set(f"{total_eur:.2f}")

    def new_quote(self):
        if messagebox.askyesno("Nuovo Preventivo", "Sei sicuro di voler creare un nuovo preventivo? Eventuali modifiche non salvate andranno perse.", parent=self):
            for i in self.quote_tree.get_children():
                self.quote_tree.delete(i)
            self.update_summary()
            self.num_soglie_var.set("")
            self.lunghezza_var.set("")
            self.larghezza_var.set("")
            if self.material_combobox['values']:
                 self.material_combobox.current(0)
                 self.on_material_selected(None)

    def save_quote_to_json(self):
        quote_items = []
        for row_id in self.quote_tree.get_children():
            quote_items.append(list(self.quote_tree.item(row_id, 'values')))
        
        if not quote_items:
            messagebox.showinfo("Salvataggio JSON", "Nessun dato da salvare.", parent=self)
            return

        totals = {
            "mq": self.total_mq_var.get(),
            "eur": self.total_eur_var.get()
        }
        filepath = tk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Salva Preventivo Come...",
            parent=self
        )
        if filepath:
            utils.save_quote_to_json(quote_items, totals, filepath)

    def open_quote_from_json(self):
        filepath = tk.filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Apri Preventivo",
            parent=self
        )
        if filepath:
            items, totals = utils.load_quote_from_json(filepath)
            if items is not None:
                self.new_quote() # Clear current quote first (or ask user)
                for item_values in items:
                    self.quote_tree.insert("", "end", values=item_values)
                if totals:
                    self.total_mq_var.set(totals.get("mq", "0,0000"))
                    self.total_eur_var.set(totals.get("eur", "0,00"))
                else: # Recalculate if totals not in JSON (older format?)
                    self.update_summary()

    def export_quote_to_pdf(self):
        quote_items = []
        for row_id in self.quote_tree.get_children():
            quote_items.append(list(self.quote_tree.item(row_id, 'values')))
        
        if not quote_items:
            messagebox.showinfo("Esporta PDF", "Nessun dato da esportare.", parent=self)
            return

        totals = {
            "mq": self.total_mq_var.get(),
            "eur": self.total_eur_var.get()
        }
        # Ensure filedialog is imported or use tk.filedialog
        try:
            from tkinter import filedialog
        except ImportError:
            pass 
 
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Esporta Preventivo in PDF...",
            parent=self
        )
        if filepath:
            utils.export_to_pdf(quote_items, totals, filepath)

    def open_edge_editor(self, event=None, from_add_row=False, row_id_to_edit=None):
        item_to_edit_iid = None
        if row_id_to_edit: # Prioritize row_id_to_edit if provided (from add_quote_row)
            item_to_edit_iid = row_id_to_edit
        elif event: # Called by double-click
            item_to_edit_iid = self.quote_tree.focus() # or self.quote_tree.identify_row(event.y)
        else: # Called by button "Gestisci Bordi Riga Selezionata"
            selected_items = self.quote_tree.selection()
            if selected_items:
                item_to_edit_iid = selected_items[0]

        if not item_to_edit_iid:
            messagebox.showwarning("Nessuna Selezione", "Selezionare una riga per gestire i bordi.", parent=self)
            return
        
        item_values = self.quote_tree.item(item_to_edit_iid, 'values')

        try:
            material_name_full = item_values[3]
            # Estrai il nome del materiale prima della parentesi, se presente
            material_name = material_name_full.split(' (')[0] if ' (' in material_name_full else material_name_full
            thickness_str = item_values[4]
            length_cm = float(item_values[1])
            width_cm = float(item_values[2])
            num_soglie = int(item_values[0])  # Numero di soglie dalla prima colonna
            # L'ID della riga è l'IID stesso dell'elemento nel Treeview, che abbiamo in item_to_edit_iid
            # row_id_from_values = item_values[10] # Questo è ridondante se usiamo item_to_edit_iid

            thickness = None
            if thickness_str and thickness_str.lower() != 'n/a':
                try:
                    thickness = float(thickness_str)
                except ValueError:
                    messagebox.showerror("Errore Dati Riga", f"Spessore non valido: {thickness_str}", parent=self)
                    return
            
            # Usa item_to_edit_iid come chiave per edge_details_map
            current_edge_details = self.edge_details_map.get(item_to_edit_iid)
            if not current_edge_details and from_add_row:
                # Se chiamato da add_row e non ci sono dettagli (dovrebbe esserci la struttura base)
                # assicuriamoci che esista una entry base in edge_details_map
                if item_to_edit_iid not in self.edge_details_map:
                     self.edge_details_map[item_to_edit_iid] = {
                        'front': {'active': False, 'type': '', 'length_cm': length_cm, 'price_lm': 0, 'cost': 0},
                        'back': {'active': False, 'type': '', 'length_cm': length_cm, 'price_lm': 0, 'cost': 0},
                        'left': {'active': False, 'type': '', 'length_cm': width_cm, 'price_lm': 0, 'cost': 0},
                        'right': {'active': False, 'type': '', 'length_cm': width_cm, 'price_lm': 0, 'cost': 0},
                        'total_edge_cost': 0.0
                    }
                current_edge_details = self.edge_details_map[item_to_edit_iid]
            elif not current_edge_details: # Caso generale se non trovato (non dovrebbe succedere se add_quote_row lo inizializza)
                 messagebox.showerror("Errore Interno", f"Dettagli bordi non trovati per la riga {item_to_edit_iid}.", parent=self)
                 return
 
        except (IndexError, ValueError) as e:
            messagebox.showerror("Errore Dati Riga", f"Impossibile leggere i dati dalla riga: {e}", parent=self)
            return

        dialog = EdgeEditorDialog(self, item_to_edit_iid, material_name, thickness, length_cm, width_cm, current_edge_details, num_soglie)
        self.wait_window(dialog)
        # L'aggiornamento della tabella e del sommario viene fatto da EdgeEditorDialog al salvataggio

    def import_materials_from_excel_dialog(self):
        try:
            from tkinter import filedialog # Ensure filedialog is available
        except ImportError:
            pass # Should already be available if tkinter is used

        filepath = filedialog.askopenfilename(
            title="Importa Materiali da Excel",
            filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"))
            # parent=self # parent can be omitted or set to self
        )
        if filepath:
            try:
                # Placeholder for actual import logic
                # For example: utils.import_materials_from_excel(filepath, database.add_material)
                messagebox.showinfo("Importazione Excel", 
                                    "Funzionalità di importazione da Excel non ancora implementata.\n" 
                                    f"File selezionato: {filepath}", 
                                    parent=self)
                self._load_materials_to_combobox() # Refresh materials after import
            except Exception as e:
                messagebox.showerror("Errore Importazione", f"Errore durante l'importazione: {e}", parent=self)

        
        # Define a callback for the import function to update the progress bar
        def progress_update_callback(percentage):
            progress_win.update_progress(percentage)
            self.update_idletasks() # Keep UI responsive

        try:
            success = utils.import_materials_from_excel(filepath, progress_callback=progress_update_callback)
            if success:
                self._load_materials_to_combobox() # Refresh combobox after import
                messagebox.showinfo("Importazione Completata", "Importazione dei materiali completata.", parent=self)
            # Error messages are handled within import_materials_from_excel now
        except Exception as e:
            # This is a fallback, most errors should be caught in utils
            messagebox.showerror("Errore Importazione", f"Si è verificato un errore imprevisto: {e}", parent=self)
        finally:
            if progress_win.winfo_exists(): # Check if window still exists before trying to destroy
                 progress_win.destroy() # Ensure progress window is closed

if __name__ == "__main__":
    print("Avvio dell'applicazione...")
    try:
        app = App()
        print("Applicazione inizializzata, avvio del mainloop...")
        app.mainloop()
    except Exception as e:
        print(f"Errore non gestito durante l'esecuzione dell'applicazione: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Applicazione terminata.")