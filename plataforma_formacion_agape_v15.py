import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA (WEB SAAS PREMIUM) ---
st.set_page_config(
    page_title="Formación Histórica y Teológica - Iglesia Ágape",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNCIÓN AUTO-SCROLL AL INICIO ---
def scroll_to_top():
    components.html(
        "<script>window.parent.scrollTo({top: 0, behavior: 'smooth'});</script>",
        height=0,
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

# --- ESTILOS CSS WEB PREMIUM (MOBILE-FIRST) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        background-color: #FFFFFF !important;
        color: #2B3744 !important;
        font-size: 1.18rem !important;
        line-height: 1.85 !important;
    }
    
    .stApp {
        background-color: #FFFFFF !important;
        max-width: 850px !important;
        margin: 0 auto !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, #1E2A38 0%, #2D3E50 100%) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 14px 28px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(30, 42, 56, 0.2) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }

    .stButton>button:hover {
        background: #D4AF37 !important;
        color: #1E2A38 !important;
        transform: translateY(-2px);
    }

    .stRadio label {
        font-size: 1.1rem !important;
        color: #2B3744 !important;
        padding: 8px 0 !important;
    }

    .stTextInput>div>div>input {
        border-radius: 10px !important;
        font-size: 1.1rem !important;
        padding: 12px !important;
        border: 1.5px solid #CBD5E1 !important;
    }

    /* Estilos de Enfoque Accesible para Lectores de Pantalla (JAWS / TalkBack) */
    button:focus, [role="aria-radio"]:focus, [role="radio"]:focus, input:focus, select:focus {
        outline: 3px solid #D4AF37 !important;
        outline-offset: 3px !important;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.6) !important;
    }

</style>
""", unsafe_allow_html=True)

# --- CABECERA PRINCIPAL NATURA Y LIMPIA ---
with st.container(border=True):
    st.title("🏛️ Formación Teológica e Histórica")
    st.caption("### Congregación Familiar Cristiana Ágape")
    st.write("Un recorrido interactivo y guiado desde el 400 a.C. hasta la Era Digital")

# --- BARRA LATERAL (Navegación & Admin) ---
st.sidebar.title("📌 Menú de la Plataforma")
modo_view = st.sidebar.radio("Selecciona tu Experiencia:", ["🎓 Mi Recorrido de Formación", "🔒 Panel de Administración (Líderes)"])

if modo_view == "🔒 Panel de Administración (Líderes)":
    st.header("🔒 Panel de Control de Liderazgo")
    st.write("El acceso a este panel es exclusivo para el liderazgo autorizado. Ingresa tu clave de acceso.")
    
    if "admin_autenticado" not in st.session_state:
        st.session_state.admin_autenticado = False
        
    if not st.session_state.admin_autenticado:
        password_admin = st.text_input("Clave de Acceso:", type="password", placeholder="••••••••", key="admin_pwd_input", help="Campo para escribir la clave secreta del panel de administración")
        if st.button("🔓 Desbloquear Panel", help="Botón para validar la clave e ingresar al panel de control de liderazgo"):
            pwd_clean = password_admin.strip().replace("Á", "A").replace("á", "a").lower()
            if pwd_clean == "agape2026":
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
            if st.button("🔒 Bloquear Panel", help="Botón para cerrar la sesión de administración y bloquear el acceso"):
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

    # Pantalla Inicial: Parábola, Objetivo e Inicio de Registro
    if st.session_state.user_id is None:
        scroll_to_top()
        with st.container(border=True):
            st.subheader("📜 La Parábola del Creyente sin Raíces: La Historia de Mateo")
            st.write("""
            *Imagina a Mateo. Mateo lleva más de 10 años asistiendo fielmente a su congregación cada domingo. Canta los coros con entusiasmo, lleva su Biblia digital en el teléfono y se considera un cristiano comprometido.*
            
            *Un día, un compañero de estudio le pregunta: "Mateo, tú que te dices cristiano... ¿sabes de dónde salió esa Biblia en español que lees? ¿Sabes quién la tradujo y cuántas personas murieron quemadas en la hoguera para que hoy la tengas en tu pantalla? ¿Sabes por qué no le rezamos a estatuas ni compramos indulgencias? ¿Qué pasó con la iglesia entre los apóstoles y el día de hoy?"*
            
            *Mateo se quedó en absoluto silencio. Descubrió que vivía un **"cristianismo de microondas"**: consumía el producto final, pero ignoraba los 2,400 años de providencia, sangre, oración y estudio que lo hicieron posible.*
            
            👉 **¿Podrías ser tú este Mateo?** Vamos a hacer este recorrido juntos para descubrir tus verdaderas raíces en la fe de Jesucristo.
            """)
        
        with st.container(border=True):
            st.subheader("🎯 Objetivo de Tu Formación Teológica e Histórica")
            st.write("""
            Aprenderás cómo Dios preparó el escenario geopolítico desde la Roma del 400 a.C. y la helenización, cómo nació la iglesia en Pentecostés, sus luchas en la clandestinidad, los concilios teológicos, el surgimiento de las adiciones romanas (purgatorio, indulgencias, sacramentos salvíficos), el rescate de la verdad en la Reforma Protestante y nuestro rol actual en la **Congregación Familiar Cristiana Ágape**.
            """)
        
        nombre_input = st.text_input("Escribe tu Nombre y Apellido para iniciar tu registro:", placeholder="Ej. Juan Pérez", help="Escribe tu nombre y apellido completos para guardar tu avance y personalizar tu certificado")
        
        if st.button("🚀 Iniciar Mi Recorrido de Formación", help="Botón para guardar tu registro e iniciar el primer tema histórico"):
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
        st.sidebar.caption(f"Progreso General: {int(progreso_pct*100)}% Completado")
        
        st.sidebar.markdown("---")
        st.sidebar.write("📌 **Navegación Directa de Temas:**")
        opciones_temas = {
            1: "1. Roma, Helenización (400 a.C.)",
            2: "2. Iglesia Primitiva y Persecuciones",
            3: "3. Giro Constantiniano y Nicea",
            4: "4. Adiciones Dogmáticas de Roma",
            5: "5. La Reforma Protestante",
            6: "6. Avivamientos y Misión Digital"
        }
        
        tema_sel = st.sidebar.selectbox("Selecciona un tema para revisar:", list(opciones_temas.keys()), format_func=lambda x: opciones_temas[x], index=st.session_state.pantalla-1)
        if tema_sel != st.session_state.pantalla:
            st.session_state.pantalla = tema_sel
            st.rerun()
            
        if st.sidebar.button("🔒 Salir de la Sesión"):
            st.session_state.user_id = None
            st.session_state.nombre = ""
            st.rerun()

        # EJECUTAR SCROLL AL INICIO AL CAMBIAR DE PANTALLA
        scroll_to_top()

        # BOTONES SUPERIORES DE NAVEGACIÓN
        col_top1, col_top2 = st.columns([1, 1])
        with col_top1:
            if st.session_state.pantalla > 1:
                if st.button("⬅️ Volver al Tema Anterior", key="btn_back_top", help="Botón para regresar al tema previo en la formación"):
                    st.session_state.pantalla -= 1
                    st.rerun()
        with col_top2:
            st.caption(f"📍 Tema {st.session_state.pantalla} de 6")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- DESARROLLO DE TEMAS DE APRENDIZAJE ---
        
        # TEMA 1
        if st.session_state.pantalla == 1:
            st.header("Roma, la Helenización y la Preparación del Escenario (400 a.C. - Siglo I a.C.)")
            
            with st.container(border=True):
                st.subheader("🏛️ ¿Cómo preparó Dios el mundo para la venida del Mesías?")
                st.write("¡Hola y bienvenido/a! **Vamos a hacer este recorrido juntos**. Para comprender el Nuevo Testamento, **debes viajar cuatro siglos antes de Cristo**. Durante este periodo, dos fuerzas geopolíticas prepararon el camino:")
                
                st.info("""
                ### 🔑 Dos Conceptos Clave que Debes Dominar:
                * **¿Qué es Roma y su Imperio?:** Roma comenzó como una república que hacia el 400 a.C. inició una expansión militar. Se convirtió en el Imperio Romano, aportando la *Pax Romana*, un sistema legal uniforme y una inmensa red de **carreteras y calzadas seguras**. Gracias a esto, los apóstoles pudieron viajar miles de kilómetros anunciando el Evangelio.
                * **¿Qué es la Helenización?:** Es la difusión de la cultura y del **idioma griego Koiné** iniciada por Alejandro Magno (Siglo IV a.C.). Unificó el idioma del mundo conocido, permitiendo traducir el Antiguo Testamento al griego (**la Septuaginta LXX**) y escribir el Nuevo Testamento en una lengua universal.
                """)

                st.subheader("👤 Personajes Clave del Tema:")
                st.success("**• Alejandro Magno (356–323 a.C.):** Rey de Macedonia y estratega militar. *Interés:* Difundir el helenismo. *Impacto:* Aportó el griego Koiné en el que se redactó el Nuevo Testamento.")
                st.success("**• César Augusto (63 a.C.–14 d.C.):** Primer emperador romano. *Interés:* Pax romana y administración imperial. *Impacto:* Bajo su censo nació Jesús (Lucas 2:1) y sus carreteras sirvieron para la difusión de la fe.")
                
                st.caption("✍️ *¿Ya tomaste nota de estas fechas y eventos en tu libreta? Continuemos con otros puntos muy interesantes.*")

            st.markdown("##### 📺 Recurso Audiovisual de Refuerzo:")
            st.video("https://www.youtube.com/watch?v=FcCONB80WH8")
            st.caption("🎥 *Recurso de audio y video explicativo. Si utilizas un lector de pantalla como TalkBack o JAWS, activa el reproductor para escuchar la síntesis narrada de este tema.*");
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.subheader("💡 Pregunta de Afianzamiento (Recompensa: +100 XP)")
            q1 = st.radio(
                "¿Cómo contribuyeron Roma y la Helenización a la preparación del mundo para el Evangelio?",
                [
                    "A) Roma prohibió el uso del griego y aisló las ciudades de Judea.",
                    "B) Roma aportó paz y carreteras seguras; la Helenización unificó el idioma griego Koiné y la Septuaginta.",
                    "C) Ninguna de las anteriores, el Evangelio solo se difundió en latín."
                ], help="Selecciona la respuesta correcta usando las flechas o la pantalla táctil."
            )
            
            col_b1, col_b2 = st.columns([1, 1])
            with col_b2:
                if st.button("Confirmar Respuesta y Avanzar 🚀", key="btn_next_1", help="Botón para enviar tu respuesta y avanzar al tema 2"):
                    if "B)" in q1:
                        st.success("¡Excelente deducción histórica! 🎉 Has desbloqueado tu primera Insignia: **'Pionero del Escenario Histórico'** y +100 XP.")
                        st.session_state.xp += 100
                        st.session_state.pantalla = 2
                        actualizar_progreso(st.session_state.user_id, 2, st.session_state.xp)
                        st.rerun()
                    else:
                        st.error("Respuesta incorrecta. Revisa el recuadro sobre la Pax Romana y el griego Koiné.")

        # TEMA 2
        elif st.session_state.pantalla == 2:
            st.header("La Iglesia Primitiva, Persecución y Apologética (Siglos I - III d.C.)")
            
            with st.container(border=True):
                st.subheader("📜 De Pentecostés a la Clandestinidad")
                st.write("Avancemos a nuestro siguiente paso. Tras Pentecostés, la iglesia creció con poder, pero al separarse del judaísmo perdió la protección legal romana y fue perseguida por emperadores como **Nerón, Domiciano y Diocleciano**. Durante esta etapa destacan dos pilares de preservación:")
                
                st.info("""
                ### 🛡️ Tu Aprendizaje Teológico Clave:
                * **Los Apologetas:** Defensores teológicos que redactaron escritos para argumentar la verdad bíblica frente a calumnias y persecuciones.
                * **Monasticismo Primitivo:** Comunidades de oración e intercesión (como Pacomio en Egipto), donde los monjes copistas se dedicated a copiar meticulosamente los manuscritos bíblicos en papiro y pergamino.
                """)

                st.subheader("👤 Personajes Clave del Tema:")
                st.success("**• Emperador Nerón (37–68 d.C.):** Culpó a los cristianos del incendio de Roma (64 d.C.). Ejecutó a Pedro y Pablo.")
                st.success("**• Justino Mártir (100–165 d.C.):** Filósofo convertido en apologeta. Defendió la fe ante el Senado romano hasta su martirio.")
                st.success("**• Pacomio (292–346 d.C.):** Padre del monasticismo cenobítico en Egipto. Organizó comunidades dedicadas a copiar manuscritos bíblicos.")

            st.markdown("##### 📺 Recurso Audiovisual de Refuerzo:")
            st.video("https://www.youtube.com/watch?v=1OcITwb7Fgg")
            st.caption("🎥 *Recurso de audio y video explicativo. Si utilizas un lector de pantalla como TalkBack o JAWS, activa el reproductor para escuchar la síntesis narrada de este tema.*");
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.subheader("💡 Pregunta de Afianzamiento (Recompensa: +100 XP)")
            q2 = st.radio(
                "¿Qué rol desempeñaron los Apologetas y el monasticismo primitivo durante las persecuciones?",
                [
                    "A) Defender la fe bíblica con argumentos sólidos y copiar manuscritos de las Escrituras.",
                    "B) Buscar cargos políticos dentro del Senado romano para cobrar impuestos.",
                    "C) Cancelar las reuniones de la iglesia y eliminar el Antiguo Testamento."
                ], help="Selecciona la respuesta correcta usando las flechas o la pantalla táctil."
            )
            
            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
                if st.button("⬅️ Volver al Tema 1", key="btn_back_2", help="Botón para regresar al tema 1"):
                    st.session_state.pantalla = 1
                    st.rerun()
            with col_b2:
                if st.button("Confirmar Respuesta y Avanzar 🚀", key="btn_next_2", help="Botón para enviar tu respuesta y avanzar al tema 3"):
                    if "A)" in q2:
                        st.success("¡Respuesta Correcta! 🛡️ Has obtenido la Insignia: **'Apologeta de la Fe'** y +100 XP.")
                        st.session_state.xp += 100
                        st.session_state.pantalla = 3
                        actualizar_progreso(st.session_state.user_id, 3, st.session_state.xp)
                        st.rerun()
                    else:
                        st.error("Respuesta incorrecta. Recuerda la labor de preservación y defensa doctrinal.")

        # TEMA 3
        elif st.session_state.pantalla == 3:
            st.header("Giro Constantiniano y Catolicidad vs. Catolicismo (Siglo IV d.C.)")
            
            with st.container(border=True):
                st.subheader("🏛️ Legalización y la Distinción Teológica Crucial")
                st.write("Llegamos a un momento de quiebre. En el 313 d.C., Constantino promulga el **Edicto de Milán**, legalizando el cristianismo. En el 325 d.C. se convoca el **Concilio de Nicea** para combatir el arianismo y proclamar la deidad de Cristo. Sin embargo, debes comprender esta distinción fundamental:")
                
                st.info("""
                ### 💡 Aprende la Diferencia entre Catolicidad y Catolicismo Romano:
                * **Catolicidad (del griego *katholikos* = "universal"):** Es la cualidad bíblica original de la iglesia primitiva enviada a todas las naciones. Es la fe pura compartida por el cuerpo de Cristo.
                * **Catolicismo Romano:** Es la estructura político-religiosa e institucional centrada en Roma que se desarrolló progresivamente tras la oficialización estatal impulsada por Teodosio I (380 d.C.).
                """)

                st.subheader("👤 Personajes Clave del Tema:")
                st.success("**• Constantino I (272–337 d.C.):** Emperador romano que legalizó la iglesia e inició la mezcla Estado-Iglesia.")
                st.success("**• Atanasio de Alejandría (296–373 d.C.):** Teólogo que defendió en Nicea que Jesús es verdaderamente Dios (*Homoousios*).")
                st.success("**• Emperador Teodosio I (347–395 d.C.):** Proclamó el cristianismo romano como religión estatal obligatoria.")

            st.markdown("##### 📺 Recurso Audiovisual de Refuerzo:")
            st.video("https://www.youtube.com/watch?v=5dfCj33z3bo")
            st.caption("🎥 *Recurso de audio y video explicativo. Si utilizas un lector de pantalla como TalkBack o JAWS, activa el reproductor para escuchar la síntesis narrada de este tema.*");
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.subheader("💡 Pregunta de Afianzamiento (Recompensa: +100 XP)")
            q3 = st.radio(
                "Como estudiante de la Palabra, ¿cómo diferencias la 'catolicidad' del 'catolicismo romano'?",
                [
                    "A) Son términos idénticos que significan exactamente lo mismo en la Biblia.",
                    "B) Catolicidad es la universalidad de la iglesia bíblica; Catolicismo Romano es la estructura institucional iniciada tras la oficialización estatal.",
                    "C) Catolicidad es un invento del siglo XX y Catolicismo Romano fue fundado en Pentecostés."
                ], help="Selecciona la respuesta correcta usando las flechas o la pantalla táctil."
            )
            
            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
                if st.button("⬅️ Volver al Tema 2", key="btn_back_3", help="Botón para regresar al tema 2"):
                    st.session_state.pantalla = 2
                    st.rerun()
            with col_b2:
                if st.button("Confirmar Respuesta y Avanzar 🚀", key="btn_next_3", help="Botón para enviar tu respuesta y avanzar al tema 4"):
                    if "B)" in q3:
                        st.success("¡Excelente comprensión teológica! 📜 Ganaste la Insignia: **'Defensor de Nicea'** y +100 XP.")
                        st.session_state.xp += 100
                        st.session_state.pantalla = 4
                        actualizar_progreso(st.session_state.user_id, 4, st.session_state.xp)
                        st.rerun()
                    else:
                        st.error("Respuesta incorrecta. Vuelve a revisar la distinción entre universalidad e institución.")

        # TEMA 4
        elif st.session_state.pantalla == 4:
            st.header("Adiciones Dogmáticas de Roma: Purgatorio, Indulgencias y Cisma (Siglos V - XV d.C.)")
            
            with st.container(border=True):
                st.subheader("🏰 Las Desviaciones Doctrinales e Institucionales de Roma")
                st.write("Acompañame a analizar cómo la iglesia institucional de Roma fue agregando dogmas humanos alejados de la verdad bíblica:")
                
                st.warning("""
                ### ⚠️ Desviaciones Documentadas:
                * **Veneración e Idolatría de Imágenes:** Lo que comenzó como arte pedagógico derivó en culto e idolatría a estatuas.
                * **Sacramentos Salvíficos y Transustanciación:** Se enseñó que los sacramentos salvan por sí mismos y que el pan se convierte en carne física.
                * **El Purgatorio y las Indulgencias:** Invención del purgatorio y cobro financiero de indulgencias para comprar la salvación.
                * **El Gran Cisma de 1054:** Fractura definitiva entre la Iglesia Católica Romana (Occidente) y la Iglesia Ortodoxa (Oriente).
                """)

                st.subheader("👤 Personajes Clave del Tema:")
                st.success("**• Papa Gregorio I Magno (540–604):** Consolidó la autoridad del papado e impulsó ideas tempranas sobre el purgatorio.")
                st.success("**• Tomás de Aquino (1225–1274):** Teólogo escolástico que estructuró los 7 sacramentos salvíficos y la transustanciación.")
                st.success("**• Papa León X (1475–1521):** Autorizó la venta masiva de indulgencias para financiar la Basílica de San Pedro.")

            st.markdown("##### 📺 Recurso Audiovisual de Refuerzo:")
            st.video("https://www.youtube.com/watch?v=GiJg729sHxQ")
            st.caption("🎥 *Recurso de audio y video explicativo. Si utilizas un lector de pantalla como TalkBack o JAWS, activa el reproductor para escuchar la síntesis narrada de este tema.*");
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.subheader("💡 Pregunta de Afianzamiento (Recompensa: +100 XP)")
            q4 = st.radio(
                "¿Qué práctica financiera e invocación doctrinal aceleró la deformación del cristianismo bíblico en la Edad Media?",
                [
                    "A) La traducción de la Biblia al español por las universidades europeas.",
                    "B) La invención del purgatorio, los sacramentos salvíficos y la venta de indulgencias papales.",
                    "C) La eliminación del papado y el retorno a las enseñanzas de los apóstoles."
                ], help="Selecciona la respuesta correcta usando las flechas o la pantalla táctil."
            )
            
            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
                if st.button("⬅️ Volver al Tema 3", key="btn_back_4", help="Botón para regresar al tema 3"):
                    st.session_state.pantalla = 3
                    st.rerun()
            with col_b2:
                if st.button("Confirmar Respuesta y Avanzar 🚀", key="btn_next_4", help="Botón para enviar tu respuesta y avanzar al tema 5"):
                    if "B)" in q4:
                        st.success("¡Respuesta Correcta! 🏛️ Has obtenido la Insignia: **'Guardián Histórico'** y +100 XP.")
                        st.session_state.xp += 100
                        st.session_state.pantalla = 5
                        actualizar_progreso(st.session_state.user_id, 5, st.session_state.xp)
                        st.rerun()
                    else:
                        st.error("Respuesta incorrecta. Revisa el evento de la venta de indulgencias.")

        # TEMA 5
        elif st.session_state.pantalla == 5:
            st.header("La Reforma Protestante: Rescate de la Catolicidad Bíblica (Siglos XVI - XVII d.C.)")
            
            with st.container(border=True):
                st.subheader("📖 El Retorno a la Autoridad de la Palabra de Dios")
                st.write("En 1517, el monje **Martín Lutero** clavó sus 95 Tesis en Wittenberg denunciando las indulgencias. La Reforma no buscaba inventar una fe nueva, sino rescatar la *catolicidad bíblica* frente a las desviaciones de Roma bajo las 5 Solas (*Sola Scriptura, Sola Fide, Sola Gratia, Solus Christus, Soli Deo Gloria*).")
                
                st.subheader("👤 Héroes y Traductores de la Reforma:")
                st.success("**• John Wycliffe (1320–1384):** 'La Estrella Matutina de la Reforma'. Tradujo la Biblia al inglés.")
                st.success("**• Johannes Gutenberg (1400–1468):** Inventor de la imprenta, permitiendo multiplicar las Biblias por millones.")
                st.success("**• Martín Lutero (1483–1546):** Monje agustino que impulsó la Reforma Protestante en 1517.")
                st.success("**• Casiodoro de Reina (1520–1594) y Cipriano de Valera (1532–1602):** Monjes españoles que tradujeron la gloriosa Biblia **Reina-Valera** directamente del hebreo y griego.")

            st.markdown("##### 📺 Recurso Audiovisual de Refuerzo:")
            st.video("https://www.youtube.com/watch?v=V1zdeV-q5u8")
            st.caption("🎥 *Recurso de audio y video explicativo. Si utilizas un lector de pantalla como TalkBack o JAWS, activa el reproductor para escuchar la síntesis narrada de este tema.*");
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.subheader("💡 Pregunta de Afianzamiento (Recompensa: +100 XP)")
            q5 = st.radio(
                "¿Cuál fue el mayor aporte de los reformadores y traductores como Casiodoro de Reina para tu fe hoy?",
                [
                    "A) Rescatar las Escrituras y poner la Biblia traducida en nuestra lengua materna (Reina-Valera).",
                    "B) Crear una nueva jerarquía papal con sede en Alemania.",
                    "C) Mantener los servicios religiosos exclusivamente en latín."
                ], help="Selecciona la respuesta correcta usando las flechas o la pantalla táctil."
            )
            
            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
                if st.button("⬅️ Volver al Tema 4", key="btn_back_5", help="Botón para regresar al tema 4"):
                    st.session_state.pantalla = 4
                    st.rerun()
            with col_b2:
                if st.button("Confirmar Respuesta y Avanzar 🚀", key="btn_next_5", help="Botón para enviar tu respuesta y avanzar al tema 6"):
                    if "A)" in q5:
                        st.success("¡Extraordinario! 📖 Has ganado la Insignia: **'Reformador de Wittenberg'** y +100 XP.")
                        st.session_state.xp += 100
                        st.session_state.pantalla = 6
                        actualizar_progreso(st.session_state.user_id, 6, st.session_state.xp)
                        st.rerun()
                    else:
                        st.error("Respuesta incorrecta. Reflexiona sobre el acceso popular a la Palabra.")

        # TEMA 6
        elif st.session_state.pantalla == 6:
            st.header("Avivamientos y Tu Misión en la Congregación Familiar Ágape (Siglos XVIII - XXI d.C.)")
            
            with st.container(border=True):
                st.subheader("🔥 Tu Misión Hoy en la Era Digital")
                st.write("Has recorrido 2,400 años de historia. Desde el avivamiento metodista con **John Wesley** hasta la **Calle Azusa (1906)** con William J. Seymour, el Espíritu Santo ha avivado a la iglesia. Hoy, como miembro de la **Congregación Familiar Cristiana Ágape**, tu deber es comunicar esta fe histórica con amor y poder en la era digital.")
                
                st.subheader("👤 Personajes Clave del Tema:")
                st.success("**• John Wesley (1703–1791):** Lideró el avivamiento metodista recorriendo 400,000 km a caballo predicando la santidad.")
                st.success("**• William J. Seymour (1870–1922):** Predicador afroamericano líder del Avivamiento de la Calle Azusa (1906), origen del movimiento pentecostal.")

            st.markdown("##### 📺 Recurso Audiovisual de Refuerzo:")
            st.video("https://www.youtube.com/watch?v=36az8KoxSZs")
            st.caption("🎥 *Recurso de audio y video explicativo. Si utilizas un lector de pantalla como TalkBack o JAWS, activa el reproductor para escuchar la síntesis narrada de este tema.*");
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.subheader("🏆 Pregunta Final e Integradora (Recompensa Máxima)")
            q6 = st.radio(
                "¿Cuál es la enseñanza más valiosa que te llevas al concluir esta formación histórica y teológica?",
                [
                    "A) Que la historia carece de relevancia para nuestra vida de fe hoy.",
                    "B) Que Dios ha guiado soberanamente a su iglesia a través de los siglos y nos encomienda hoy comunicar la fe con fidelidad.",
                    "C) Que la iglesia debe aislarse de la sociedad y evitar el uso de la tecnología."
                ], help="Selecciona la respuesta correcta usando las flechas o la pantalla táctil."
            )
            
            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
                if st.button("⬅️ Volver al Tema 5", key="btn_back_6", help="Botón para regresar al tema 5"):
                    st.session_state.pantalla = 5
                    st.rerun()
            with col_b2:
                if st.button("🎓 Finalizar Mi Formación y Obtener Certificado", key="btn_next_6", help="Botón para finalizar la formación, registrar tu logro y generar tu certificado"):
                    if "B)" in q6:
                        st.session_state.xp += 100
                        actualizar_progreso(st.session_state.user_id, 6, st.session_state.xp, completado=True)
                        st.balloons()
                        st.success(f"🏆 ¡FELICITACIONES, {st.session_state.nombre.upper()}! Has graduado exitosamente en la Formación Histórica y Teológica de la Iglesia Familiar Cristiana Ágape. Puntaje Total Obtenido: {st.session_state.xp} XP ⭐")
                    else:
                        st.error("Por favor selecciona la opción correcta para certificar tu formación.")
