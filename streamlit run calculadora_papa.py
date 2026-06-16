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

    /* Subtítulos de secciones (st.subheader fuera de tarjetas) */
    div[data-testid="stMarkdownContainer"] h3 {
        color: #E6F2F7 !important;
    }

    /* Captions y texto de apoyo fuera de tarjetas */
    div[data-testid="stCaptionContainer"] p,
    .stCaption p {
        color: #aac4d4 !important;
    }

    /* Texto markdown general (links, párrafos fuera de tarjetas) */
    .stMarkdown p, .stMarkdown li,
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li {
        color: #d0e8f2 !important;
    }

    /* Expander label */
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

    /* Labels de inputs */
    .stNumberInput label,
    .stTextInput label,
    .stRadio label,
    .stSelectbox label {
        color: #2d3748 !important;
        font-weight: 500 !important;
    }

    /* Valores dentro de inputs */
    .stNumberInput input,
    .stTextInput input {
        color: #1a2e5a !important;
    }
</style>
""", unsafe_allow_html=True)

def generar_pdf(df, papa_global, papas_periodo, ultimo_periodo,
                df_ultimo, sugerencias, total_pres, total_auto):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []

    azul  = colors.HexColor("#1a2e5a")
    medio = colors.HexColor("#4f8ef7")
    gris  = colors.HexColor("#f0f4f8")
    borde = colors.HexColor("#e2e8f0")
    rojo  = colors.HexColor("#e74c3c")
    verde = colors.HexColor("#27ae60")

    def ep(name, **kw):
        base = dict(fontSize=10, textColor=colors.HexColor("#2d3748"),
                    spaceAfter=4, leading=14)
        base.update(kw)
        return ParagraphStyle(name, **base)

    et  = ep('t',  fontSize=20, textColor=azul, alignment=TA_CENTER,
             spaceAfter=4, fontName='Helvetica-Bold')
    es  = ep('s',  fontSize=11, textColor=colors.HexColor("#5a6a7e"),
             alignment=TA_CENTER, spaceAfter=16)
    ec  = ep('c',  fontSize=13, textColor=azul, spaceBefore=14,
             spaceAfter=6, fontName='Helvetica-Bold')
    en  = ep('n')
    ef  = ep('f',  fontSize=8, textColor=colors.HexColor("#94a3b8"),
             alignment=TA_CENTER)
    ea  = ep('a',  fontSize=10, textColor=rojo,  fontName='Helvetica-Bold')
    eok = ep('ok', fontSize=10, textColor=verde, fontName='Helvetica-Bold')

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

    story += [
        Paragraph("Calculadora Academica", et),
        Paragraph("Reporte de P.A.P.A. por Periodo y Global", es),
        HRFlowable(width="100%", thickness=2, color=medio),
        Spacer(1, 12),
        Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", en),
        Spacer(1, 10),
    ]

    story.append(Paragraph("P.A.P.A. por Periodo", ec))
    rows = [["Periodo", "Creditos", "P.A.P.A."]]
    for p, vals in sorted(papas_periodo.items()):
        rows.append([str(p), str(vals['creditos']), str(vals['papa'])])
    rows.append(["GLOBAL", str(int(df["Creditos"].sum())), str(papa_global)])
    story += [tbl(rows, [3*inch, 1.5*inch, 1.5*inch]), Spacer(1, 14)]

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

    story.append(Paragraph(f"Carga Horaria - Ultimo Periodo ({ultimo_periodo})", ec))
    ch = [["Horas Presenciales / semana", "Horas Autonomas / semana"],
          [str(int(total_pres)), str(int(total_auto))]]
    story += [tbl(ch, [3.25*inch, 3.25*inch]), Spacer(1, 14)]

    if sugerencias:
        story.append(Paragraph("Proyecciones de Mejora (Ultimo Periodo)", ec))
        for s in sugerencias:
            story.append(Paragraph(f"- {s.replace('**','')}", en))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            "Si no obtienes los resultados esperados, busca ayuda en "
            "Direccion Academica para generar una estrategia personalizada.", en))
        story.append(Spacer(1, 10))

    # Estado académico
    story.append(Paragraph("Estado Academico (P.A.P.A. Global)", ec))
    if papa_global < 2.7:
        story += [Paragraph("Estado: RIESGO ALTO", ea),
                  Paragraph("Solicitar excepcionalidad ante el Consejo Superior "
                             "Universitario. Acudir a Direccion Academica.", en)]
    elif papa_global < 3.0:
        story += [Paragraph("Estado: RIESGO MODERADO", en),
                  Paragraph("Solicitar reingreso ante el Consejo de Facultad.", en)]
    elif papa_global < 3.4:
        story += [Paragraph("Estado: ZONA DE ALERTA", en),
                  Paragraph("Visitar Direccion Academica para plan de mejora.", en)]
    else:
        story += [Paragraph("Estado: ZONA ESTABLE", eok),
                  Paragraph("Asistir a Direccion Academica para fortalecer procesos.", en)]

    story += [
        Spacer(1, 16),
        HRFlowable(width="100%", thickness=1, color=borde),
        Spacer(1, 6),
        Paragraph(
            "Documento generado por la Calculadora Academica - Direccion Academica",
            ef)
    ]

    doc.build(story)
    buffer.seek(0)
    return buffer

st.markdown("<div class='titulo-principal'>🎓 Calculadora Académica</div>",
            unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>P.A.P.A. por periodo y global</div>",
            unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

datos = []

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📚 Ingreso de Asignaturas")

num = st.number_input("¿Cuántas asignaturas deseas ingresar?",
                      min_value=1, max_value=200, step=1, value=5)

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
    st.info("Ingresa al menos una asignatura para ver los resultados.")
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
st.subheader("📊 P.A.P.A. por Periodo")

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
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.metric("P.A.P.A. Global", papa_global,
              help="Calculado sobre todas las asignaturas ingresadas")
with col_g2:
    st.metric("Créditos matriculados durante los diferentes periodos", int(suma_cred_global))

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader(f"📋 Detalle — Último Periodo: {ultimo_periodo}")

df_ult_vista = df_ultimo[["Asignatura", "Creditos", "Nota"]].copy()
df_ult_vista.insert(3, "Estado", df_ult_vista["Nota"].apply(
    lambda n: "✅ Aprobó" if n >= 3.0 else "❌ Perdió"))
df_ult_vista = df_ult_vista.rename(columns={"Creditos": "Créditos"})
df_ult_vista.index = [""] * len(df_ult_vista)
st.dataframe(df_ult_vista, use_container_width=True)

col_u1, col_u2 = st.columns(2)
with col_u1:
    st.metric(f"P.A.P.A. {ultimo_periodo}", papa_ultimo)
with col_u2:
    st.metric("Créditos vistos en este periodo", int(sc_ultimo))

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader(f"⏰ Carga Horaria — {ultimo_periodo}")
st.caption("Calculada únicamente con las asignaturas del último periodo inscrito.")

colA, colB, colC = st.columns(3)
with colA:
    st.metric("Horas presenciales / semana", total_pres)
with colB:
    st.metric("Horas autónomas / semana", total_auto)
with colC:
    st.metric("Total horas / semana", total_pres + total_auto)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📌 Estado Académico Global")
st.caption("Basado en el P.A.P.A. acumulado de todos los periodos ingresados.")

if papa_global < 2.7:
    st.error(
        "🔴 **Riesgo alto.** Puedes solicitar excepcionalidad ante el Consejo "
        "Superior Universitario. Acércate a Dirección Académica para orientaciones."
    )
elif papa_global < 3.0:
    st.warning(
        "🟠 **Riesgo moderado.** Puedes solicitar reingreso ante el Consejo de "
        "Facultad. Acércate a Dirección Académica para revisar fechas y orientaciones."
    )
elif papa_global < 3.4:
    st.info(
        "🔵 **Zona de alerta.** Acércate a Dirección Académica para trazar "
        "un plan que fortalezca las asignaturas con bajo rendimiento."
    )
else:
    st.success(
        "🟢 **Zona estable.** Puedes asistir a Dirección Académica para explorar "
        "estrategias que potencien aún más tu rendimiento."
    )

st.markdown("</div>", unsafe_allow_html=True)

sugerencias = []

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader(f"💡 Sugerencias de Mejora — {ultimo_periodo}")
st.caption("Las proyecciones se calculan únicamente con las asignaturas del último periodo inscrito.")

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
    st.error("#### 🔴 Asignaturas en riesgo")
    for _, row in en_riesgo.iterrows():
        faltantes = round(3.0 - float(row["Nota"]), 1)
        st.markdown(
            f"- ❌ **{row['Asignatura']}** — nota: `{row['Nota']}` · "
            f"Te faltan **{faltantes} puntos** para aprobar."
        )

if not en_alerta.empty:
    st.warning("#### 🟠 Asignaturas en alerta")
    for _, row in en_alerta.iterrows():
        mejora = round(3.5 - float(row["Nota"]), 1)
        st.markdown(
            f"- ⚠️ **{row['Asignatura']}** — nota: `{row['Nota']}` · "
            f"Con **{mejora} puntos más** llegarías a 3.5."
        )

st.markdown("---")
st.info("#### 📈 Proyecciones de mejora del P.A.P.A.")

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
                        f"→ P.A.P.A. del periodo aprox. **{round(nuevo_papa, 3)}** "
                        f"({signo}{diff} pts · {nivel})"
                    )
                    break

if sugerencias:
    for s in sugerencias:
        st.markdown(f"- {s}")
    st.markdown("")
    st.markdown(
        "> 📌 **Si no obtienes los resultados esperados con estas proyecciones, "
        "busca ayuda en Dirección Académica para generar una estrategia "
        "personalizada según tu situación académica.**"
    )
else:
    st.success("✅ El P.A.P.A. del último periodo está en zona sólida.")

st.markdown("---")
st.markdown("#### 🗺️ Plan de Acción")

if papa_ultimo < 2.7:
    st.error(
        "**Situación crítica en el último periodo.** Acércate a **Dirección Académica** para:\n"
        "- Conocer el proceso de solicitud de excepcionalidad.\n"
        "- Identificar las asignaturas prioritarias a recuperar.\n"
        "- Construir un plan semestre a semestre."
    )
elif papa_ultimo < 3.0:
    st.warning(
        "**Situación de riesgo en el último periodo.** En **Dirección Académica** puedes:\n"
        "- Orientarte sobre el proceso de reingreso si aplica.\n"
        "- Diseñar un plan de mejora enfocado en las materias con mayor peso.\n"
        "- Explorar estrategias de estudio y gestión del tiempo."
    )
elif papa_ultimo < 3.4:
    st.info(
        "**Zona de alerta en el último periodo.** En **Dirección Académica** puedes:\n"
        "- Trazar un plan para subir el P.A.P.A. al menos a 3.5.\n"
        "- Identificar asignaturas donde un pequeño esfuerzo genera mayor impacto.\n"
        "- Acceder a tutorías o acompañamiento académico."
    )
else:
    st.success(
        "**Último periodo en zona estable.** Para mantenerlo:\n"
        "- Prioriza las asignaturas en alerta antes de que afecten el promedio.\n"
        "- Consulta en **Dirección Académica** estrategias para alcanzar un P.A.P.A. de 4.0 o más.\n"
        "- Considera opciones como monitorias o semilleros de investigación."
    )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📄 Exportar Reporte")
st.caption("Reporte completo con P.A.P.A. por periodo, estado académico y sugerencias.")

pdf_buffer = generar_pdf(
    df, papa_global, papas_periodo, ultimo_periodo,
    df_ultimo, sugerencias, total_pres, total_auto
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

with st.expander("ℹ️ ¿Cómo se realizan los cálculos?"):
    st.markdown("""
    **P.A.P.A. por periodo:**
    Σ(nota × créditos) / Σ(créditos) de cada periodo.

    **P.A.P.A. Global:**
    Σ(nota × créditos) / Σ(créditos) de todos los periodos ingresados.

    **Sugerencias y horas:**
    Se calculan únicamente con el último periodo ingresado
    (el de mayor valor alfanumérico entre los periodos registrados).

    **Estado académico:**
    Se evalúa siempre sobre el P.A.P.A. global.

    **Horas presenciales:** 1 hora semanal por crédito.
    **Horas autónomas:** 2 horas semanales por crédito.

    **Ejemplo:** (3,8×4 + 4,2×3 + 3,5×4 + 4,5×2 + 3,2×3) / 16 = **3,775**

    > Para orientación personalizada acude a **Acompañamiento Académico**.
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
