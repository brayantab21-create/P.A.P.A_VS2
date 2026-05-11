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

    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# -----------------------------------
# FUNCIÓN PARA GENERAR PDF
# -----------------------------------
def generar_pdf(df, papa, total_presenciales, total_autonomas,
                sugerencias_texto, balance_creditos, tope_alcanzado):

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

    def ep(name, **kw):
        base = dict(fontSize=10, textColor=colors.HexColor("#2d3748"),
                    spaceAfter=4, leading=14)
        base.update(kw)
        return ParagraphStyle(name, **base)

    e_titulo    = ep('t',   fontSize=20, textColor=azul_oscuro,
                     alignment=TA_CENTER, spaceAfter=4, fontName='Helvetica-Bold')
    e_subtitulo = ep('s',   fontSize=11, textColor=colors.HexColor("#5a6a7e"),
                     alignment=TA_CENTER, spaceAfter=16)
    e_seccion   = ep('sec', fontSize=13, textColor=azul_oscuro,
                     spaceBefore=14, spaceAfter=6, fontName='Helvetica-Bold')
    e_normal    = ep('n')
    e_footer    = ep('f',   fontSize=8,  textColor=colors.HexColor("#94a3b8"),
                     alignment=TA_CENTER)
    e_alerta    = ep('a',   fontSize=10, textColor=rojo,  fontName='Helvetica-Bold')
    e_ok        = ep('ok',  fontSize=10, textColor=verde, fontName='Helvetica-Bold')

    def tabla_base(data, col_widths):
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND',     (0,0), (-1,0), azul_oscuro),
            ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
            ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',       (0,0), (-1,-1), 9),
            ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
            ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [gris_claro, colors.white]),
            ('GRID',           (0,0), (-1,-1), 0.5, gris_borde),
            ('TOPPADDING',     (0,0), (-1,-1), 7),
            ('BOTTOMPADDING',  (0,0), (-1,-1), 7),
        ]))
        return t

    story += [
        Paragraph("Calculadora Academica", e_titulo),
        Paragraph("Reporte de P.A.P.A. y Carga Horaria", e_subtitulo),
        HRFlowable(width="100%", thickness=2, color=azul_medio),
        Spacer(1, 12),
        Paragraph(
            f"Fecha de generacion: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            e_normal),
        Spacer(1, 10),
    ]

    # Tabla asignaturas
    story.append(Paragraph("Asignaturas", e_seccion))
    enc = ["Asignatura", "Creditos", "Nota", "Estado",
           "H. Presenciales", "H. Autonomas"]
    filas = [enc]
    for _, row in df.iterrows():
        aprueba = row["Nota"] >= 3.0
        filas.append([
            str(row["Asignatura"]),
            str(int(row["Creditos"])),
            str(round(float(row["Nota"]), 1)),
            "Aprobo" if aprueba else "Perdio",
            str(int(row["Horas Presenciales"])),
            str(int(row["Horas Autonomas"])),
        ])
    col_w = [2.0*inch, 0.75*inch, 0.65*inch, 0.75*inch, 1.1*inch, 1.05*inch]
    t_asig = Table(filas, colWidths=col_w)
    t_asig.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,0), azul_oscuro),
        ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
        ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,-1), 9),
        ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
        ('ALIGN',          (0,1), (0,-1), 'LEFT'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [gris_claro, colors.white]),
        ('GRID',           (0,0), (-1,-1), 0.5, gris_borde),
        ('TOPPADDING',     (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 6),
        ('LEFTPADDING',    (0,1), (0,-1), 6),
    ]))
    story += [t_asig, Spacer(1, 14)]

    # Resultados
    story.append(Paragraph("Resultados", e_seccion))
    res = [
        ["Indicador", "Valor"],
        ["P.A.P.A. del semestre",         str(round(papa, 2))],
        ["Total creditos matriculados",   str(int(df["Creditos"].sum()))],
        ["Horas presenciales / semana",   str(int(total_presenciales))],
        ["Horas autonomas / semana",      str(int(total_autonomas))],
        ["Creditos disponibles en bolsa", str(int(balance_creditos))],
        ["Tope de 80 alcanzado",
         "Si" if tope_alcanzado else "No"],
    ]
    story += [tabla_base(res, [3.5*inch, 3.0*inch]), Spacer(1, 14)]

    # Sugerencias
    if sugerencias_texto:
        story.append(Paragraph("Sugerencias Academicas", e_seccion))
        for s in sugerencias_texto:
            story.append(Paragraph(f"- {s.replace('**','')}", e_normal))
        story.append(Spacer(1, 10))

    # Estado
    story.append(Paragraph("Estado Academico", e_seccion))
    if papa < 2.7:
        story += [Paragraph("Estado: RIESGO ALTO", e_alerta),
                  Paragraph("Solicitar excepcionalidad ante el Consejo Superior "
                             "Universitario. Acudir a Direccion Academica.", e_normal)]
    elif papa < 3.0:
        story += [Paragraph("Estado: RIESGO MODERADO", e_normal),
                  Paragraph("Solicitar reingreso ante el Consejo de Facultad. "
                             "Acudir a Direccion Academica.", e_normal)]
    elif papa < 3.4:
        story += [Paragraph("Estado: ZONA DE ALERTA", e_normal),
                  Paragraph("Visitar Direccion Academica para plan de mejora.", e_normal)]
    else:
        story += [Paragraph("Estado: ZONA ESTABLE", e_ok),
                  Paragraph("Asistir a Direccion Academica para fortalecer procesos.",
                             e_normal)]

    story += [
        Spacer(1, 16),
        HRFlowable(width="100%", thickness=1, color=gris_borde),
        Spacer(1, 6),
        Paragraph(
            "Documento generado por la Calculadora Academica - Direccion Academica",
            e_footer)
    ]

    doc.build(story)
    buffer.seek(0)
    return buffer


