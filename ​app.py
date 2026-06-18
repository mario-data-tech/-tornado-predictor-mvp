import streamlit as st
import requests

st.set_page_config(page_title="Tornado MVP", layout="wide")
st.title("🌪️ Tornado Prediction MVP")

def get_tornado_data():
    url = "https://api.weather.gov/alerts/active?area=US"
        headers = {'User-Agent': 'TornadoPredictorApp'}
            try:
                    response = requests.get(url, headers=headers)
                            if response.status_code == 200:
                                        return response.json().get('features', [])
                                                return []
                                                    except:
                                                            return []

                                                            if st.button("Check Tornado Alerts"):
                                                                alerts = get_tornado_data()
                                                                    if alerts:
                                                                            st.success(f"Found {len(alerts)} alerts.")
                                                                                    for alert in alerts[:5]:
                                                                                                props = alert.get('properties', {})
                                                                                                            st.write(f"**Location:** {props.get('areaDesc')}")
                                                                                                                        st.write(f"**Event:** {props.get('event')}")
                                                                                                                                    st.write("---")
                                                                                                                                        else:
                                                                                                                                                st.error("No alerts found.")
                                                                                                                                                