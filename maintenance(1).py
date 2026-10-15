from datetime import datetime, timedelta
from database import conectar

# Intervalos sugeridos por tipo de servicio (en días)
INTERVALOS = {
    "aceite": 180,
    "filtro_aire": 365,
    "frenos": 365,
    "llantas": 540,
    "revision_general": 90,
}

def registrar_mantenimiento(placa, tipo, descripcion, km_actual=None):
    hoy = datetime.now()
    dias = INTERVALOS.get(tipo, 180)
    proxima = hoy + timedelta(days=dias)

    conn = conectar()
    conn.execute("""
        INSERT INTO mantenimientos (placa, tipo, descripcion, fecha, proxima_revision)
        VALUES (?, ?, ?, ?, ?)
    """, (placa.upper(), tipo, descripcion,
          hoy.strftime("%Y-%m-%d"),
          proxima.strftime("%Y-%m-%d")))

    if km_actual is not None:
        conn.execute("UPDATE vehiculos SET kilometraje = ? WHERE placa = ?",
                     (km_actual, placa.upper()))
    conn.commit()
    conn.close()
    print(f"✅ Mantenimiento registrado. Próxima revisión: {proxima.date()}")

def recordatorios_pendientes():
    """Devuelve los mantenimientos cuya próxima revisión está vencida o por vencer (≤15 días)."""
    hoy = datetime.now().date()
    limite = hoy + timedelta(days=15)
    conn = conectar()
    filas = conn.execute("""
        SELECT v.placa, v.marca, v.modelo, m.tipo, m.descripcion, m.proxima_revision
        FROM mantenimientos m
        JOIN vehiculos v ON v.placa = m.placa
        WHERE date(m.proxima_revision) <= date(?)
    """, (limite.strftime("%Y-%m-%d"),)).fetchall()
    conn.close()

    if not filas:
        print("🎉 No hay recordatorios pendientes.")
        return
    print("\n🔔 RECORDATORIOS PENDIENTES")
    print("-"*55)
    for f in filas:
        print(f"🚗 {f['placa']} ({f['marca']} {f['modelo']}) "
              f"→ {f['tipo']} · vence {f['proxima_revision']}")