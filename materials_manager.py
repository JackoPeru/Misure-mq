import tkinter as tk
from tkinter import ttk, messagebox
import database

class MaterialsManager(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gestione Materiali")
        self.geometry("700x500")
        self.parent = parent

        # Frame for Treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Treeview to display materials
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Nome", "Spessore (cm)", "Prezzo (€/m²)", "Descrizione", "Fornitore"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome Materiale")
        self.tree.heading("Spessore (cm)", text="Spessore (cm)")
        self.tree.heading("Prezzo (€/m²)", text="Prezzo (€/m²)")
        self.tree.heading("Descrizione", text="Descrizione")
        self.tree.heading("Fornitore", text="Fornitore")

        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Nome", width=150)
        self.tree.column("Spessore (cm)", width=100, anchor="e")
        self.tree.column("Prezzo (€/m²)", width=100, anchor="e")
        self.tree.column("Descrizione", width=150)
        self.tree.column("Fornitore", width=100)

        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Frame for buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10, padx=10, fill="x")

        add_button = ttk.Button(button_frame, text="Aggiungi Materiale", command=self.open_add_material_dialog)
        add_button.pack(side="left", padx=5)

        edit_button = ttk.Button(button_frame, text="Modifica Selezionato", command=self.open_edit_material_dialog)
        edit_button.pack(side="left", padx=5)

        delete_button = ttk.Button(button_frame, text="Elimina Selezionato", command=self.delete_selected_material)
        delete_button.pack(side="left", padx=5)

        self.load_materials()

        self.transient(parent) # Keep this window on top of the main window
        self.grab_set() # Modal behavior

    def load_materials(self):
        """Carica i materiali dal database e li visualizza nella Treeview."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        materials = database.get_all_materials()
        for mat in materials:
            thickness = mat['thickness'] if mat['thickness'] is not None else "N/A"
            supplier = mat['supplier'] if mat['supplier'] else "N/A"
            self.tree.insert("", "end", values=(mat['id'], mat['name'], thickness, f"{mat['price_per_sqm']:.2f}", mat['description'], supplier))

    def open_add_material_dialog(self):
        """Apre la finestra di dialogo per aggiungere un nuovo materiale."""
        MaterialDialog(self, "Aggiungi Nuovo Materiale", self.load_materials)

    def open_edit_material_dialog(self):
        """Apre la finestra di dialogo per modificare il materiale selezionato."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Nessuna Selezione", "Seleziona un materiale da modificare.", parent=self)
            return
        
        item_values = self.tree.item(selected_item[0], 'values')
        material_id = item_values[0]
        MaterialDialog(self, "Modifica Materiale", self.load_materials, material_id=material_id)

    def delete_selected_material(self):
        """Elimina il materiale selezionato dal database."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Nessuna Selezione", "Seleziona un materiale da eliminare.", parent=self)
            return

        item_values = self.tree.item(selected_item[0], 'values')
        material_id = item_values[0]
        material_name = item_values[1]

        if messagebox.askyesno("Conferma Eliminazione", f"Sei sicuro di voler eliminare il materiale '{material_name}'?", parent=self):
            if database.delete_material(material_id):
                messagebox.showinfo("Successo", "Materiale eliminato con successo.", parent=self)
                self.load_materials()
            else:
                messagebox.showerror("Errore", "Impossibile eliminare il materiale.", parent=self)

class MaterialDialog(tk.Toplevel):
    def __init__(self, parent, title, callback_on_save, material_id=None):
        super().__init__(parent)
        self.title(title)
        self.parent = parent
        self.callback_on_save = callback_on_save
        self.material_id = material_id

        # Fields
        ttk.Label(self, text="Nome Materiale:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(self, textvariable=self.name_var, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Spessore (cm, opzionale):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.thickness_var = tk.StringVar()
        self.thickness_entry = ttk.Entry(self, textvariable=self.thickness_var, width=10)
        self.thickness_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(self, text="Prezzo (€/m²):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(self, textvariable=self.price_var, width=10)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(self, text="Descrizione:").grid(row=3, column=0, padx=5, pady=5, sticky="nw")
        self.description_text = tk.Text(self, height=4, width=30)
        self.description_text.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Fornitore:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.supplier_var = tk.StringVar()
        self.supplier_entry = ttk.Entry(self, textvariable=self.supplier_var, width=40)
        self.supplier_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # Load data if editing
        if self.material_id:
            self.load_material_data()

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10) # Adjusted row for buttons

        save_button = ttk.Button(button_frame, text="Salva", command=self.save_material)
        save_button.pack(side="left", padx=5)
        cancel_button = ttk.Button(button_frame, text="Annulla", command=self.destroy)
        cancel_button.pack(side="left", padx=5)

        self.grid_columnconfigure(1, weight=1)
        self.transient(parent)
        self.grab_set()
        self.name_entry.focus_set()

    def load_material_data(self):
        material = database.get_material_by_id(self.material_id)
        if material:
            self.name_var.set(material['name'])
            self.thickness_var.set(str(material['thickness']) if material['thickness'] is not None else "")
            self.price_var.set(f"{material['price_per_sqm']:.2f}")
            self.description_text.insert("1.0", material['description'] or "")
            self.supplier_var.set(material['supplier'] or "")

    def save_material(self):
        name = self.name_var.get().strip()
        thickness_str = self.thickness_var.get().strip()
        price_str = self.price_var.get().strip().replace(',', '.')
        description = self.description_text.get("1.0", tk.END).strip()
        supplier = self.supplier_var.get().strip() or None # Supplier can be None if empty

        if not name:
            messagebox.showerror("Errore Validazione", "Il nome del materiale è obbligatorio.", parent=self)
            return
        
        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError("Il prezzo deve essere positivo.")
        except ValueError:
            messagebox.showerror("Errore Validazione", "Il prezzo deve essere un numero valido (es. 120.50).", parent=self)
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

        if self.material_id:
            success = database.update_material(self.material_id, name, price, thickness, description, supplier)
            action = "aggiornato"
        else:
            new_id = database.add_material(name, price, thickness, description, supplier)
            success = new_id is not None
            action = "aggiunto"

        if success:
            messagebox.showinfo("Successo", f"Materiale {action} con successo.", parent=self.parent) # Show on parent of dialog
            self.callback_on_save() # Refresh the list in MaterialsManager
            self.destroy()
        else:
            messagebox.showerror("Errore Database", f"Impossibile {action.replace('o','are')} il materiale. Controlla se il nome esiste già.", parent=self)

if __name__ == '__main__':
    # Example usage (requires a root window)
    root = tk.Tk()
    root.title("Main App (Test)")
    root.geometry("300x200")

    def open_manager():
        # Ensure DB and tables are created for testing
        database.create_tables()
        # Example data
        if not database.get_all_materials():
            database.add_material("Marmo Test", 100.0, 2, "Descrizione test")
        MaterialsManager(root)

    btn = ttk.Button(root, text="Gestisci Materiali", command=open_manager)
    btn.pack(pady=20)
    root.mainloop()