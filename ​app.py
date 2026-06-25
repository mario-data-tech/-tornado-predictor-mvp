import streamlit as st
import requests
import pandas as pd  # Importamos pandas para manejar las coordenadas del mapa

st.set_page_config(page_title="Mario Data Tech | Risk Management Dashboard", layout="wide")

# ==========================================
# PANEL LATERAL (SIDEBAR): PROPUESTA DE VALOR
# ==========================================
st.sidebar.title("🚀 Mario Data Tech")
st.sidebar.markdown("""
**Mitigación de Riesgo Climático B2B**
Transformamos datos meteorológicos duros en decisiones financieras y operativas. 

*No competimos con el pronóstico masivo: protegemos tus activos, tus choferes y tu capital.*
""")

st.sidebar.write("---")

# Sección interactiva para atraer clientes (El simulador)
st.sidebar.subheader("🛠️ Simulador de Impacto Comercial")
st.sidebar.write("Probá cómo nuestra plataforma calcula el riesgo y las pérdidas operativas en tiempo real si ocurriera un tornado ahora.")
simular_crisis = st.sidebar.button("Simular Escenario de Crisis (Demo)")


# ==========================================
# CONTENIDO PRINCIPAL
# ==========================================
st.title("🌪️ Mario Data Tech | Risk Management Dashboard")
st.markdown("**Monitoreo de amenazas extremas en tiempo real para optimización logística y de seguros**")

# --- LÓGICA DEL SIMULADOR ACTIVADO ---
if simular_crisis:
    st.write("---")
    st.subheader("🚨 SIMULACIÓN: Protocolo Activo de Mitigación de Pérdidas")
    
    # Métricas de impacto inmediato
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🚚 Flotas/Camiones en Ruta de Colisión", value="4 Unidades", delta="Acción: Desvío Crítico")
    with col2:
        st.metric(label="💰 Capital Expuesto (Mercadería/Bienes)", value="$280,000 USD", delta="-85% Pérdida Estimada")
    with col3:
        st.metric(label="🛡️ Pólizas de Seguro en Zona de Siniestro", value="14 Clientes", delta="Alertas Preventivas Enviadas")

    # Mapa Interactivo de las Unidades en Riesgo (Eje Kansas / Ruta I-35)
    st.write("### 🗺️ Mapa de Operaciones en Riesgo Imminente")
    
    # Coordenadas simuladas de los 4 camiones en el corredor de tornados de Kansas
    coordenadas_camiones = pd.DataFrame({
        'lat': [38.9637, 38.6105, 37.6872, 39.0997],
        'lon': [-95.2600, -95.1433, -97.3301, -94.5786]
    })
    
    # Renderiza el mapa en la app
    st.map(coordenadas_camiones, zoom=6)
    st.caption("📍 Puntos rojos: Ubicación en tiempo real de las unidades logísticas dentro del cono de evacuación (Kansas, USA).")

    # Alerta visual detallada
    st.error("""
    💥 **[ALERTA SIMULADA] Tornado Warning Detectado en Eje Logístico Clave (Kansas - Ruta I-35)**
    
    * **Impacto Logístico:** El tornado cruzará la autopista principal en los próximos 35 minutos. Se ha enviado una orden automática de desvío hacia la Ruta Alternativa Este a las 4 unidades visualizadas en el mapa.
    * **Impacto Aseguradoras:** 14 pólizas comerciales (depósitos e industrias) se encuentran en el radio de impacto de granizo severo. Notificaciones push enviadas para resguardo inmediato de inventario.
    """)
    st.write("---")


# --- LÓGICA DE DATOS REALES DE LA NOAA ---
st.subheader("📡 Monitoreo de Datos Reales (Live API)")

# Eventos relevantes para el negocio (logística / seguros)
EVENTOS_RELEVANTES = ["Tornado Warning", "Tornado Watch", "Severe Thunderstorm Warning"]

def get_tornado_data():
    url = "https://api.weather.gov/alerts/active?area=US"
    headers = {"User-Agent": "TornadoPredictorApp"}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            features = response.json().get("features", [])
            # Filtro exacto
            filtradas = [
                f for f in features
                if f.get("properties", {}).get("event") in EVENTOS_RELEVANTES
            ]
            return filtradas

        return []

    except Exception:
        return []


if st.button("Buscar Alertas de Tornados en Tiempo Real"):
    alerts = get_tornado_data()

    if alerts:
        st.success(f"Se encontraron {len(alerts)} alertas críticas activas en este momento.")

        for alert in alerts[:5]:
            props = alert.get("properties", {})
            zona = props.get("areaDesc", "Zona no especificada")
            evento = props.get("event", "Evento desconocido")

            if "Warning" in evento:
                st.error(f"🚨 **{evento}**\n\n📍 Zona afectada: {zona}")
            else:
                st.warning(f"⚠️ **{evento}**\n\n📍 Zona afectada: {zona}")

    else:
        st.info("No se encontraron alertas meteorológicas extremas activas en este instante. El tráfico logístico opera bajo condiciones normales.")
