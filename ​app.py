
# risk_dashboard_mario_data_tech.py
import streamlit as st
import pandas as pd
from math import isfinite

st.set_page_config(page_title="Mario Data Tech — Risk Management Dashboard",
                   layout="wide",
                   page_icon="🚚")

# --- Sidebar corporativa ---
with st.sidebar:
    st.image("https://placehold.co/300x80?text=Mario+Data+Tech", use_column_width=True)
    st.title("Risk Management")
    st.markdown("Motor de Riesgo Mínimo (MRE) — Logística & Rerouting")
    st.markdown("Operador: Equipo de Ingeniería")
    st.divider()
    st.markdown("Parámetros:")
    S_SEVERITY = st.number_input("Severidad (S)", value=0.8, step=0.1, format="%.2f", help="Factor fijo de destrucción para tornados severos")
    EL_THRESHOLD = st.number_input("Umbral EL para Reroute (USD)", value=10000, step=1000, format="%d", help="Si EL > umbral, cambiar a 'Reroute' automáticamente")
    st.caption("Nota: el botón 'Simular Escenario de Crisis' ejecuta el motor matemático sobre la flota actual.")

# --- 1. DEFINICIÓN DE LA FLOTA (3 camiones reales) ---
# Estructura: lista de dicts (cada camión: ID, lat, lon, tipo_carga, valor_usd, estado)
# Ubicaciones estratégicas: Truck-01 cerca de Kansas (zona tornados simulada), otros en Texas e Illinois
FLOTA_INICIAL = [
    {
        "id": "🚚 Truck-01",
        "lat": 38.9637,   # Kansas (zona simulada)
        "lon": -95.2600,
        "tipo_carga": "Electrónica de alta gama",
        "valor_usd": 150000.0,
        "estado": "Normal",
    },
    {
        "id": "🚚 Truck-02",
        "lat": 31.9686,   # Texas (lugar seguro relativo)
        "lon": -99.9018,
        "tipo_carga": "Repuestos industriales",
        "valor_usd": 35000.0,
        "estado": "Normal",
    },
    {
        "id": "🚚 Truck-03",
        "lat": 40.6331,   # Illinois (lugar seguro relativo)
        "lon": -89.3985,
        "tipo_carga": "Textiles",
        "valor_usd": 12000.0,
        "estado": "Normal",
    },
]

# Convertir a DataFrame para UI/mapeo
def flota_to_df(flotas):
    df = pd.DataFrame([{
        "id": f["id"],
        "lat": f["lat"],
        "lon": f["lon"],
        "tipo_carga": f["tipo_carga"],
        "valor_usd": f["valor_usd"],
        "estado": f["estado"]
    } for f in flotas])
    return df

# --- 2. MOTOR DE RIESGO MATEMÁTICO ---
# Geofencing básico: definimos una zona de impacto (círculo) centrada en la ubicación de tornado simulado.
TORNADO_CENTER = (38.9637, -95.2600)
TORNADO_RADIUS_KM = 80.0  # radio de influencia (aprox.) para considerar Watch/Warning

from math import radians, sin, cos, sqrt, atan2

def haversine_km(lat1, lon1, lat2, lon2):
    # retorna distancia aproximada en km
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def _probabilidad_por_geofencing(distance_km):
    # Lógica: si dentro de radio, distinguimos Warning vs Watch por umbrales.
    # Dentro de 25 km -> Warning (P=0.9); entre 25 y TORANDO_RADIUS_KM -> Watch (P=0.3); fuera -> 0.0
    if distance_km <= 25.0:
        return 0.9  # Tornado Warning
    elif distance_km <= TORNADO_RADIUS_KM:
        return 0.3  # Tornado Watch
    else:
        return 0.0

