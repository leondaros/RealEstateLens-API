import os
import csv
import django
from django.contrib.gis.geos import MultiPolygon, GEOSGeometry
import sys
import csv

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from real_estate_lens.models import Location  # Importe o modelo correto

def import_locations_from_csv(file_path):
    """
    Importa localizações de um arquivo CSV.

    :param file_path: Caminho para o arquivo CSV.
    """
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row['CD_MUN']
                location_type = 'CT'
                geometry_wkt = row['geometry']

                # Verifica e cria a geometria, se fornecida
                geometry = GEOSGeometry(geometry_wkt) if geometry_wkt else None

                # Cria a instância
                location = Location(name=name, location_type=location_type, geometry=geometry)
                location.save()
                print(f"Location '{name}' adicionada com sucesso!")
    except Exception as e:
        print(f"Erro ao importar localizações: {e}")

if __name__ == "__main__":
    # Caminho para o arquivo CSV
    file_path = "../out.csv"

    csv.field_size_limit(sys.maxsize)

    # Importa as localizações
    import_locations_from_csv(file_path)
