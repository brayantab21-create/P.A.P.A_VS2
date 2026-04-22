import streamlit as st
import pandas as pd

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
st.set_page_config(page_title="Calculadora P.A.P.A.", layout="centered")

st.title("Calculadora Académica")
st.caption("Promedio ponderado y carga horaria")

# -----------------------------
# CANTIDAD DE ASIGNATURAS
# -----------------------------
num_asignaturas = st.number_input(
    "¿Cuántas asignaturas desea ingresar?",
    min_value=1,
    max_value=15,
    step=1
)

datos = []

total_presenciales = 0
total_autonomas = 0

# -----------------------------
# INGRESO DE DATOS
# -----------------------------
for i in range(int(num_asignaturas)):
    st.subheader(f"Asignatura {i+1}")

    nombre = st.text_input(f"Nombre de la asignatura {i+1}", key=f"nombre_{i}")

    creditos = st.number_input(
        f"Créditos",
        min_value=1,
        max_value=10,
        step=1,
        key=f"creditos_{i}"
    )

    nota = st.number_input(
        f"Nota numérica",
        min_value=0.0,
        max_value=5.0,
        step=0.1,
        key=f"nota_{i}"
    )

    horas_presenciales = creditos
    horas_autonomas = (creditos * 3) - creditos

    total_presenciales += horas_presenciales
    total_autonomas += horas_autonomas

    datos.append({
        "Asignatura": nombre,
        "Créditos": creditos,
        "Nota": nota,
        "Horas Presenciales": horas_presenciales,
        "Horas Autónomas": horas_autonomas
    })

# -----------------------------
# TABLA RESUMEN
# -----------------------------
df = pd.DataFrame(datos)

st.subheader("Resumen Académico")
st.dataframe(df, width="stretch")

# -----------------------------
# CÁLCULO P.A.P.A.
# -----------------------------
if len(df) > 0:
    suma_ponderada = (df["Créditos"] * df["Nota"]).sum()
    suma_creditos = df["Créditos"].sum()

    if suma_creditos > 0:
        papa = suma_ponderada / suma_creditos
        st.metric("P.A.P.A. Calculado", round(papa, 2))

# -----------------------------
# CARGA HORARIA TOTAL
# -----------------------------
st.subheader("Carga Horaria Total")

col1, col2 = st.columns(2)

with col1:
    st.metric("Horas Presenciales", total_presenciales)

with col2:
    st.metric("Horas Autónomas", total_autonomas)

# -----------------------------
# FÓRMULAS
# -----------------------------
st.markdown("### Fórmulas aplicadas")
st.latex(r"P.A.P.A. = \frac{\sum (Créditos_i \cdot Nota_i)}{\sum Créditos_i}")
st.latex(r"Horas\ Totales = Créditos \times 3")
st.latex(r"Horas\ Autónomas = (Créditos \times 3) - Créditos")
