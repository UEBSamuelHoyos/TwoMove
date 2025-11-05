import threading
import json
import time
import requests
import paho.mqtt.client as mqtt
from django.utils import timezone
from apps.stations.models import Station
from apps.rentals.models import Rental


def get_route_points(lat1, lon1, lat2, lon2):
    """
    Obtiene una ruta real entre dos coordenadas usando OSRM.
    """
    url = f"https://router.project-osrm.org/route/v1/bike/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    try:
        response = requests.get(url)
        data = response.json()
        if "routes" in data and len(data["routes"]) > 0:
            coords = data["routes"][0]["geometry"]["coordinates"]
            return [(lat, lon) for lon, lat in coords]
    except Exception as e:
        print(f"⚠️ Error obteniendo ruta OSRM: {e}")

    # Fallback: línea recta
    return [(lat1, lon1), (lat2, lon2)]


def simulate_route_async(rental_id):
    """
    Lanza un hilo para simular la ruta sin bloquear Django.
    """
    thread = threading.Thread(target=simulate_bike_route, args=(rental_id,))
    thread.daemon = True
    thread.start()
    print(f"🚴 Simulación IoT lanzada en background para alquiler #{rental_id}")


def simulate_bike_route(rental_id):
    """
    Envía telemetría simulada MQTT para un viaje real.
    """
    try:
        rental = Rental.objects.get(id=rental_id)
    except Rental.DoesNotExist:
        print(f"❌ No se encontró la reserva #{rental_id}")
        return

    bike = rental.bike
    estacion_origen = rental.estacion_origen
    estacion_destino = rental.estacion_destino

    if not estacion_origen or not estacion_destino:
        print(f"⚠️ Reserva #{rental_id} sin estaciones válidas.")
        return

    print(f"🚴 Iniciando simulación → Bike {bike.id} ({estacion_origen.nombre} → {estacion_destino.nombre})")

    # Conectar al broker MQTT
    client = mqtt.Client()
    client.connect("localhost", 1883, 60)

    # Obtener ruta
    route_points = get_route_points(
        float(estacion_origen.latitud), float(estacion_origen.longitud),
        float(estacion_destino.latitud), float(estacion_destino.longitud),
    )

    for i, (lat, lon) in enumerate(route_points):
        payload = {
            "bike_id": bike.id,
            "rental_id": rental.id,
            "lat": lat,
            "lon": lon,
            "bateria": max(10.0, 100 - i * 0.2),
            "velocidad": 15 + (i % 4),
            "timestamp": timezone.now().isoformat(),
        }
        client.publish("bikes/telemetry", json.dumps(payload))
        time.sleep(1)

    client.disconnect()
    print(f"✅ Simulación completada → Bike {bike.id}")
