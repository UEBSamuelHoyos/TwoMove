import os
import sys
import django
import json
import time
import random
import paho.mqtt.client as mqtt
from decimal import Decimal

# ======================================================
# CONFIGURACIÓN DEL ENTORNO DJANGO
# ======================================================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TwoMove.settings")
django.setup()

from apps.bikes.models import Bike

# ======================================================
# CONFIGURACIÓN MQTT
# ======================================================
BROKER = "localhost"
PORT = 1883
TOPIC = "bikes/telemetry"

# ======================================================
# CONEXIÓN MQTT
# ======================================================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"🚴 Conectado al broker MQTT ({BROKER}:{PORT})")
    else:
        print(f"❌ Error al conectar al broker MQTT (código {rc})")


def simulate_bikes():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    print("🔍 Cargando bicicletas activas desde la base de datos...")
    bikes = list(Bike.objects.filter(estado__in=["available", "reserved", "en_uso"]))
    print(f"📦 Bicicletas activas encontradas: {len(bikes)}")

    if not bikes:
        print("⚠️ No hay bicicletas activas para simular.")
        return

    try:
        while True:
            for bike in bikes:
                try:
                    # Convierte Decimals a float para cálculos
                    lat = float(bike.latitud)
                    lon = float(bike.longitud)

                    # Movimiento aleatorio pequeño (simula desplazamiento)
                    lat += random.uniform(-0.0002, 0.0002)
                    lon += random.uniform(-0.0002, 0.0002)

                    # Batería baja lentamente
                    battery = max(0, getattr(bike, "bateria_porcentaje", 100) - random.uniform(0, 0.2))
                    bike.bateria_porcentaje = Decimal(str(round(battery, 2)))
                    bike.latitud = Decimal(str(lat))
                    bike.longitud = Decimal(str(lon))
                    bike.save(update_fields=["latitud", "longitud", "bateria_porcentaje"])

                    # Publicar telemetría MQTT
                    payload = json.dumps({
                        "bike_id": bike.id,
                        "latitude": float(bike.latitud),
                        "longitude": float(bike.longitud),
                        "battery": float(bike.bateria_porcentaje),
                        "lock_status": "unlocked" if bike.estado == "en_uso" else "locked",
                    })
                    client.publish(TOPIC, payload)
                    print(f"📡 Enviando telemetría: {payload}")

                except Exception as e:
                    print(f"⚠️ Error simulando bicicleta {bike.id}: {e}")

            time.sleep(5)  # cada 5 segundos
    except KeyboardInterrupt:
        print("\n🛑 Simulación finalizada.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    simulate_bikes()