def calcular_riesgo_flota(flotas, es_simulacion=True):
    """
    Calcula EL = P * E * S para cada camión y retorna:
    - flotas_resultado: lista con campos añadidos 'P', 'EL'
    - resumen: dict con métricas agregadas: total_EL, camiones_reroute_count, total_valor_en_riesgo
    Reglas:
    - P: por geofencing respecto a TORNADO_CENTER con umbrales.
    - E: valor_usd del camión.
    - S: severidad fija (S_SEVERITY).
    - Si EL > EL_THRESHOLD => cambiar estado a 'Reroute' y sugerir acción crítica.
    """
    flotas_res = []
    total_EL = 0.0
    camiones_reroute_count = 0
    total_valor_en_riesgo = 0.0

    for cam in flotas:
        dist_km = haversine_km(cam["lat"], cam["lon"], TORNADO_CENTER[0], TORNADO_CENTER[1])
        P = _probabilidad_por_geofencing(dist_km)
        E = float(cam["valor_usd"])
        S = float(S_SEVERITY)
        EL = P * E * S

        cam_result = cam.copy()
        cam_result["dist_km_center"] = dist_km
        cam_result["P"] = P
        cam_result["S"] = S
        cam_result["EL"] = EL

        # Acción automática: si EL > threshold -> Reroute
        if EL > float(EL_THRESHOLD):
            cam_result["estado"] = "Reroute"
            cam_result["accion_sugerida"] = f"Reroute inmediato: replanificar ruta y evacuar carga (EL={EL:,.2f} USD)"
            camiones_reroute_count += 1
            total_valor_en_riesgo += E
        else:
            cam_result["accion_sugerida"] = "Monitorear"
        total_EL += EL
        flotas_res.append(cam_result)

    resumen = {
        "total_EL": total_EL,
        "camiones_reroute_count": camiones_reroute_count,
        "total_valor_en_riesgo": total_valor_en_riesgo
    }
    return flotas_res, resumen

# --- 3. UI principal ---
st.title("Mario Data Tech — Risk Management Dashboard (MRE)")
st.markdown("Panel orientado a Logística y Rerouting Automático — Motor de Riesgo Mínimo")

# Mostrar flota editable (simplemente vista, para mantener control de producción).
st.subheader("Flota actual")
df_flota = flota_to_df(FLOTA_INICIAL)
st.dataframe(df_flota.astype({"valor_usd":"float"}), use_container_width=True)

# Botón que ejecuta el motor matemático (reemplaza simulación cinematográfica)
if st.button("Simular Escenario de Crisis"):
    flotas_resultado, resumen = calcular_riesgo_flota(FLOTA_INICIAL, es_simulacion=True)

    # DataFrame resultante para visualización y mapeo
    df_result = pd.DataFrame(flotas_resultado)
    # Asegurarnos columnas para mapeo lat/lon
    map_df = df_result.rename(columns={"lat":"lat", "lon":"lon"})[["lat","lon","id","estado","valor_usd","P","EL","accion_sugerida"]]

    # Métricas dinámicas (reemplazan números fijos)
    col1, col2, col3 = st.columns(3)
    col1.metric("Camiones en Reroute", value=f"{int(resumen['camiones_reroute_count'])}")
    col2.metric("Dinero en riesgo (valor expuesto) USD", value=f"${resumen['total_valor_en_riesgo']:,.2f}")
    col3.metric("Pérdida Esperada (EL) total USD", value=f"${resumen['total_EL']:,.2f}")

    # Mostrar tabla con detalles por camión
    st.subheader("Resultados por camión")
    # Selecciono columnas de interés
    cols_orden = ["id","estado","valor_usd","P","S","EL","dist_km_center","accion_sugerida"]
    st.dataframe(df_result[cols_orden].sort_values(by="EL", ascending=False).reset_index(drop=True), use_container_width=True)

    # Mostrar mapa dinámico
    st.subheader("Mapa de la flota")
    # Streamlit espera columnas lat/lon con nombres 'lat' y 'lon'
    map_plot_df = map_df[["lat","lon"]].copy()
    st.map(map_plot_df)

    # Mensajes accionables
    st.subheader("Acciones sugeridas")
    for cam in flotas_resultado:
        if cam["accion_sugerida"] and cam["accion_sugerida"] != "Monitorear":
            st.error(f"{cam['id']}: {cam['accion_sugerida']} (EL={cam['EL']:,.2f} USD, P={cam['P']})")
        else:
            st.info(f"{cam['id']}: {cam['accion_sugerida']} (EL={cam['EL']:,.2f} USD, P={cam['P']})")

else:
    st.info("Presioná 'Simular Escenario de Crisis' para ejecutar el Motor de Riesgo Matemático (MRE).")

# --- Footer con versión y nota técnica ---
st.markdown("---")
st.caption("MRE v1.0 — Engine: EL = P * E * S; Geofencing básico (haversine). Implementado en Python / Streamlit.")
