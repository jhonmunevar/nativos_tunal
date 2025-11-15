import streamlit as st
import pandas as pd
import numpy as np

# ============================================
# CONFIGURACIÓN GENERAL DE LA APP
# ============================================

st.set_page_config(
    page_title="Dashboard Nativos",
    page_icon="logo_nativos.png",   # logo en la pestaña
    layout="wide"
)

# Encabezado sin logo (solo título)
st.markdown("## Dashboard de Ventas")

# Credenciales
USER = "nativos_tunal"
PASS = "Nativos2025*"


# ============================================
# LOGIN
# ============================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:

    # Logo solo en el login
    st.image("logo_nativos.png", width=300)
    st.title("Ingreso al Dashboard")

    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        ingresar = st.form_submit_button("Ingresar")

        if ingresar:
            if usuario == USER and clave == PASS:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.warning("❌ Credenciales incorrectas")

    st.stop()


# ============================================
# BARRA LATERAL
# ============================================

# Logo en la barra lateral (corregido: use_container_width)
st.sidebar.image("logo_nativos.png", use_container_width=True)
#st.sidebar.markdown("### 🥤 Nativos — Alimentos y Bebidas")

# Fecha de hoy para bloqueo
hoy = pd.to_datetime("today").normalize()


# ============================================
# CARGA DEL ARCHIVO
# ============================================

df = pd.read_csv("ventas_nativos.csv")
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
df = df[df["Fecha"].notna()]

# Limitar datos solo hasta hoy
df = df[df["Fecha"] <= hoy]

# Enriquecer
df["Fecha_dia"] = df["Fecha"].dt.date
df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)

# Si el archivo no trae IVA
if "Ventas sin IVA" not in df.columns or "IVA" not in df.columns:
    df["Ventas sin IVA"] = df["Total"] / 1.19
    df["IVA"] = df["Total"] - df["Ventas sin IVA"]


# ============================================
# FILTROS DE FECHA (SIN FUTURO)
# ============================================

st.sidebar.header("📅 Filtro por Fechas")

fecha_inicio = st.sidebar.date_input(
    "Desde:",
    value=hoy.replace(day=1),
    max_value=hoy
)

fecha_fin = st.sidebar.date_input(
    "Hasta:",
    value=hoy,
    max_value=hoy
)

df_filtrado = df[
    (df["Fecha_dia"] >= fecha_inicio) &
    (df["Fecha_dia"] <= fecha_fin)
]

if df_filtrado.empty:
    st.warning("⚠️ No hay datos para el rango seleccionado.")
    st.stop()


# ============================================
# KPIs
# ============================================

ventas_totales = df_filtrado["Total"].sum()
ventas_sin_iva = df_filtrado["Ventas sin IVA"].sum()
iva_total = df_filtrado["IVA"].sum()
unidades_totales = df_filtrado["Unidades"].sum()

tickets_estimados = max(1, int(unidades_totales / 2))
ticket_promedio = ventas_totales / tickets_estimados

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas Totales (c/ IVA)", f"${ventas_totales:,.0f}")
col2.metric("Ventas sin IVA", f"${ventas_sin_iva:,.0f}")
col3.metric("IVA estimado", f"${iva_total:,.0f}")
col4.metric("Ticket promedio", f"${ticket_promedio:,.0f}")

st.markdown("---")


# ============================================
# PRODUCTOS VENDIDOS
# ============================================

st.subheader("📦 Productos Vendidos")

df_productos = df_filtrado.groupby(
    ["Nombre", "Valor Unitario"], as_index=False
).agg({
    "Unidades": "sum",
    "Total": "sum"
})

st.dataframe(
    df_productos[["Nombre", "Valor Unitario", "Unidades", "Total"]]
        .sort_values("Total", ascending=False),
    use_container_width=True
)

st.bar_chart(
    df_productos.sort_values("Total", ascending=False)
               .set_index("Nombre")["Total"]
)

st.markdown("---")


# ============================================
# VENTAS POR DÍA
# ============================================

st.subheader("📈 Ventas por Día")

ventas_dia = df_filtrado.groupby("Fecha_dia")["Total"].sum().reset_index()
st.line_chart(ventas_dia.set_index("Fecha_dia")["Total"])


# ============================================
# VENTAS POR MES
# ============================================

st.subheader("📆 Ventas por Mes")

ventas_mes = df_filtrado.groupby("Mes")["Total"].sum().reset_index()
st.bar_chart(ventas_mes.set_index("Mes")["Total"])


# ============================================
# VENTAS POR HORA (SIMULADAS)
# ============================================

st.subheader("🕒 Ventas por Hora")

np.random.seed(42)
df_filtrado = df_filtrado.copy()
df_filtrado["Hora"] = np.random.randint(9, 21, size=len(df_filtrado))

ventas_hora = (
    df_filtrado.groupby("Hora")["Total"]
    .sum()
    .reset_index()
    .sort_values("Hora")
)

st.bar_chart(ventas_hora.set_index("Hora")["Total"])
