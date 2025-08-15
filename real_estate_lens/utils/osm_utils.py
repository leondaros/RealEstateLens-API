# services/osm.py
import json, requests
from shapely.geometry import shape

def _polygon_to_poly_string(polygon_geojson, max_points=2000, simplify_tolerance=0.0):
    geom = shape(json.loads(polygon_geojson))
    if geom.geom_type == "MultiPolygon":
        geom = max(geom.geoms, key=lambda g: g.area)
    if simplify_tolerance > 0:
        geom = geom.simplify(simplify_tolerance, preserve_topology=True)
    coords = list(geom.exterior.coords)
    if len(coords) > max_points:
        step = max(1, len(coords) // max_points)
        coords = coords[::step]
    return " ".join(f"{y} {x}" for x, y in coords)

def fetch_osm_count_in_poly(polygon_geojson, filters, timeout=25, verify=True):
    """
    Faz um único UNION com todos os key=value dentro do polígono e retorna 1 count deduplicado.
    """
    poly = _polygon_to_poly_string(polygon_geojson, simplify_tolerance=0.00005)

    # Um único conjunto (nwr) com todas as combinações key=value
    lines = []
    for f in filters:
        key = f["key"]
        for v in f["values"]:
            lines.append(f'nwr["{key}"="{v}"](poly:"{poly}");')

    query = f'[out:json][timeout:{timeout}];\n(\n  ' + "\n  ".join(lines) + '\n);\nout count;'

    r = requests.post(
        "https://overpass-api.de/api/interpreter",
        data=query.encode("utf-8"),
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept-Encoding": "gzip",
        },
        timeout=timeout,
        verify=verify,
    )
    r.raise_for_status()
    data = r.json()
    elems = [el for el in data.get("elements", []) if el.get("type") == "count"]
    return int(elems[0]["tags"]["total"]) if elems else 0
