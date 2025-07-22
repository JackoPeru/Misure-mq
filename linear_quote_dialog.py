import tkinter as tk
from tkinter import ttk, messagebox
import database

class LinearQuoteDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Aggiungi Elemento Lineare al Preventivo")
        self.geometry("700x550")
        self.resizable(True, True)
        self.minsize(650, 500)
        
        # Rendi la finestra modale
        self.transient(parent)
        self.grab_set()
        
        self.result = None
        self.element_added = False  # Flag per indicare se un elemento è stato aggiunto
        
        self.create_widgets()
        self.load_linear_elements()
        
        # Centra la finestra
        self.center_window()
        
    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
    def create_widgets(self):
        # Frame principale
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Frame per l'input
        input_frame = ttk.LabelFrame(main_frame, text="Dati Elemento Lineare", padding="10")
        input_frame.pack(fill="x", pady=(0, 10))
        
        # Quantità
        ttk.Label(input_frame, text="Quantità:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_entry = ttk.Entry(input_frame, textvariable=self.quantity_var, width=10)
        self.quantity_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Lunghezza in metri lineari
        ttk.Label(input_frame, text="Lunghezza (ml):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.length_var = tk.StringVar()
        self.length_entry = ttk.Entry(input_frame, textvariable=self.length_var, width=15)
        self.length_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Tipo elemento
        ttk.Label(input_frame, text="Tipo Elemento:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.element_var = tk.StringVar()
        self.element_combobox = ttk.Combobox(input_frame, textvariable=self.element_var, state="readonly", width=30)
        self.element_combobox.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        self.element_combobox.bind("<<ComboboxSelected>>", self.on_element_selected)
        
        # Prezzo unitario (readonly)
        ttk.Label(input_frame, text="Prezzo €/ml:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.price_var = tk.StringVar(value="0.00")
        self.price_label = ttk.Label(input_frame, textvariable=self.price_var, relief="sunken", width=15)
        self.price_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Costo totale (readonly)
        ttk.Label(input_frame, text="Costo Totale €:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.total_cost_var = tk.StringVar(value="0.00")
        self.total_cost_label = ttk.Label(input_frame, textvariable=self.total_cost_var, relief="sunken", width=15)
        self.total_cost_label.grid(row=2, column=3, padx=5, pady=5, sticky="ew")
        
        # Note
        ttk.Label(input_frame, text="Note:").grid(row=3, column=0, padx=5, pady=5, sticky="nw")
        self.notes_var = tk.StringVar()
        self.notes_entry = ttk.Entry(input_frame, textvariable=self.notes_var, width=50)
        self.notes_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        
        # Configura il ridimensionamento
        input_frame.columnconfigure(3, weight=1)
        
        # Bind per calcolo automatico
        self.quantity_var.trace("w", self.calculate_total)
        self.length_var.trace("w", self.calculate_total)
        
        # Frame per la lista degli elementi disponibili
        list_frame = ttk.LabelFrame(main_frame, text="Elementi Lineari Disponibili", padding="10")
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Treeview per mostrare gli elementi disponibili
        columns = ("tipo", "materiale", "prezzo")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=6)
        
        # Definisci le intestazioni
        self.tree.heading("tipo", text="Tipo Elemento")
        self.tree.heading("materiale", text="Materiale")
        self.tree.heading("prezzo", text="Prezzo €/ml")
        
        # Definisci le larghezze delle colonne
        self.tree.column("tipo", width=200)
        self.tree.column("materiale", width=200)
        self.tree.column("prezzo", width=100, anchor="e")
        
        # Scrollbar per la treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack della treeview e scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind per selezione dalla lista
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Frame per i pulsanti con padding maggiore
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Aggiungi i bottoni con stile migliorato
        cancel_btn = ttk.Button(buttons_frame, text="Annulla", command=self.cancel)
        cancel_btn.pack(side="right", padx=(10, 0))
        
        add_btn = ttk.Button(buttons_frame, text="Aggiungi al Preventivo", command=self.add_to_quote)
        add_btn.pack(side="right", padx=(0, 10))
        
        # Rendi il bottone "Aggiungi" più prominente
        add_btn.configure(style="Accent.TButton" if hasattr(ttk.Style(), "theme_names") else "TButton")
        
        # Binding per tasti di scelta rapida
        self.bind("<Return>", lambda e: self.add_to_quote())
        self.bind("<Escape>", lambda e: self.cancel())
        
        # Focus iniziale sulla quantità
        self.quantity_entry.focus_set()
        
        # Messaggio di aiuto
        help_frame = ttk.Frame(main_frame)
        help_frame.pack(fill="x", pady=(5, 0))
        
        help_text = "💡 Suggerimento: Seleziona un elemento dalla lista o dal menu a tendina, inserisci quantità e lunghezza. Usa Enter per aggiungere, Esc per annullare."
        help_label = ttk.Label(help_frame, text=help_text, foreground="gray", font=("TkDefaultFont", 8))
        help_label.pack(anchor="w")
        
    def load_linear_elements(self):
        """Carica gli elementi lineari disponibili."""
        # Pulisci la treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Carica gli elementi lineari
        edges = database.get_all_edge_types()
        element_options = []
        
        for edge in edges:
            if edge['edge_type'].startswith('LINEAR_'):
                # Rimuovi il prefisso LINEAR_ per la visualizzazione
                element_type = edge['edge_type'][7:]
                material_display = f"{edge['material_name'] or 'Generico'}"
                if edge['thickness']:
                    material_display += f" ({edge['thickness']} cm)"
                
                display_name = f"{element_type} - {material_display}"
                element_options.append(display_name)
                
                self.tree.insert("", "end", values=(
                    element_type,
                    material_display,
                    f"{edge['price_per_lm']:.2f}"
                ), tags=(edge['id'], edge['price_per_lm']))
                
        # Aggiorna il combobox
        self.element_combobox['values'] = sorted(element_options)
        
    def on_element_selected(self, event):
        """Gestisce la selezione di un elemento dal combobox."""
        selected_text = self.element_var.get()
        if not selected_text:
            return
            
        # Trova l'elemento corrispondente nella treeview
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            item_display = f"{values[0]} - {values[1]}"
            if item_display == selected_text:
                tags = self.tree.item(item, "tags")
                if len(tags) >= 2:
                    price = float(tags[1])
                    self.price_var.set(f"{price:.2f}")
                    self.calculate_total()
                break
                
    def on_tree_select(self, event):
        """Gestisce la selezione di un elemento dalla treeview."""
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            values = self.tree.item(item, "values")
            tags = self.tree.item(item, "tags")
            
            # Aggiorna il combobox
            display_name = f"{values[0]} - {values[1]}"
            self.element_var.set(display_name)
            
            # Aggiorna il prezzo
            if len(tags) >= 2:
                price = float(tags[1])
                self.price_var.set(f"{price:.2f}")
                self.calculate_total()
                
    def on_tree_double_click(self, event):
        """Gestisce il doppio click sulla treeview per selezionare un elemento."""
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            values = self.tree.item(item, "values")
            display_name = f"{values[0]} - {values[1]}"
            self.element_var.set(display_name)
            self.on_element_selected(None)
            
    def calculate_total(self, *args):
        """Calcola il costo totale."""
        try:
            quantity = float(self.quantity_var.get() or "0")
            length = float(self.length_var.get().replace(',', '.') or "0")
            price = float(self.price_var.get() or "0")
            
            total = quantity * length * price
            self.total_cost_var.set(f"{total:.2f}")
            
            # Cambia il colore del totale se è valido
            if total > 0:
                self.total_cost_label.configure(foreground="green")
            else:
                self.total_cost_label.configure(foreground="black")
                
        except ValueError:
            self.total_cost_var.set("0.00")
            self.total_cost_label.configure(foreground="red")
            
    def add_to_quote(self):
        """Aggiunge l'elemento lineare al preventivo."""
        if not self.validate_input():
            return
            
        try:
            quantity = int(self.quantity_var.get())
            length = float(self.length_var.get().replace(',', '.'))
            price = float(self.price_var.get())
            total_cost = float(self.total_cost_var.get())
            element_type = self.element_var.get()
            notes = self.notes_var.get().strip()
            
            # Genera un ID univoco per la riga lineare
            row_id = f"linear_{len(self.parent.quote_tree.get_children())}_{element_type.replace(' ','_').replace('-','_')}"
            
            # Aggiungi alla Treeview del preventivo principale
            # Formato: (Quantità, Lunghezza, Larghezza, Materiale, Spessore, MQ, Prezzo/MQ, Costo Lastra, Costo Bordi, Totale, ID)
            # Per elementi lineari: Quantità=quantità, Lunghezza=lunghezza ml, Larghezza="LINEAR", Materiale=tipo elemento
            self.parent.quote_tree.insert("", "end", iid=row_id, values=(
                quantity,
                f"{length:.2f}",
                "LINEAR",  # Indica che è un elemento lineare
                element_type,
                "N/A",  # Spessore non applicabile
                f"{quantity * length:.4f}",  # Usiamo questo campo per i metri lineari totali
                f"{price:.2f}",  # Prezzo per metro lineare
                "0.00",  # Costo lastra non applicabile
                "0.00",  # Costo bordi non applicabile
                f"{total_cost:.2f}",  # Costo totale
                row_id
            ))
            
            # Inizializza i dettagli dei bordi (vuoti per elementi lineari)
            if not hasattr(self.parent, 'edge_details_map'):
                self.parent.edge_details_map = {}
            self.parent.edge_details_map[row_id] = {
                'front': {'active': False, 'type': '', 'length_cm': 0, 'price_lm': 0, 'cost': 0},
                'back': {'active': False, 'type': '', 'length_cm': 0, 'price_lm': 0, 'cost': 0},
                'left': {'active': False, 'type': '', 'length_cm': 0, 'price_lm': 0, 'cost': 0},
                'right': {'active': False, 'type': '', 'length_cm': 0, 'price_lm': 0, 'cost': 0},
                'total_edge_cost': 0.0,
                'is_linear': True,  # Flag per identificare elementi lineari
                'notes': notes
            }
            
            # Segna che l'elemento è stato aggiunto
            self.element_added = True
            
            messagebox.showinfo("Successo", "Elemento lineare aggiunto al preventivo!")
            self.destroy()
            
        except ValueError as e:
            messagebox.showerror("Errore", f"Errore nei dati inseriti: {e}")
            
    def validate_input(self):
        """Valida l'input dell'utente."""
        if not self.element_var.get():
            messagebox.showerror("Errore", "Selezionare un tipo di elemento!")
            return False
            
        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                raise ValueError("Quantità deve essere positiva")
        except ValueError:
            messagebox.showerror("Errore", "Inserire una quantità valida!")
            return False
            
        try:
            length = float(self.length_var.get().replace(',', '.'))
            if length <= 0:
                raise ValueError("Lunghezza deve essere positiva")
        except ValueError:
            messagebox.showerror("Errore", "Inserire una lunghezza valida!")
            return False
            
        return True
        
    def cancel(self):
        """Annulla l'operazione."""
        self.result = None
        self.destroy()
        
    def get_result(self):
        """Restituisce il risultato della finestra di dialogo."""
        return self.result