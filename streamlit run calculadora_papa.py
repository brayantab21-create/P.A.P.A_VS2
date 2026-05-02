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
# ESTILOS CSS MEJORADOS
# -----------------------------------
st.markdown("""
<style>
    /* Fondo general */
    .stApp {
        background-color: #f0f4f8;
    }

    /* Tarjetas de sección */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 5px solid #4f8ef7;
    }

    .card-warning {
        border-left: 5px solid #f5a623;
    }

    .card-danger {
        border-left: 5px solid #e74c3c;
    }

    .card-success {
        border-left: 5px solid #27ae60;
    }

    /* Título principal */
    .titulo-principal {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 800;
        color: #1a2e5a;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }

    .subtitulo {
        text-align: center;
        font-size: 1.05rem;
        color: #5a6a7e;
        margin-bottom: 1.5rem;
    }

    /* Separador decorativo */
    .divider {
        height: 3px;
        background: linear-gradient(90deg, #4f8ef7, #a78bfa);
        border-radius: 2px;
        margin: 1.2rem 0;
    }

    /* Asignatura header */
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

    /* Métricas personalizadas */
    .metric-box {
        background: #1a2e5a;
        color: white;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        text-align: center;
        margin: 0.5rem 0;
    }

    .metric-label {
        font-size: 0.85rem;
        opacity: 0.75;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 800;
    }

    /* Botón PDF */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4f8ef7, #a78bfa) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 0.3px !important;
        box-shadow: 0 4px 12px rgba(79,142,247,0.35) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }

    /* Tabla más limpia */
    .dataframe {
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* Ocultar footer de Streamlit */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# -----------------------------------
# FUNCIÓN PARA GENERAR PDF
# -----------------------------------
def generar_pdf(df, papa_semestre, papa_final, tiene_historial,
                papa_anterior, creditos_anteriores,
                total_presenciales, total_autonomas, sugerencias_texto):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()
    story = []

    # Colores institucionales
    azul_oscuro = colors.HexColor("#1a2e5a")
    azul_medio = colors.HexColor("#4f8ef7")
    gris_claro = colors.HexColor("#f0f4f8")
    gris_borde = colors.HexColor("#e2e8f0")

    # Estilos
    estilo_titulo = ParagraphStyle(
        'titulo', fontSize=20, textColor=azul_oscuro,
        alignment=TA_CENTER, spaceAfter=4, fontName='Helvetica-Bold'
    )
    estilo_subtitulo = ParagraphStyle(
        'subtitulo', fontSize=11, textColor=colors.HexColor("#5a6a7e"),
        alignment=TA_CENTER, spaceAfter=16
    )
    estilo_seccion = ParagraphStyle(
        'seccion', fontSize=13, textColor=azul_oscuro,
        spaceBefore=14, spaceAfter=6, fontName='Helvetica-Bold'
    )
    estilo_normal = ParagraphStyle(
        'normal', fontSize=10, textColor=colors.HexColor("#2d3748"),
        spaceAfter=4, leading=14
    )
    estilo_footer = ParagraphStyle(
        'footer', fontSize=8, textColor=colors.HexColor("#94a3b8"),
        alignment=TA_CENTER
    )

    # --- Encabezado ---
    story.append(Paragraph("Calculadora Académica", estilo_titulo))
    story.append(Paragraph("Reporte de P.A.P.A. y Carga Horaria", estilo_subtitulo))
    story.append(HRFlowable(width="100%", thickness=2, color=azul_medio))
    story.append(Spacer(1, 12))

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    story.append(Paragraph(f"Fecha de generación: {fecha}", estilo_normal))
    story.append(Spacer(1, 10))

    # --- Historial previo ---
    if tiene_historial:
        story.append(Paragraph("Historial Académico Previo", estilo_seccion))
        data_hist = [
            ["P.A.P.A. anterior", "Créditos anteriores"],
            [str(round(papa_anterior, 2)), str(int(creditos_anteriores))]
        ]
        t = Table(data_hist, colWidths=[3 * inch, 3 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), azul_oscuro),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [gris_claro, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, gris_borde),
            ('ROUNDEDCORNERS', [6, 6, 6, 6]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

    # --- Tabla de asignaturas ---
    story.append(Paragraph("Asignaturas del Semestre", estilo_seccion))

    encabezados = ["Asignatura", "Créditos", "Nota", "H. Presenciales", "H. Autónomas"]
    tabla_data = [encabezados]
    for _, row in df.iterrows():
        tabla_data.append([
            str(row["Asignatura"]) if row["Asignatura"] else "—",
            str(int(row["Créditos"])),
            str(round(row["Nota"], 1)),
            str(int(row["Horas Presenciales"])),
            str(int(row["Horas Autónomas"]))
        ])

    col_widths = [2.5 * inch, 1 * inch, 0.8 * inch, 1.2 * inch, 1.2 * inch]
    tabla = Table(tabla_data, colWidths=col_widths)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), azul_oscuro),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [gris_claro, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, gris_borde),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 1), (0, -1), 8),
    ]))
    story.append(tabla)
    story.append(Spacer(1, 14))

    # --- Resultados P.A.P.A. ---
    story.append(Paragraph("Resultados", estilo_seccion))

    resultados = [["Indicador", "Valor"]]
    resultados.append(["P.A.P.A. del semestre actual", str(round(papa_semestre, 2))])
    if tiene_historial:
        resultados.append(["P.A.P.A. acumulado real", str(round(papa_final, 2))])
    resultados.append(["Horas presenciales totales", str(int(total_presenciales))])
    resultados.append(["Horas autónomas totales", str(int(total_autonomas))])

    tr = Table(resultados, colWidths=[3.5 * inch, 3 * inch])
    tr.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), azul_oscuro),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [gris_claro, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, gris_borde),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(tr)
    story.append(Spacer(1, 14))

    # --- Sugerencias ---
    if sugerencias_texto:
        story.append(Paragraph("Sugerencias Académicas", estilo_seccion))
        for sug in sugerencias_texto:
            sug_limpio = sug.replace("**", "")
            story.append(Paragraph(f"• {sug_limpio}", estilo_normal))
        story.append(Spacer(1, 10))

    # --- Estado académico ---
    story.append(Paragraph("Estado Académico", estilo_seccion))
    papa_eval = papa_final if tiene_historial else papa_semestre

    if papa_eval < 2.7:
        estado = ("RIESGO ALTO",
                  "Puedes solicitar excepcionalidad a la norma ante el Consejo Superior Universitario. "
                  "Acércate a Dirección Académica para orientaciones.")
    elif papa_eval < 3.0:
        estado = ("RIESGO MODERADO",
                  "Puedes solicitar reingreso ante el Consejo de Facultad. "
                  "Acércate a Dirección Académica para revisar fechas y orientaciones.")
    elif papa_eval < 3.4:
        estado = ("ZONA DE ALERTA",
                  "Tu promedio está en zona de alerta. Visita Dirección Académica para trazar un plan de mejora.")
    else:
        estado = ("ZONA ESTABLE",
                  "Tu promedio está en una zona estable. Puedes asistir a Dirección Académica "
                  "para fortalecer tus procesos.")

    story.append(Paragraph(f"Estado: {estado[0]}", estilo_normal))
    story.append(Paragraph(estado[1], estilo_normal))
    story.append(Spacer(1, 16))

    # --- Footer ---
    story.append(HRFlowable(width="100%", thickness=1, color=gris_borde))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Documento generado automáticamente por la Calculadora Académica · Dirección Académica",
        estilo_footer
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


# =============================================
# APP PRINCIPAL
# =============================================

# --- Título ---
st.markdown("<div class='titulo-principal'>🎓 Calculadora Académica</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Cálculo de P.A.P.A. y carga horaria semestral</div>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# -----------------------------------
# SECCIÓN: HISTORIAL PREVIO
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📋 Historial Académico Previo")
st.caption("Si ya cursaste semestres anteriores, ingresa tu P.A.P.A. y créditos acumulados para obtener el promedio real.")

col_hist1, col_hist2 = st.columns(2)
with col_hist1:
    papa_anterior = st.number_input(
        "P.A.P.A. acumulado anterior",
        min_value=0.0, max_value=5.0, step=0.01, value=0.0,
        help="Promedio Aritmético Ponderado Acumulado de semestres previos"
    )
with col_hist2:
    creditos_anteriores = st.number_input(
        "Total de créditos vistos anteriormente",
        min_value=0, max_value=500, step=1, value=0,
        help="Suma de todos los créditos aprobados o cursados hasta el semestre anterior"
    )

tiene_historial = creditos_anteriores > 0 and papa_anterior > 0

if tiene_historial:
    st.success(f"✅ Historial cargado: {int(creditos_anteriores)} créditos con P.A.P.A. de {round(papa_anterior, 2)}")
else:
    st.info("ℹ️ Sin historial previo — se calculará solo el semestre actual.")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# SECCIÓN: NÚMERO DE ASIGNATURAS
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📚 Asignaturas del Semestre")

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
total_autonomas = 0

st.markdown("<div class='card'>", unsafe_allow_html=True)

for i in range(int(num_asignaturas)):
    st.markdown(f"<span class='asignatura-header'>Asignatura {i+1}</span>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([5, 1, 1])

    with col1:
        nombre = st.text_input("Nombre", key=f"nombre_{i}", label_visibility="collapsed",
                                placeholder=f"Nombre de la asignatura {i+1}")
    with col2:
        creditos = st.number_input("Créditos", min_value=1, max_value=10, step=1,
                                    key=f"creditos_{i}", label_visibility="visible")
    with col3:
        nota = st.number_input("Nota", min_value=0.0, max_value=5.0, step=0.1,
                                key=f"nota_{i}", label_visibility="visible")

    horas_presenciales = creditos
    horas_autonomas = (creditos * 3) - creditos
    total_presenciales += horas_presenciales
    total_autonomas += horas_autonomas

    datos.append({
        "Asignatura": nombre if nombre else f"Asignatura {i+1}",
        "Créditos": creditos,
        "Nota": nota,
        "Horas Presenciales": horas_presenciales,
        "Horas Autónomas": horas_autonomas
    })

    if i < int(num_asignaturas) - 1:
        st.markdown("---")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# CÁLCULOS
# -----------------------------------
df = pd.DataFrame(datos)
df.index = [""] * len(df)

suma_ponderada = (df["Créditos"] * df["Nota"]).sum()
suma_creditos = df["Créditos"].sum()
papa_semestre = round(suma_ponderada / suma_creditos, 2) if suma_creditos > 0 else 0

if tiene_historial:
    suma_total = (papa_anterior * creditos_anteriores) + suma_ponderada
    creditos_totales = creditos_anteriores + suma_creditos
    papa_final = round(suma_total / creditos_totales, 2) if creditos_totales > 0 else 0
else:
    papa_final = papa_semestre
    creditos_totales = suma_creditos

# -----------------------------------
# RESUMEN
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📊 Resumen Académico")
st.dataframe(df, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# MÉTRICAS P.A.P.A.
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("🎯 Resultados P.A.P.A.")

if tiene_historial:
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("P.A.P.A. Este Semestre", papa_semestre,
                  help="Promedio calculado solo con las asignaturas actuales")
    with col_m2:
        delta = round(papa_final - papa_anterior, 2)
        st.metric("P.A.P.A. Acumulado Real", papa_final, delta=delta,
                  help="Promedio real incluyendo todo el historial académico")
    with col_m3:
        st.metric("Créditos Totales Acumulados", int(creditos_totales))
else:
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("P.A.P.A. del Semestre", papa_semestre)
    with col_m2:
        st.metric("Total Créditos", int(suma_creditos))

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# ESTADO ACADÉMICO
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📌 Estado Académico")

papa_eval = papa_final

if papa_eval < 2.7:
    st.error("🔴 **Riesgo alto.** Puedes solicitar excepcionalidad a la norma ante el Consejo Superior Universitario. "
             "Acércate a Dirección Académica para orientaciones sobre la solicitud.")
elif papa_eval < 3.0:
    st.warning("🟠 **Riesgo moderado.** Puedes solicitar reingreso ante el Consejo de Facultad. "
               "Acércate a Dirección Académica para revisar fechas y orientaciones.")
elif papa_eval < 3.4:
    st.info("🔵 **Zona de alerta.** Tu promedio requiere atención. Acércate a Dirección Académica "
            "para trazar un plan que fortalezca las asignaturas con bajo rendimiento.")
else:
    st.success("🟢 **Zona estable.** Tu promedio está en buen nivel. Puedes asistir a Dirección Académica "
               "para explorar estrategias que potencien aún más tu rendimiento.")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# SUGERENCIAS ACADÉMICAS
# -----------------------------------
sugerencias = []

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("💡 Sugerencias Académicas")

if suma_creditos > 0:
    for index, row in df.iterrows():
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
st.caption("Descarga un reporte completo con tus resultados académicos en formato PDF.")

if suma_creditos > 0:
    pdf_buffer = generar_pdf(
        df, papa_semestre, papa_final, tiene_historial,
        papa_anterior, creditos_anteriores,
        total_presenciales, total_autonomas, sugerencias
    )

    nombre_archivo = f"reporte_papa_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

    st.download_button(
        label="⬇️  Descargar Reporte PDF",
        data=pdf_buffer,
        file_name=nombre_archivo,
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
    Se multiplica la nota de cada asignatura por sus créditos, se suman esos productos
    y se divide entre el total de créditos. Así las materias con más créditos tienen mayor peso.

    **Con historial previo:**
    `PAPA_real = (PAPA_anterior × Créditos_anteriores + Suma_ponderada_semestre) / Créditos_totales`

    **Horas presenciales:** 1 hora semanal por cada crédito.

    **Horas autónomas:** Cada crédito equivale a 3 horas de trabajo total semanal
    (1 presencial + 2 autónomas).

    **Ejemplo:** 4 créditos = 4 h presenciales + 8 h autónomas = 12 h totales.

    > Si tienes dificultades para organizar tu tiempo, acude a **Acompañamiento Académico**.
    """)
