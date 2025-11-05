import os
import sys
import django
import random

# === Inicializar entorno Django ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TwoMove.settings")

django.setup()

from apps.bikes.models import Bike
from apps.stations.models import Station


def seed_bikes():
    stations = list(Station.objects.all())

    if not stations:
        print("⚠️ No hay estaciones creadas. Ejecuta primero seed_stations.py.")
        return

    print(f"🚲 Creando bicicletas en {len(stations)} estaciones...")

    tipos = ["electric", "manual"]
    estados = ["available"]
    total_bikes = 0

    for station in stations:
        for tipo in tipos:
            # 📊 4 bicicletas de cada tipo por estación
            for i in range(4):
                serial = f"{tipo[0].upper()}-{station.id:03d}-{i+1:03d}"
                Bike.objects.update_or_create(
                    numero_serie=serial,
                    defaults={
                        "tipo": tipo,
                        "estado": random.choice(estados),
                        "station": station,
                        "bateria_porcentaje": random.randint(60, 100),
                    },
                )
                total_bikes += 1

    print(f"✅ Se han creado o actualizado {total_bikes} bicicletas correctamente.")
    print("📊 Distribución: 4 eléctricas + 4 mecánicas por estación.")


if __name__ == "__main__":
    seed_bikes()
