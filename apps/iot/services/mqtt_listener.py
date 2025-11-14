import os
import sys
import django
import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime

# ============================================================
#  Inicialización del entorno Django
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_DIR = os.path.dirname(BASE_DIR)
print(f"📂 Base dir detectado: {PROJECT_DIR}")

sys.path.append(PROJECT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TwoMove.settings")

print("⚙️  Inicializando entorno Django...")
django.setup()

from apps.iot.models import BikeTelemetry


# ============================================================
# 🔄 Callback: recepción de mensajes MQTT
# ============================================================
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print("📥 Telemetría recibida:", payload)

        # Extraer datos del mensaje MQTT
        bike_id = payload.get("bike_id")
        lat = payload.get("lat")
        lon = payload.get("lon")
        bateria = payload.get("bateria") or payload.get("battery")
        velocidad = payload.get("velocidad") or payload.get("speed")
        timestamp = payload.get("timestamp")

        # Validaciones básicas
        if lat is None or lon is None:
            print("⚠️ Coordenadas inválidas, mensaje ignorado.")
            return

        if bike_id is None:
            print("⚠️ ID de bicicleta no especificado.")
            return

        # Determinar estado del candado (simplemente para ejemplo)
        lock_status = "UNLOCKED" if velocidad and velocidad > 0 else "LOCKED"

        # Crear registro en la base de datos
        telemetria = BikeTelemetry.objects.create(
            bike_id=bike_id,
            latitude=lat,
            longitude=lon,
            battery=bateria or 100.0,  # ✅ usa 'battery' real del modelo
            lock_status=lock_status,
            timestamp=timestamp or datetime.now(),
        )

        print(f"💾 Telemetría guardada correctamente → Bike {bike_id} ({lat}, {lon}) [{lock_status}]")

    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")


# ============================================================
# ⚙️ Configuración del cliente MQTT
# ============================================================
def main():
    client = mqtt.Client()

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✅ Conectado a MQTT (localhost:1883) — Suscrito a 'bikes/telemetry'")
            client.subscribe("bikes/telemetry")
        else:
            print(f"❌ Error de conexión MQTT: código {rc}")

    client.on_connect = on_connect
    client.on_message = on_message

    # Conexión al broker local Mosquitto
    client.connect("localhost", 1883, 60)
    print("🎧 Esperando mensajes MQTT...\n")

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n🛑 Listener detenido manualmente.")


# ============================================================
# 🚀 Ejecución principal
# ============================================================
if __name__ == "__main__":
    main()
