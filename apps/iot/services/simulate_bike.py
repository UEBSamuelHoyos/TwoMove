import time
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime

BROKER = "localhost"           # Broker local (Mosquitto)
PORT = 1883                    # Puerto por defecto
TOPIC = "bikes/1/telemetry"    # Canal MQTT donde se publican los datos
BIKE_ID = 1                    # ID simulado de la bicicleta

# Coordenadas simuladas (ejemplo: ruta en Bogotá)
RUTA = [
    (4.648283, -74.247894),
    (4.649120, -74.246802),
    (4.650342, -74.245129),
    (4.651012, -74.244001),
    (4.652340, -74.243010),
    (4.653550, -74.241845),
]

# ============================================================
# 🔋 ESTADO INICIAL
# ============================================================
bateria = 100
lock_status = "LOCKED"  # LOCKED | UNLOCKED


def conectar_cliente():
    """
    Conecta el cliente MQTT al broker local.
    """
    cliente = mqtt.Client()
    cliente.connect(BROKER, PORT, 60)
    print(f"✅ Conectado al broker MQTT ({BROKER}:{PORT})")
    return cliente


def publicar_estado(cliente, lat, lon, lock_status, bateria):
    """
    Publica el estado actual de la bicicleta (telemetría) en formato JSON.
    """
    mensaje = {
        "bikeId": BIKE_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "latitude": lat,
        "longitude": lon,
        "battery": bateria,
        "lockStatus": lock_status,
    }

    cliente.publish(TOPIC, json.dumps(mensaje))
    print(f"📡 Publicado en {TOPIC}: {mensaje}")


def simular_viaje():
    """
    Simula un recorrido completo de la bicicleta:
      1️⃣ Candado cerrado
      2️⃣ Inicio del viaje
      3️⃣ Movimiento progresivo
      4️⃣ Fin del viaje
    """
    global bateria, lock_status

    cliente = conectar_cliente()

    # 1️⃣ Estado inicial (candado cerrado)
    publicar_estado(cliente, *RUTA[0], lock_status, bateria)
    time.sleep(2)

    # 2️⃣ Inicio del viaje (desbloqueo)
    lock_status = "UNLOCKED"
    publicar_estado(cliente, *RUTA[0], lock_status, bateria)
    time.sleep(2)

    # 3️⃣ Movimiento: cada punto representa ~5 segundos de viaje
    for lat, lon in RUTA:
        bateria -= random.uniform(0.5, 1.2)
        publicar_estado(cliente, lat, lon, lock_status, round(bateria, 1))
        time.sleep(5)

    # 4️⃣ Fin del viaje (bloqueo nuevamente)
    lock_status = "LOCKED"
    publicar_estado(cliente, *RUTA[-1], lock_status, bateria)

    print("✅ Viaje completado correctamente.")


if __name__ == "__main__":
    simular_viaje()
