import os
import sys
import json
import time
import requests
import django
import paho.mqtt.client as mqtt
from django.utils import timezone

# ============================================================
# 🔧 Inicialización del entorno Django
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TwoMove.settings")

django.setup()

from apps.stations.models import Station
from apps.bikes.models import Bike
from apps.rentals.models import Rental


# ============================================================
# 🚴 Función para obtener una ruta real (OSRM)
# ============================================================

def get_route_points(lat1, lon1, lat2, lon2):
    """
    Obtiene una ruta real entre dos coordenadas usando el motor
    de rutas de OpenStreetMap (OSRM).
    """
    url = (
        f"https://router.project-osrm.org/route/v1/bike/"
        f"{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    )

    try:
        response = requests.get(url)
        data = response.json()

        if "routes" in data and len(data["routes"]) > 0:
            coords = data["routes"][0]["geometry"]["coordinates"]
            # OSRM devuelve [lon, lat] — los convertimos a [lat, lon]
            print(f"🗺️ Ruta OSRM obtenida con {len(coords)} puntos.")
            return [(lat, lon) for lon, lat in coords]

        print("⚠️ No se obtuvo ruta OSRM, usando línea recta.")
        return [(lat1, lon1), (lat2, lon2)]

    except Exception as e:
        print(f"❌ Error obteniendo ruta OSRM: {e}")
        return [(lat1, lon1), (lat2, lon2)]


# ============================================================
# 🚲 Simulador de recorrido
# ============================================================

def simulate_bike_route(rental_id):
    """
    Simula la telemetría de una bicicleta siguiendo una ruta
    real entre estación de origen y destino.
    """
    try:
        rental = Rental.objects.get(id=rental_id)
    except Rental.DoesNotExist:
        print(f"❌ No existe la reserva con ID {rental_id}")
        return

    bike = rental.bike
    start_station = rental.estacion_origen
    end_station = rental.estacion_destino

    if not start_station or not end_station:
        print("⚠️ La reserva no tiene estaciones definidas.")
        return

    print(f"🚴 Iniciando simulación para bicicleta {bike.id}")
    print(f"📍 De {start_station.nombre} → {end_station.nombre}")

    # Conexión MQTT
    client = mqtt.Client()
    client.connect("localhost", 1883, 60)
    print("✅ Conectado al broker MQTT (localhost:1883)")

    # Obtener ruta real
    route_points = get_route_points(
        float(start_station.latitud),
        float(start_station.longitud),
        float(end_station.latitud),
        float(end_station.longitud),
    )

    # Simulación punto a punto
    for i, (lat, lon) in enumerate(route_points):
        payload = {
            "bike_id": bike.id,
            "rental_id": rental.id,
            "lat": lat,
            "lon": lon,
            "bateria": max(10.0, 100 - i * 0.2),  # 🔋 se descarga poco a poco
            "velocidad": 15 + (i % 5),  # 🚲 velocidad variable
            "timestamp": timezone.now().isoformat(),
        }

        client.publish("bikes/telemetry", json.dumps(payload))
        print(f"📡 [{i+1}/{len(route_points)}] → {lat:.5f}, {lon:.5f}")
        time.sleep(1)  # segundos entre puntos

    client.disconnect()
    print(f"✅ Simulación finalizada para bicicleta {bike.id}")


# ============================================================
# 🚀 Ejecución directa desde terminal
# ============================================================

if __name__ == "__main__":
    print("=== SIMULADOR DE RUTA IOT ===")
    rental_id = input("Ingrese el ID del alquiler a simular: ").strip()

    if rental_id.isdigit():
        simulate_bike_route(int(rental_id))
    else:
        print("❌ Debe ingresar un ID numérico válido.")
