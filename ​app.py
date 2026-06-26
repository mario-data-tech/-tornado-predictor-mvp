# app.py
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(
    page_title="Decision Intelligence Layer | Climate Risk",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛡️ Mario Data Tech | Decision Intelligence Layer")
st.caption("Climate Risk Exposure Engine & Policy-Driven Execution Framework.")
st.divider()

# --- 1. CAPA DE PERSISTENCIA DE DATOS (DATA LAYER) ---
if "fleet" not in st.session_state:
    st.session_state.fleet = pd.DataFrame([
        {
            "Truck": "Truck-01 (Kansas)",
            "Latitude": 38.9637,
            "Longitude": -95.2600,
            "P": 0.90,
            "E": 150000.0,
            "Base_Rerouting_Cost_USD": 8000.0,
            "SLA_Penalty_USD": 4000.0,
        },
        {
            "Truck": "Truck-02 (Texas)",
            "Latitude": 31.9686,
            "Longitude": -99.9018,
            "P": 0.10,
            "E": 35000.0,
            "Base_Rerouting_Cost_USD": 3000.0,
            "SLA_Penalty_USD": 1000.0,
        },
        {
            "Truck": "Truck-03 (Illinois)",
            "Latitude": 40.6331,
            "Longitude": -89.3985,
            "P": 0.05,
            "E": 12000.0,
            "Base_Rerouting_Cost_USD": 1500.0,
            "SLA_Penalty_USD": 500.0,
        },
    ])

if "weather" not in st.session_state:
    st.session_state.weather = {"S": 0.80}

# --- 2. CAPA DEL MOTOR DE OPTIMIZACIÓN (POLICY ENGINE) ---
def ejecutar_policy_engine(df: pd.DataFrame, s_factor: float) -> pd.DataFrame:
    out = df.copy()
    out["S"] = float(s_factor)
    
    # Escenario Contrafáctico A: Línea de Base (No hacer nada)
    out["Baseline_Expected_Loss_USD"] = out["P"] * out["E"] * out["S"]
    
    # Costo de Mitigación Compuesto (Restricciones operativas)
    out["Mitigation_Cost_USD"] = out["Base_Rerouting_Cost_USD"] + out["SLA_Penalty_USD"]
    
    # REGLA DE POLÍTICA COMPUESTA (Policy Rule ID: CLIM_RISK_v1)
    out["Decision"] = np.where(out["Baseline_Expected_Loss_USD"] > out["Mitigation_Cost_USD"], "REROUTE", "HOLD_ROUTE")
    
    # Escenario Contrafáctico B: Mitigación Activa
    out["Post_Mitigation_Loss_USD"] = np.where(out["Decision"] == "REROUTE", 0.0, out["Baseline_Expected_Loss_USD"])
    out["Costo_Operativo_Asumido"] = np.where(out["Decision"] == "REROUTE", out["Mitigation_Cost_USD"], 0.0)
    
    # Impacto Neto Realizado (Ahorro Auditables para el CFO)
    out["Net_Financial_Savings_USD"] = np.where(
        out["Decision"] == "REROUTE",
        out["Baseline_Expected_Loss_USD"] - out["Mitigation_Cost_USD"],
        0.0
    )
    return out

# =====================================================================
# INTERFAZ DE USUARIO EN 3 CAPAS (UI LAYER)
# =====================================================================

# --- CAPA 1: MODEL INPUTS (Sidebar) ---
with st.sidebar:
    st.header("🎛️ Capa 1: Model Inputs")
    st.markdown("Variables exógenas y parámetros financieros del modelo.")
    
    s_value = st.slider("Severidad Climática (S)", 0.0, 1.0, float(st.session_state.weather["S"]), 0.01)
    st.session_state.weather["S"] = s_value

    st.subheader("📝 Parámetros Operativos de Flota")
    editable = st.data_editor(
        st.session_state.fleet[["Truck", "P", "E", "Base_Rerouting_Cost_USD", "SLA_Penalty_USD", "Latitude", "Longitude"]],
        width='stretch',
        num_rows="fixed",
        hide_index=True,
        disabled=["Truck"]
    )
st.session_state.fleet.update(editable)

# Ejecución del motor central
engine_df = ejecutar_policy_engine(st.session_state.fleet, st.session_state.weather["S"])

# --- CAPA 2: ENGINE OUTPUTS (Trazabilidad y Modelado Contrafáctico) ---
st.header("🧠 Capa 2: Engine Outputs & Counterfactual Simulation")
st.markdown("Simulación auditable de escenarios para control financiero y de seguros (Mitigación vs. Status Quo).")

# Armamos la tabla contrafáctica que exigió el feedback
st.dataframe(
    engine_df[[
        "Truck",
        "Baseline_Expected_Loss_USD",
        "Mitigation_Cost_USD",
        "Decision",
        "Post_Mitigation_Loss_USD",
        "Net_Financial_Savings_USD"
    ]].style.format({
        "Baseline_Expected_Loss_USD": "${:,.2f}",
        "Mitigation_Cost_USD": "${:,.2f}",
        "Post_Mitigation_Loss_USD": "${:,.2f}",
        "Net_Financial_Savings_USD": "${:,.2f}"
    }),
    width='stretch',
    hide_index=True
)

# Métricas consolidadas de impacto financiero
total_rerouted = int((engine_df["Decision"] == "REROUTE").sum())
total_operational_cost = float(engine_df["Costo_Operativo_Asumido"].sum())
net_savings = float(engine_df["Net_Financial_Savings_USD"].sum())
roi = (net_savings / total_operational_cost * 100.0) if total_operational_cost > 0 else 0.0

# --- CAPA 3: DECISION & EXECUTION LAYER (Objetos de Decisión Autónomos) ---
st.header("📡 Capa 3: Policy-Driven Decision & Audit Logs")
st.markdown("Monitoreo geoespacial, órdenes de despacho y objetos de decisión ledger-ready.")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Camiones Desviados (Reroute)", total_rerouted)
with c2:
    st.metric("Costo Operativo Asumido", f"${total_operational_cost:,.2f}")
with c3:
    st.metric("ROI / Impacto Financiero Neto", f"${net_savings:,.2f}", f"{roi:.2f}% Evitado")

# Mapa Logístico
map_center = [36.0000, -94.0000]
m = folium.Map(location=map_center, zoom_start=5, tiles="CartoDB dark_matter")

for _, row in engine_df.iterrows():
    color = "#FF4B4B" if row["Decision"] == "REROUTE" else "#00D48A"
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=9, color=color, fill=True, fill_color=color, fill_opacity=0.8,
        popup=f"<b>{row['Truck']}</b><br>Decisión: {row['Decision']}"
    ).add_to(m)

