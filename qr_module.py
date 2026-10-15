import qrcode
import os

# Intentamos importar cv2 y pyzbar, pero si fallan (ej. en la nube), no rompemos la app
try:
    import cv2
    from pyzbar.pyzbar import decode
    CAMARA_DISPONIBLE = True
except ImportError:
    CAMARA_DISPONIBLE = False

QR_DIR = "qr_codes"

def generar_qr(codigo):
    """Genera un PNG con el código QR que se pegará en la pieza física."""
    os.makedirs(QR_DIR, exist_ok=True)
    img = qrcode.make(codigo)
    ruta = os.path.join(QR_DIR, f"{codigo}.png")
    img.save(ruta)
    print(f"✅ QR generado: {ruta}")
    return ruta

def escanear_qr():
    """
    Abre la webcam y devuelve el texto del primer QR detectado.
    Solo funciona en local. En la nube (Streamlit Cloud) retorna None.
    """
    if not CAMARA_DISPONIBLE:
        print("⚠️ Escaneo con cámara no disponible en este entorno.")
        return None
    
    cap = cv2.VideoCapture(0)
    print("📷 Apunta la cámara al QR. Presiona 'q' para salir.")
    codigo_detectado = None
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        for obj in decode(frame):
            codigo_detectado = obj.data.decode("utf-8")
            pts = obj.polygon
            if len(pts) == 4:
                import numpy as np
                pts = np.array([(p.x, p.y) for p in pts], dtype="int32")
                cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
            cv2.putText(frame, codigo_detectado, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Mecanica System - Escaner QR", frame)
        if codigo_detectado or cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return codigo_detectado