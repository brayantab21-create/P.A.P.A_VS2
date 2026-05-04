import streamlit as st
import pandas as pd
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# -----------------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------------
st.set_page_config(
    page_title="Calculadora Académica",
    layout="wide",
    page_icon="🎓"
)

# -----------------------------------
# ESTILOS CSS
# -----------------------------------
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

    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# -----------------------------------
# FUNCIÓN PARA GENERAR PDF
# -----------------------------------
def generar_pdf(df, papa_semestre, papa_final, tiene_historial,
                papa_anterior, creditos_anteriores,
                total_presenciales, total_autonomas, sugerencias_texto,
                creditos_disponibles, variacion_creditos, creditos_finales,
                tiene_creditos):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch
    )

    story = []

    azul_oscuro = colors.HexColor("#1a2e5a")
    azul_medio  = colors.HexColor("#4f8ef7")
    gris_claro  = colors.HexColor("#f0f4f8")
    gris_borde  = colors.HexColor("#e2e8f0")
    rojo        = colors.HexColor("#e74c3c")
    verde       = colors.HexColor("#27ae60")
    naranja     = colors.HexColor("#f39c12")

    def ep(name, **kw):
        base = dict(fontSize=10, textColor=colors.HexColor("#2d3748"), spaceAfter=4, leading=14)
        base.update(kw)
        return ParagraphStyle(name, **base)

    e_titulo    = ep('t', fontSize=20, textColor=azul_oscuro, alignment=TA_CENTER, spaceAfter=4, fontName='Helvetica-Bold')
    e_subtitulo = ep('s', fontSize=11, textColor=colors.HexColor("#5a6a7e"), alignment=TA_CENTER, spaceAfter=16)
    e_seccion   = ep('sec', fontSize=13, textColor=azul_oscuro, spaceBefore=14, spaceAfter=6, fontName='Helvetica-Bold')
    e_normal    = ep('n')
    e_footer    = ep('f', fontSize=8, textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER)
    e_alerta    = ep('a', fontSize=10, textColor=rojo, fontName='Helvetica-Bold')
    e_ok        = ep('ok', fontSize=10, textColor=verde, fontName='Helvetica-Bold')

    def tabla_simple(data, col_widths):
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), azul_oscuro),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [gris_claro, colors.white]),
            ('GRID', (0,0), (-1,-1), 0.5, gris_borde),
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ]))
        return t

    # Encabezado
    story += [
        Paragraph("Calculadora Académica", e_titulo),
        Paragraph("Reporte de P.A.P.A., Carga Horaria y Créditos Disponibles", e_subtitulo),
        HRFlowable(width="100%", thickness=2, color=azul_medio),
        Spacer(1, 12),
        Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", e_normal),
        Spacer(1, 10),
    ]

    # Historial previo
    if tiene_historial:
        story.append(Paragraph("Historial Académico Previo", e_seccion))
        cols = ["P.A.P.A. anterior", "Créditos cursados anteriores"]
        vals = [str(round(papa_anterior, 2)), str(int(creditos_anteriores))]
        if tiene_creditos:
            cols.append("Créditos disponibles actuales")
            vals.append(str(int(creditos_disponibles)))
        w = [6.5*inch / len(cols)] * len(cols)
        story += [tabla_simple([cols, vals], w), Spacer(1, 12)]

    # Tabla asignaturas
    story.append(Paragraph("Asignaturas del Semestre", e_seccion))
    enc = ["Asignatura", "Créd.", "Nota", "Estado", "H. Pres.", "H. Aut.", "Var. Créd."]
    filas = [enc]
    for _, row in df.iterrows():
        aprueba = row["Nota"] >= 3.0
        filas.append([
            str(row["Asignatura"]),
            str(int(row["Créditos"])),
            str(round(row["Nota"], 1)),
            "Aprobó" if aprueba else "Perdió",
            str(int(row["Horas Presenciales"])),
            str(int(row["Horas Autónomas"])),
            f"+{int(row['Créditos']*2)}" if aprueba else f"-{int(row['Créditos'])}"
        ])
    col_w = [2.0*inch, 0.55*inch, 0.55*inch, 0.75*inch, 0.65*inch, 0.65*inch, 0.85*inch]
    t_asig = Table(filas, colWidths=col_w)
    t_asig.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), azul_oscuro),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [gris_claro, colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, gris_borde),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,1), (0,-1), 6),
    ]))
    story += [t_asig, Spacer(1, 14)]

    # Resultados P.A.P.A.
    story.append(Paragraph("Resultados P.A.P.A.", e_seccion))
    res = [["Indicador", "Valor"],
           ["P.A.P.A. del semestre actual", str(round(papa_semestre, 2))]]
    if tiene_historial:
        res.append(["P.A.P.A. acumulado real", str(round(papa_final, 2))])
    res += [
        ["Horas presenciales / semana", str(int(total_presenciales))],
        ["Horas autónomas / semana",    str(int(total_autonomas))],
    ]
    story += [tabla_simple(res, [3.5*inch, 3*inch]), Spacer(1, 14)]

    # Créditos disponibles
    if tiene_creditos:
        story.append(Paragraph("Créditos Disponibles", e_seccion))
        signo = "+" if variacion_creditos >= 0 else ""
        cr = [
            ["Antes del semestre", "Variación", "Después del semestre"],
            [str(int(creditos_disponibles)),
             f"{signo}{int(variacion_creditos)}",
             str(int(creditos_finales))]
        ]
        tc = Table(cr, colWidths=[2.1*inch, 2.1*inch, 2.1*inch])
        var_color = verde if variacion_creditos >= 0 else rojo
        fin_color = rojo if creditos_finales <= 10 else (naranja if creditos_finales <= 20 else azul_oscuro)
        tc.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), azul_oscuro),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,1), (-1,1), gris_claro),
            ('GRID', (0,0), (-1,-1), 0.5, gris_borde),
            ('TEXTCOLOR', (1,1), (1,1), var_color),
            ('FONTNAME', (1,1), (1,1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (2,1), (2,1), fin_color),
            ('FONTNAME', (2,1), (2,1), 'Helvetica-Bold'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story += [tc, Spacer(1, 8)]

        if creditos_finales <= 0:
            story.append(Paragraph(
                f"RIESGO DE PERDIDA DE CALIDAD DE ESTUDIANTE: Creditos disponibles = {int(creditos_finales)}. "
                "Es urgente acercarse a Direccion Academica.", e_alerta))
        elif creditos_finales <= 10:
            story.append(Paragraph(
                f"Creditos muy bajos ({int(creditos_finales)}). Acercarse con urgencia a Direccion Academica.", e_alerta))
        elif creditos_finales <= 20:
            story.append(Paragraph(
                f"Creditos en zona de alerta ({int(creditos_finales)}). Consultar con Direccion Academica.", e_normal))
        else:
            story.append(Paragraph(f"Creditos en zona estable ({int(creditos_finales)}).", e_ok))

        story.append(Spacer(1, 14))

    # Sugerencias
    if sugerencias_texto:
        story.append(Paragraph("Sugerencias Academicas", e_seccion))
        for s in sugerencias_texto:
            story.append(Paragraph(f"- {s.replace('**','')}", e_normal))
        story.append(Spacer(1, 10))

    # Estado académico
    story.append(Paragraph("Estado Academico (P.A.P.A.)", e_seccion))
    pev = papa_final
    if pev < 2.7:
        story += [Paragraph("Estado: RIESGO ALTO", e_alerta),
                  Paragraph("Puedes solicitar excepcionalidad ante el Consejo Superior Universitario. Puedes acudir a Dirección Académica y solicitar información al respecto.", e_normal)]
    elif pev < 3.0:
        story += [Paragraph("Estado: RIESGO MODERADO", e_normal),
                  Paragraph("Puedes solicitar reingreso ante el Consejo de Facultad. Puedes acudir a Dirección Académica y solicitar información al respecto", e_normal)]
    elif pev < 3.4:
        story += [Paragraph("Estado: ZONA DE ALERTA", e_normal),
                  Paragraph("Visita Direccion Academica para trazar un plan de mejora.", e_normal)]
    else:
        story += [Paragraph("Estado: ZONA ESTABLE", e_ok),
                  Paragraph("Puedes asistir a Direccion Academica para fortalecer tus procesos.", e_normal)]

    story += [
        Spacer(1, 16),
        HRFlowable(width="100%", thickness=1, color=gris_borde),
        Spacer(1, 6),
        Paragraph("Documento generado por la Calculadora Academica - Direccion Academica", e_footer)
    ]

    doc.build(story)
    buffer.seek(0)
    return buffer


# =============================================
# APP PRINCIPAL
# =============================================

st.markdown("<div class='titulo-principal'>🎓 Calculadora Académica</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Cálculo de P.A.P.A., carga horaria y créditos disponibles</div>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# -----------------------------------
# HISTORIAL ACADÉMICO PREVIO
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📋 Historial Académico Previo")
st.caption("Ingresa tus datos acumulados de semestres anteriores para obtener resultados reales.")

col_h1, col_h2, col_h3 = st.columns(3)

with col_h1:
    papa_anterior = st.number_input(
        "P.A.P.A. acumulado anterior.",
        min_value=0.0, max_value=5.0, step=0.01, value=0.0,
        help="Promedio Aritmético Ponderado Acumulado de semestres previos. En caso que sea tu primer semestre no debes diligenciarlo."
    )
with col_h2:
    creditos_anteriores = st.number_input(
        "Créditos cursados anteriormente. En caso que sea tu primer semestre no debes diligenciarlo.",
        min_value=0, max_value=500, step=1, value=0,
        help="Total de créditos cursados hasta el semestre anterior"
    )
with col_h3:
    creditos_disponibles = st.number_input(
        "Créditos disponibles en tu bolsa.",
        min_value=0, max_value=500, step=1, value=0,
        help="Créditos que tienes disponibles actualmente. Si apruebas se duplican; si pierdes se descuentan; hasta un total de 80 créditos, puedes revisar el Acuerdo 008 de 2008 del Consejo Superior Universitario. En caso que sea tu primer semestre no debes diligenciarlo."
    )

tiene_historial = creditos_anteriores > 0 and papa_anterior > 0
tiene_creditos  = creditos_disponibles > 0

if tiene_historial and tiene_creditos:
    st.success(
        f"✅ Historial cargado · P.A.P.A.: {round(papa_anterior,2)} · "
        f"Créditos cursados: {int(creditos_anteriores)} · "
        f"Créditos disponibles: {int(creditos_disponibles)}"
    )
elif tiene_historial:
    st.success(f"✅ Historial cargado · P.A.P.A.: {round(papa_anterior,2)} · Créditos: {int(creditos_anteriores)}")
elif tiene_creditos:
    st.info(f"ℹ️ Créditos disponibles registrados: {int(creditos_disponibles)}")
else:
    st.info("ℹ️ Sin historial previo — se calculará solo el semestre actual.")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# NÚMERO DE ASIGNATURAS
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📚 Asignaturas del Semestre actual")
num_asignaturas = st.number_input(
    "¿Cuántas asignaturas deseas ingresar?",
    min_value=1, max_value=15, step=1, value=5
)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# INGRESO DE DATOS
# -----------------------------------
datos = []
total_presenciales = 0
total_autonomas    = 0

st.markdown("<div class='card'>", unsafe_allow_html=True)

for i in range(int(num_asignaturas)):
    st.markdown(f"<span class='asignatura-header'>Asignatura {i+1}</span>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([5, 1, 1])

    with col1:
        nombre = st.text_input("Nombre", key=f"nombre_{i}",
                               label_visibility="collapsed",
                               placeholder=f"Nombre de la asignatura {i+1}")
    with col2:
        creditos = st.number_input("Créditos", min_value=1, max_value=10, step=1, key=f"creditos_{i}")
    with col3:
        nota = st.number_input("Nota", min_value=0.0, max_value=5.0, step=0.1, key=f"nota_{i}")

    horas_presenciales  = creditos
    horas_autonomas     = (creditos * 3) - creditos
    total_presenciales += horas_presenciales
    total_autonomas    += horas_autonomas

    datos.append({
        "Asignatura":         nombre if nombre else f"Asignatura {i+1}",
        "Créditos":           creditos,
        "Nota":               nota,
        "Horas Presenciales": horas_presenciales,
        "Horas Autónomas":    horas_autonomas
    })

    if i < int(num_asignaturas) - 1:
        st.markdown("---")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# CÁLCULOS GENERALES
# -----------------------------------
df = pd.DataFrame(datos)

suma_ponderada  = (df["Créditos"] * df["Nota"]).sum()
suma_creditos   = df["Créditos"].sum()
papa_semestre   = round(suma_ponderada / suma_creditos, 2) if suma_creditos > 0 else 0

if tiene_historial:
    creditos_totales = creditos_anteriores + suma_creditos
    papa_final       = round(((papa_anterior * creditos_anteriores) + suma_ponderada) / creditos_totales, 2) if creditos_totales > 0 else 0
else:
    papa_final       = papa_semestre
    creditos_totales = suma_creditos

# -----------------------------------
# CÁLCULO CRÉDITOS DISPONIBLES
# -----------------------------------
variacion_creditos = 0
for _, row in df.iterrows():
    if row["Nota"] >= 3.0:
        variacion_creditos += row["Créditos"] * 2   # Aprueba: se duplican
    else:
        variacion_creditos -= row["Créditos"]        # Pierde: se descuentan

creditos_finales = creditos_disponibles + variacion_creditos

# -----------------------------------
# RESUMEN CON ESTADO POR ASIGNATURA
# -----------------------------------
df_vista = df.copy()
df_vista.insert(3, "Estado",         df_vista["Nota"].apply(lambda n: "✅ Aprobó" if n >= 3.0 else "❌ Perdió"))
df_vista.insert(4, "Variación Créd.", df_vista.apply(
    lambda r: f"+{int(r['Créditos']*2)}" if r["Nota"] >= 3.0 else f"-{int(r['Créditos'])}", axis=1))
df_vista.index = [""] * len(df_vista)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📊 Resumen Académico")
st.dataframe(df_vista, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# MÉTRICAS P.A.P.A.
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("🎯 Resultados P.A.P.A.")

if tiene_historial:
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("P.A.P.A. Este Semestre", papa_semestre)
    with col_m2:
        delta = round(papa_final - papa_anterior, 2)
        st.metric("P.A.P.A. Acumulado Real", papa_final, delta=delta)
    with col_m3:
        st.metric("Créditos Cursados Acumulados", int(creditos_totales))
else:
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("P.A.P.A. del Semestre", papa_semestre)
    with col_m2:
        st.metric("Total Créditos", int(suma_creditos))

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# SECCIÓN: CRÉDITOS DISPONIBLES
# -----------------------------------
if tiene_creditos:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🪙 Créditos Disponibles")
    st.caption("Proyección de tu bolsa de créditos después de este semestre.")

    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        st.metric("Créditos antes del semestre", int(creditos_disponibles))
    with col_c2:
        signo = "+" if variacion_creditos >= 0 else ""
        st.metric("Variación este semestre", f"{signo}{int(variacion_creditos)}",
                  delta=int(variacion_creditos))
    with col_c3:
        st.metric("Créditos después del semestre", int(creditos_finales))

    st.markdown("---")

    # Desglose por asignatura
    for _, row in df.iterrows():
        if row["Nota"] >= 3.0:
            st.markdown(
                f"- ✅ **{row['Asignatura']}** — aprobó con {row['Nota']} → "
                f"suma **+{int(row['Créditos']*2)}** créditos a tu bolsa"
            )
        else:
            st.markdown(
                f"- ❌ **{row['Asignatura']}** — perdió con {row['Nota']} → "
                f"descuenta **{int(row['Créditos'])}** créditos de tu bolsa"
            )

    st.markdown("---")

    # Alertas
    if creditos_finales <= 0:
        st.error(
            f"🚨 **Riesgo de pérdida de calidad de estudiante.** "
            f"Tu bolsa de créditos llegaría a **{int(creditos_finales)}**. "
            "Sin créditos disponibles no podrás matricular el próximo semestre. "
            "Es urgente que te acerques a **Dirección Académica** para explorar opciones."
        )
    elif creditos_finales <= 10:
        st.error(
            f"⚠️ **Créditos muy bajos ({int(creditos_finales)} restantes).** "
            "Estás en riesgo de no poder continuar matriculando. "
            "Acércate con urgencia a **Dirección Académica**."
        )
    elif creditos_finales <= 20:
        st.warning(
            f"🟠 **Créditos en zona de alerta ({int(creditos_finales)} restantes).** "
            "Se recomienda consultar con **Dirección Académica** para planificar los próximos semestres."
        )
    else:
        st.success(
            f"🟢 **Créditos en zona estable ({int(creditos_finales)} restantes).** "
            "Puedes continuar con normalidad."
        )

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# ESTADO ACADÉMICO (P.A.P.A.)
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📌 Estado Académico")

papa_eval = papa_final

if papa_eval < 2.7:
    st.error(
        "🔴 **Riesgo alto (P.A.P.A.).** Puedes solicitar excepcionalidad ante el Consejo Superior Universitario. "
        "Acércate a Dirección Académica para orientaciones."
    )
elif papa_eval < 3.0:
    st.warning(
        "🟠 **Riesgo moderado (P.A.P.A.).** Puedes solicitar reingreso ante el Consejo de Facultad. "
        "Acércate a Dirección Académica para revisar fechas y orientaciones."
    )
elif papa_eval < 3.4:
    st.info(
        "🔵 **Zona de alerta (P.A.P.A.).** Acércate a Dirección Académica para trazar "
        "un plan que fortalezca las asignaturas con bajo rendimiento."
    )
else:
    st.success(
        "🟢 **Zona estable (P.A.P.A.).** Puedes asistir a Dirección Académica para explorar "
        "estrategias que potencien aún más tu rendimiento."
    )

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# SUGERENCIAS ACADÉMICAS
# -----------------------------------
sugerencias = []

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("💡 Sugerencias Académicas")

if suma_creditos > 0:
    for _, row in df.iterrows():
        nota_actual = row["Nota"]
        if nota_actual < 3.5:
            for meta_nota in [3.0, 3.5, 4.0]:
                if meta_nota > nota_actual:
                    nueva_sp = suma_ponderada - (nota_actual * row["Créditos"]) + (meta_nota * row["Créditos"])
                    if tiene_historial:
                        nuevo_papa = ((papa_anterior * creditos_anteriores) + nueva_sp) / creditos_totales
                    else:
                        nuevo_papa = nueva_sp / suma_creditos

                    if nuevo_papa >= 3.0:
                        sugerencias.append(
                            f"Si subes **{row['Asignatura']}** de {nota_actual} a {meta_nota}, "
                            f"tu P.A.P.A. {'acumulado ' if tiene_historial else ''}sería aprox. **{round(nuevo_papa, 2)}**."
                        )
                        break

    if sugerencias:
        for s in sugerencias:
            st.markdown(f"- {s}")
    else:
        st.info("No se encontraron ajustes relevantes para mejorar el P.A.P.A.")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# CARGA HORARIA
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("⏰ Carga Horaria Total del Semestre")

colA, colB = st.columns(2)
with colA:
    st.metric("Horas Presenciales por semana", total_presenciales)
with colB:
    st.metric("Horas Autónomas por semana", total_autonomas)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# EXPORTAR PDF
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📄 Exportar Reporte")
st.caption("Descarga un reporte completo en PDF con todos tus resultados.")

if suma_creditos > 0:
    pdf_buffer = generar_pdf(
        df, papa_semestre, papa_final, tiene_historial,
        papa_anterior, creditos_anteriores,
        total_presenciales, total_autonomas, sugerencias,
        creditos_disponibles, variacion_creditos, creditos_finales,
        tiene_creditos
    )

    st.download_button(
        label="⬇️  Descargar Reporte PDF",
        data=pdf_buffer,
        file_name=f"reporte_academico_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf"
    )
else:
    st.warning("Ingresa al menos una asignatura con créditos válidos para generar el PDF.")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# EXPLICACIÓN
# -----------------------------------
with st.expander("ℹ️ ¿Cómo se realizan los cálculos?"):
    st.markdown("""
    **Cálculo del P.A.P.A.:**
    Se multiplica la nota de cada asignatura por sus créditos, se suman y se dividen entre el total de créditos.

    **Con historial previo:**
    `PAPA_real = (PAPA_anterior × Créditos_anteriores + Suma_ponderada_semestre) / Créditos_totales`

    **Créditos disponibles:**
    - Si **apruebas** (nota ≥ 3.0) → tu bolsa suma `créditos × 2`
    - Si **pierdes** (nota < 3.0) → tu bolsa descuenta `créditos × 1`
    - Si la bolsa llega a 0 o menos → riesgo de pérdida de calidad de estudiante

    **Horas presenciales:** 1 hora semanal por crédito.

    **Horas autónomas:** 2 horas semanales adicionales por crédito.

    **Ejemplo:** 4 créditos = 4 h presenciales + 8 h autónomas = 12 h totales por semana.

    > Si tienes dificultades, acude a **Acompañamiento Académico**.
    """)
