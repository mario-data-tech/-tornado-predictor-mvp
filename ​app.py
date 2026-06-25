# app.py
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Policy Optimizer | Fleet Rerouting Engine",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛡️ Mario Data Tech | Policy Optimizer")
st.caption("Motor corporativo de decisión para desvío de flota con trazabilidad matemática completa.")
st.divider()

# --- PERSISTENCIA DE LA FLOTA (Coordenadas reales en USA) ---
if "fleet" not in st.session_state:
    st.session_state.fleet = pd.DataFrame([
        {
            "Truck": "🚚 Truck-01 (Kansas)",
            "Latitude": 38.9637,    # Cono de impacto inminente
            "Longitude": -95.2600,
            "P": 0.90,              # Tornado Warning Activo
            "E": 150000.0,          # Electrónica de alta gama
            "Distance_km": 12.5,
            "Base_Rerouting_Cost_USD": 8000.0,
            "SLA_Penalty_USD": 4000.0,
        },
        {
            "Truck": "🚚 Truck-02 (Texas)",
            "Latitude": 31.9686,    # Zona segura
            "Longitude": -99.9018,
            "P": 0.00,
            "E": 35000.0,           # Repuestos industriales
            "Distance_km": 480.2,
            "Base_Rerouting_Cost_USD": 3000.0,
            "SLA_Penalty_USD": 1000.0,
        },
        {
            "Truck": "🚚 Truck-03 (Illinois)",
            "Latitude": 40.6331,    # Zona segura
            "Longitude": -89.3985,
            "P": 0.00,
            "E": 12000.0,           # Textiles
            "Distance_km": 350.1,
            "Base_Rerouting_Cost_USD": 1500.0,
            "SLA_Penalty_USD": 500.0,
        },
    ])

if "weather" not in st.session_state:
    st.session_state.weather = {
        "S": 0.80  # Severidad por defecto para tornado severo
    }

# --- MOTOR DE RIESGO Y OPTIMIZACIÓN FINANCIERA ---
def calcular_riesgo_flota(df: pd.DataFrame, s_factor: float) -> pd.DataFrame:
    out = df.copy()
    out["S"] = float(s_factor)
    
    # Pérdida Esperada individual (Expected Loss)
    out["EL_individual"] = out["P"] * out["E"] * out["S"]
    
    # Función de Costo de Desvío Compuesta
    out["Costo_Total_Desvio"] = out["Base_Rerouting_Cost_USD"] + out["SLA_Penalty_USD"]
    
    # REGLA DE ORO OPERATIVA: Reroute SOLO si el riesgo financiero supera el costo logístico
    out["Decision"] = np.where(out["EL_individual"] > out["Costo_Total_Desvio"], "Reroute", "Normal")
    
    # Cálculo de Retorno y Costos Asumidos
    out["Ahorro_Neto_Realizado"] = np.where(
        out["Decision"] == "Reroute",
        out["EL_individual"] - out["Costo_Total_Desvio"],
        0.0
    )
    out["Costo_Operativo_Asumido"] = np.where(
        out["Decision"] == "Reroute",
        out["Costo_Total_Desvio"],
        0.0
    )
    return out

# =====================================================================
# CAPA 1: MODEL INPUTS (Panel de Control e Ingesta de Datos)
# =====================================================================
with st.sidebar:
    st.header("🎛️ Capa 1: Model Inputs")
    st.markdown("Ajuste de parámetros meteorológicos y financieros en tiempo real.")
    
    s_value = st.slider("Severidad del Evento (S)", 0.0, 1.0, float(st.session_state.weather["S"]), 0.01)
    st.session_state.weather["S"] = s_value

    st.subheader("📝 Parámetros de Flota")
    st.caption("Editá los valores directamente en la tabla si cambian los costos o la carga:")
    
    editable = st.data_editor(
        st.session_state.fleet[[
            "Truck",
            "P",
            "E",
            "Base_Rerouting_Cost_USD",
            "SLA_Penalty_USD",
            "Latitude",
            "Longitude"
        ]],
        use_container_width=True,
        num_rows="fixed",
        hide_index=True,
        disabled=["Truck"]
    )

st.session_state.fleet.update(editable)

# Ejecución del motor con los datos actualizados
engine_df = calcular_riesgo_flota(st.session_state.fleet, st.session_state.weather["S"])

