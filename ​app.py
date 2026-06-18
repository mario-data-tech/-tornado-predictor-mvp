import requests
import json

def rastrear_tornados_usa():
    print("==================================================")
    print(" INICIANDO MOTOR DE PREDICCIÓN TORNADO-PREDICTOR ")
    print(" Conectando con Radares e Inteligencia de EE.UU...")
    print("==================================================")
    
    # Conexión directa a la API oficial del Servicio Meteorológico de EE.UU.
    url = "https://api.weather.gov/alerts/active?event=Tornado%20Warning"
    headers = {'User-Agent': '(tornado-predictor-mvp, mario-data-tech)'}
    
    try:
        respuesta = requests.get(url, headers=headers)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            alertas = datos.get('features', [])
            
            print(f"\n[SISTEMA OK] Conexión exitosa con el servidor meteorológico.")
            print(f"[ALERTA] Tornados activos detectados en este momento: {len(alertas)}")
            
            # Aquí procesamos los datos crudos para tu modelo de negocio B2B
            for alerta in alertas[:3]: # Muestra las primeras 3 alertas como prueba
                propiedades = alerta.get('properties', {})
                area = propiedades.get('areaDesc', 'Área no especificada')
                detalles = propiedades.get('headline', 'Sin detalles')
                print(f"\n📍 Ubicación: {area}\n⚠️ Detalle: {detalles}")
                
            return alertas
        else:
            print(f"\n[ERROR] Error de respuesta del radar comercial: Código {respuesta.status_code}")
            return []
    except Exception as e:
        print(f"\n[ERROR] Falla crítica de conexión: {e}")
        return []

if __name__ == "__main__":
    rastrear_tornados_usa()
