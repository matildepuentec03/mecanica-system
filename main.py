from database import crear_tablas
import parts, qr_module, vehicles, maintenance

def menu():
    crear_tablas()
    while True:
        print("""
╔══════════════════════════════════════════╗
║        MECÁNICA SYSTEM  🔧🚗             ║
╠══════════════════════════════════════════╣
║ 1. Registrar autoparte                   ║
║ 2. Buscar ficha técnica por código       ║
║ 3. Generar QR de una pieza               ║
║ 4. Escanear QR con cámara                ║
║ 5. Registrar vehículo                    ║
║ 6. Registrar mantenimiento               ║
║ 7. Ver recordatorios pendientes          ║
║ 8. Ver historial de un vehículo          ║
║ 0. Salir                                 ║
╚══════════════════════════════════════════╝
""")
        op = input("Opción: ").strip()

        if op == "1":
            c = input("Código (ej MOT-002): ")
            n = input("Nombre: ")
            f = input("Función: ")
            u = input("Ubicación: ")
            e = input("Especificaciones: ")
            fa = input("Fallas comunes: ")
            ca = input("Causas: ")
            se = input("Señales de falla: ")
            parts.agregar_parte(c, n, f, u, e, fa, ca, se)

        elif op == "2":
            parts.mostrar_ficha(input("Código: ").strip().upper())

        elif op == "3":
            qr_module.generar_qr(input("Código a generar QR: ").strip().upper())

        elif op == "4":
            codigo = qr_module.escanear_qr()
            if codigo:
                parts.mostrar_ficha(codigo)

        elif op == "5":
            placa = input("Placa: ")
            marca = input("Marca: ")
            modelo = input("Modelo: ")
            anio = int(input("Año: "))
            prop = input("Propietario: ")
            km = int(input("Kilometraje (0 si n/d): ") or 0)
            vehicles.registrar_vehiculo(placa, marca, modelo, anio, prop, km)

        elif op == "6":
            placa = input("Placa: ")
            tipo = input("Tipo (aceite/filtro_aire/frenos/llantas/revision_general): ")
            desc = input("Descripción: ")
            km = input("Kilometraje actual (Enter para omitir): ")
            maintenance.registrar_mantenimiento(placa, tipo, desc,
                                                 int(km) if km else None)

        elif op == "7":
            maintenance.recordatorios_pendientes()

        elif op == "8":
            placa = input("Placa: ")
            for h in vehicles.historial(placa):
                print(f"  {h['fecha']} · {h['tipo']} · {h['descripcion']} "
                      f"(próx: {h['proxima_revision']})")

        elif op == "0":
            print("👋 Hasta luego, futuro mecánico.")
            break
        else:
            print("❌ Opción inválida.")

if __name__ == "__main__":
    menu()