import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA (WEB SAAS PREMIUM) ---
st.set_page_config(
    page_title="Formación Histórica y Teológica - Iglesia Ágape",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BASE DE DATOS Y PERSISTENCIA ---
DB_FILE = "registro_participantes_agape.db"

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

def obtener_todos_los_participantes():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT nombre as 'Participante', fecha_inicio as 'Fecha de Inicio', pantalla_actual as 'Módulo Actual', estado as 'Estado', puntos_xp as 'Puntos XP', fecha_completado as 'Fecha de Finalización' FROM participantes ORDER BY id DESC", conn)
    conn.close()
    return df

# Inicializar DB
init_db()

# --- ESTILOS CSS WEB PREMIUM (HELVETICA, BORDES REDONDEADOS, FUENTE AMPLIA) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        background-color: #FFFFFF !important;
        color: #2B3744 !important;
        font-size: 1.25rem !important;
        line-height: 1.95 !important;
    }
    
    .stApp {
        background-color: #FFFFFF !important;
        max-width: 850px !important;
        margin: 0 auto !important;
    }

    .web-navbar {
        background: linear-gradient(135deg, #1E2A38 0%, #2D3E50 100%);
        color: #FFFFFF;
        padding: 30px 25px;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(30, 42, 56, 0.15);
        margin-bottom: 30px;
        text-align: center;
        border-bottom: 4px solid #D4AF37;
    }

    .web-navbar h1 {
        color: #D4AF37 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        font-weight: 700 !important;
        font-size: 2.3rem !important;
        margin-bottom: 8px !important;
        letter-spacing: -0.5px;
    }

    .web-navbar p {
        font-size: 1.15rem !important;
        color: #E2E8F0 !important;
        margin: 0 !important;
    }

    .card-box {
        background-color: #FFFFFF !important;
        border-left: 6px solid #D4AF37 !important;
        border-radius: 14px !important;
        padding: 32px 24px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06) !important;
        margin-bottom: 35px !important;
        border-top: 1px solid #F1F5F9;
        border-right: 1px solid #F1F5F9;
        border-bottom: 1px solid #F1F5F9;
    }

    .card-box h3, .card-box h4 {
        color: #1E2A38 !important;
        font-weight: 700 !important;
        margin-top: 0 !important;
        font-size: 1.4rem !important;
    }

    .parable-box {
        background-color: #FFFDF9 !important;
        border: 2px dashed #E5C158 !important;
        border-radius: 14px !important;
        padding: 25px !important;
        margin-bottom: 35px !important;
    }

    .parable-box h3 {
        color: #D4AF37 !important;
        font-size: 1.35rem !important;
    }

    .highlight-box {
        background-color: #FFF9E6 !important;
        border: 1px solid #D4AF37 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin: 18px 0 !important;
    }

    .character-card {
        background-color: #F8FAFC !important;
        border-left: 4px solid #1E2A38 !important;
        border-radius: 10px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, #1E2A38 0%, #2D3E50 100%) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 14px 32px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(30, 42, 56, 0.2) !important;
        transition: all 0.3s ease !important;
    }

    .stButton>button:hover {
        background: #D4AF37 !important;
        color: #1E2A38 !important;
        transform: translateY(-2px);
    }

    .stRadio label {
        font-size: 1.05rem !important;
        color: #2B3744 !important;
        padding: 8px 0 !important;
    }

    .stTextInput>div>div>input {
        border-radius: 10px !important;
        font-size: 1.05rem !important;
        padding: 12px !important;
        border: 1.5px solid #CBD5E1 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CABECERA PRINCIPAL ESTILO SITIO WEB ---
st.markdown("""
<div class="web-navbar">
    <h1>🏛️ Formación Teológica e Histórica</h1>
    <h3>Congregación Familiar Cristiana Ágape</h3>
    <p>Un recorrido interactivo y guiado desde el 400 a.C. hasta la Era Digital</p>
</div>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (Navegación & Admin) ---
st.sidebar.title("📌 Menú de la Plataforma")
modo_view = st.sidebar.radio("Selecciona tu Experiencia:", ["🎓 Mi Recorrido de Formación", "🔒 Panel de Administración (Líderes)"])

if modo_view == "🔒 Panel de Administración (Líderes)":
    st.header("🔒 Panel de Control de Liderazgo")
    st.write("El acceso a este panel es exclusivo para el liderazgo autorizado. Ingresa tu clave de acceso.")
    
    if "admin_autenticado" not in st.session_state:
        st.session_state.admin_autenticado = False
        
    if not st.session_state.admin_autenticado:
        password_admin = st.text_input("Clave de Acceso:", type="password", placeholder="••••••••", key="admin_pwd_input")
        if st.button("🔓 Desbloquear Panel"):
            if password_admin == "Agape2026":
                st.session_state.admin_autenticado = True
                st.success("Acceso concedido.")
                st.rerun()
            else:
                st.error("Clave incorrecta. Acceso denegado.")
    else:
        col_title, col_logout = st.columns([3, 1])
        with col_title:
            st.success(" Panel de Administración Activo")
        with col_logout:
            if st.button("🔒 Bloquear Panel"):
                st.session_state.admin_autenticado = False
                st.rerun()
        
        df_part = obtener_todos_los_participantes()
        
        if not df_part.empty:
            col1, col2, col3 = st.columns(3)
            total = len(df_part)
            completados = len(df_part[df_part['Estado'] == 'Completado'])
            porcentaje = round((completados / total) * 100, 1) if total > 0 else 0
            
            col1.metric("Total Participantes", total)
            col2.metric("Completados", completados)
            col3.metric("Tasa de Finalización", f"{porcentaje}%")
            
            st.subheader("📋 Registro de Avance en Tiempo Real")
            st.dataframe(df_part, use_container_width=True)
            
            csv_data = df_part.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Reporte en Excel / CSV",
                data=csv_data,
                file_name="reporte_formacion_agape.csv",
                mime="text/csv"
            )
        else:
            st.info("Aún no se han registrado participantes en la plataforma.")

else:
    # --- MODO RECORRIDO INTERACTIVO DIRECTO AL ESTUDIANTE ---
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
        st.session_state.nombre = ""
        st.session_state.pantalla = 1
        st.session_state.xp = 0

    # : Parábola, Objetivo e Inicio de Registro
    if st.session_state.user_id is None:
        st.markdown("""
        <div class="parable-box">
            <h3>📜 La Parábola del Creyente sin Raíces: La Historia de Mateo</h3>
            <p><i>Imagina a Mateo. Mateo lleva más de 10 años asistiendo fielmente a su congregación cada domingo. Canta los coros con entusiasmo, lleva su Biblia digital en el teléfono y se considera un cristiano comprometido.</i></p>
            <p><i>Un día, un compañero de estudio le pregunta: "Mateo, tú que te dices cristiano... ¿sabes de dónde salió esa Biblia en español que lees? ¿Sabes quién la tradujo y cuántas personas murieron quemadas en la hoguera para que hoy la tengas en tu pantalla? ¿Sabes por qué no le rezamos a estatuas ni compramos indulgencias? ¿Qué pasó con la iglesia entre los apóstoles y el día de hoy?"</i></p>
            <p><i>Mateo se quedó en absoluto silencio. Descubrió que vivía un <b>"cristianismo de microondas"</b>: consumía el producto final, pero ignoraba los 2,400 años de providencia, sangre, oración y estudio que lo hicieron posible.</i></p>
            <p style="font-weight: bold; color: #1E2A38;">👉 ¿Podrías ser tú este Mateo? Vamos a hacer este recorrido juntos para descubrir tus verdaderas raíces en la fe de Jesucristo.</p>
        </div>
        
        <div class="card-box">
            <h3>🎯 Objetivo de Tu Formación Teológica e Histórica</h3>
            <p>Aprenderás cómo Dios preparó el escenario geopolítico desde la Roma del 400 a.C. y la helenización, cómo nació la iglesia en Pentecostés, sus luchas en la clandestinidad, los concilios teológicos, el surgimiento de las adiciones romanas (purgatorio, indulgencias, sacramentos salvíficos), el rescate de la verdad en la Reforma Protestante y nuestro rol actual en la <b>Congregación Familiar Cristiana Ágape</b>.</p>
        </div>
        """, unsafe_allow_html=True)
        
        nombre_input = st.text_input("Escribe tu Nombre y Apellido para iniciar tu registro:", placeholder="Ej. Juan Pérez")
        
        if st.button("🚀 Iniciar Mi Recorrido de Formación"):
            if nombre_input.strip() != "":
                u_id, pant, xp_val, estado, f_comp = registrar_o_cargar_usuario(nombre_input.strip())
                st.session_state.user_id = u_id
                st.session_state.nombre = nombre_input.strip()
                st.session_state.pantalla = pant
                st.session_state.xp = xp_val
                st.success(f"¡Hola {nombre_input.strip()}! Tu viaje ha comenzado. Tu progreso se guardará automáticamente.")
                st.rerun()
            else:
                st.warning("Por favor escribe tu nombre completo para identificarte en la formación.")

    else:
        # Menú Lateral del Estudiante
        st.sidebar.markdown("---")
        st.sidebar.subheader("👤 Tu Perfil de Estudiante")
        st.sidebar.write(f"**Estudiante:** {st.session_state.nombre}")
        st.sidebar.write(f"**Puntuación XP:** {st.session_state.xp} ⭐")
        progreso_pct = min(st.session_state.pantalla / 6, 1.0)
        st.sidebar.progress(progreso_pct)
        st.sidebar.caption(f"Módulo {st.session_state.pantalla} de 6 ({int(progreso_pct*100)}% Completado)")
        
        if st.sidebar.button("🔒 Salir de la Sesión"):
            st.session_state.user_id = None
            st.session_state.nombre = ""
            st.rerun()

        # --- DESARROLLO DE PANTALLAS CON DIRECCIÓN DIRECTA ("TÚ") ---
        
        # PANTALLA 1
        if st.session_state.pantalla == 1:
            st.subheader("Roma, la Helenización y la Preparación del Escenario (400 a.C. - Siglo I a.C.)")
            st.markdown("""
            <div class="card-box">
                <h4>🏛️ ¿Cómo preparó Dios el mundo para la venida del Mesías?</h4>
                <p>¡Hola y bienvenido/a! <b>Vamos a hacer este recorrido juntos</b>. Para comprender el Nuevo Testamento, <b>debes viajar cuatro siglos antes de Cristo</b>. Durante este periodo, dos fuerzas geopolíticas prepararon el camino:</p>
                
                <div class="highlight-box">
                    <h5>🔑 Dos Conceptos Clave que Debes Dominar:</h5>
                    <ul>
                        <li><b>¿Qué es Roma y su Imperio?:</b> Roma comenzó como una república que hacia el 400 a.C. inició una expansión militar. Se convirtió en el Imperio Romano, aportando la <i>Pax Romana</i>, un sistema legal uniforme y una inmensa red de <b>carreteras y calzadas seguras</b>. Gracias a esto, los apóstoles pudieron viajar miles de kilómetros anunciando el Evangelio.</li>
                        <li><b>¿Qué es la Helenización?:</b> Es la difusión de la cultura y del <b>idioma griego Koiné</b> iniciada por Alejandro Magno (Siglo IV a.C.). Unificó el idioma del mundo conocido, permitiendo traducir el Antiguo Testamento al griego (<b>la Septuaginta LXX</b>) y escribir el Nuevo Testamento en una lengua universal.</li>
                    </ul>
                </div>

                <h5>👤 Personajes Clave del Módulo 1:</h5>
                <div class="character-card">
                    <b>• Alejandro Magno (356–323 a.C.):</b> Rey de Macedonia y estratega militar. <i>Interés:</i> Difundir el helenismo. <i>Impacto:</i> Aportó el griego Koiné en el que se redactó el Nuevo Testamento.
                </div>
                <div class="character-card">
                    <b>• César Augusto (63 a.C.–14 d.C.):</b> Primer emperador romano. <i>Interés:</i> Pax romana y administración imperial. <i>Impacto:</i> Bajo su censo nació Jesús (Lucas 2:1) y sus carreteras sirvieron para la difusión de la fe.
                </div>
                
                <p><i>¿Ya tomaste nota de estas fechas y eventos en tu libreta? Continuemos con otros puntos muy interesantes.</i></p>
            </div>
            """, unsafe_allow_html=True)
            
            
            st.markdown("##### 📺 Recurso Audiovisual de Refuerzo:")
            st.video("https://example.com/video_educativo.mp4")
            st.caption("🎥 *Video de refuerzo audiovisual para profundizar en los contenidos de este tema.*")
            st.markdown("<br>", unsafe_allow_html=True)
st.subheader("💡 Pregunta de Afianzamiento (Recompensa: +100 XP)")
            q1 = st.radio(
                "¿Cómo contribuyeron Roma y la Helenización a la preparación del mundo para el Evangelio?",
                [
                    "A) Roma prohibió el uso del griego y aisló las ciudades de Judea.",
                    "B) Roma aportó paz y carreteras seguras; la Helenización unificó el idioma griego Koiné y la Septuaginta.",
                    "C) Ninguna de las anteriores, el Evangelio solo se difundió en latín."
                ]
            )
            
            if st.button("Confirmar Respuesta y Avanzar"):
                if "B)" in q1:
                    st.success("¡Excelente deducción histórica! 🎉 Has desbloqueado tu primera Insignia: **'Pionero del Escenario Histórico'** y +100 XP.")
                    st.session_state.xp += 100
                    st.session_state.pantalla = 2
                    actualizar_progreso(st.session_state.user_id, 2, st.session_state.xp)
                    st.rerun()
                else:
                    st.error("Respuesta incorrecta. Revisa el recuadro sobre la Pax Romana y el griego Koiné.")

        # PANTALLA 2
        elif st.session_state.pantalla == 2:
            st.subheader("La Iglesia Primitiva, Persecución y Apologética (Siglos I - III d.C.)")
            st.markdown("""
            <div class="card-box">
                <h4>📜 De Pentecostés a la Clandestinidad</h4>
                <p>Avancemos a nuestro siguiente paso. Tras Pentecostés, la iglesia creció con poder, pero al separarse del judaísmo perdió la protección legal romana y fue perseguida por emperadores como <b>Nerón, Domiciano y Diocleciano</b>. Durante esta etapa destacan dos pilares de preservación:</p>
                
                <div class="highlight-box">
                    <h5>🛡️ Tu Aprendizaje Teológico Clave:</h5>
                    <p>• <b>Los Apologetas:</b> Defensores teológicos que redactaron escritos para argumentar la verdad bíblica frente a calumnias y persecuciones.<br/>
                    • <b>Monasticismo Primitivo:</b> Comunidades de oración e intercesión (como Pacomio en Egipto), donde los monjes copistas se dedicaron a copiar meticulosamente los manuscritos bíblicos en papiro y pergamino.</p>
                </div>

                <h5>👤 Personajes Clave del Módulo 2:</h5>
                <div class="character-card">
                    <b>• Emperador Nerón (37–68 d.C.):</b> Culpó a los cristianos del incendio de Roma (64 d.C.). Ejecutó a Pedro y Pablo.
                </div>
                <div class="character-card">
                    <b>• Justino Mártir (100–165 d.C.):</b> Filósofo convertido en apologeta. Defendió la fe ante el Senado romano hasta su martirio.
                </div>
                <div class="character-card">
                    <b>• Pacomio (292–346 d.C.):</b> Padre del monasticismo cenobítico en Egipto. Organizó comunidades dedicadas a copiar manuscritos bíblicos.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            
            st.markdown("##### 📺 Recurso Audiovisual de Refuerzo:")
            st.video("https://example.com/video_educativo.mp4")
            st.caption("🎥 *Video de refuerzo audiovisual para profundizar en los contenidos de este tema.*")
            st.markdown("<br>", unsafe_allow_html=True)
st.subheader("💡 Pregunta de Afianzamiento (Recompensa: +100 XP)")
            q2 = st.radio(
                "¿Qué rol desempeñaron los Apologetas y el monasticismo primitivo durante las persecuciones?",
                [
                    "A) Defender la fe bíblica con argumentos sólidos y copiar manuscritos de las Escrituras.",
                    "B) Buscar cargos políticos dentro del Senado romano para cobrar impuestos.",
                    "C) Cancelar las reuniones de la iglesia y eliminar el Antiguo Testamento."
                ]
            )
            
            if st.button("Confirmar Respuesta y Avanzar"):
                if "A)" in q2:
                    st.success("¡Respuesta Correcta! 🛡️ Has obtenido la Insignia: **'Apologeta de la Fe'** y +100 XP.")
                    st.session_state.xp += 100
                    st.session_state.pantalla = 3
                    actualizar_progreso(st.session_state.user_id, 3, st.session_state.xp)
                    st.rerun()
                else:
                    st.error("Respuesta incorrecta. Recuerda la labor de preservación y defensa doctrinal.")

        # PANTALLA 3
        elif st.session_state.pantalla == 3:
            st.subheader("Giro Constantiniano y Catolicidad vs. Catolicismo (Siglo IV d.C.)")
            st.markdown("""
            <div class="card-box">
                <h4>🏛️ Legalización y la Distinción Teológica Crucial</h4>
                <p>Llegamos a un momento de quiebre. En el 313 d.C., Constantino promulga el <b>Edicto de Milán</b>, legalizando el cristianismo. En el 325 d.C. se convoca el <b>Concilio de Nicea</b> para combatir el arianismo y proclamar la deidad de Cristo. Sin embargo, debes comprender esta distinción fundamental:</p>
                
                <div class="highlight-box">
                    <h5>💡 Aprende la Diferencia entre Catolicidad y Catolicismo Romano:</h5>
                    <ul>
                        <li><b>Catolicidad (del griego <i>katholikos</i> = "universal"):</b> Es la cualidad bíblica original de la iglesia primitiva enviada a todas las naciones. Es la fe pura compartida por el cuerpo de Cristo.</li>
                        <li><b>Catolicismo Romano:</b> Es la estructura político-religiosa e institucional centrada en Roma que se desarrolló progresivamente tras la oficialización estatal impulsada por Teodosio I (380 d.C.).</li>
                    </ul>
                </div>

                <h5>👤 Personajes Clave del Módulo 3:</h5>
                <div class="character-card">
                    <b>• Constantino I (272–337 d.C.):</b> Emperador romano que legalizó la iglesia e inició la mezcla Estado-Iglesia.
                </div>
                <div class="character-card">
                    <b>• Atanasio de Alejandría (296–373 d.C.):</b> Teólogo que defendió en Nicea que Jesús es verdaderamente Dios (<i>Homoousios</i>).
                </div>
                <div class="character-card">
                    <b>• Emperador Teodosio I (347–395 d.C.):</b> Proclamó el cristianismo romano como religión estatal obligatoria.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            
            st.markdown("##### 📺 Recurso Audiovisual de Refuerzo:")
            st.video("https://example.com/video_educativo.mp4")
            st.caption("🎥 *Video de refuerzo audiovisual para profundizar en los contenidos de este tema.*")
            st.markdown("<br>", unsafe_allow_html=True)
st.subheader("💡 Pregunta de Afianzamiento (Recompensa: +100 XP)")
            q3 = st.radio(
                "Como estudiante de la Palabra, ¿cómo diferencias la 'catolicidad' del 'catolicismo romano'?",
                [
                    "A) Son términos idénticos que significan exactamente lo mismo en la Biblia.",
                    "B) Catolicidad es la universalidad de la iglesia bíblica; Catolicismo Romano es la estructura institucional iniciada tras la oficialización estatal.",
                    "C) Catolicidad es un invento del siglo XX y Catolicismo Romano fue fundado en Pentecostés."
                ]
            )
            
            if st.button("Confirmar Respuesta y Avanzar"):
                if "B)" in q3:
                    st.success("¡Excelente comprensión teológica! 📜 Ganaste la Insignia: **'Defensor de Nicea'** y +100 XP.")
                    st.session_state.xp += 100
                    st.session_state.pantalla = 4
                    actualizar_progreso(st.session_state.user_id, 4, st.session_state.xp)
                    st.rerun()
                else:
                    st.error("Respuesta incorrecta. Vuelve a revisar la distinción entre universalidad e institución.")

        # PANTALLA 4
        elif st.session_state.pantalla == 4:
            st.subheader("Adiciones Dogmáticas de Roma: Purgatorio, Indulgencias y Cisma (Siglos V - XV d.C.)")
            st.markdown("""
            <div class="card-box">
                <h4>🏰 Las Desviaciones Doctrinales e Institucionales de Roma</h4>
                <p>Acompañame a analizar cómo la iglesia institucional de Roma fue agregando dogmas humanos alejados de la verdad bíblica:</p>
                
                <div class="highlight-box">
                    <h5>⚠️ Desviaciones Documentadas:</h5>
                    <ul>
                        <li><b>Veneración e Idolatría de Imágenes:</b> Lo que comenzó como arte pedagógico derivó en culto e idolatría a estatuas.</li>
                        <li><b>Sacramentos Salvíficos y Transustanciación:</b> Se enseñó que los sacramentos salvan por sí mismos y que el pan se convierte en carne física.</li>
                        <li><b>El Purgatorio y las Indulgencias:</b> Invención del purgatorio y cobro financiero de indulgencias para comprar la salvación.</li>
                        <li><b>El Gran Cisma de 1054:</b> Fractura definitiva entre la Iglesia Católica Romana (Occidente) y la Iglesia Ortodoxa (Oriente).</li>
                    </ul>
                </div>

                <h5>👤 Personajes Clave del Módulo 4:</h5>
                <div class="character-card">
                    <b>• Papa Gregorio I Magno (540–604):</b> Consolidó la autoridad del papado e impulsó ideas tempranas sobre el purgatorio.
                </div>
                <div class="character-card">
                    <b>• Tomás de Aquino (1225–1274):</b> Teólogo escolástico que estructuró los 7 sacramentos salvíficos y la transustanciación.
                </div>
                <div class="character-card">
                    <b>• Papa León X (1475–1521):</b> Autorizó la venta masiva de indulgencias para financiar la Basílica de San Pedro.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            
            st.markdown("##### 📺 Recurso Audiovisual de Refuerzo:")
            st.video("https://example.com/video_educativo.mp4")
            st.caption("🎥 *Video de refuerzo audiovisual para profundizar en los contenidos de este tema.*")
            st.markdown("<br>", unsafe_allow_html=True)
st.subheader("💡 Pregunta de Afianzamiento (Recompensa: +100 XP)")
            q4 = st.radio(
                "¿Qué práctica financiera e invocación doctrinal aceleró la deformación del cristianismo bíblico en la Edad Media?",
                [
                    "A) La traducción de la Biblia al español por las universidades europeas.",
                    "B) La invención del purgatorio, los sacramentos salvíficos y la venta de indulgencias papales.",
                    "C) La eliminación del papado y el retorno a las enseñanzas de los apóstoles."
                ]
            )
            
            if st.button("Confirmar Respuesta y Avanzar"):
                if "B)" in q4:
                    st.success("¡Respuesta Correcta! 🏛️ Has obtenido la Insignia: **'Guardián Histórico'** y +100 XP.")
                    st.session_state.xp += 100
                    st.session_state.pantalla = 5
                    actualizar_progreso(st.session_state.user_id, 5, st.session_state.xp)
                    st.rerun()
                else:
                    st.error("Respuesta incorrecta. Revisa el evento de la venta de indulgencias.")

        # PANTALLA 5
        elif st.session_state.pantalla == 5:
            st.subheader("La Reforma Protestante: Rescate de la Catolicidad Bíblica (Siglos XVI - XVII d.C.)")
            st.markdown("""
            <div class="card-box">
                <h4>📖 El Retorno a la Autoridad de la Palabra de Dios</h4>
                <p>En 1517, el monje <b>Martín Lutero</b> clavó sus 95 Tesis en Wittenberg denunciando las indulgencias. La Reforma no buscaba inventar una fe nueva, sino rescatar la <i>catolicidad bíblica</i> frente a las desviaciones de Roma bajo las 5 Solas (<i>Sola Scriptura, Sola Fide, Sola Gratia, Solus Christus, Soli Deo Gloria</i>).</p>
                
                <h5>👤 Héroes y Traductores de la Reforma:</h5>
                <div class="character-card">
                    <b>• John Wycliffe (1320–1384):</b> "La Estrella Matutina de la Reforma". Tradujo la Biblia al inglés.
                </div>
                <div class="character-card">
                    <b>• Johannes Gutenberg (1400–1468):</b> Inventor de la imprenta, permitiendo multiplicar las Biblias por millones.
                </div>
                <div class="character-card">
                    <b>• Martín Lutero (1483–1546):</b> Monje agustino que impulsó la Reforma Protestante en 1517.
                </div>
                <div class="character-card">
                    <b>• Casiodoro de Reina (1520–1594) y Cipriano de Valera (1532–1602):</b> Monjes españoles que tradujeron la gloriosa Biblia <b>Reina-Valera</b> directamente del hebreo y griego.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            
            st.markdown("##### 📺 Recurso Audiovisual de Refuerzo:")
            st.video("https://example.com/video_educativo.mp4")
            st.caption("🎥 *Video de refuerzo audiovisual para profundizar en los contenidos de este tema.*")
            st.markdown("<br>", unsafe_allow_html=True)
st.subheader("💡 Pregunta de Afianzamiento (Recompensa: +100 XP)")
            q5 = st.radio(
                "¿Cuál fue el mayor aporte de los reformadores y traductores como Casiodoro de Reina para tu fe hoy?",
                [
                    "A) Rescatar las Escrituras y poner la Biblia traducida en nuestra lengua materna (Reina-Valera).",
                    "B) Crear una nueva jerarquía papal con sede en Alemania.",
                    "C) Mantener los servicios religiosos exclusivamente en latín."
                ]
            )
            
            if st.button("Confirmar Respuesta y Avanzar"):
                if "A)" in q5:
                    st.success("¡Extraordinario! 📖 Has ganado la Insignia: **'Reformador de Wittenberg'** y +100 XP.")
                    st.session_state.xp += 100
                    st.session_state.pantalla = 6
                    actualizar_progreso(st.session_state.user_id, 6, st.session_state.xp)
                    st.rerun()
                else:
                    st.error("Respuesta incorrecta. Reflexiona sobre el acceso popular a la Palabra.")

        # PANTALLA 6
        elif st.session_state.pantalla == 6:
            st.subheader("Avivamientos y Tu Misión en la Congregación Familiar Ágape (Siglos XVIII - XXI d.C.)")
            st.markdown("""
            <div class="card-box">
                <h4>🔥 Tu Misión Hoy en la Era Digital</h4>
                <p>Has recorrido 2,400 años de historia. Desde el avivamiento metodista con <b>John Wesley</b> hasta la <b>Calle Azusa (1906)</b> con William J. Seymour, el Espíritu Santo ha avivado a la iglesia. Hoy, como miembro de la <b>Congregación Familiar Cristiana Ágape</b>, tu deber es comunicar esta fe histórica con amor y poder en la era digital.</p>
                
                <h5>👤 Personajes Clave del Módulo 6:</h5>
                <div class="character-card">
                    <b>• John Wesley (1703–1791):</b> Lideró el avivamiento metodista recorriendo 400,000 km a caballo predicando la santidad.
                </div>
                <div class="character-card">
                    <b>• William J. Seymour (1870–1922):</b> Predicador afroamericano líder del Avivamiento de la Calle Azusa (1906), origen del movimiento pentecostal.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            
            st.markdown("##### 📺 Recurso Audiovisual de Refuerzo:")
            st.video("https://example.com/video_educativo.mp4")
            st.caption("🎥 *Video de refuerzo audiovisual para profundizar en los contenidos de este tema.*")
            st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🏆 Pregunta Final e Integradora (Recompensa Máxima)")
            q6 = st.radio(
                "¿Cuál es la enseñanza más valiosa que te llevas al concluir esta formación histórica y teológica?",
                [
                    "A) Que la historia carece de relevancia para nuestra vida de fe hoy.",
                    "B) Que Dios ha guiado soberanamente a su iglesia a través de los siglos y nos encomienda hoy comunicar la fe con fidelidad.",
                    "C) Que la iglesia debe aislarse de la sociedad y evitar el uso de la tecnología."
                ]
            )
            
            if st.button("🎓 Finalizar Mi Formación y Obtener Certificado"):
                if "B)" in q6:
                    st.session_state.xp += 100
                    actualizar_progreso(st.session_state.user_id, 6, st.session_state.xp, completado=True)
                    st.balloons()
                    st.markdown(f"""
                    <div class="highlight-box" style="text-align: center;">
                        <h2>🏆 ¡FELICITACIONES, {st.session_state.nombre.upper()}!</h2>
                        <h3>Has graduado exitosamente en la Formación Histórica y Teológica</h3>
                        <p><b>Iglesia Familiar Cristiana Ágape</b></p>
                        <hr>
                        <p><b>Puntaje Total Obtenido:</b> {st.session_state.xp} XP ⭐</p>
                        <p><b>Ruta Histórica Dominada:</b> 400 a.C. → Siglo I → Constantinopolis → Cisma 1054 → Reforma 1517 → Era Digital</p>
                        <p><i>Tu constancia y dedicación han sido registradas formalmente en el sistema.</i></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Por favor selecciona la opción correcta para certificar tu formación.")
