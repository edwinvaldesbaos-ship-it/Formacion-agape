import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Formación Histórica - Iglesia Familiar Cristiana Ágape",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONTRASEÑA DE ADMINISTRACIÓN Y CONFIGURACIÓN ---
ADMIN_PASSWORD = "Agape2026"
DB_FILE = "registro_participantes_agape.db"

# --- BASE DE DATOS LOCAL Y SINCRONIZACIÓN GOOGLE SHEETS ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS participantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            fecha_inicio TEXT,
            pantalla_actual INTEGER DEFAULT 1,
            puntos_xp INTEGER DEFAULT 0,
            estado TEXT DEFAULT 'En Progreso',
            fecha_completado TEXT
        )
    ''')
    conn.commit()
    conn.close()

def sync_to_google_sheets(df):
    """
    Intenta sincronizar los datos con Google Sheets si st.connection('gsheets') o st.secrets están configurados.
    Si no está configurado aún en Streamlit Cloud, almacena localmente y permite la exportación.
    """
    try:
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            from streamlit_gsheets import GSheetsConnection
            conn_gs = st.connection("gsheets", type=GSheetsConnection)
            conn_gs.update(data=df)
            return True, "Sincronizado con Google Sheets exitosamente."
    except Exception as e:
        return False, str(e)
    return False, "Google Sheets no configurado aún en secrets."

def registrar_o_cargar_usuario(nombre):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, pantalla_actual, puntos_xp, estado, fecha_completado FROM participantes WHERE nombre = ?", (nombre,))
    user = c.fetchone()
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if user is None:
        c.execute('''
            INSERT INTO participantes (nombre, fecha_inicio, pantalla_actual, puntos_xp, estado)
            VALUES (?, ?, 1, 0, 'En Progreso')
        ''', (nombre, now_str))
        conn.commit()
        user_id = c.lastrowid
        pantalla, xp, estado, f_comp = 1, 0, 'En Progreso', None
    else:
        user_id, pantalla, xp, estado, f_comp = user
        
    conn.close()
    
    # Intentar sync
    df_all = obtener_todos_los_participantes()
    sync_to_google_sheets(df_all)
    
    return user_id, pantalla, xp, estado, f_comp

def actualizar_progreso(user_id, pantalla, xp, completado=False):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if completado:
        c.execute('''
            UPDATE participantes 
            SET pantalla_actual = ?, puntos_xp = ?, estado = 'Completado', fecha_completado = ?
            WHERE id = ?
        ''', (pantalla, xp, now_str, user_id))
    else:
        c.execute('''
            UPDATE participantes 
            SET pantalla_actual = ?, puntos_xp = ?
            WHERE id = ?
        ''', (pantalla, xp, user_id))
    conn.commit()
    conn.close()
    
    # Intentar sync
    df_all = obtener_todos_los_participantes()
    sync_to_google_sheets(df_all)

def obtener_todos_los_participantes():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(
        "SELECT id as 'ID', nombre as 'Participante', fecha_inicio as 'Fecha de Inicio', pantalla_actual as 'Pantalla Actual', puntos_xp as 'Puntos XP', estado as 'Estado', fecha_completado as 'Fecha de Finalización' FROM participantes ORDER BY id DESC", 
        conn
    )
    conn.close()
    return df

# Inicializar Base de Datos
init_db()

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
<style>
    .stApp {
        background-color: #FDFBF7;
        color: #1E2A38;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #1E2A38 0%, #2D3E50 100%);
        color: #FDFBF7;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        text-align: center;
    }
    .main-header h1 {
        color: #D4AF37 !important;
        margin-bottom: 8px;
        font-weight: 700;
    }
    .card-box {
        background-color: #FFFFFF;
        border-left: 5px solid #D4AF37;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .badge-box {
        background-color: #FFF9E6;
        border: 1px solid #D4AF37;
        color: #8A6D3B;
        padding: 12px;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        margin-top: 15px;
    }
    .stButton>button {
        background-color: #1E2A38;
        color: #FDFBF7;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #D4AF37;
        color: #1E2A38;
    }
</style>
""", unsafe_allow_html=True)

# --- CABECERA PRINCIPAL ---
st.markdown("""
<div class="main-header">
    <h1>🏛️ Formación Teológica e Histórica</h1>
    <h3>Iglesia Familiar Cristiana Ágape</h3>
    <p><i>Un recorrido interactivo desde Pentecostés hasta la Era Digital</i></p>
</div>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (Navegación & Acceso Protegido) ---
st.sidebar.title("📌 Menú Principal")
modo_view = st.sidebar.radio("Selecciona una Vista:", ["🎓 Recorrido Interactivo", "🔒 Panel de Administración (Líderes)"])

if modo_view == "🔒 Panel de Administración (Líderes)":
    st.header("🔒 Panel de Control de Administración")
    st.caption("Acceso restringido únicamente para líderes autorizados.")
    
    # Verificación de Contraseña
    input_pass = st.text_input("🔑 Ingrese la Contraseña de Administrador:", type="password")
    
    if input_pass == ADMIN_PASSWORD:
        st.success("🔓 Acceso concedido. Bienvenido/a al Panel de Administración de Ágape.")
        
        df_part = obtener_todos_los_participantes()
        
        if not df_part.empty:
            col1, col2, col3 = st.columns(3)
            total = len(df_part)
            completados = len(df_part[df_part['Estado'] == 'Completado'])
            porcentaje = round((completados / total) * 100, 1) if total > 0 else 0
            
            col1.metric("Total Participantes", total)
            col2.metric("Completados", completados)
            col3.metric("Tasa de Finalización", f"{porcentaje}%")
            
            st.subheader("📊 Tabla de Registro y Progreso")
            st.dataframe(df_part, use_container_width=True)
            
            # Integración y Descarga Google Sheets
            st.markdown("---")
            st.subheader("🟢 Sincronización con Google Sheets")
            st.info("💡 **Instrucciones para conectar con tu Google Sheet personal:**\n"
                    "1. Crea una hoja de cálculo en Google Drive llamada **'Formacion_Agape_Progreso'**.\n"
                    "2. En Streamlit Cloud, ve a `Settings` > `Secrets` y añade la URL de tu hoja bajo la clave `[connections.gsheets]`.\n"
                    "3. Cada nuevo participante o avance se actualizará automáticamente en tu hoja de Google Drive.")
            
            csv_data = df_part.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Reporte Completo (CSV / Excel)",
                data=csv_data,
                file_name="progreso_formacion_agape.csv",
                mime="text/csv"
            )
        else:
            st.info("Aún no hay participantes registrados en el sistema.")
            
    elif input_pass != "":
        st.error("❌ Contraseña incorrecta. Solo el administrador con la clave autorizada puede ver el progreso de los participantes.")
    else:
        st.warning("⚠️ Esta área requiere la contraseña (`Agape2026`) para visualizar los registros.")

else:
    # --- MODO RECORRIDO INTERACTIVO (Para Estudiantes) ---
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
        st.session_state.nombre = ""
        st.session_state.pantalla = 1
        st.session_state.xp = 0

    # Pantalla de Registro Inicial
    if st.session_state.user_id is None:
        st.markdown("""
        <div class="card-box">
            <h3>👋 ¡Bienvenido/a a la Formación Virtual!</h3>
            <p>Para comenzar tu recorrido histórico y registrar tu progreso, por favor ingresa tu nombre completo a continuación:</p>
        </div>
        """, unsafe_allow_html=True)
        
        nombre_input = st.text_input("Escribe tu Nombre y Apellido:", placeholder="Ej. Maria Gonzalez")
        
        if st.button("🚀 Comenzar Formación"):
            if nombre_input.strip() != "":
                u_id, pant, xp_val, estado, f_comp = registrar_o_cargar_usuario(nombre_input.strip())
                st.session_state.user_id = u_id
                st.session_state.nombre = nombre_input.strip()
                st.session_state.pantalla = pant
                st.session_state.xp = xp_val
                st.success(f"¡Bienvenido/a {nombre_input.strip()}! Tu progreso se guardará automáticamente.")
                st.rerun()
            else:
                st.warning("Por favor ingresa un nombre válido para continuar.")

    else:
        # Estado del Usuario Registrado
        st.sidebar.markdown("---")
        st.sidebar.subheader("👤 Participante Actual")
        st.sidebar.write(f"**Nombre:** {st.session_state.nombre}")
        st.sidebar.write(f"**Puntos XP:** {st.session_state.xp} ⭐")
        st.sidebar.progress(min(st.session_state.pantalla / 5, 1.0))
        st.sidebar.caption(f"Pantalla {st.session_state.pantalla} de 5")
        
        if st.sidebar.button("🔒 Cerrar Sesión / Cambiar Usuario"):
            st.session_state.user_id = None
            st.session_state.nombre = ""
            st.rerun()

        # --- CONTENIDO DE PANTALLAS ---
        
        # PANTALLA 1
        if st.session_state.pantalla == 1:
            st.subheader("Pantalla 1: La Iglesia Primitiva y las Persecuciones (Siglos I - III)")
            st.markdown("""
            <div class="card-box">
                <h4>📜 De Pentecostés a la Clandestinidad</h4>
                <p>Tras Pentecostés, el cristianismo experimentó una rápida expansión a pesar de ser declarado ilegal por el Imperio Romano. Durante este periodo, la iglesia creció en clandestinidad bajo duras persecuciones imperiales dirigidas por emperadores como <b>Nerón, Domiciano y Diocleciano</b>.</p>
                <p>En medio de estas pruebas surgieron los <i>apologetas</i> (defensores de la fe) y el <i>monasticismo primitivo</i> (encabezado por Pacomio en Egipto), fundamentales para la preservación de las Escrituras y la formación espiritual.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("💡 Pregunta de Afianzamiento (Recompensa: +100 XP)")
            q1 = st.radio(
                "¿Qué función crucial cumplió el monasticismo primitivo y los apologetas durante este periodo?",
                [
                    "A) Gobernar políticamente el Imperio Romano",
                    "B) Defender la fe y preservar los manuscritos bíblicos en medio de la persecución",
                    "C) Eliminar la enseñanza del Evangelio en las ciudades"
                ]
            )
            
            if st.button("Enviar Respuesta - Pantalla 1"):
                if "B)" in q1:
                    st.success("¡Correcto! 🎉 Has ganado la Insignia **'Apologeta Primitivo'** y +100 XP.")
                    st.session_state.xp += 100
                    st.session_state.pantalla = 2
                    actualizar_progreso(st.session_state.user_id, 2, st.session_state.xp)
                    st.rerun()
                else:
                    st.error("Respuesta incorrecta. Revisa el texto y vuelve a intentarlo.")

        # PANTALLA 2
        elif st.session_state.pantalla == 2:
            st.subheader("Pantalla 2: Giro Constantiniano y el Concilio de Nicea (Siglo IV)")
            st.markdown("""
            <div class="card-box">
                <h4>🏛️ Legalización y Definición Teológica</h4>
                <p>En el año 313 d.C., el emperador Constantino promulgó el <b>Edicto de Milán</b>, legalizando el cristianismo. Más tarde, en el año 325 d.C., convocó el <b>Concilio de Nicea</b> para combatir la herejía del arianismo y definir la divinidad de Jesucristo.</p>
                <hr>
                <h5>💡 Clarificación Teológica Fundamental:</h5>
                <ul>
                    <li><b>Catolicidad:</b> Proviene del griego <i>katholikos</i> ("universal"). Es la cualidad original de la iglesia primitiva abierta a todas las naciones y pueblos sin distinción.</li>
                    <li><b>Catolicismo Romano:</b> Desarrollo institucional, político y dogmático con sede en Roma que se consolidó progresivamente tras la oficialización del cristianismo con el emperador Teodosio I.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("💡 Pregunta de Afianzamiento (Recompensa: +100 XP)")
            q2 = st.radio(
                "¿Cuál es la diferencia entre 'catolicidad' y 'catolicismo romano' según las notas de estudio?",
                [
                    "A) Son exactamente lo mismo y significan lo mismo en la historia.",
                    "B) Catolicidad es la cualidad de universalidad de la iglesia primitiva; Catolicismo Romano es la estructura institucional consolidada en Roma.",
                    "C) Catolicidad se refiere a la iglesia protestante y Catolicismo a los apologetas."
                ]
            )
            
            if st.button("Enviar Respuesta - Pantalla 2"):
                if "B)" in q2:
                    st.success("¡Excelente precisión teológica! 📜 Ganaste la Insignia **'Defensor de Nicea'** y +100 XP.")
                    st.session_state.xp += 100
                    st.session_state.pantalla = 3
                    actualizar_progreso(st.session_state.user_id, 3, st.session_state.xp)
                    st.rerun()
                else:
                    st.error("Respuesta incorrecta. Recuerda la distinción entre universalidad e institucionalización.")

        # PANTALLA 3
        elif st.session_state.pantalla == 3:
            st.subheader("Pantalla 3: Edad Media y el Gran Cisma de 1054 (Siglos V - XV)")
            st.markdown("""
            <div class="card-box">
                <h4>🏰 Cisma, Preservación y Universidad</h4>
                <p>Con la caída del Imperio Romano de Occidente (476 d.C.), la iglesia asumió un rol central en la preservación de la cultura europea. Los monasterios copiaban meticulosamente las Sagradas Escrituras.</p>
                <p>En el año <b>1054 d.C.</b> ocurrió el <b>Gran Cisma</b>, dividiendo a la Cristiandad entre la Iglesia Católica Romana (Occidente) y la Iglesia Ortodoxa (Oriente) debido a disputas teológicas, litúrgicas y de autoridad papal.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("💡 Pregunta de Afianzamiento (Recompensa: +100 XP)")
            q3 = st.radio(
                "¿Qué hito marcó la división definitiva entre la iglesia occidental (Latina) y oriental (Griega) en el siglo XI?",
                [
                    "A) La Reforma Protestante de Lutero",
                    "B) El Gran Cisma de 1054 d.C.",
                    "C) La traducción de la Biblia al español por Casiodoro de Reina"
                ]
            )
            
            if st.button("Enviar Respuesta - Pantalla 3"):
                if "B)" in q3:
                    st.success("¡Correcto! 🏛️ Has desbloqueado la Insignia **'Guardián Histórico'** y +100 XP.")
                    st.session_state.xp += 100
                    st.session_state.pantalla = 4
                    actualizar_progreso(st.session_state.user_id, 4, st.session_state.xp)
                    st.rerun()
                else:
                    st.error("Respuesta incorrecta. Inténtalo de nuevo.")

        # PANTALLA 4
        elif st.session_state.pantalla == 4:
            st.subheader("Pantalla 4: La Reforma Protestante y la Biblia Vernácula (Siglos XVI - XVII)")
            st.markdown("""
            <div class="card-box">
                <h4>📖 El Retorno a las Escrituras</h4>
                <p>En 1517, <b>Martín Lutero</b> clavó las 95 Tesis en la puerta de la iglesia de Wittenberg, cuestionando las indulgencias y llamando al arrepentimiento. Esto desencadenó la <b>Reforma Protestante</b>, impulsada por la invención de la imprenta de Gutenberg y la labor de traductores como John Wycliffe, Juan Hus, y más adelante Casiodoro de Reina y Cipriano de Valera.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("💡 Pregunta de Afianzamiento (Recompensa: +100 XP)")
            q4 = st.radio(
                "¿Qué tecnología y qué factor teológico fueron clave para expandir la Reforma Protestante?",
                [
                    "A) La imprenta de Gutenberg y la traducción de la Biblia a la lengua del pueblo (vernácula)",
                    "B) El uso de redes sociales y el Edicto de Milán",
                    "C) Las indulgencias papales y las cruzadas"
                ]
            )
            
            if st.button("Enviar Respuesta - Pantalla 4"):
                if "A)" in q4:
                    st.success("¡Magnífico! 📖 Has ganado la Insignia **'Reformador de Wittenberg'** y +100 XP.")
                    st.session_state.xp += 100
                    st.session_state.pantalla = 5
                    actualizar_progreso(st.session_state.user_id, 5, st.session_state.xp)
                    st.rerun()
                else:
                    st.error("Respuesta incorrecta. Revisa el texto sobre Gutenberg y las traducciones.")

        # PANTALLA 5
        elif st.session_state.pantalla == 5:
            st.subheader("Pantalla 5: Avivamientos y Desafíos Contemporáneos (Siglos XVIII - XXI)")
            st.markdown("""
            <div class="card-box">
                <h4>🔥 De Azusa a la Era Digital</h4>
                <p>El cristianismo contemporáneo fue modelado por grandes movimientos de avivamiento, como el metodismo fundado por <b>John Wesley</b> y el surgimiento del movimiento pentecostal en la <b>Calle Azusa (1906)</b> en Los Ángeles.</p>
                <p>Hoy, la <b>Iglesia Familiar Cristiana Ágape</b> y la iglesia global enfrentan el desafío de comunicar la fe inmutable del Evangelio a través de plataformas digitales y redes sociales.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("🏆 Evaluación Final y Finalización")
            q5 = st.radio(
                "¿Cuál es el propósito central de estudiar la historia de la iglesia en la congregación?",
                [
                    "A) Memorizar fechas sin aplicación práctica",
                    "B) Valorar nuestras raíces teológicas, aprender del pasado y comunicar la fe con efectividad hoy",
                    "C) Criticar a otras culturas e imperios antiguos"
                ]
            )
            
            if st.button("🎓 Finalizar Formación y Obtener Certificado"):
                if "B)" in q5:
                    st.session_state.xp += 100
                    actualizar_progreso(st.session_state.user_id, 5, st.session_state.xp, completado=True)
                    st.balloons()
                    st.markdown(f"""
                    <div class="badge-box">
                        <h2>🏆 ¡FELICITACIONES, {st.session_state.nombre.upper()}!</h2>
                        <p>Has completado exitosamente la formación histórica y teológica de la <b>Iglesia Familiar Cristiana Ágape</b>.</p>
                        <p><b>Puntaje Total acumulado:</b> {st.session_state.xp} XP ⭐</p>
                        <p><i>Tu registro de finalización ha sido guardado exitosamente en el sistema.</i></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Por favor selecciona la opción correcta para finalizar.")
