from database import conectar

def registrar_vehiculo(placa, marca, modelo, anio, propietario, km=0):
    conn = conectar()
    try:
        conn.execute("""
            INSERT INTO vehiculos (placa, marca, modelo, anio, propietario, kilometraje)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (placa.upper(), marca, modelo, anio, propietario, km))
        conn.commit()
        print(f"✅ Vehículo {placa.upper()} registrado.")
    except Exception as e:
        print(f"⚠️ {e}")
    finally:
        conn.close()

def buscar_vehiculo(placa):
    conn = conectar()
    v = conn.execute("SELECT * FROM vehiculos WHERE placa = ?",
                     (placa.upper(),)).fetchone()
    conn.close()
    return v

def historial(placa):
    conn = conectar()
    filas = conn.execute("""
        SELECT * FROM mantenimientos
        WHERE placa = ? ORDER BY fecha DESC
    """, (placa.upper(),)).fetchall()
    conn.close()
    return filas