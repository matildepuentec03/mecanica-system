import streamlit as st
import os
from datetime import datetime, timedelta
from database import conectar, crear_tablas
from parts import agregar_parte, buscar_por_codigo
from qr_module import generar_qr
from vehicles import registrar_vehiculo, buscar_vehiculo, historial
from maintenance import registrar_mantenimiento

# ==========================================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================================
st.set_page_config(
    page_title="Mecánica System PRO",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

crear_tablas()

# ==========================================================
# 🎨 CSS PERSONALIZADO - ESTILO AUTOMOTRIZ PROFESIONAL
# ==========================================================
st.markdown("""
<style>
    /* Fondo general */
    .stApp {
        background: linear-gradient(180deg, #0E1117 0%, #161A22 100%);
    }
    
    /* Header principal con gradiente */
    .main-header {
        background: linear-gradient(90deg, #1C1F26 0%, #2A2E38 100%);
        padding: 1.8rem 2rem;
        border-radius: 15px;
        border-left: 6px solid #E63946;
        margin-bottom: 2rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
    }
    .main-header h1 {
        color: #F1FAEE;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: 1px;
    }
    .main-header p {
        color: #A8B2BD;
        margin: 0.3rem 0 0 0;
        font-size: 1rem;
    }
    
    /* Tarjetas de métricas (KPIs) */
    .kpi-card {
        background: linear-gradient(135deg, #1C1F26 0%, #252932 100%);
        padding: 1.3rem;
        border-radius: 12px;
        border: 1px solid #2E3440;
        text-align: center;
        transition: transform 0.2s, border-color 0.2s;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: #E63946;
    }
    .kpi-number {
        font-size: 2.2rem;
        font-weight: 800;
        color: #E63946;
        margin: 0;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #A8B2BD;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 0.3rem;
    }
    
    /* Tarjeta de ficha técnica */
    .ficha-card {
        background: #1C1F26;
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 4px solid #E63946;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        margin: 1rem 0;
    }
    .ficha-card h2 {
        color: #F1FAEE;
        margin-top: 0;
        border-bottom: 1px solid #2E3440;
        padding-bottom: 0.7rem;
    }
    .ficha-item {
        background: #252932;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #457B9D;
    }
    .ficha-item .label {
        color: #A8B2BD;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .ficha-item .value {
        color: #F1FAEE;
        font-size: 1rem;
        margin-top: 0.2rem;
    }
    .ficha-item.warning { border-left-color: #F4A261; }
    .ficha-item.danger  { border-left-color: #E63946; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A0D12 0%, #1C1F26 100%);
        border-right: 1px solid #2E3440;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(90deg, #E63946 0%, #C1121F 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.2s;
        box-shadow: 0 4px 12px rgba(230, 57, 70, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(230, 57, 70, 0.5);
    }
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background-color: #1C1F26 !important;
        color: #F1FAEE !important;
        border: 1px solid #2E3440 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus {
        border-color: #E63946 !important;
        box-shadow: 0 0 0 2px rgba(230, 57, 70, 0.2) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1C1F26;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #A8B2BD;
        border: 1px solid #2E3440;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E63946 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# FUNCIÓN PARA CONTAR DATOS (para el dashboard)
# ==========================================================
def obtener_estadisticas():
    conn = conectar()
    partes = conn.execute("SELECT COUNT(*) as c FROM partes").fetchone()["c"]
    vehiculos = conn.execute("SELECT COUNT(*) as c FROM vehiculos").fetchone()["c"]
    mantenimientos = conn.execute("SELECT COUNT(*) as c FROM mantenimientos").fetchone()["c"]
    hoy = datetime.now().date()
    limite = hoy + timedelta(days=15)
    pendientes = conn.execute("""
        SELECT COUNT(*) as c FROM mantenimientos
        WHERE date(proxima_revision) <= date(?)
    """, (limite.strftime("%Y-%m-%d"),)).fetchone()["c"]
    conn.close()
    return partes, vehiculos, mantenimientos, pendientes

# ==========================================================
# HEADER PRINCIPAL
# ==========================================================
st.markdown("""
<div class="main-header">
    <h1>🔧 MECÁNICA SYSTEM</h1>
    <p>Plataforma de educación y gestión automotriz · v2.0 PRO</p>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# DASHBOARD (solo en la vista principal)
# ==========================================================
partes_count, vehiculos_count, mantenimientos_count, pendientes_count = obtener_estadisticas()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-number">{partes_count}</p>
        <p class="kpi-label">🔩 Autopartes</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-number">{vehiculos_count}</p>
        <p class="kpi-label">🚗 Vehículos</p>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-number">{mantenimientos_count}</p>
        <p class="kpi-label">🛠️ Servicios</p>
    </div>""", unsafe_allow_html=True)
with c4:
    color = "#E63946" if pendientes_count > 0 else "#2A9D8F"
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-number" style="color:{color};">{pendientes_count}</p>
        <p class="kpi-label">🔔 Alertas</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# SIDEBAR - NAVEGACIÓN
# ==========================================================
with st.sidebar:
    st.markdown("### 🔧 MENÚ PRINCIPAL")
    menu = st.radio(
        "Selecciona una sección:",
        [
            "🏠 Inicio",
            "🔩 Autopartes",
            "🚗 Vehículos",
            "🗓️ Mantenimiento",
            "📱 Códigos QR"
        ],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("💡 *Tip:* Usa la cámara de tu celular para escanear los QR pegados en las piezas del motor.")

# ==========================================================
# SECCIÓN INICIO
# ==========================================================
if menu == "🏠 Inicio":
    st.markdown("## 🏁 Bienvenido al Taller Digital")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        Esta plataforma fusiona la *tecnología móvil* con la *formación técnica automotriz*.
        
        #### ¿Qué puedes hacer?
        - 🔩 *Consultar fichas técnicas* de cada pieza del motor mediante código QR.
        - 🚗 *Registrar vehículos* por placa y llevar su historial.
        - 🗓️ *Programar mantenimientos* con recordatorios automáticos.
        - 🎓 *Guiar prácticas* de taller vinculando teoría y hardware real.
        """)
        
        st.info("👈 *Navega en el menú lateral* para comenzar a usar cada módulo.")
    
    with col2:
        st.markdown("""
        <div class="ficha-card">
            <h2>🎯 Estado del Sistema</h2>
            <div class="ficha-item">
                <div class="label">Base de datos</div>
                <div class="value">✅ Conectada</div>
            </div>
            <div class="ficha-item">
                <div class="label">Última actualización</div>
                <div class="value">""" + datetime.now().strftime("%d/%m/%Y %H:%M") + """</div>
            </div>
            <div class="ficha-item">
                <div class="label">Versión</div>
                <div class="value">2.0 PRO</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================================
# SECCIÓN AUTOPARTES
# ==========================================================
elif menu == "🔩 Autopartes":
    st.markdown("## 🔩 Catálogo de Autopartes")
    tab1, tab2 = st.tabs(["🔍 Buscar Pieza", "➕ Registrar Pieza"])
    
    with tab1:
        col1, col2 = st.columns([3, 1])
        with col1:
            codigo_buscar = st.text_input("Código de la pieza", placeholder="Ej: MOT-001").upper()
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            buscar = st.button("🔍 Buscar", use_container_width=True)
        
        if buscar and codigo_buscar:
            pieza = buscar_por_codigo(codigo_buscar)
            if pieza:
                st.markdown(f"""
                <div class="ficha-card">
                    <h2>🔧 {pieza['nombre']} <span style="color:#E63946;font-size:1rem;">[{pieza['codigo']}]</span></h2>
                </div>
                """, unsafe_allow_html=True)

                # Mostrar foto si existe
                if pieza["foto"] and os.path.exists(pieza["foto"]):
                    col_foto, col_info = st.columns([1, 2])
                    with col_foto:
                        st.image(pieza["foto"], caption=pieza["nombre"], use_container_width=True)
                    with col_info:
                        st.markdown(f"""
                        <div class="ficha-item">
                            <div class="label">📷 Imagen de referencia</div>
                            <div class="value">Foto real de la pieza en el taller.</div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"""
                    <div class="ficha-item">
                        <div class="label">🎯 Función</div>
                        <div class="value">{pieza['funcion']}</div>
                    </div>
                    <div class="ficha-item">
                        <div class="label">📍 Ubicación</div>
                        <div class="value">{pieza['ubicacion']}</div>
                    </div>
                    <div class="ficha-item">
                        <div class="label">📐 Especificaciones</div>
                        <div class="value">{pieza['especificaciones']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class="ficha-item warning">
                        <div class="label">⚠️ Fallas comunes</div>
                        <div class="value">{pieza['fallas_comunes']}</div>
                    </div>
                    <div class="ficha-item warning">
                        <div class="label">🧠 Causas</div>
                        <div class="value">{pieza['causas']}</div>
                    </div>
                    <div class="ficha-item danger">
                        <div class="label">🔔 Señales de falla</div>
                        <div class="value">{pieza['senales']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error(f"❌ No existe ninguna pieza con el código *{codigo_buscar}*.")
    
    with tab2:
        st.markdown("#### 📝 Datos de la nueva autoparte")
        
        foto_subida = st.file_uploader(
            "📷 Sube una foto de la pieza (JPG, PNG)",
            type=["jpg", "jpeg", "png", "webp"],
            help="La foto se guardará junto con la ficha técnica de la pieza."
        )
        
        if foto_subida is not None:
            st.image(foto_subida, caption="Vista previa", width=250)
        
        with st.form("form_parte", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                c = st.text_input("Código único *", placeholder="MOT-002")
                n = st.text_input("Nombre de la pieza *", placeholder="Bomba de agua")
                f = st.text_area("Función", height=80)
                u = st.text_input("Ubicación en el vehículo")
            with c2:
                e = st.text_input("Especificaciones técnicas")
                fa = st.text_area("Fallas comunes", height=80)
                ca = st.text_area("Causas probables", height=80)
                se = st.text_area("Señales de falla", height=80)
            
            if st.form_submit_button("💾 Guardar Autoparte", use_container_width=True):
                if c and n:
                    ruta_foto = None
                    if foto_subida is not None:
                        from parts import guardar_foto
                        ruta_foto = guardar_foto(foto_subida, c.upper())
                    
                    agregar_parte(c.upper(), n, f, u, e, fa, ca, se, ruta_foto)
                    st.success(f"✅ Pieza *{n}* registrada con código {c.upper()}.")
                    st.balloons()
                else:
                    st.error("Los campos marcados con * son obligatorios.")

# ==========================================================
# SECCIÓN VEHÍCULOS
# ==========================================================
elif menu == "🚗 Vehículos":
    st.markdown("## 🚗 Gestión de Vehículos")
    tab1, tab2, tab3 = st.tabs(["➕ Registrar", "🔍 Buscar", "📋 Historial"])
    
    with tab1:
        with st.form("form_vehiculo", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                placa = st.text_input("Placa *", placeholder="ABC-123")
                marca = st.text_input("Marca *", placeholder="Toyota")
                modelo = st.text_input("Modelo", placeholder="Corolla")
            with c2:
                anio = st.number_input("Año", min_value=1900, max_value=2050, value=2020)
                prop = st.text_input("Propietario")
                km = st.number_input("Kilometraje (km)", min_value=0, value=0, step=100)
            
            if st.form_submit_button("💾 Registrar Vehículo", use_container_width=True):
                if placa and marca:
                    registrar_vehiculo(placa, marca, modelo, anio, prop, km)
                    st.success(f"✅ Vehículo *{placa.upper()}* registrado.")
                    st.balloons()
                else:
                    st.error("La placa y la marca son obligatorias.")
    
    with tab2:
        placa_buscar = st.text_input("Ingresa la placa", placeholder="ABC-123").upper()
        if st.button("🔍 Buscar Vehículo"):
            v = buscar_vehiculo(placa_buscar)
            if v:
                st.markdown(f"""
                <div class="ficha-card">
                    <h2>🚗 {v['marca']} {v['modelo']} <span style="color:#E63946;font-size:1rem;">[{v['placa']}]</span></h2>
                </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"""
                    <div class="ficha-item">
                        <div class="label">Año</div>
                        <div class="value">{v['anio']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class="ficha-item">
                        <div class="label">Kilometraje</div>
                        <div class="value">{v['kilometraje']} km</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="ficha-item">
                    <div class="label">Propietario</div>
                    <div class="value">{v['propietario'] or 'No registrado'}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("🔍 Vehículo no encontrado.")
    
    with tab3:
        placa_hist = st.text_input("Placa para historial", placeholder="ABC-123").upper()
        if st.button("📋 Ver Historial"):
            registros = historial(placa_hist)
            if registros:
                for r in registros:
                    st.markdown(f"""
                    <div class="ficha-item">
                        <div class="label">{r['fecha']} · {r['tipo'].upper()}</div>
                        <div class="value">{r['descripcion']}<br><small style="color:#A8B2BD;">Próxima revisión: {r['proxima_revision']}</small></div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📭 No hay mantenimientos registrados para esta placa.")

# ==========================================================
# SECCIÓN MANTENIMIENTO
# ==========================================================
elif menu == "🗓️ Mantenimiento":
    st.markdown("## 🗓️ Control de Mantenimiento")
    tab1, tab2 = st.tabs(["🔧 Registrar Servicio", "🔔 Alertas"])
    
    with tab1:
        with st.form("form_mantenimiento", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                placa_m = st.text_input("Placa del vehículo *", placeholder="ABC-123").upper()
                tipo = st.selectbox("Tipo de servicio", 
                    ["aceite", "filtro_aire", "frenos", "llantas", "revision_general"])
            with c2:
                km_actual = st.number_input("Kilometraje actual", min_value=0, value=0, step=100)
                st.markdown("<br>", unsafe_allow_html=True)
                st.caption("ℹ️ El sistema calculará automáticamente la próxima revisión.")
            desc = st.text_area("Descripción del trabajo realizado *", height=100)
            
            if st.form_submit_button("💾 Registrar Mantenimiento", use_container_width=True):
                if placa_m and desc:
                    registrar_mantenimiento(placa_m, tipo, desc, km_actual)
                    st.success("✅ Mantenimiento registrado y recordatorio programado.")
                else:
                    st.error("La placa y la descripción son obligatorias.")
    
    with tab2:
        st.markdown("### 🔔 Alertas de próximos servicios")
        if st.button("🔄 Actualizar Alertas", use_container_width=True):
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
            
            if filas:
                for f in filas:
                    st.markdown(f"""
                    <div class="ficha-item danger">
                        <div class="label">🚗 {f['placa']} · {f['marca']} {f['modelo']}</div>
                        <div class="value"><b>{f['tipo'].replace('_',' ').title()}</b> vence el {f['proxima_revision']}<br>
                        <small style="color:#A8B2BD;">{f['descripcion']}</small></div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("🎉 No hay recordatorios pendientes por ahora.")

# ==========================================================
# SECCIÓN QR
# ==========================================================
elif menu == "📱 Códigos QR":
    st.markdown("## 📱 Generador de Códigos QR")
    st.caption("Genera los QR que pegarás físicamente en las piezas del motor.")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        codigo_qr = st.text_input("Código de la pieza", placeholder="MOT-001").upper()
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        generar = st.button("🎨 Generar QR", use_container_width=True)
    
    if generar and codigo_qr:
        pieza = buscar_por_codigo(codigo_qr)
        if pieza:
            ruta = generar_qr(codigo_qr)
            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(ruta, caption=f"QR: {codigo_qr}", width=250)
            with c2:
                st.markdown(f"""
                <div class="ficha-card">
                    <h2>✅ QR Generado</h2>
                    <div class="ficha-item">
                        <div class="label">Pieza asociada</div>
                        <div class="value">{pieza['nombre']}</div>
                    </div>
                    <div class="ficha-item">
                        <div class="label">Ubicación</div>
                        <div class="value">{pieza['ubicacion']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.info("💡 Imprime esta imagen y pégala en la pieza física. Al escanearla con tu celular, se abrirá la ficha técnica completa.")
        else:
            st.warning(f"⚠️ La pieza {codigo_qr} no está registrada. Regístrala primero en la sección **Autopartes**.")