# =====================================================================
# CAPA 2: ENGINE OUTPUTS (Trazabilidad y Desglose Matemático)
# =====================================================================
st.header("🧠 Capa 2: Engine Outputs")
st.markdown("Desglose auditable del riesgo por unidad. La transparencia que exigen los gerentes de riesgo.")

st.dataframe(
    engine_df[[
        "Truck",
        "P",
        "E",
        "S",
        "EL_individual",
        "Costo_Total_Desvio",
        "Decision",
        "Ahorro_Neto_Realizado"
    ]].style.format({
        "P": "{:.2f}",
        "E": "${:,.2f}",
        "S": "{:.2f}",
        "EL_individual": "${:,.2f}",
        "Costo_Total_Desvio": "${:,.2f}",
        "Ahorro_Neto_Realizado": "${:,.2f}"
    }),
    use_container_width=True,
    hide_index=True
)

# Métricas agregadas de negocio
total_rerouted = int((engine_df["Decision"] == "Reroute").sum())
total_operational_cost = float(engine_df["Costo_Operativo_Asumido"].sum())
net_savings = float(engine_df["Ahorro_Neto_Realizado"].sum())
roi = (net_savings / total_operational_cost * 100.0) if total_operational_cost > 0 else 0.0

# =====================================================================
# CAPA 3: DECISION LAYER (Optimización y Acciones Críticas)
# =====================================================================
st.header("📡 Capa 3: Decision Layer")
st.markdown("Métricas clave de ROI y ruteo geoespacial optimizado bajo restricciones.")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Camiones Desviados", total_rerouted, help="Unidades cuya orden automática fue cambiada a Reroute.")

with col2:
    st.metric("Costo Operativo Asumido", f"${total_operational_cost:,.2f}", help="Suma de combustible adicional y penalizaciones de SLA por desvío.")

with col3:
    st.metric("ROI / Riesgo Neto Evitado", f"${net_savings:,.2f}", f"{roi:.2f}% de Retorno", help="Capital financiero neto salvado tras descontar los costos del desvío.")

# Construcción del mapa interactivo profesional (Folium)
st.subheader("🗺️ Monitoreo de Rutas y Alertas")
map_center = [36.0000, -94.0000] # Centro estratégico de la visualización en USA
m = folium.Map(location=map_center, zoom_start=5, tiles="CartoDB dark_matter")

for _, row in engine_df.iterrows():
    # Rojo para desvío mandatorio, verde para mantener ruta normal
    color = "#FF4B4B" if row["Decision"] == "Reroute" else "#00D48A"
    
    popup_text = f"""
    <div style='font-family: Arial, sans-serif; font-size: 12px; min-width: 200px;'>
        <b>{row['Truck']}</b><br>
        <hr style='margin: 4px 0;'>
        <b>Decisión:</b> <span style='color:{color}; font-weight:bold;'>{row['Decision']}</span><br>
        <b>Pérdida Esperada (EL):</b> ${row['EL_individual']:,.2f}<br>
        <b>Costo de Desvío:</b> ${row['Costo_Total_Desvio']:,.2f}<br>
        <b>Ahorro Generado:</b> ${row['Ahorro_Neto_Realizado']:,.2f}
    </div>
    """
    
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=9,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8,
        popup=folium.Popup(popup_text, max_width=300)
    ).add_to(m)

st_folium(m, width="100%", height=450, returned_objects=[])

# Alertas Críticas Dinámicas
st.subheader("🚨 Órdenes de Despacho Automatizadas")
for _, row in engine_df.iterrows():
    if row["Decision"] == "Reroute":
        st.error(f"**{row['Truck']}**: Ejecutar desvío inmediato hacia la ruta alternativa este. Riesgo climático crítico superó los costos logísticos por **${row['Ahorro_Neto_Realizado']:,.2f} USD**.")
    else:
        st.success(f"**{row['Truck']}**: Mantener ruta original activa. El riesgo financiero actual (${row['EL_individual']:,.2f} USD) no justifica asumir costos extras de desvío.")

st.markdown("---")
st.caption("Mario Data Tech Enterprise Engine v2.0 — Policy Optimizer Module. Lógica matemática de optimización bajo restricciones logísticas.")

