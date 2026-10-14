import os
from database import conectar

FOTOS_DIR = "fotos_partes"

def guardar_foto(archivo_subido, codigo):
    """Guarda el archivo subido en la carpeta fotos_partes y devuelve la ruta."""
    if archivo_subido is None:
        return None
    os.makedirs(FOTOS_DIR, exist_ok=True)
    extension = archivo_subido.name.split(".")[-1].lower()
    ruta = os.path.join(FOTOS_DIR, f"{codigo}.{extension}")
    with open(ruta, "wb") as f:
        f.write(archivo_subido.getbuffer())
    return ruta

def agregar_parte(codigo, nombre, funcion, ubicacion,
                  especificaciones, fallas, causas, senales, foto=None):
    conn = conectar()
    try:
        conn.execute("""
            INSERT INTO partes (codigo, nombre, funcion, ubicacion,
                                especificaciones, fallas_comunes, causas, senales, foto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (codigo, nombre, funcion, ubicacion,
              especificaciones, fallas, causas, senales, foto))
        conn.commit()
        print(f"✅ Parte '{nombre}' registrada con código {codigo}.")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        conn.close()

def buscar_por_codigo(codigo):
    conn = conectar()
    fila = conn.execute("SELECT * FROM partes WHERE codigo = ?", (codigo,)).fetchone()
    conn.close()
    return fila

def mostrar_ficha(codigo):
    p = buscar_por_codigo(codigo)
    if not p:
        print("❌ No se encontró la pieza.")
        return
    print("\n" + "="*55)
    print(f"🔩  {p['nombre']}  ({p['codigo']})")
    print("="*55)
    print(f"⚙️ Función:        {p['funcion']}")
    print(f"📍 Ubicación:      {p['ubicacion']}")
    print(f"📐 Especificación: {p['especificaciones']}")
    print(f"⚠️  Fallas comunes: {p['fallas_comunes']}")
    print(f"🧠 Causas:         {p['causas']}")
    print(f"🚨 Señales:        {p['senales']}")
    if p["foto"]:
        print(f"📷 Foto:           {p['foto']}")
    print("="*55 + "\n")