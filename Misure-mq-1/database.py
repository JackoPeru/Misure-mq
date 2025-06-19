import sqlite3

DATABASE_NAME = 'preventivi.db'

def get_db_connection():
    """Crea e restituisce una connessione al database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Per accedere alle colonne per nome
    return conn

def create_tables():
    """Crea la tabella dei materiali se non esiste."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            thickness REAL, -- Spessore in cm, può essere NULL
            price_per_sqm REAL NOT NULL, -- Prezzo €/m²
            description TEXT,
            supplier TEXT, -- New column for supplier
            UNIQUE (name, thickness, supplier) -- Composite unique key updated
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name TEXT, -- Can be NULL if price is general
            thickness REAL,    -- Can be NULL if price is general
            edge_type TEXT NOT NULL,
            price_per_lm REAL NOT NULL, -- Prezzo €/metro lineare
            UNIQUE (material_name, thickness, edge_type)
        )
    ''')
    conn.commit()
    conn.close()

def add_material(name, price_per_sqm, thickness=None, description='', supplier=None):
    """Aggiunge un nuovo materiale al database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO materials (name, thickness, price_per_sqm, description, supplier)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, thickness, price_per_sqm, description, supplier))
        conn.commit()
    except sqlite3.IntegrityError:
        # Updated error message
        print(f"Errore: Il materiale '{name}' con spessore '{thickness}' e fornitore '{supplier}' esiste già.")
        return None
    finally:
        conn.close()
    return cursor.lastrowid

def get_all_materials():
    """Recupera tutti i materiali dal database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Added supplier to SELECT statement
    cursor.execute('SELECT id, name, thickness, price_per_sqm, description, supplier FROM materials ORDER BY name, supplier, thickness')
    materials = cursor.fetchall()
    conn.close()
    return materials

def get_material_by_id(material_id):
    """Recupera un materiale specifico per ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Added supplier to SELECT statement
    cursor.execute('SELECT id, name, thickness, price_per_sqm, description, supplier FROM materials WHERE id = ?', (material_id,))
    material = cursor.fetchone()
    conn.close()
    return material

def update_material(material_id, name, price_per_sqm, thickness=None, description='', supplier=None):
    """Aggiorna un materiale esistente."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE materials
            SET name = ?, thickness = ?, price_per_sqm = ?, description = ?, supplier = ?
            WHERE id = ?
        ''', (name, thickness, price_per_sqm, description, supplier, material_id))
        conn.commit()
    except sqlite3.IntegrityError:
        # Updated error message
        print(f"Errore: Il nome materiale '{name}' con spessore '{thickness}' e fornitore '{supplier}' potrebbe essere già in uso da un altro record.")
        return False
    finally:
        conn.close()
    return True

def delete_material(material_id):
    """Elimina un materiale dal database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM materials WHERE id = ?', (material_id,))
    conn.commit()
    conn.close()
    # The 'return edge_types' was likely a copy-paste error and has been removed.
# --- CRUD Functions for Edge Types ---

def add_edge_type(edge_type, price_per_lm, material_name=None, thickness=None):
    """Adds a new edge type to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO edges (material_name, thickness, edge_type, price_per_lm)
            VALUES (?, ?, ?, ?)
        ''', (material_name, thickness, edge_type, price_per_lm))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Error: Edge type '{edge_type}' for material '{material_name}' and thickness '{thickness}' already exists.")
        return None
    finally:
        conn.close()
    return cursor.lastrowid

def get_all_edge_types():
    """Retrieves all edge types from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, material_name, thickness, edge_type, price_per_lm FROM edges ORDER BY material_name, thickness, edge_type')
    edge_types = cursor.fetchall()
    conn.close()
    return edge_types

def get_edge_by_id(edge_id):
    """Retrieves a specific edge type by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, material_name, thickness, edge_type, price_per_lm FROM edges WHERE id = ?', (edge_id,))
    edge = cursor.fetchone()
    conn.close()
    return edge

def update_edge_type(edge_id, edge_type, price_per_lm, material_name=None, thickness=None):
    """Updates an existing edge type."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE edges
            SET material_name = ?, thickness = ?, edge_type = ?, price_per_lm = ?
            WHERE id = ?
        ''', (material_name, thickness, edge_type, price_per_lm, edge_id))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Error: Edge type '{edge_type}' for material '{material_name}' and thickness '{thickness}' might already be in use.")
        return False
    finally:
        conn.close()
    return True

def delete_edge_type(edge_id):
    """Deletes an edge type from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM edges WHERE id = ?', (edge_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def get_edge_types_by_material_thickness(material_name, thickness):
    """Retrieves edge types filtered by material and thickness, plus generic ones.
    Prioritizes more specific matches.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT id, material_name, thickness, edge_type, price_per_lm 
        FROM edges 
        WHERE 
            (material_name = ? AND thickness = ?) OR 
            (material_name = ? AND thickness IS NULL AND ? IS NOT NULL) OR
            (material_name IS NULL AND thickness = ? AND ? IS NOT NULL) OR
            (material_name IS NULL AND thickness IS NULL)
        ORDER BY 
            CASE
                WHEN material_name = ? AND thickness = ? THEN 1
                WHEN material_name = ? AND thickness IS NULL THEN 2
                WHEN material_name IS NULL AND thickness = ? THEN 3
                WHEN material_name IS NULL AND thickness IS NULL THEN 4
                ELSE 5
            END,
            edge_type
    '''
    params = [
        material_name, thickness,
        material_name, material_name,
        thickness, thickness,
        material_name, thickness,
        material_name,
        thickness
    ]
    
    cursor.execute(query, params)
    edge_types = cursor.fetchall()
    conn.close()
    return edge_types

def get_distinct_edge_types():
    """Retrieves complete records of distinct edge types, prioritizing generic ones."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, material_name, thickness, edge_type, price_per_lm
        FROM (
            SELECT 
                id, material_name, thickness, edge_type, price_per_lm,
                ROW_NUMBER() OVER (PARTITION BY edge_type ORDER BY 
                    CASE WHEN material_name IS NULL THEN 0 ELSE 1 END, 
                    CASE WHEN thickness IS NULL THEN 0 ELSE 1 END
                ) as rn
            FROM edges
        )
        WHERE rn = 1
        ORDER BY edge_type
    ''')
    edge_types_data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return edge_types_data

def get_edge_price(material_name, thickness, edge_type):
    """Retrieves the price of a specific edge type, looking for the most precise match."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'SELECT price_per_lm FROM edges WHERE edge_type = ?'
    params = [edge_type]

    # Try matches in order of specificity
    for condition, extra_params in [
        ("AND material_name = ? AND thickness = ?", [material_name, thickness]),
        ("AND material_name = ? AND thickness IS NULL", [material_name]),
        ("AND material_name IS NULL AND thickness = ?", [thickness]),
        ("AND material_name IS NULL AND thickness IS NULL", [])
    ]:
        cursor.execute(f"{query} {condition}", params + extra_params)
        result = cursor.fetchone()
        if result:
            conn.close()
            return result['price_per_lm']
    
    conn.close()
    return None

if __name__ == '__main__':
    create_tables()
    print("Database and tables initialized.")

    # Add generic edge types
    add_edge_type("normal edge", 3.00)
    add_edge_type("polished normal edge", 7.00)
    add_edge_type("half bull nose 3cm", 25.00)
    print("Generic edge types added.")

    print("Content of 'edges' table after insertion:")
    all_edges = get_all_edge_types()
    if all_edges:
        for edge in all_edges:
            print(dict(edge))
    else:
        print("No data found in 'edges' table.")
