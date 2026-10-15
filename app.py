import json
import platform

import paho.mqtt.client as paho
import streamlit as st

st.set_page_config(page_title="MQTT Control", page_icon="🟢", layout="centered")

# ------------------------------------------------------------------
# Estilos: minimalista, fondo verde muy oscuro y un solo acento
# ------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&display=swap');

:root {
    --bg: #07130F;
    --panel: #0D1F18;
    --accent: #34D399;
    --text: #E8F5EE;
    --muted: #8DB5A2;
    --line: rgba(52, 211, 153, 0.22);
}

.stApp { background: var(--bg); color: var(--text); font-family: 'Space Grotesk', sans-serif; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 3rem; max-width: 640px; }

h1, h2, h3, p, label, li, span { font-family: 'Space Grotesk', sans-serif; }
h1 { font-weight: 600 !important; letter-spacing: -0.02em; color: var(--text); }
h1::after {
    content: ""; display: block; width: 44px; height: 3px;
    background: var(--accent); margin-top: 10px; border-radius: 2px;
}
h3 { font-weight: 500 !important; color: var(--accent) !important; font-size: 1.05rem !important; }

.sub { color: var(--muted); font-size: 0.9rem; margin: -0.4rem 0 1.6rem; }

/* Tarjetas */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--panel);
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
}

/* Instrucciones */
[data-testid="stExpander"] {
    background: transparent;
    border: 1px solid var(--line);
    border-radius: 12px;
}
[data-testid="stExpander"] summary { color: var(--text); }

/* Botones: contorno verde, se rellenan al pasar el mouse */
.stButton button {
    width: 100%;
    background: transparent;
    color: var(--accent);
    border: 1px solid var(--accent);
    border-radius: 8px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 500;
    transition: background .15s ease, color .15s ease;
}
.stButton button:hover, .stButton button:focus-visible {
    background: var(--accent);
    color: var(--bg);
    border-color: var(--accent);
}

/* Alertas */
[data-testid="stAlert"] {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 10px;
    color: var(--text);
}

@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------
# Configuración MQTT (igual que en el ESP32 de Wokwi)
# ------------------------------------------------------------------
BROKER = "broker.mqttdashboard.com"
PORT = 1883
# Distinto al ID del ESP32 ("Lizalda"): si fueran iguales, el broker
# desconectaría a uno de los dos cada vez que el otro entrara.
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
        st.success(f"Enviado: {json.dumps(payload)}")
    except Exception as e:
        st.error(f"No se pudo enviar: {e}")


# ------------------------------------------------------------------
# Interfaz
# ------------------------------------------------------------------
st.title("MQTT Control")
st.markdown(
    f'<p class="sub">Panel para controlar el ESP32 de Wokwi · Python {platform.python_version()}</p>',
    unsafe_allow_html=True,
)

with st.expander("Instrucciones de uso", expanded=True):
    st.markdown(
        """
1. **Inicia la simulación en Wokwi.** Espera a que el monitor serial muestre
   *conectado* y la suscripción a los tópicos.
2. **LED:** presiona **ON** para encenderlo y **OFF** para apagarlo.
3. **Servo:** mueve el control deslizante (0 a 100) y presiona
   **Enviar valor analógico**. El valor se convierte a un ángulo de 0° a 180°.
4. Cuando aparezca el mensaje **Enviado**, el comando llegó al broker.
   Revisa el monitor serial de Wokwi para confirmar que el ESP32 lo recibió.

*Si no pasa nada, verifica que la simulación siga corriendo y que los tópicos
de Wokwi y de esta app sean los mismos.*
        """
    )

with st.container(border=True):
    st.markdown("### LED")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("ON"):
            publicar(TOPIC_ACT, {"Act1": "ON"})
    with col2:
        if st.button("OFF"):
            publicar(TOPIC_ACT, {"Act1": "OFF"})

with st.container(border=True):
    st.markdown("### Servo")
    values = st.slider("Valor", 0.0, 100.0, label_visibility="collapsed")
    st.caption(f"Valor: {values:.1f} → {values * 1.8:.0f}°")
    if st.button("Enviar valor analógico"):
        publicar(TOPIC_ANALOG, {"Analog": float(values)})
