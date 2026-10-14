import sqlite3
import os

DB_PATH = os.path.join("data", "mecanica.db")

def conectar():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acceder por nombre de columna
    return conn

def crear_tablas():
    conn = conectar()
    cur = conn.cursor()

    # 1. Autopartes / componentes del motor
    cur.execute("""
        CREATE TABLE IF NOT EXISTS partes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,      -- ej: MOT-001
            nombre TEXT NOT NULL,             -- ej: Filtro de aceite
            funcion TEXT,
            ubicacion TEXT,
            especificaciones TEXT,
            fallas_comunes TEXT,
            causas TEXT,
            senales TEXT
	    foto TEXT
        )
    """)

    # Migración: agregar columna 'foto' si la tabla ya existía sin ella 
    try:
        cur.execute("ALTER TABLE partes ADD COLUMN foto TEXT")
        print ("🔧 Columna 'foto' agregada a la tabla partes.")
    except sqlite3.OperationalError:
        pass  # Ya existe la columna, no hacer nada


    # 2. Vehículos (registro por placa)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vehiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT UNIQUE NOT NULL,
            marca TEXT,
            modelo TEXT,
            anio INTEGER,
            propietario TEXT,
            kilometraje INTEGER DEFAULT 0
        )
    """)

    # 3. Mantenimientos
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mantenimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL,
            tipo TEXT,               -- preventivo / correctivo
            descripcion TEXT,
            fecha TEXT,
            proxima_revision TEXT,
            FOREIGN KEY (placa) REFERENCES vehiculos(placa)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Tablas creadas correctamente.")