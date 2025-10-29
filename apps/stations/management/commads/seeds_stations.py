from django.core.management.base import BaseCommand
from apps.stations.models import Station

class Command(BaseCommand):
    help = "Crea estaciones base (3 para MVP) o completa hasta 170 en modo expansión"

    def add_arguments(self, parser):
        parser.add_argument('--full', action='store_true', help='Crea las 170 estaciones (modo completo)')

    def handle(self, *args, **options):
        estaciones_mvp = [
            {
                "nombre": "Estación A - Parque Central",
                "direccion": "Calle 10 #5-20, Bogotá",
                "latitud": 4.611,
                "longitud": -74.081,
                "capacidad_electricas": 10,
                "capacidad_mecanicas": 10,
            },
            {
                "nombre": "Estación B - Plaza Norte",
                "direccion": "Av. 19 #145-30, Bogotá",
                "latitud": 4.748,
                "longitud": -74.052,
                "capacidad_electricas": 10,
                "capacidad_mecanicas": 10,
            },
            {
                "nombre": "Estación C - Universidad Nacional",
                "direccion": "Cra 30 #45-03, Bogotá",
                "latitud": 4.637,
                "longitud": -74.083,
                "capacidad_electricas": 10,
                "capacidad_mecanicas": 10,
            },
        ]

        estaciones = estaciones_mvp

        if options["full"]:
            self.stdout.write(self.style.WARNING("🚧 Modo completo: creando hasta 170 estaciones..."))
            for i in range(4, 171):
                estaciones.append({
                    "nombre": f"Estación {i}",
                    "direccion": f"Ubicación #{i}, Bogotá",
                    "latitud": 4.60 + (i * 0.001),
                    "longitud": -74.08 + (i * 0.001),
                    "capacidad_electricas": 15,
                    "capacidad_mecanicas": 15,
                })

        for e in estaciones:
            Station.objects.get_or_create(nombre=e["nombre"], defaults=e)

        self.stdout.write(self.style.SUCCESS(f"✅ Se han creado o verificado {len(estaciones)} estaciones."))
