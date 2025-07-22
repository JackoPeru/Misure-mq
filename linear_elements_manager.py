import tkinter as tk
from tkinter import ttk, messagebox
import database

class LinearElementsManager(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Gestione Elementi Lineari")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Rendi la finestra modale
        self.transient(parent)
        self.grab_set()
        
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
        input_frame = ttk.LabelFrame(main_frame, text="Aggiungi Elemento Lineare", padding="10")
        input_frame.pack(fill="x", pady=(0, 10))
        
        # Tipo elemento
        ttk.Label(input_frame, text="Tipo Elemento:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.element_type_var = tk.StringVar()
        self.element_type_entry = ttk.Entry(input_frame, textvariable=self.element_type_var, width=30)
        self.element_type_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Materiale
        ttk.Label(input_frame, text="Materiale:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.material_var = tk.StringVar()
        self.material_combobox = ttk.Combobox(input_frame, textvariable=self.material_var, state="readonly", width=25)
        self.material_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Prezzo al metro lineare
        ttk.Label(input_frame, text="Prezzo €/ml:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(input_frame, textvariable=self.price_var, width=15)
        self.price_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Descrizione
        ttk.Label(input_frame, text="Descrizione:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(input_frame, textvariable=self.description_var, width=25)
        self.description_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        
        # Pulsanti
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        self.add_button = ttk.Button(buttons_frame, text="Aggiungi", command=self.add_linear_element)
        self.add_button.pack(side="left", padx=5)
        
        self.update_button = ttk.Button(buttons_frame, text="Modifica", command=self.update_linear_element, state="disabled")
        self.update_button.pack(side="left", padx=5)
        
        self.delete_button = ttk.Button(buttons_frame, text="Elimina", command=self.delete_linear_element, state="disabled")
        self.delete_button.pack(side="left", padx=5)
        
        self.clear_button = ttk.Button(buttons_frame, text="Pulisci", command=self.clear_fields)
        self.clear_button.pack(side="left", padx=5)
        
        # Configura il ridimensionamento
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        # Frame per la lista
        list_frame = ttk.LabelFrame(main_frame, text="Elementi Lineari", padding="10")
        list_frame.pack(fill="both", expand=True)
        
        # Treeview per mostrare gli elementi
        columns = ("tipo", "materiale", "prezzo", "descrizione")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Definisci le intestazioni
        self.tree.heading("tipo", text="Tipo Elemento")
        self.tree.heading("materiale", text="Materiale")
        self.tree.heading("prezzo", text="Prezzo €/ml")
        self.tree.heading("descrizione", text="Descrizione")
        
        # Definisci le larghezze delle colonne
        self.tree.column("tipo", width=200)
        self.tree.column("materiale", width=200)
        self.tree.column("prezzo", width=100, anchor="e")
        self.tree.column("descrizione", width=250)
        
        # Scrollbar per la treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack della treeview e scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind eventi
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Frame per i pulsanti di chiusura
        close_frame = ttk.Frame(main_frame)
        close_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(close_frame, text="Chiudi", command=self.destroy).pack(side="right")
        
        # Carica i materiali nel combobox
        self.load_materials()
        
    def load_materials(self):
        """Carica i materiali nel combobox."""
        materials = database.get_all_materials()
        material_names = [f"{mat['name']} ({mat['thickness'] if mat['thickness'] else 'N/A'} cm)" for mat in materials]
        self.material_combobox['values'] = sorted(material_names)
        
    def load_linear_elements(self):
        """Carica gli elementi lineari dalla tabella edges con filtro per tipo."""
        # Pulisci la treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Carica gli elementi lineari (usiamo la tabella edges con una convenzione)
        # Gli elementi lineari avranno edge_type che inizia con "LINEAR_"
        edges = database.get_all_edge_types()
        for edge in edges:
            if edge['edge_type'].startswith('LINEAR_'):
                # Rimuovi il prefisso LINEAR_ per la visualizzazione
                element_type = edge['edge_type'][7:]  # Rimuovi "LINEAR_"
                material_display = f"{edge['material_name'] or 'Generico'}"
                if edge['thickness']:
                    material_display += f" ({edge['thickness']} cm)"
                
                self.tree.insert("", "end", values=(
                    element_type,
                    material_display,
                    f"{edge['price_per_lm']:.2f}",
                    ""  # Descrizione vuota per ora
                ), tags=(edge['id'],))
                
    def add_linear_element(self):
        """Aggiunge un nuovo elemento lineare."""
        if not self.validate_input():
            return
            
        element_type = f"LINEAR_{self.element_type_var.get().strip()}"
        material_name = self.extract_material_name()
        thickness = self.extract_material_thickness()
        price = float(self.price_var.get().replace(',', '.'))
        
        try:
            result = database.add_edge_type(
                edge_type=element_type,
                price_per_lm=price,
                material_name=material_name,
                thickness=thickness
            )
            
            if result:
                messagebox.showinfo("Successo", "Elemento lineare aggiunto con successo!")
                self.clear_fields()
                self.load_linear_elements()
            else:
                messagebox.showerror("Errore", "Elemento lineare già esistente!")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'aggiunta: {e}")
            
    def update_linear_element(self):
        """Modifica l'elemento lineare selezionato."""
        selected = self.tree.selection()
        if not selected:
            return
            
        if not self.validate_input():
            return
            
        item = selected[0]
        edge_id = self.tree.item(item, "tags")[0]
        
        element_type = f"LINEAR_{self.element_type_var.get().strip()}"
        material_name = self.extract_material_name()
        thickness = self.extract_material_thickness()
        price = float(self.price_var.get().replace(',', '.'))
        
        try:
            success = database.update_edge_type(
                edge_id=edge_id,
                edge_type=element_type,
                price_per_lm=price,
                material_name=material_name,
                thickness=thickness
            )
            
            if success:
                messagebox.showinfo("Successo", "Elemento lineare modificato con successo!")
                self.clear_fields()
                self.load_linear_elements()
                self.update_button.config(state="disabled")
                self.delete_button.config(state="disabled")
            else:
                messagebox.showerror("Errore", "Errore durante la modifica!")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la modifica: {e}")
            
    def delete_linear_element(self):
        """Elimina l'elemento lineare selezionato."""
        selected = self.tree.selection()
        if not selected:
            return
            
        if messagebox.askyesno("Conferma", "Sei sicuro di voler eliminare questo elemento lineare?"):
            item = selected[0]
            edge_id = self.tree.item(item, "tags")[0]
            
            try:
                success = database.delete_edge_type(edge_id)
                if success:
                    messagebox.showinfo("Successo", "Elemento lineare eliminato con successo!")
                    self.clear_fields()
                    self.load_linear_elements()
                    self.update_button.config(state="disabled")
                    self.delete_button.config(state="disabled")
                else:
                    messagebox.showerror("Errore", "Errore durante l'eliminazione!")
                    
            except Exception as e:
                messagebox.showerror("Errore", f"Errore durante l'eliminazione: {e}")
                
    def validate_input(self):
        """Valida l'input dell'utente."""
        if not self.element_type_var.get().strip():
            messagebox.showerror("Errore", "Inserire il tipo di elemento!")
            return False
            
        try:
            price = float(self.price_var.get().replace(',', '.'))
            if price <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Errore", "Inserire un prezzo valido!")
            return False
            
        return True
        
    def extract_material_name(self):
        """Estrae il nome del materiale dal combobox."""
        material_text = self.material_var.get()
        if not material_text:
            return None
        # Estrai il nome prima della parentesi
        return material_text.split(' (')[0] if ' (' in material_text else material_text
        
    def extract_material_thickness(self):
        """Estrae lo spessore del materiale dal combobox."""
        material_text = self.material_var.get()
        if not material_text or ' (' not in material_text:
            return None
        try:
            # Estrai lo spessore dalla parentesi
            thickness_part = material_text.split(' (')[1].split(' cm')[0]
            if thickness_part == 'N/A':
                return None
            return float(thickness_part)
        except (IndexError, ValueError):
            return None
            
    def clear_fields(self):
        """Pulisce tutti i campi di input."""
        self.element_type_var.set("")
        self.material_var.set("")
        self.price_var.set("")
        self.description_var.set("")
        
    def on_select(self, event):
        """Gestisce la selezione di un elemento nella treeview."""
        selected = self.tree.selection()
        if selected:
            self.update_button.config(state="normal")
            self.delete_button.config(state="normal")
        else:
            self.update_button.config(state="disabled")
            self.delete_button.config(state="disabled")
            
    def on_double_click(self, event):
        """Gestisce il doppio click su un elemento per modificarlo."""
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            values = self.tree.item(item, "values")
            
            # Popola i campi con i valori selezionati
            self.element_type_var.set(values[0])
            self.material_var.set(values[1])
            self.price_var.set(values[2])
            self.description_var.set(values[3])