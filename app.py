import json
import platform

import paho.mqtt.client as paho
import streamlit as st

st.write("Versión de Python:", platform.python_version())

# ---------- Configuración (igual que en el ESP32 de Wokwi) ----------
BROKER = "broker.mqttdashboard.com"
PORT = 1883
# Debe ser distinto al ID del ESP32 ("Lizalda"); si fueran iguales,
# el broker desconectaría a uno de los dos cada vez que el otro entre.
CLIENT_ID = "Lizalda_App"

TOPIC_ACT = "lizalda/cmqtt_s"      # ON / OFF  -> LED
TOPIC_ANALOG = "lizalda/cmqtt_a"   # 0 - 100   -> servo


def crear_cliente():
    """Compatible con paho-mqtt 1.x y 2.x."""
    try:
        return paho.Client(paho.CallbackAPIVersion.VERSION1, CLIENT_ID)
    except AttributeError:
        return paho.Client(CLIENT_ID)


def publicar(topic, payload):
    """Conecta, publica, espera confirmación y se desconecta."""
    try:
        client = crear_cliente()
        client.connect(BROKER, PORT, keepalive=30)
        client.loop_start()
        info = client.publish(topic, json.dumps(payload))
        info.wait_for_publish(timeout=5)
        client.loop_stop()
        client.disconnect()
        st.success(f"Publicado en {topic}: {json.dumps(payload)}")
    except Exception as e:
        st.error(f"No se pudo publicar: {e}")


st.title("MQTT Control")

col1, col2 = st.columns(2)
with col1:
    if st.button("ON"):
        publicar(TOPIC_ACT, {"Act1": "ON"})
with col2:
    if st.button("OFF"):
        publicar(TOPIC_ACT, {"Act1": "OFF"})

values = st.slider("Selecciona el rango de valores", 0.0, 100.0)
st.write("Values:", values)

if st.button("Enviar valor analógico"):
    publicar(TOPIC_ANALOG, {"Analog": float(values)})
