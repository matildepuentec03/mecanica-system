"""Generación, lectura y validación de códigos QR para Mecánica System."""
import json
import os
import re

import qrcode

QR_DIR = os.path.join(os.path.dirname(__file__), "qr_codes")


def crear_contenido_qr(tipo, identificador, datos=None):
    """Crea un payload versionado; el contenido complementa, no reemplaza, la BD."""
    return json.dumps({
        "version": 1,
        "tipo": str(tipo).strip().lower(),
        "id": str(identificador).strip(),
        "datos": datos or {},
    }, ensure_ascii=False, separators=(",", ":"))


def generar_qr(codigo, tipo="autoparte", datos=None):
    """Genera un PNG QR. Acepta códigos antiguos de texto plano."""
    os.makedirs(QR_DIR, exist_ok=True)
    contenido = codigo if isinstance(codigo, str) and codigo.lstrip().startswith("{") else crear_contenido_qr(tipo, codigo, datos)
    identificador = str(codigo)
    if isinstance(contenido, str) and contenido.lstrip().startswith("{"):
        try:
            identificador = str(json.loads(contenido).get("id", codigo))
        except (json.JSONDecodeError, AttributeError):
            pass
    nombre = re.sub(r"[^A-Za-z0-9_.-]+", "_", identificador)[:80] or "registro"
    ruta = os.path.join(QR_DIR, f"{nombre}.png")
    qrcode.make(contenido).save(ruta)
    return ruta


def leer_qr_desde_bytes(contenido_imagen):
    """Decodifica un QR desde bytes de una foto cargada o tomada con Streamlit."""
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("Falta OpenCV. Instala las dependencias de requirements.txt.") from exc

    imagen = cv2.imdecode(np.frombuffer(contenido_imagen, dtype=np.uint8), cv2.IMREAD_COLOR)
    if imagen is None:
        raise ValueError("El archivo no parece ser una imagen válida.")
    detector = cv2.QRCodeDetector()
    texto, puntos, _ = detector.detectAndDecode(imagen)
    if not texto:
        raise ValueError("No se encontró un QR legible. Acerca el código, mejora la luz o prueba otra imagen.")
    return interpretar_contenido_qr(texto)


def interpretar_contenido_qr(texto):
    """Admite payload JSON nuevo y códigos antiguos como MOT-001 o ABC-123."""
    try:
        obj = json.loads(texto)
    except (json.JSONDecodeError, TypeError):
        return {"version": 0, "tipo": "auto", "id": str(texto).strip(), "datos": {}}

    if not isinstance(obj, dict):
        raise ValueError("El contenido del QR no tiene el formato esperado.")
    tipo = str(obj.get("tipo", "auto")).strip().lower()
    identificador = str(obj.get("id", "")).strip()
    datos = obj.get("datos", {})
    if not identificador:
        raise ValueError("El QR no contiene un identificador.")
    if tipo not in {"auto", "autoparte", "parte", "vehiculo", "mantenimiento"}:
        raise ValueError(f"Tipo de QR no reconocido: {tipo}")
    if not isinstance(datos, dict):
        datos = {}
    return {"version": obj.get("version", 1), "tipo": tipo, "id": identificador, "datos": datos}
