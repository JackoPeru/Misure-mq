import tkinter as tk
from tkinter import ttk, messagebox
import database

class EdgesManager(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gestione Tipi di Bordo")
        self.geometry("800x500") # Adjusted size for more columns
        self.parent = parent

        # Frame for Treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Treeview to display edge types
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Nome Tipo Bordo", "Materiale Specifico", "Spessore Specifico (cm)", "Prezzo (€/ml)"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome Tipo Bordo", text="Nome Tipo Bordo")
        self.tree.heading("Materiale Specifico", text="Materiale Specifico")
        self.tree.heading("Spessore Specifico (cm)", text="Spessore Specifico (cm)")
        self.tree.heading("Prezzo (€/ml)", text="Prezzo (€/ml)")

        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Nome Tipo Bordo", width=150)
        self.tree.column("Materiale Specifico", width=150)
        self.tree.column("Spessore Specifico (cm)", width=150, anchor="e")
        self.tree.column("Prezzo (€/ml)", width=100, anchor="e")

        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Frame for buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10, padx=10, fill="x")

        add_button = ttk.Button(button_frame, text="Aggiungi Tipo Bordo", command=self.open_add_edge_dialog)
        add_button.pack(side="left", padx=5)

        edit_button = ttk.Button(button_frame, text="Modifica Selezionato", command=self.open_edit_edge_dialog)
        edit_button.pack(side="left", padx=5)

        delete_button = ttk.Button(button_frame, text="Elimina Selezionato", command=self.delete_selected_edge)
        delete_button.pack(side="left", padx=5)

        self.load_edge_types()

        self.transient(parent) # Keep this window on top of the main window
        self.grab_set() # Modal behavior

    def load_edge_types(self):
        """Carica i tipi di bordo dal database e li visualizza nella Treeview."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        edge_types = database.get_all_edge_types()
        for et in edge_types:
            material_name = et['material_name'] if et['material_name'] else "Generico"
            thickness = et['thickness'] if et['thickness'] is not None else "Generico"
            self.tree.insert("", "end", values=(et['id'], et['edge_type'], material_name, thickness, f"{et['price_per_lm']:.2f}"))

    def open_add_edge_dialog(self):
        """Apre la finestra di dialogo per aggiungere un nuovo tipo di bordo."""
        EdgeDialog(self, "Aggiungi Nuovo Tipo Bordo", self.load_edge_types)

    def open_edit_edge_dialog(self):
        """Apre la finestra di dialogo per modificare il tipo di bordo selezionato."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Nessuna Selezione", "Seleziona un tipo di bordo da modificare.", parent=self)
            return
        
        item_values = self.tree.item(selected_item[0], 'values')
        edge_id = item_values[0]
        EdgeDialog(self, "Modifica Tipo Bordo", self.load_edge_types, edge_id=edge_id)

    def delete_selected_edge(self):
        """Elimina il tipo di bordo selezionato dal database."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Nessuna Selezione", "Seleziona un tipo di bordo da eliminare.", parent=self)
            return

        item_values = self.tree.item(selected_item[0], 'values')
        edge_id = item_values[0]
        edge_name = item_values[1]

        if messagebox.askyesno("Conferma Eliminazione", f"Sei sicuro di voler eliminare il tipo di bordo '{edge_name}'?", parent=self):
            if database.delete_edge_type(edge_id):
                messagebox.showinfo("Successo", "Tipo di bordo eliminato con successo.", parent=self)
                self.load_edge_types()
            else:
                messagebox.showerror("Errore", "Impossibile eliminare il tipo di bordo.", parent=self)

class EdgeDialog(tk.Toplevel):
    def __init__(self, parent, title, callback_on_save, edge_id=None):
        super().__init__(parent)
        self.title(title)
        self.parent = parent
        self.callback_on_save = callback_on_save
        self.edge_id = edge_id

        # Fields
        ttk.Label(self, text="Nome Tipo Bordo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.edge_type_var = tk.StringVar()
        self.edge_type_entry = ttk.Entry(self, textvariable=self.edge_type_var, width=40)
        self.edge_type_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Materiale Specifico (opzionale):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.material_name_var = tk.StringVar()
        self.material_name_entry = ttk.Entry(self, textvariable=self.material_name_var, width=40)
        self.material_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Spessore Specifico (cm, opzionale):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.thickness_var = tk.StringVar()
        self.thickness_entry = ttk.Entry(self, textvariable=self.thickness_var, width=10)
        self.thickness_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(self, text="Prezzo (€/ml):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(self, textvariable=self.price_var, width=10)
        self.price_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Load data if editing
        if self.edge_id:
            self.load_edge_data()

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        save_button = ttk.Button(button_frame, text="Salva", command=self.save_edge)
        save_button.pack(side="left", padx=5)
        cancel_button = ttk.Button(button_frame, text="Annulla", command=self.destroy)
        cancel_button.pack(side="left", padx=5)

        self.grid_columnconfigure(1, weight=1)
        self.transient(parent)
        self.grab_set()
        self.edge_type_entry.focus_set()

    def load_edge_data(self):
        edge = database.get_edge_by_id(self.edge_id)
        if edge:
            self.edge_type_var.set(edge['edge_type'])
            self.material_name_var.set(edge['material_name'] or "")
            self.thickness_var.set(str(edge['thickness']) if edge['thickness'] is not None else "")
            self.price_var.set(f"{edge['price_per_lm']:.2f}")

    def save_edge(self):
        edge_type = self.edge_type_var.get().strip()
        material_name = self.material_name_var.get().strip() or None
        thickness_str = self.thickness_var.get().strip()
        price_str = self.price_var.get().strip().replace(',', '.')

        if not edge_type:
            messagebox.showerror("Errore Validazione", "Il nome del tipo di bordo è obbligatorio.", parent=self)
            return
        
        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError("Il prezzo deve essere positivo.")
        except ValueError:
            messagebox.showerror("Errore Validazione", "Il prezzo deve essere un numero valido (es. 3.50).", parent=self)
            return

        thickness = None
        if thickness_str:
            try:
                thickness = float(thickness_str.replace(',', '.'))
                if thickness <= 0:
                    raise ValueError("Lo spessore deve essere positivo.")
            except ValueError:
                messagebox.showerror("Errore Validazione", "Lo spessore deve essere un numero valido (es. 2.0) o lasciato vuoto.", parent=self)
                return

        if self.edge_id:
            success = database.update_edge_type(self.edge_id, edge_type, price, material_name, thickness)
            action = "aggiornato"
        else:
            new_id = database.add_edge_type(edge_type, price, material_name, thickness)
            success = new_id is not None
            action = "aggiunto"

        if success:
            messagebox.showinfo("Successo", f"Tipo di bordo {action} con successo.", parent=self.parent)
            self.callback_on_save()
            self.destroy()
        else:
            # Error message is already printed by database functions in case of IntegrityError
            # For other errors, a generic message might be needed or specific handling in database functions.
            # messagebox.showerror("Errore", f"Impossibile {action.replace('o','are')} il tipo di bordo.", parent=self.parent)
            pass # Assuming database function prints specific error