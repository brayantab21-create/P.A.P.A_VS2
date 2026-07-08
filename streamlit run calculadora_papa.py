import streamlit as st
import pandas as pd
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER


st.set_page_config(
    page_title="Calculadora Académica",
    layout="wide",
    page_icon="🎓"
)

st.markdown("""
<style>
    .stApp { background-color: #1A1616; }

    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 5px solid #4f8ef7;
    }

    .titulo-principal {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 800;
        color: #E6F2F7;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }

    .subtitulo {
        text-align: center;
        font-size: 1.05rem;
        color: #C5E1ED;
        margin-bottom: 1.5rem;
    }

    .divider {
        height: 2px;
        background: linear-gradient(90deg, #4f8ef7, #a78bfa);
        border-radius: 2px;
        margin: 1.2rem 0;
    }

    .asignatura-header {
        font-size: 1rem;
        font-weight: 600;
        color: #2d3748;
        background: #eef2ff;
        border-radius: 8px;
        padding: 0.4rem 0.8rem;
        margin-bottom: 0.3rem;
        display: inline-block;
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, #4f8ef7, #a78bfa) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 12px rgba(79,142,247,0.35) !important;
        width: 100% !important;
    }

    footer { visibility: hidden; }

    /* ── Textos globales sobre fondo oscuro ── */
    h1, h2, h3, h4, h5, h6 {
        color: #E6F2F7 !important;
    }

    div[data-testid="stMarkdownContainer"] h3 {
        color: #E6F2F7 !important;
    }

    div[data-testid="stCaptionContainer"] p,
    .stCaption p {
        color: #aac4d4 !important;
    }

    .stMarkdown p, .stMarkdown li,
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li {
        color: #d0e8f2 !important;
    }

    details summary p,
    .streamlit-expanderHeader p {
        color: #C5E1ED !important;
    }

    /* ── Textos dentro de tarjetas blancas: oscuros ── */
    .card p, .card li, .card label,
    .card div[data-testid="stMarkdownContainer"] p,
    .card div[data-testid="stMarkdownContainer"] li {
        color: #2d3748 !important;
    }

    .stNumberInput label,
    .stTextInput label,
    .stRadio label,
    .stSelectbox label {
        color: #2d3748 !important;
        font-weight: 500 !important;
    }

    .stNumberInput input,
    .stTextInput input {
        color: #1a2e5a !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# FUNCIÓN PARA GENERAR PDF
# -----------------------------------
def generar_pdf(df, papa_global, papas_periodo, ultimo_periodo,
                df_ultimo, sugerencias, total_pres, total_auto,
                nombre, cedula, correo, telefono):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []

    azul     = colors.HexColor("#1a2e5a")
    medio    = colors.HexColor("#4f8ef7")
    gris     = colors.HexColor("#f0f4f8")
    borde    = colors.HexColor("#e2e8f0")
    rojo     = colors.HexColor("#e74c3c")
    verde    = colors.HexColor("#27ae60")
    naranja  = colors.HexColor("#f39c12")
    amarillo = colors.HexColor("#b8860b")

    def ep(name, **kw):
        base = dict(fontSize=10, textColor=colors.HexColor("#2d3748"),
                    spaceAfter=4, leading=14)
        base.update(kw)
        return ParagraphStyle(name, **base)

    et  = ep('t',  fontSize=20, textColor=azul, alignment=TA_CENTER,
             spaceAfter=4, fontName='Helvetica-Bold')
    ec  = ep('c',  fontSize=13, textColor=azul, spaceBefore=14,
             spaceAfter=6, fontName='Helvetica-Bold')
    en  = ep('n')
    ef  = ep('f',  fontSize=8, textColor=colors.HexColor("#94a3b8"),
             alignment=TA_CENTER)
    ea  = ep('a',  fontSize=12, textColor=rojo, fontName='Helvetica-Bold',
             alignment=TA_CENTER)
    eo  = ep('o',  fontSize=12, textColor=naranja, fontName='Helvetica-Bold',
             alignment=TA_CENTER)
    ey  = ep('y',  fontSize=12, textColor=amarillo, fontName='Helvetica-Bold',
             alignment=TA_CENTER)
    eok = ep('ok', fontSize=12, textColor=verde, fontName='Helvetica-Bold',
             alignment=TA_CENTER)
    ecen = ep('cen', alignment=TA_CENTER)

    def tbl(data, widths):
        t = Table(data, colWidths=widths)
        t.setStyle(TableStyle([
            ('BACKGROUND',     (0,0), (-1,0), azul),
            ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
            ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',       (0,0), (-1,-1), 9),
            ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
            ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [gris, colors.white]),
            ('GRID',           (0,0), (-1,-1), 0.5, borde),
            ('TOPPADDING',     (0,0), (-1,-1), 7),
            ('BOTTOMPADDING',  (0,0), (-1,-1), 7),
        ]))
        return t

    # ── Título ──
    story += [
        Paragraph("Calculadora de P.A.P.A.", et),
        HRFlowable(width="100%", thickness=2, color=medio),
        Spacer(1, 10),
    ]

    # ── Estado de alerta debajo del título ──
    if papa_global < 2.7:
        story.append(Paragraph("ESTADO: RIESGO ALTO", ea))
        story.append(Paragraph(
            "Puedes solicitar excepcionalidad ante el Consejo Superior "
            "Universitario. Acude a Direccion Academica para orientaciones.", ecen))
    elif papa_global < 3.0:
        story.append(Paragraph("ESTADO: RIESGO MODERADO", eo))
        story.append(Paragraph(
            "Puedes solicitar reingreso ante el Consejo de Facultad. "
            "Acude a Direccion Academica.", ecen))
    elif papa_global < 3.4:
        story.append(Paragraph("ESTADO: ZONA DE ALERTA", ey))
        story.append(Paragraph(
            "Visita Direccion Academica para trazar un plan de mejora.", ecen))
    else:
        story.append(Paragraph("ESTADO: ZONA ESTABLE", eok))
        story.append(Paragraph(
            "Puedes asistir a Direccion Academica para fortalecer tus procesos.", ecen))

    story.append(Spacer(1, 12))

    # ── Datos del estudiante ──
    story.append(Paragraph("Datos del Estudiante", ec))
    datos_est = [
        ["Nombre",              nombre.strip()   if nombre.strip()   else "—"],
        ["Cedula / Codigo",     cedula.strip()   if cedula.strip()   else "—"],
        ["Correo",              correo.strip()   if correo.strip()   else "—"],
        ["Telefono",            telefono.strip() if telefono.strip() else "—"],
        ["Fecha de generacion", datetime.now().strftime('%d/%m/%Y %H:%M')],
    ]
    t_est = Table(datos_est, colWidths=[2.2*inch, 4.3*inch])
    t_est.setStyle(TableStyle([
        ('FONTNAME',      (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 9),
        ('TEXTCOLOR',     (0,0), (-1,-1), colors.HexColor("#2d3748")),
        ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS',(0,0), (-1,-1), [gris, colors.white]),
        ('GRID',          (0,0), (-1,-1), 0.5, borde),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
    ]))
    story += [t_est, Spacer(1, 14)]

    # ── PAPA por periodo ──
    story.append(Paragraph("P.A.P.A. por Periodo", ec))
    rows = [["Periodo", "Creditos", "P.A.P.A."]]
    for p, vals in sorted(papas_periodo.items()):
        rows.append([str(p), str(vals['creditos']), str(vals['papa'])])
    rows.append(["GLOBAL", str(int(df["Creditos"].sum())), str(papa_global)])
    story += [tbl(rows, [3*inch, 1.5*inch, 1.5*inch]), Spacer(1, 14)]

    # ── Asignaturas último periodo ──
    story.append(Paragraph(f"Asignaturas - Ultimo Periodo ({ultimo_periodo})", ec))
    enc = ["Asignatura", "Cred.", "Nota", "Estado"]
    filas = [enc]
    for _, row in df_ultimo.iterrows():
        filas.append([
            str(row["Asignatura"]),
            str(int(row["Creditos"])),
            str(round(float(row["Nota"]), 1)),
            "Aprobo" if row["Nota"] >= 3.0 else "Perdio"
        ])
    story += [tbl(filas, [3.0*inch, 0.8*inch, 0.8*inch, 1.0*inch]), Spacer(1, 14)]

    # ── Carga horaria ──
    story.append(Paragraph(f"Carga Horaria - Ultimo Periodo ({ultimo_periodo})", ec))
    ch = [["Horas Presenciales / semana", "Horas Autonomas / semana"],
          [str(int(total_pres)), str(int(total_auto))]]
    story += [tbl(ch, [3.25*inch, 3.25*inch]), Spacer(1, 14)]

    # ── Sugerencias ──
    if sugerencias:
        story.append(Paragraph("Proyecciones de Mejora (Ultimo Periodo)", ec))
        for s in sugerencias:
            story.append(Paragraph(f"- {s.replace('**','')}", en))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            "Si no obtienes los resultados esperados, busca ayuda en "
            "Direccion Academica para generar una estrategia personalizada.", en))
        story.append(Spacer(1, 10))

    story += [
        Spacer(1, 16),
        HRFlowable(width="100%", thickness=1, color=borde),
        Spacer(1, 6),
        Paragraph(
            "Documento generado por la Calculadora de P.A.P.A. - Direccion Academica",
            ef)
    ]

    doc.build(story)
    buffer.seek(0)
    return buffer


# =============================================
# APP PRINCIPAL
# =============================================

st.markdown("<div class='titulo-principal'>🎓 Calculadora Académica</div>",
            unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Conoce tu P.A.P.A. por periodo y global, "
            "y descubre cómo va tu proceso académico</div>",
            unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# -----------------------------------
# DATOS DEL ESTUDIANTE
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("👤 Cuéntanos quién eres")
st.caption("Estos datos aparecerán en tu reporte PDF. Puedes dejarlos en blanco si prefieres.")

col_n, col_c = st.columns(2)
with col_n:
    estudiante_nombre = st.text_input("Nombre completo",
                                      placeholder="Ej. María García López")
with col_c:
    estudiante_cedula = st.text_input("Cédula o código estudiantil",
                                      placeholder="Ej. 1234567890")

col_e, col_t = st.columns(2)
with col_e:
    estudiante_correo = st.text_input("Correo institucional",
                                      placeholder="Ej. mgarcia@unal.edu.co")
with col_t:
    estudiante_telefono = st.text_input("Teléfono de contacto",
                                        placeholder="Ej. 3001234567")

st.markdown("</div>", unsafe_allow_html=True)

datos = []

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📚 Tus Asignaturas")
st.caption("Ingresa las materias que has cursado con su nota, créditos y periodo. "
           "Con esto calcularemos todo por ti.")

num = st.number_input("¿Cuántas asignaturas quieres ingresar?",
                      min_value=1, max_value=60, step=1, value=5)

for i in range(int(num)):
    st.markdown(f"<span class='asignatura-header'>Asignatura {i+1}</span>",
                unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([4, 1, 1, 2])
    with c1:
        nombre = st.text_input("Nombre", key=f"n_{i}",
                               label_visibility="collapsed",
                               placeholder=f"Nombre de la asignatura {i+1}")
    with c2:
        creditos = st.number_input("Cred.", min_value=1, max_value=10,
                                   step=1, key=f"c_{i}",
                                   label_visibility="visible")
    with c3:
        nota = st.number_input("Nota", min_value=0.0, max_value=5.0,
                               step=0.1, key=f"nota_{i}",
                               label_visibility="visible")
    with c4:
        periodo = st.text_input("Periodo", key=f"p_{i}",
                                label_visibility="visible",
                                placeholder="Ej: 2024-1")

    datos.append({
        "Asignatura":         nombre if nombre else f"Asignatura {i+1}",
        "Creditos":           creditos,
        "Nota":               nota,
        "Periodo":            periodo.strip() if periodo.strip() else "Sin periodo",
        "Horas Presenciales": creditos,
        "Horas Autonomas":    (creditos * 3) - creditos
    })

    if i < int(num) - 1:
        st.markdown("---")

st.markdown("</div>", unsafe_allow_html=True)

datos_validos = [d for d in datos if d["Creditos"] > 0]
if not datos_validos:
    st.info("✨ Ingresa al menos una asignatura y te mostraremos tus resultados al instante.")
    st.stop()

df = pd.DataFrame(datos_validos)

# PAPA global
suma_pond_global = (df["Creditos"] * df["Nota"]).sum()
suma_cred_global = df["Creditos"].sum()
papa_global      = round(suma_pond_global / suma_cred_global, 3) if suma_cred_global > 0 else 0.0

# PAPA por periodo
periodos_ordenados = sorted(df["Periodo"].unique())
ultimo_periodo     = periodos_ordenados[-1]

papas_periodo = {}
for p in periodos_ordenados:
    sub = df[df["Periodo"] == p]
    sp  = (sub["Creditos"] * sub["Nota"]).sum()
    sc  = sub["Creditos"].sum()
    papas_periodo[p] = {
        "papa":     round(sp / sc, 3) if sc > 0 else 0.0,
        "creditos": int(sc)
    }

# Último periodo
df_ultimo   = df[df["Periodo"] == ultimo_periodo].copy()
sp_ultimo   = (df_ultimo["Creditos"] * df_ultimo["Nota"]).sum()
sc_ultimo   = df_ultimo["Creditos"].sum()
papa_ultimo = round(sp_ultimo / sc_ultimo, 3) if sc_ultimo > 0 else 0.0
total_pres  = int(df_ultimo["Horas Presenciales"].sum())
total_auto  = int(df_ultimo["Horas Autonomas"].sum())

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📊 Así va tu P.A.P.A. por Periodo")
st.caption("Aquí puedes ver cómo ha evolucionado tu promedio a lo largo de tu carrera.")

filas_periodo = []
for p in periodos_ordenados:
    v = papas_periodo[p]
    etiqueta = f"⭐ {p} (último)" if p == ultimo_periodo else f"🔵 {p}"
    filas_periodo.append({
        "Periodo":  etiqueta,
        "Créditos": v["creditos"],
        "P.A.P.A.": v["papa"],
        "Estado": (
            "🔴 Riesgo alto"     if v["papa"] < 2.7 else
            "🟠 Riesgo moderado" if v["papa"] < 3.0 else
            "🟡 Alerta"          if v["papa"] < 3.4 else
            "🟢 Estable"
        )
    })

df_periodos       = pd.DataFrame(filas_periodo)
df_periodos.index = [""] * len(df_periodos)
st.dataframe(df_periodos, use_container_width=True)

st.markdown("---")
st.metric("P.A.P.A. Global", papa_global,
          help="Calculado sobre todas las asignaturas ingresadas")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader(f"📋 Tu último periodo: {ultimo_periodo}")

df_ult_vista = df_ultimo[["Asignatura", "Creditos", "Nota"]].copy()
df_ult_vista.insert(3, "Estado", df_ult_vista["Nota"].apply(
    lambda n: "✅ Aprobó" if n >= 3.0 else "❌ Perdió"))
df_ult_vista = df_ult_vista.rename(columns={"Creditos": "Créditos"})
df_ult_vista.index = [""] * len(df_ult_vista)
st.dataframe(df_ult_vista, use_container_width=True)

st.metric(f"P.A.P.A. {ultimo_periodo}", papa_ultimo)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader(f"⏰ Tu tiempo de estudio — {ultimo_periodo}")
st.caption("Este es el tiempo semanal estimado que requiere tu carga académica actual. "
           "Si sientes que no te alcanza el tiempo, en Acompañamiento Académico podemos ayudarte a organizarlo.")

colA, colB, colC = st.columns(3)
with colA:
    st.metric("Horas presenciales / semana", total_pres)
with colB:
    st.metric("Horas autónomas / semana", total_auto)
with colC:
    st.metric("Total horas / semana", total_pres + total_auto)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📌 ¿Cómo va tu proceso?")
st.caption("Este estado se calcula con tu P.A.P.A. global, el de toda tu carrera.")

if papa_global < 2.7:
    st.error(
        "🔴 **Tu promedio necesita atención urgente, pero hay opciones.** "
        "Una alternativa es solicitar excepcionalidad ante el Consejo Superior Universitario. "
        "No estás solo/a en esto: acércate a **Dirección Académica** y te orientamos en el proceso."
    )
elif papa_global < 3.0:
    st.warning(
        "🟠 **Estás pasando por un momento difícil, pero tiene salida.** "
        "Una alternativa es solicitar reingreso ante el Consejo de Facultad. "
        "En **Dirección Académica** te ayudamos a revisar fechas y requisitos."
    )
elif papa_global < 3.4:
    st.info(
        "🔵 **Vas aprobando, aunque con margen de mejora.** "
        "Un pequeño esfuerzo en las materias correctas puede marcar la diferencia. "
        "En **Dirección Académica** podemos ayudarte a armar un plan."
    )
else:
    st.success(
        "🟢 **¡Tu promedio va muy bien!** Sigue así. "
        "Y si quieres potenciarlo aún más, en **Dirección Académica** "
        "encuentras estrategias y oportunidades para crecer."
    )

st.markdown("</div>", unsafe_allow_html=True)

sugerencias = []

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader(f"💡 Ideas para mejorar — {ultimo_periodo}")
st.caption("Estas sugerencias se basan en tu último periodo. Míralas como oportunidades, no como obligaciones.")

en_riesgo  = df_ultimo[df_ultimo["Nota"] < 3.0]
en_alerta  = df_ultimo[(df_ultimo["Nota"] >= 3.0) & (df_ultimo["Nota"] < 3.5)]
destacadas = df_ultimo[df_ultimo["Nota"] >= 4.0]

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.metric("En riesgo (< 3.0)", len(en_riesgo),
              delta=f"-{len(en_riesgo)}" if len(en_riesgo) > 0 else None,
              delta_color="inverse")
with col_s2:
    st.metric("En alerta (3.0 – 3.4)", len(en_alerta))
with col_s3:
    st.metric("Destacadas (≥ 4.0)", len(destacadas))

st.markdown("---")

if not en_riesgo.empty:
    st.error("#### 🔴 Materias que necesitan tu atención")
    for _, row in en_riesgo.iterrows():
        faltantes = round(3.0 - float(row["Nota"]), 1)
        st.markdown(
            f"- **{row['Asignatura']}** — nota actual: `{row['Nota']}` · "
            f"Estás a **{faltantes} puntos** de aprobarla. ¡Aún puedes lograrlo!"
        )

if not en_alerta.empty:
    st.warning("#### 🟠 Materias que puedes fortalecer")
    for _, row in en_alerta.iterrows():
        mejora = round(3.5 - float(row["Nota"]), 1)
        st.markdown(
            f"- **{row['Asignatura']}** — nota actual: `{row['Nota']}` · "
            f"Con solo **{mejora} puntos más** llegas a 3.5 y proteges tu promedio."
        )

st.markdown("---")
st.info("#### 📈 ¿Y si subes una nota? Mira el impacto")

for _, row in df_ultimo.iterrows():
    nota_actual = float(row["Nota"])
    if nota_actual < 4.5:
        for meta in [3.0, 3.5, 4.0, 4.5]:
            if meta > nota_actual:
                nueva_sp   = (sp_ultimo
                              - (nota_actual * row["Creditos"])
                              + (meta        * row["Creditos"]))
                nuevo_papa = nueva_sp / sc_ultimo if sc_ultimo > 0 else 0
                if nuevo_papa >= 3.0:
                    diff  = round(nuevo_papa - papa_ultimo, 3)
                    signo = "+" if diff >= 0 else ""
                    nivel = ("impacto alto 🚀"  if abs(diff) >= 0.3 else
                             "impacto medio 📊" if abs(diff) >= 0.1 else
                             "impacto leve 📌")
                    sugerencias.append(
                        f"Si subes **{row['Asignatura']}** de {nota_actual} a **{meta}** "
                        f"→ Te quedaría en **{round(nuevo_papa, 3)}** "
                        f"({signo}{diff} pts · {nivel})"
                    )
                    break

if sugerencias:
    for s in sugerencias:
        st.markdown(f"- {s}")
    st.markdown("")
    st.markdown(
        "> 📌 **Si sientes que necesitas apoyo para lograrlo, en Dirección Académica "
        "podemos construir contigo una estrategia a tu medida. No dudes en buscarnos.**"
    )
else:
    st.success("✅ ¡Tu último periodo va muy bien! No hay ajustes urgentes que hacer.")

st.markdown("---")
st.markdown("#### 🗺️ Tu siguiente paso")
st.markdown(
    "El equipo de [Acompañamiento Académico de Dirección Académica](https://lnk.bio/PROFESIONALES) "
    "está para apoyarte. Agenda una cita cuando lo necesites."
)

if papa_ultimo < 2.7:
    st.error(
        "**Tu último periodo fue difícil, y está bien pedir ayuda.** Juntos podemos:\n"
        "- Revisar el proceso de solicitud de excepcionalidad.\n"
        "- Identificar qué materias priorizar para recuperarte.\n"
        "- Construir un plan realista, semestre a semestre."
    )
elif papa_ultimo < 3.0:
    st.warning(
        "**Este periodo fue retador, pero puedes darle la vuelta.** Te podemos acompañar a:\n"
        "- Orientarte sobre el reingreso si llegara a aplicar.\n"
        "- Enfocar tu esfuerzo en las materias con mayor peso en créditos.\n"
        "- Encontrar estrategias de estudio y manejo del tiempo que te funcionen."
    )
elif papa_ultimo < 3.4:
    st.info(
        "**Vas bien encaminado/a, solo falta un empujón.** Podemos ayudarte a:\n"
        "- Trazar un plan para llevar tu P.A.P.A. a 3.5 o más.\n"
        "- Detectar dónde un pequeño esfuerzo genera el mayor impacto.\n"
        "- Conectarte con tutorías y acompañamiento académico."
    )
else:
    st.success(
        "**¡Excelente periodo! Sigue construyendo sobre esto:**\n"
        "- Cuida las materias en alerta antes de que afecten tu promedio.\n"
        "- Pregunta por estrategias para alcanzar un P.A.P.A. de 4.0 o más.\n"
        "- Explora oportunidades como monitorias o semilleros de investigación."
    )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📄 Llévate tu reporte")
st.caption("Descarga un PDF con todos tus resultados para guardarlo o compartirlo cuando lo necesites.")

pdf_buffer = generar_pdf(
    df, papa_global, papas_periodo, ultimo_periodo,
    df_ultimo, sugerencias, total_pres, total_auto,
    estudiante_nombre, estudiante_cedula, estudiante_correo, estudiante_telefono
)
st.download_button(
    label="⬇️  Descargar Reporte PDF",
    data=pdf_buffer,
    file_name=f"reporte_academico_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
    mime="application/pdf"
)

st.markdown(
    "📄 Para más información sobre el cálculo del P.A.P.A. y créditos disponibles, "
    "consulta el [Acuerdo 008 de 2008 del CSU](https://legal.unal.edu.co/rlunal/home/doc.jsp?d_i=34983)."
)

st.markdown("</div>", unsafe_allow_html=True)

with st.expander("ℹ️ ¿Quieres saber cómo calculamos todo?"):
    st.markdown("""
    **Tu P.A.P.A.** se calcula multiplicando cada nota por sus créditos,
    sumando todo y dividiendo entre el total de créditos. Así las materias
    con más créditos pesan más en tu promedio.

    **Ejemplo:** (3,8×4 + 4,2×3 + 3,5×4 + 4,5×2 + 3,2×3) / 16 = **3,775**

    - El **P.A.P.A. por periodo** usa solo las materias de ese periodo.
    - El **P.A.P.A. global** usa todas las materias que ingresaste.
    - Las **sugerencias y horas de estudio** se basan en tu último periodo.
    - Tu **estado académico** se evalúa con el P.A.P.A. global.

    **Sobre las horas:** cada crédito equivale a 1 hora de clase y 2 horas
    de trabajo autónomo a la semana.

    > ¿Dudas? En **Acompañamiento Académico** te las resolvemos con gusto.
    """)

st.markdown("""
<style>
.footer-icons {
    position: fixed;
    bottom: 0; left: 0;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    background: black;
    padding: 10px 0;
    z-index: 999;
    font-size: 14px;
    color: white;
}
</style>
<div class="footer-icons">
    <div>Síguenos en nuestras redes sociales</div>
    <div style="display:flex; gap:15px;">
        <a href="https://www.facebook.com/share/1B6kSKkmCS/?mibextid=wwXIfr" target="_blank">
            <img src="https://cdn-icons-png.flaticon.com/32/733/733547.png"/>
        </a>
        <a href="https://www.instagram.com/palmiradiracademica?igsh=MTYzMXgwMG5zNDIxbQ%3D%3D&utm_source=qr" target="_blank">
            <img src="https://cdn-icons-png.flaticon.com/32/733/733558.png"/>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)
