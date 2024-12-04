import os
import django
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
import pandas as pd
import sys, csv
# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from real_estate_lens.models import Location  # Importe o modelo correto


def import_locations_from_csv(file_path, parent_location_name):
    """
    Importa bairros de um arquivo CSV e os associa a uma localização pai.

    :param file_path: Caminho para o arquivo CSV.
    :param parent_location_name: Nome da localização pai.
    """
    try:
        # Recupera a localização pai
        parent_location = Location.objects.get(name=parent_location_name)
        print(f"Associando bairros à localização pai: {parent_location_name}")

        # Carregar o CSV como DataFrame
        print("Carregando CSV...")
        df = pd.read_csv(file_path)

        if 'geometry' not in df.columns:
            raise ValueError("A coluna 'geometry' não foi encontrada no CSV.")
        if 'NAME' not in df.columns:
            raise ValueError("A coluna 'NAME' não foi encontrada no CSV.")

        # Iterar sobre os dados e criar objetos Django
        for idx, row in df.iterrows():
            name = row['NAME']
            geometry_wkt = row['geometry']

            try:
                # Criar geometria Django
                geometry = GEOSGeometry(geometry_wkt, srid=4326)
                if geometry.geom_type == "Polygon":
                    geometry = MultiPolygon([geometry])

                if geometry.geom_type != "MultiPolygon":
                    print(f"Geometria do tipo inválido para '{name}': {geometry.geom_type}")
                    continue

                # Criar a instância Location
                location = Location(
                    name=name,
                    parent=parent_location,
                    geometry=geometry,
                    location_type="N"  # Defina o tipo conforme necessário
                )
                location.save()
                print(f"Bairro '{name}' adicionado com sucesso!")

            except Exception as e:
                print(f"Erro ao adicionar '{name}': {e}")

    except Location.DoesNotExist:
        print(f"Localização pai '{parent_location_name}' não encontrada.")
    except Exception as e:
        print(f"Erro ao importar bairros: {e}")


if __name__ == "__main__":
    # Caminho para o arquivo CSV
    file_path = "/home/leon/Downloads/bairros4326.csv"  # Substitua pelo caminho correto do CSV

    csv.field_size_limit(sys.maxsize)

    # Nome da localização pai
    parent_location_name = "Garopaba"  # Substitua pelo nome correto da localização pai

    # Importar bairros e associar à localização pai
    import_locations_from_csv(file_path, parent_location_name)
