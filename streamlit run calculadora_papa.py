import streamlit as st
import pandas as pd

# -----------------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------------
st.set_page_config(page_title="Calculadora Académica", layout="wide")

# -----------------------------------
# TÍTULO CENTRADO
# -----------------------------------
st.markdown(
    """
    <h1 style='text-align: center;'>Calculadora Académica</h1>
    <p style='text-align: center; font-size:18px;'>
        Cálculo de P.A.P.A. y carga horaria
    </p>
    """,
    unsafe_allow_html=True
)

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
# TABLA RESUMEN
# -----------------------------------
df = pd.DataFrame(datos)

# eliminar índice visible
df.index = [""] * len(df)

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
# ALERTAS INSTITUCIONALES
# -----------------------------------
st.subheader("Estado Académico")

if papa <= 2.6:
    st.error(
        "Debes hacer reingreso por el Consejo Superior Universitario. "
        "Revisa las fechas y orientaciones para la solicitud."
    )

elif papa >= 2.7 and papa < 3.0:
    st.warning(
        "Debes hacer reingreso por el Consejo de Facultad. "
        "Revisa las fechas y orientaciones para la solicitud."
    )

elif papa >= 3.0 and papa < 3.4:
    st.info(
        "Tu promedio está en zona de alerta. Se recomienda fortalecer las asignaturas con bajo rendimiento."
    )

else:
    st.success(
        "Tu promedio se encuentra en una zona estable."
    )

# -----------------------------------
# SUGERENCIAS ACADÉMICAS
# -----------------------------------
st.subheader("Sugerencias Académicas")

if suma_creditos > 0:
    
    if papa < 3.0:
        st.error("Actualmente estás en zona de riesgo académico.")

    elif papa < 3.4:
        st.warning("Estás en zona de alerta. Lo ideal es alcanzar 3.4 o más.")

    else:
        st.success("Tu promedio está en una zona estable.")

    sugerencias = []

    for index, row in df.iterrows():
        nota_actual = row["Nota"]

        if nota_actual < 3.5:
            for meta_nota in [3.0, 3.5, 4.0]:
                if meta_nota > nota_actual:
                    nuevo_total = suma_ponderada - (nota_actual * row["Créditos"]) + (meta_nota * row["Créditos"])
                    nuevo_papa = nuevo_total / suma_creditos

                    if nuevo_papa >= 3.0:
                        sugerencias.append(
                            f"Si subes **{row['Asignatura']}** de {nota_actual} a {meta_nota}, "
                            f"tu P.A.P.A. sería aproximadamente **{round(nuevo_papa,2)}**."
                        )
                        break

    if sugerencias:
        for s in sugerencias:
            st.markdown(f"- {s}")
    else:
        st.info("No se encontraron ajustes relevantes.")

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
# EXPLICACIÓN CENTRADA
# -----------------------------------
st.markdown(
    """
    <h2 style='text-align: center;'>¿Cómo se realizan los cálculos?</h2>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style='text-align: center; font-size:16px;'>

    <b>Cálculo del P.A.P.A.:</b><br>
    El sistema multiplica la nota obtenida en cada asignatura por la cantidad de créditos.<br>
    Luego suma todos esos resultados y los divide entre el total de créditos matriculados.<br><br>

    Esto permite que las materias con más créditos tengan mayor peso en el promedio.<br><br>

    <b>Cálculo de horas presenciales:</b><br>
    Cada crédito equivale a <b>1 hora presencial semanal</b>.<br><br>

    <b>Cálculo de horas autónomas:</b><br>
    Cada crédito equivale a <b>3 horas de trabajo total semanal</b>.<br>
    De esas 3 horas:<br>
    1 hora corresponde a trabajo presencial.<br>
    2 horas corresponden a trabajo autónomo.<br><br>

    <b>Ejemplo:</b><br>
    4 créditos = 12 horas totales<br>
    4 horas presenciales<br>
    8 horas autónomas

    </div>
    """,
    unsafe_allow_html=True
)
