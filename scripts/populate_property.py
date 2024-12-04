import os
import django
import csv
import random
from django.contrib.gis.geos import MultiPolygon, Point


# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from real_estate_lens.models import Location, Property

def populate_properties_from_csv(file_path):
    """
    Popula o banco de dados com dados do arquivo CSV e gera propriedades dentro de Garopaba.
    """
    try:
        # Busca a Location correspondente a Garopaba
        garopaba_location = Location.objects.get(name='Garopaba')
        multipolygon = garopaba_location.geometry

        if not isinstance(multipolygon, MultiPolygon):
            raise ValueError("A geometria de Garopaba não é um MultiPolygon válido.")

        # Abrir o CSV e processar cada linha
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # Gerar uma coordenada aleatória dentro do MultiPolygon
                point = generate_random_point_in_multipolygon(multipolygon)

                # Criar uma nova propriedade
                new_property = Property(
                    price=float(row['Preco']),
                    location=garopaba_location,
                    description=row['Descricao'],
                    square_meters=row['Tamanho(m²)'],
                    bedrooms=row['Quartos'],
                    bathrooms=row['Banheiros'],
                    link=row['link'],
                    coordinates=point

                )
                new_property.save()
                print(f"Propriedade '{new_property.link}' criada com sucesso.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")


def generate_random_point_in_multipolygon(multipolygon):
    """
    Gera uma coordenada aleatória dentro de um MultiPolygon.
    """
    # Seleciona um dos polígonos aleatoriamente
    polygon = random.choice(multipolygon)

    # Obtém os limites do polígono (bounding box)
    min_x, min_y, max_x, max_y = polygon.extent

    while True:
        # Gera um ponto aleatório dentro da bounding box
        random_x = random.uniform(min_x, max_x)
        random_y = random.uniform(min_y, max_y)
        point = Point(random_x, random_y)

        # Verifica se o ponto está dentro do polígono
        if polygon.contains(point):
            return point


if __name__ == "__main__":
    csv_file_path = "../data_normalizados - data_normalizados.csv"  # Substitua pelo caminho do seu arquivo CSV
    populate_properties_from_csv(csv_file_path)
