import os
import sys
import django

# === CONFIGURACIÓN BASE ===
# Este script puede ejecutarse desde cualquier lugar
# Forzamos el BASE_DIR al nivel donde está manage.py
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(BASE_DIR)

# Configurar el módulo de settings explícitamente
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TwoMove.settings")

print(f"⚙️ Inicializando entorno Django desde: {BASE_DIR}")

# Inicializar Django
django.setup()

from apps.stations.models import Station


def seed_stations():
    estaciones = [
        ("Estación 001", 4.7521, -74.0440),
        ("Estación 002", 4.7478, -74.0523),
        ("Estación 003", 4.7426, -74.0632),
        ("Estación 004", 4.7369, -74.0708),
        ("Estación 005", 4.7295, -74.0805),
        ("Estación 006", 4.7231, -74.0831),
        ("Estación 007", 4.7160, -74.0912),
        ("Estación 008", 4.7100, -74.1000),
        ("Estación 009", 4.7042, -74.1041),
        ("Estación 010", 4.6989, -74.1098),

        ("Estación 011", 4.6820, -74.0530),
        ("Estación 012", 4.6765, -74.0588),
        ("Estación 013", 4.6708, -74.0654),
        ("Estación 014", 4.6642, -74.0703),
        ("Estación 015", 4.6591, -74.0751),

        ("Estación 016", 4.6721, -74.0930),
        ("Estación 017", 4.6760, -74.1004),
        ("Estación 018", 4.6808, -74.1067),
        ("Estación 019", 4.6855, -74.1145),
        ("Estación 020", 4.6910, -74.1211),

        ("Estación 021", 4.6451, -74.1219),
        ("Estación 022", 4.6395, -74.1138),
        ("Estación 023", 4.6340, -74.1073),
        ("Estación 024", 4.6284, -74.0998),
        ("Estación 025", 4.6220, -74.0919),

        ("Estación 026", 4.6123, -74.0824),
        ("Estación 027", 4.6059, -74.0741),
        ("Estación 028", 4.6000, -74.0672),
        ("Estación 029", 4.5938, -74.0603),
        ("Estación 030", 4.5870, -74.0542),

        ("Estación 031", 4.6215, -74.1451),
        ("Estación 032", 4.6110, -74.1508),
        ("Estación 033", 4.6028, -74.1564),
        ("Estación 034", 4.5931, -74.1620),
        ("Estación 035", 4.5848, -74.1685),
        ("Estación 036", 4.5752, -74.1749),
        ("Estación 037", 4.5658, -74.1801),

        ("Estación 038", 4.5781, -74.1281),
        ("Estación 039", 4.5702, -74.1329),
        ("Estación 040", 4.5619, -74.1388),

        ("Estación 041", 4.5839, -74.0860),
        ("Estación 042", 4.5785, -74.0789),
        ("Estación 043", 4.5720, -74.0724),
        ("Estación 044", 4.5658, -74.0651),
        ("Estación 045", 4.5601, -74.0578),
        ("Estación 046", 4.5544, -74.0510),
        ("Estación 047", 4.5483, -74.0455),
        ("Estación 048", 4.5420, -74.0398),
        ("Estación 049", 4.5365, -74.0342),
        ("Estación 050", 4.5300, -74.0287),
    ]

    for nombre, lat, lon in estaciones:
        Station.objects.update_or_create(
            nombre=nombre,
            defaults={
                "direccion": f"{nombre}, Bogotá D.C.",
                "latitud": lat,
                "longitud": lon,
                "capacidad_electricas": 10,
                "capacidad_mecanicas": 10,
            },
        )

    print(f"✅ Se han creado o actualizado {len(estaciones)} estaciones correctamente.")


if __name__ == "__main__":
    seed_stations()