st_folium(m, width="100%", height=400, returned_objects=[])

# Sección de Auditoría Avanzada con los Objetos de Decisión JSON
st.subheader("🕵️‍♂️ Ledger Audit Trail: Objetos de Decisión Generados")
st.markdown("Estructura de datos exportable e inmutable para auditoría de cumplimiento corporativo:")

for _, row in engine_df.iterrows():
    # Construcción exacta del Objeto de Decisión intermedio solicitado
    decision_object = {
        "truck_id": row["Truck"],
        "decision": row["Decision"],
        "confidence_threshold_met": True if row["Decision"] == "REROUTE" else False,
        "cost_reroute_total": float(row["Mitigation_Cost_USD"]),
        "expected_loss_if_no_action": float(row["Baseline_Expected_Loss_USD"]),
        "policy_rule_id": "RULE_CLIM_RISK_EL_GT_MITIGATION_v2",
        "explanation_payload": [
            f"Severidad climática S calculada en {row['S']:.2f}.",
            f"Probabilidad de evento P={row['P']:.2f} con exposición comercial E=${row['E']:,.2f}.",
            "Optimización: El riesgo financiero excede los costos operativos combinados de desvío y penalizaciones de SLA." if row["Decision"] == "REROUTE" else "Optimización: Mantener ruta es el escenario óptimo. El costo de desvío supera el riesgo financiero estimado."
        ]
    }
    
    # Mostramos los JSON en colapsables elegantes por camión
    estado_emoji = "🔴" if row["Decision"] == "REROUTE" else "🟢"
    with st.expander(f"{estado_emoji} Audit Log: {row['Truck']} — State: {row['Decision']}"):
        st.json(decision_object)

st.divider()
st.caption("Mario Data Tech | Decision Intelligence Engine v3.0 Enterprise — Compliance Ledger Ready.")
