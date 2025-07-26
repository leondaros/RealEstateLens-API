import requests
from shapely.geometry import shape, Point
import json

def fetch_osm_pois(polygon_geojson, filters, timeout=30, verify=True):
    """
    Busca POIs via Overpass API de acordo com os filtros desejados.

    polygon_geojson: string GeoJSON do polígono
    filters: lista de dicts, ex: [{"key": "amenity", "values": ["school","college","university"]}]
    """
    polygon = shape(json.loads(polygon_geojson))
    minx, miny, maxx, maxy = polygon.bounds

    query_blocks = []
    for f in filters:
        key = f['key']
        for value in f['values']:
            for el_type in ['node', 'way', 'relation']:
                query_blocks.append(f'{el_type}["{key}"="{value}"]({miny},{minx},{maxy},{maxx});')
    query = f"""
    [out:json][timeout:25];
    (
        {''.join(query_blocks)}
    );
    out center;
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    response = requests.post(overpass_url, data=query, timeout=timeout, verify=verify)
    response.raise_for_status()
    data = response.json().get("elements", [])

    # Filtra pelo polígono real
    pois = []
    for el in data:
        if "lat" in el and "lon" in el:
            pt = Point(el["lon"], el["lat"])
        elif "center" in el:
            pt = Point(el["center"]["lon"], el["center"]["lat"])
        else:
            continue
        if polygon.contains(pt):
            pois.append({
                "name": el.get("tags", {}).get("name"),
                "lat": pt.y,
                "lon": pt.x,
                "tags": el.get("tags", {})
            })
    return pois
