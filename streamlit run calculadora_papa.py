import streamlit as st
import pandas as pd

# -----------------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------------
st.set_page_config(page_title="Calculadora Académica", layout="wide")

st.title("Calculadora Académica")
st.caption("Cálculo de P.A.P.A. y carga horaria")

# -----------------------------------
# CANTIDAD DE ASIGNATURAS
# -----------------------------------
num_asignaturas = st.number_input(
    "¿Cuántas asignaturas desea ingresar?",
    min_value=1,
    max_value=15,
    step=1
)

# -----------------------------------
# VARIABLES
# -----------------------------------
datos = []
total_presenciales = 0
total_autonomas = 0

# -----------------------------------
# INGRESO DE DATOS
# -----------------------------------
for i in range(int(num_asignaturas)):

    st.subheader(f"Asignatura {i+1}")

    col1, col2, col3 = st.columns([5, 1, 1])

    with col1:
        nombre = st.text_input(
            "Asignatura",
            key=f"nombre_asignatura_{i}"
        )

    with col2:
        creditos = st.number_input(
            "Créditos",
            min_value=1,
            max_value=10,
            step=1,
            key=f"creditos_asignatura_{i}"
        )

    with col3:
        nota = st.number_input(
            "Nota",
            min_value=0.0,
            max_value=5.0,
            step=0.1,
            key=f"nota_asignatura_{i}"
        )

    # -----------------------------------
    # CÁLCULO DE HORAS
    # -----------------------------------
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

# -----------------------------------
# DATAFRAME
# -----------------------------------
df = pd.DataFrame(datos)

st.subheader("Resumen Académico")
st.dataframe(df, width="stretch")

# -----------------------------------
# CÁLCULO DEL P.A.P.A.
# -----------------------------------
if len(df) > 0:
    suma_ponderada = (df["Créditos"] * df["Nota"]).sum()
    suma_creditos = df["Créditos"].sum()

    if suma_creditos > 0:
        papa = suma_ponderada / suma_creditos
        st.metric("P.A.P.A. Calculado", round(papa, 2))
    else:
        st.warning("No hay créditos válidos.")

# -----------------------------------
# CARGA HORARIA
# -----------------------------------
st.subheader("Carga Horaria Total")

colA, colB = st.columns(2)

with colA:
    st.metric("Horas Presenciales", total_presenciales)

with colB:
    st.metric("Horas Autónomas", total_autonomas)

# -----------------------------------
# FÓRMULAS
# -----------------------------------
st.subheader("Fórmulas aplicadas")

st.latex(r"P.A.P.A. = \frac{\sum (Créditos_i \cdot Nota_i)}{\sum Créditos_i}")
st.latex(r"Horas\ Presenciales = Créditos")
st.latex(r"Horas\ Autónomas = (Créditos \times 3) - Créditos")