# =============================================
# APP PRINCIPAL
# =============================================

st.markdown(
    "<div class='titulo-principal'>🎓 Calculadora Académica</div>",
    unsafe_allow_html=True)
st.markdown(
    "<div class='subtitulo'>Cálculo de P.A.P.A. y carga horaria</div>",
    unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# -----------------------------------
# MÉTODO DE INGRESO
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📚 Asignaturas del Semestre")

metodo = st.radio(
    "¿Cómo deseas ingresar las asignaturas?",
    ["✍️ Ingresar manualmente", "📋 Pegar desde Excel"],
    horizontal=True
)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# RECOLECCIÓN DE DATOS
# -----------------------------------
datos              = []
total_presenciales = 0
total_autonomas    = 0

if metodo == "✍️ Ingresar manualmente":

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    num_asignaturas = st.number_input(
        "¿Cuántas asignaturas deseas ingresar?",
        min_value=1, max_value=300, step=1, value=5
    )

    for i in range(int(num_asignaturas)):
        st.markdown(
            f"<span class='asignatura-header'>Asignatura {i+1}</span>",
            unsafe_allow_html=True)
        col1, col2, col3 = st.columns([5, 1, 1])
        with col1:
            nombre = st.text_input(
                "Nombre", key=f"nombre_{i}",
                label_visibility="collapsed",
                placeholder=f"Nombre de la asignatura {i+1}")
        with col2:
            creditos = st.number_input(
                "Creditos", min_value=1, max_value=10,
                step=1, key=f"creditos_{i}")
        with col3:
            nota = st.number_input(
                "Nota", min_value=0.0, max_value=5.0,
                step=0.1, key=f"nota_{i}")

        h_pres = creditos
        h_auto = (creditos * 3) - creditos
        total_presenciales += h_pres
        total_autonomas    += h_auto

        datos.append({
            "Asignatura":         nombre if nombre else f"Asignatura {i+1}",
            "Creditos":           creditos,
            "Nota":               nota,
            "Horas Presenciales": h_pres,
            "Horas Autonomas":    h_auto
        })

        if i < int(num_asignaturas) - 1:
            st.markdown("---")

    st.markdown("</div>", unsafe_allow_html=True)

else:  # Pegar desde Excel
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.caption(
        "Copia las celdas directamente desde Excel "
        "(columnas en orden: Asignatura · Créditos · Nota) y pégalas aquí. "
        "Sin fila de encabezados."
    )
    texto = st.text_area(
        "Pega aquí los datos:",
        height=200,
        placeholder="Cálculo diferencial\t4\t3.5\nÁlgebra lineal\t3\t4.0\nFísica I\t4\t2.8"
    )

    if texto.strip():
        errores = []
        for i, linea in enumerate(texto.strip().split("\n")):
            partes = linea.strip().split("\t")
            if len(partes) < 3:
                errores.append(
                    f"Fila {i+1}: se esperaban 3 columnas, "
                    f"se encontraron {len(partes)}.")
                continue
            try:
                nombre   = partes[0].strip()
                cred     = int(float(partes[1].strip()))
                nota     = float(partes[2].strip().replace(",", "."))
                h_pres   = cred
                h_auto   = (cred * 3) - cred
                total_presenciales += h_pres
                total_autonomas    += h_auto
                datos.append({
                    "Asignatura":         nombre,
                    "Creditos":           cred,
                    "Nota":               nota,
                    "Horas Presenciales": h_pres,
                    "Horas Autonomas":    h_auto
                })
            except ValueError:
                errores.append(
                    f"Fila {i+1}: verifica que créditos y nota sean números.")

        if errores:
            for e in errores:
                st.warning(e)
        if datos:
            st.success(f"✅ {len(datos)} asignaturas cargadas correctamente.")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# GUARDIA: sin datos no continuar
# -----------------------------------
if not datos:
    st.info("Ingresa al menos una asignatura para ver los resultados.")
    st.stop()

# -----------------------------------
# CÁLCULOS
# -----------------------------------
df             = pd.DataFrame(datos)
suma_ponderada = (df["Creditos"] * df["Nota"]).sum()
suma_creditos  = df["Creditos"].sum()
papa           = round(suma_ponderada / suma_creditos, 2) if suma_creditos > 0 else 0.0

# -----------------------------------
# RESUMEN
# -----------------------------------
df_vista = df.copy()
df_vista.insert(3, "Estado", df_vista["Nota"].apply(
    lambda n: "✅ Aprobó" if n >= 3.0 else "❌ Perdió"
))
df_vista = df_vista.rename(columns={
    "Creditos":           "Créditos",
    "Horas Autonomas":    "Horas Autónomas",
})
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

col_m1, col_m2 = st.columns(2)
with col_m1:
    st.metric("P.A.P.A. del Semestre", papa)
with col_m2:
    st.metric("Total Créditos Matriculados", int(suma_creditos))

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# BOLSA DE CRÉDITOS
# -----------------------------------
balance        = 0
tope_alcanzado = False
historial      = []

for _, row in df.iterrows():
    if row["Nota"] >= 3.0:
        if tope_alcanzado:
            efecto = "Sin efecto (tope 80 ya alcanzado)"
            estado = "✅ Aprobó"
        else:
            antes    = balance
            ganancia = int(row["Creditos"]) * 2
            balance  = min(balance + ganancia, 80)
            if balance >= 80:
                tope_alcanzado = True
            sumado = balance - antes
            efecto = (f"+{sumado}" if sumado == ganancia
                      else f"+{sumado} (tope 80)")
            estado = "✅ Aprobó"
    else:
        balance -= int(row["Creditos"])
        efecto   = f"-{int(row['Creditos'])}"
        estado   = "❌ Perdió"

    historial.append({
        "Asignatura": row["Asignatura"],
        "Nota":       row["Nota"],
        "Estado":     estado,
        "Efecto":     efecto,
        "Saldo":      int(balance)
    })

df_bolsa       = pd.DataFrame(historial)
df_bolsa.index = [""] * len(df_bolsa)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("🪙 Bolsa de Créditos Disponibles")
st.caption(
    "Acumula hasta 80 créditos aprobando asignaturas. "
    "Una vez alcanzado ese tope, aprobar más materias ya no suma créditos. "
    "Perder una materia siempre descuenta créditos."
)

col_b1, col_b2 = st.columns(2)
with col_b1:
    st.metric("Créditos disponibles", int(balance))
with col_b2:
    if tope_alcanzado:
        st.metric("Estado del tope", "🔒 Tope de 80 alcanzado")
    else:
        st.metric("Tope máximo", 80)

if tope_alcanzado:
    st.info(
        "🔒 Ya alcanzaste el tope de 80 créditos. "
        "Aprobar más materias no incrementará tu bolsa, "
        "pero perder materias sí la reducirá.")

with st.expander("Ver detalle de movimientos de créditos"):
    st.dataframe(df_bolsa, use_container_width=True)

st.markdown("---")

if balance <= 0:
    st.error(
        f"🚨 **Riesgo de pérdida de calidad de estudiante.** "
        f"Tu bolsa llegó a **{int(balance)} créditos**. "
        "Sin créditos disponibles no podrás matricular. "
        "Acércate urgentemente a **Dirección Académica**."
    )
elif balance <= 10:
    st.error(
        f"⚠️ **Créditos muy bajos ({int(balance)} restantes).** "
        "Estás en riesgo de no poder continuar matriculando. "
        "Acércate con urgencia a **Dirección Académica**."
    )
elif balance <= 20:
    st.warning(
        f"🟠 **Créditos en zona de alerta ({int(balance)} restantes).** "
        "Consulta con **Dirección Académica** para planificar los próximos semestres."
    )
else:
    st.success(
        f"🟢 **Créditos en zona estable ({int(balance)} restantes).** "
        "Puedes continuar con normalidad."
    )

st.markdown(
    "📄 Para más información consulta el "
    "[Acuerdo 008 de 2008 del CSU](PEGA_AQUÍ_EL_LINK)."
)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# ESTADO ACADÉMICO
# -----------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📌 Estado Académico")

if papa < 2.7:
    st.error(
        "🔴 **Riesgo alto.** Puedes solicitar excepcionalidad ante el Consejo "
        "Superior Universitario. Acércate a Dirección Académica para orientaciones."
    )
elif papa < 3.0:
    st.warning(
        "🟠 **Riesgo moderado.** Puedes solicitar reingreso ante el Consejo de "
        "Facultad. Acércate a Dirección Académica para revisar fechas y orientaciones."
    )
elif papa < 3.4:
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

# -----------------------------------
# SUGERENCIAS ACADÉMICAS
# -----------------------------------
sugerencias = []

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("💡 Sugerencias Académicas")

if suma_creditos > 0:
    for _, row in df.iterrows():
        nota_actual = float(row["Nota"])
        if nota_actual < 3.5:
            for meta_nota in [3.0, 3.5, 4.0]:
                if meta_nota > nota_actual:
                    nueva_sp   = (suma_ponderada
                                  - (nota_actual      * row["Creditos"])
                                  + (meta_nota        * row["Creditos"]))
                    nuevo_papa = nueva_sp / suma_creditos
                    if nuevo_papa >= 3.0:
                        sugerencias.append(
                            f"Si subes **{row['Asignatura']}** de "
                            f"{nota_actual} a {meta_nota}, tu P.A.P.A. "
                            f"sería aprox. **{round(nuevo_papa, 2)}**."
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

pdf_buffer = generar_pdf(
    df, papa,
    total_presenciales, total_autonomas,
    sugerencias, balance, tope_alcanzado
)
st.download_button(
    label="⬇️  Descargar Reporte PDF",
    data=pdf_buffer,
    file_name=f"reporte_academico_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
    mime="application/pdf"
)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# EXPLICACIÓN
# -----------------------------------
with st.expander("ℹ️ ¿Cómo se realizan los cálculos?"):
    st.markdown("""
    **Cálculo del P.A.P.A.:**
    Se multiplica la nota de cada asignatura por sus créditos, se suman esos
    productos y se dividen entre el total de créditos matriculados.

    **Bolsa de créditos:**
    - Si **apruebas** (nota ≥ 3.0) → suma `créditos × 2`, con tope de 80.
    - Si **pierdes** (nota < 3.0) → descuenta `créditos`.
    - Una vez alcanzado el tope de 80, aprobar materias ya **no suma más créditos**,
      aunque el saldo baje después por materias perdidas.

    **Horas presenciales:** 1 hora semanal por cada crédito.

    **Horas autónomas:** 2 horas semanales adicionales por cada crédito.

    **Ejemplo:** 4 créditos = 4 h presenciales + 8 h autónomas = 12 h/semana.

    > Si tienes dificultades, acude a **Acompañamiento Académico**.
    """)

# -----------------------------------
# FOOTER
# -----------------------------------
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
    box-shadow: 0 -2px 8px rgba(0,0,0,0.08);
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
