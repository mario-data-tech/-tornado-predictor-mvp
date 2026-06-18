
import streamlit as st
import requests

# Set page layout
st.set_page_config(page_title="Tornado Tracker", layout="wide")

st.title("🌪️ Tornado Predictor MVP")

def get_tornado_data():
    # URL oficial del National Weather Service de EE.UU.
    url = "https://api.weather.gov/alerts/active?area=US"
    headers = {'User-Agent': 'TornadoPredictorApp (my-email@example.com)'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('features', [])
        else:
            return None
    except Exception as e:
        return None

# App logic
if st.button("Buscar Alertas de Tornado"):
    alerts = get_tornado_data()
    
    if alerts:
        st.success(f"Se han encontrado {len(alerts)} alertas activas.")
        for alert in alerts[:5]:  # Muestra las primeras 5
            properties = alert.get('properties', {})
            st.write(f"**Ubicación:** {properties.get('areaDesc')}")
            st.write(f"**Evento:** {properties.get('event')}")
            st.write("---")
    else:
        st.error("No se pudieron obtener los datos o no hay alertas.")
