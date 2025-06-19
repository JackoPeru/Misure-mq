import tkinter as tk
from tkinter import ttk, messagebox
import database

class EdgeEditorDialog(tk.Toplevel):
    def __init__(self, parent, row_id, material_name, thickness, length1_cm, length2_cm, current_edge_details):
        super().__init__(parent)
        self.parent = parent
        self.row_id = row_id
        self.material_name = material_name
        self.thickness = thickness
        self.length1_cm = float(length1_cm) # Fronte/Retro
        self.length2_cm = float(length2_cm) # Sinistra/Destra
        self.current_edge_details = current_edge_details

        self.title(f"Editor Bordi - {material_name} ({thickness}cm)")
        self.geometry("600x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.edge_types_data = [] # Sarà popolata con i dati da database
        self.selected_edges = {
            'front': {'active': tk.BooleanVar(), 'type': tk.StringVar(), 'cost_var': tk.StringVar(value="0.00")},
            'back':  {'active': tk.BooleanVar(), 'type': tk.StringVar(), 'cost_var': tk.StringVar(value="0.00")},
            'left':  {'active': tk.BooleanVar(), 'type': tk.StringVar(), 'cost_var': tk.StringVar(value="0.00")},
            'right': {'active': tk.BooleanVar(), 'type': tk.StringVar(), 'cost_var': tk.StringVar(value="0.00")}
        }
        self.total_edge_cost_var = tk.StringVar(value="0.00")

        # Load edge types first. If it fails or no types are found, handle appropriately.
        if not self._load_edge_types():
            # If _load_edge_types returns False (e.g., user was warned and no types exist),
            # we might want to close the dialog or prevent further initialization.
            # For now, we'll let it proceed, but create_widgets will handle empty edge_options.
            # Consider self.destroy() here if a completely empty dialog is not desired.
            # For instance, if messagebox was shown and no types, it might be best to close.
            # However, the current logic in _load_edge_types shows a warning and proceeds.
            pass # Proceed to create widgets, which will show 'Nessun bordo disponibile'

        self._create_widgets()
        self._load_current_details()
        self._update_all_costs()

    def _load_edge_types(self):
        print(f"[DEBUG] _load_edge_types: Inizio caricamento per Materiale: {self.material_name}, Spessore: {self.thickness}")
        try:
            # Prima prova a ottenere i bordi specifici per materiale e spessore
            specific_edge_types = database.get_edge_types_by_material_thickness(self.material_name, self.thickness)
            print(f"[DEBUG] _load_edge_types: Tipi di bordo specifici trovati: {specific_edge_types}")
            self.edge_types_data = list(specific_edge_types) # Converti in lista per estendere

            # Se non ci sono bordi specifici o per assicurarsi di avere anche i generici come fallback
            # (la logica originale li prendeva solo se gli specifici erano assenti, modifichiamo per prenderli sempre e poi filtrare)
            generic_edge_types = database.get_edge_types_by_material_thickness(None, None)
            print(f"[DEBUG] _load_edge_types: Tipi di bordo generici trovati: {generic_edge_types}")
            
            # Unisci e rimuovi duplicati, dando priorità agli specifici con prezzi validi
            # Converti le tuple in dizionari per una più facile manipolazione
            specific_dicts = {row['edge_type']: dict(row) for row in specific_edge_types}
            generic_dicts = {row['edge_type']: dict(row) for row in generic_edge_types}

            print(f"[DEBUG] _load_edge_types: specific_dicts: {specific_dicts}")
            print(f"[DEBUG] _load_edge_types: generic_dicts: {generic_dicts}")

            merged_data_final = {}

            # Inizia con i dati generici
            for edge_name, gen_data in generic_dicts.items():
                merged_data_final[edge_name] = gen_data

            # Sovrascrivi o aggiungi dati specifici, con logica per i prezzi None
            for edge_name, spec_data in specific_dicts.items():
                if edge_name in merged_data_final:
                    # Esiste sia specifico che generico
                    # Se il prezzo specifico NON è None, usa i dati specifici
                    if spec_data.get('price_per_lm') is not None:
                        merged_data_final[edge_name] = spec_data
                    # Altrimenti (prezzo specifico è None), i dati generici sono già lì (con il loro prezzo),
                    # quindi non fare nulla per mantenere il prezzo generico.
                else:
                    # Esiste solo specifico, aggiungilo indipendentemente dal prezzo
                    merged_data_final[edge_name] = spec_data
            
            print(f"[DEBUG] _load_edge_types: merged_data_final (before sqlite3.Row conversion): {merged_data_final}")
            # Assicurati che self.db_conn sia disponibile se necessario per sqlite3.Row
            # Se db_conn non è un attributo di istanza, dovrai passarlo o gestirlo diversamente.
            # Per ora, presumo che self.db_conn sia accessibile o che sqlite3.Row non ne abbia bisogno qui.
            # Se database.py restituisce già oggetti simili a dizionari o Row, potresti non aver bisogno di questa conversione.
            # Modifica: database.get_edge_types_by_material_thickness dovrebbe restituire oggetti che possono essere usati direttamente
            # o convertiti in un formato consistente. Se sono già dizionari, la conversione a Row potrebbe non essere necessaria
            # o potrebbe necessitare di un cursore fittizio se non si esegue una query.
            # Per semplicità, se database.py restituisce dict, usiamo quelli.
            # Se restituisce Row objects, la logica di conversione a dict e poi di nuovo a Row deve essere coerente.
            # Assumendo che database.py fornisca dict o Row-like objects:
            self.edge_types_data = list(merged_data_final.values()) # Se merged_data_final contiene già i dati nel formato corretto (es. dict)
            # Se è necessaria la conversione esplicita a sqlite3.Row e hai un self.db_conn:
            # self.edge_types_data = [sqlite3.Row(self.db_conn.cursor(), data) for data in merged_data_final.values()] 
            # Scegli la riga sopra se database.py non restituisce oggetti Row e ne hai bisogno.
            # Se database.py restituisce già oggetti Row, allora la conversione a dict e poi di nuovo a Row è ridondante.
            # Semplifichiamo assumendo che i dizionari siano sufficienti o che le Row siano gestite correttamente.
            # La riga seguente è più robusta se i dati sono già Row o dict.
            # self.edge_types_data = list(merged_data_final.values()) 
            # Tuttavia, per mantenere la coerenza con il codice originale che usa sqlite3.Row, proviamo a ricostruirli
            # se `database.py` non li fornisce già in quel formato.
            # Se `database.get_edge_types_by_material_thickness` restituisce già `sqlite3.Row` objects, 
            # allora la conversione a `dict` e poi di nuovo a `sqlite3.Row` è inefficiente.
            # Per ora, manteniamo la conversione a `list` di `dict` come formato intermedio.
            # La conversione finale a `sqlite3.Row` dipende da come il resto del codice utilizza `self.edge_types_data`.
            # Se il codice si aspetta oggetti `sqlite3.Row`, la conversione è necessaria.
            # Se il codice accede ai campi tramite `['key']`, allora i `dict` vanno bene.
            # Dato il codice in `_calculate_side_cost` e `_save_changes` che usa `et_data['edge_type']`, i dizionari sono sufficienti.
            # Quindi, la riga seguente è probabilmente la più corretta e semplice:
            self.edge_types_data = list(merged_data_final.values())
            print(f"[DEBUG] _load_edge_types: Dati finali self.edge_types_data dopo unione e deduplicazione: {self.edge_types_data}")

            if not self.edge_types_data:
                # Se non ci sono bordi specifici, prendi tutti i tipi di bordo generici (senza material_name e thickness specifici)
                # Questi dovrebbero avere i loro prezzi corretti nel database.
                generic_edge_types = database.get_edge_types_by_material_thickness(None, None) # Passa None per ottenere quelli generici
                self.edge_types_data.extend(generic_edge_types) # Aggiungili a quelli specifici (se ce ne sono)
                # Rimuovi duplicati basati su edge_type, dando priorità a quelli specifici se presenti
                seen_edge_types = set()
                unique_edge_types_data = []
                for et_data in self.edge_types_data:
                    if et_data['edge_type'] not in seen_edge_types:
                        unique_edge_types_data.append(et_data)
                        seen_edge_types.add(et_data['edge_type'])
                self.edge_types_data = unique_edge_types_data

                if not self.edge_types_data:
                     messagebox.showwarning("Nessun Tipo di Bordo", f"Nessun tipo di bordo definito nel database per {self.material_name} ({self.thickness}cm) o tipi generici.", parent=self)
                     # It's important that create_widgets can handle an empty edge_types_data
                     return False # Indicate that no types were loaded
            return True # Indicate success
        except Exception as e:
            messagebox.showerror("Errore Database", f"Errore nel caricamento dei tipi di bordo: {e}", parent=self)
            self.edge_types_data = []
            return False # Indicate failure

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        edge_options = [et['edge_type'] for et in self.edge_types_data]
        if not edge_options:
            edge_options = ["Nessun bordo disponibile"]

        sides = {
            'front': {'label': 'Fronte', 'length': self.length1_cm},
            'back':  {'label': 'Retro',  'length': self.length1_cm},
            'left':  {'label': 'Sinistra', 'length': self.length2_cm},
            'right': {'label': 'Destra', 'length': self.length2_cm}
        }

        row_idx = 0
        for side_key, side_info in sides.items():
            frame = ttk.LabelFrame(main_frame, text=side_info['label'], padding="5")
            frame.grid(row=row_idx, column=0, columnspan=3, sticky="ew", pady=5)
            row_idx += 1

            cb_active = ttk.Checkbutton(frame, text="Attivo", variable=self.selected_edges[side_key]['active'], command=lambda sk=side_key: self._on_active_toggle(sk))
            cb_active.grid(row=0, column=0, padx=5, pady=2, sticky="w")

            combo_type = ttk.Combobox(frame, textvariable=self.selected_edges[side_key]['type'], values=edge_options, state="readonly", width=20)
            # Rimosso: if not self.edge_types_data: combo_type.config(state="disabled")
            # Il Combobox sarà readonly e conterrà "Nessun bordo disponibile" se edge_options è tale.
            # L'utente potrà comunque attivare il bordo, e il costo sarà 0 se nessun tipo valido è selezionato.
            combo_type.grid(row=0, column=1, padx=5, pady=2)
            combo_type.bind("<<ComboboxSelected>>", lambda e, sk=side_key: self._on_edge_type_change(sk))
            
            ttk.Label(frame, text=f"Lunghezza: {side_info['length']:.1f} cm").grid(row=0, column=2, padx=5, pady=2, sticky="w")
            ttk.Label(frame, text="Costo:").grid(row=0, column=3, padx=5, pady=2, sticky="w")
            ttk.Label(frame, textvariable=self.selected_edges[side_key]['cost_var'], width=8, anchor="e").grid(row=0, column=4, padx=5, pady=2, sticky="e")
            frame.columnconfigure(1, weight=1)

        summary_frame = ttk.LabelFrame(main_frame, text="Riepilogo Costi Bordi", padding="5")
        summary_frame.grid(row=row_idx, column=0, columnspan=3, sticky="ew", pady=(10,5))
        row_idx +=1

        ttk.Label(summary_frame, text="Costo Totale Bordi (€):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(summary_frame, textvariable=self.total_edge_cost_var, font=("Helvetica", 10, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="e")
        summary_frame.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row_idx, column=0, columnspan=3, pady=10, sticky="e")

        save_button = ttk.Button(button_frame, text="Salva Modifiche", command=self._save_changes)
        save_button.pack(side="left", padx=5)

        cancel_button = ttk.Button(button_frame, text="Annulla", command=self.destroy)
        cancel_button.pack(side="left", padx=5)

    def _load_current_details(self):
        if not self.current_edge_details: return
        for side_key, details_vars in self.selected_edges.items():
            if side_key in self.current_edge_details:
                side_data = self.current_edge_details[side_key]
                details_vars['active'].set(side_data.get('active', False))
                details_vars['type'].set(side_data.get('type', ''))

    def _on_active_toggle(self, side_key):
        # Se il bordo viene disattivato, il tipo selezionato non è più rilevante
        if not self.selected_edges[side_key]['active'].get():
            self.selected_edges[side_key]['type'].set('') # Resetta il tipo
        self._update_all_costs()

    def _on_edge_type_change(self, side_key):
        # Se un tipo viene selezionato, assicurati che il bordo sia attivo
        if self.selected_edges[side_key]['type'].get() and self.selected_edges[side_key]['type'].get() != "Nessun bordo disponibile":
            if not self.selected_edges[side_key]['active'].get():
                self.selected_edges[side_key]['active'].set(True)
        self._update_all_costs()

    def _calculate_side_cost(self, side_key):
        if not self.selected_edges[side_key]['active'].get():
            self.selected_edges[side_key]['cost_var'].set("0.00")
            return 0.0

        edge_type_name = self.selected_edges[side_key]['type'].get()

        print(f"[DEBUG] _calculate_side_cost: Calcolo per lato: {side_key}, Tipo bordo selezionato: '{edge_type_name}'")
        if not edge_type_name or not self.edge_types_data or edge_type_name == "Nessun bordo disponibile":
            print(f"[DEBUG] _calculate_side_cost: Nessun tipo di bordo valido selezionato o self.edge_types_data è vuoto. Costo impostato a 0.")
            self.selected_edges[side_key]['cost_var'].set("0.00")
            return 0.0

        price_lm = 0.0
        et_data_found = None
        print(f"[DEBUG] _calculate_side_cost: Ricerca di '{edge_type_name}' in self.edge_types_data: {self.edge_types_data}")
        for et_data in self.edge_types_data:
            if et_data['edge_type'] == edge_type_name:
                et_data_found = et_data
                print(f"[DEBUG] _calculate_side_cost: Trovato et_data: {et_data_found}")
                break
        
        if et_data_found and 'price_per_lm' in et_data_found and et_data_found['price_per_lm'] is not None:
            try:
                price_lm = float(et_data_found['price_per_lm'])
            except ValueError:
                messagebox.showerror("Errore Prezzo", f"Prezzo non valido per '{edge_type_name}': {et_data_found['price_per_lm']}", parent=self)
                print(f"[DEBUG] _calculate_side_cost: Errore nel convertire il prezzo per '{edge_type_name}'. Prezzo impostato a 0.")
                price_lm = 0.0
        elif et_data_found is None:
            messagebox.showwarning("Tipo Bordo Non Trovato", f"Dettagli per il tipo di bordo '{edge_type_name}' non trovati.", parent=self)
            print(f"[DEBUG] _calculate_side_cost: Nessun dato trovato per il tipo di bordo '{edge_type_name}'. Prezzo impostato a 0.")
        else: # et_data_found is not None, but price_per_lm might be missing or None
            print(f"[DEBUG] _calculate_side_cost: Dati trovati per '{edge_type_name}', ma 'price_per_lm' mancante o None: {et_data_found}. Prezzo impostato a 0.")
            price_lm = 0.0 # Assicura che sia 0 se il prezzo non è valido o mancante
            
        length_m = 0.0
        if side_key in ['front', 'back']:
            length_m = self.length1_cm / 100.0
        elif side_key in ['left', 'right']:
            length_m = self.length2_cm / 100.0
        
        cost = length_m * price_lm
        self.selected_edges[side_key]['cost_var'].set(f"{cost:.2f}")
        return cost

    def _update_all_costs(self):
        total_cost = 0.0
        for side_key in self.selected_edges.keys():
            total_cost += self._calculate_side_cost(side_key)
        self.total_edge_cost_var.set(f"{total_cost:.2f}")

    def _save_changes(self):
        updated_details = {}
        total_calculated_edge_cost = 0.0

        for side_key, details_vars in self.selected_edges.items():
            is_active = details_vars['active'].get()
            edge_type = details_vars['type'].get() if is_active else ''
            cost = float(details_vars['cost_var'].get()) if is_active else 0.0
            length_cm = self.length1_cm if side_key in ['front', 'back'] else self.length2_cm
            price_lm = 0.0
            if is_active and edge_type:
                 for et_data in self.edge_types_data:
                    if et_data['edge_type'] == edge_type:
                        price_lm = float(et_data['price_per_lm']) if et_data and 'price_per_lm' in et_data else 0.0
                        break
            
            updated_details[side_key] = {
                'active': is_active,
                'type': edge_type,
                'length_cm': length_cm,
                'price_lm': price_lm,
                'cost': cost
            }
            if is_active:
                total_calculated_edge_cost += cost
        
        updated_details['total_edge_cost'] = total_calculated_edge_cost

        self.parent.edge_details_map[self.row_id] = updated_details

        current_values = list(self.parent.quote_tree.item(self.row_id, 'values'))
        
        costo_lastra = float(current_values[7])
        current_values[8] = f"{total_calculated_edge_cost:.2f}"
        current_values[9] = f"{(costo_lastra + total_calculated_edge_cost):.2f}"
        
        self.parent.quote_tree.item(self.row_id, values=tuple(current_values))
        self.parent.update_summary()
        self.destroy()

if __name__ == '__main__':
    class MockApp:
        def __init__(self):
            self.edge_details_map = {}
            self.quote_tree = None
            self.total_mq_var = tk.StringVar()
            self.total_slabs_eur_var = tk.StringVar()
            self.total_edges_eur_var = tk.StringVar()
            self.total_eur_var = tk.StringVar()

        def update_summary(self):
            print("MockApp: update_summary called")

    root = tk.Tk()
    root.withdraw()
    
    mock_parent = MockApp()
    mock_row_id = "test_row_1"
    mock_material = "Marmo Test"
    mock_thickness = 2.0
    mock_len1 = 120.0
    mock_len2 = 30.0
    mock_current_edges = {
        'front': {'active': True, 'type': 'Filo Lucido', 'length_cm': 120.0, 'price_lm': 10, 'cost': 12.0},
        'total_edge_cost': 12.0
    }
    mock_parent.edge_details_map[mock_row_id] = mock_current_edges

    class MockTree:
        def item(self, row_id, values=None):
            if values:
                print(f"MockTree: item {row_id} updated with values: {values}")
                return
            return ('1', '120.0', '30.0', 'Marmo Test', '2.0', '0.3600', '100.00', '36.00', '0.00', '36.00', row_id)
    mock_parent.quote_tree = MockTree()

    def mock_get_edges(mat_name, thick):
        print(f"mock_get_edges called for {mat_name}, {thick}")
        return [
            {'edge_type': 'Filo Lucido', 'price_per_lm': 10.0},
            {'edge_type': 'Costa Retta', 'price_per_lm': 15.0},
            {'edge_type': 'Toro', 'price_per_lm': 25.0}
        ]
    database.get_edge_types_by_material_thickness = mock_get_edges
    database.get_distinct_edge_types = lambda: [('Filo Lucido',), ('Costa Retta',), ('Toro',)]

    dialog = EdgeEditorDialog(mock_parent, mock_row_id, mock_material, mock_thickness, mock_len1, mock_len2, mock_current_edges)
    root.wait_window(dialog)
    print("Dialog closed.")
    print("Updated edge details in MockApp:", mock_parent.edge_details_map.get(mock_row_id))
    root.mainloop()