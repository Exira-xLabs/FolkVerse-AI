import hashlib
import json
from pathlib import Path

from shapely.geometry import LineString, MultiPolygon, Point, mapping, shape
from shapely.ops import polygonize_full, unary_union

atlas = json.loads(Path("apps/web/src/lib/maps/liaoning-geography.json").read_text())
raw_path = Path(".local/liaoning-v2/city-relations-v2.json")
data = json.loads(raw_path.read_text())
features = []
checks = []
province = shape(atlas["geometry"])
for city in atlas["cities"]:
    matches = [
        e
        for e in data["elements"]
        if e.get("tags", {}).get("name") == city["names"]["zh-CN"] + "市"
    ]
    assert len(matches) == 1, (city["id"], len(matches))
    relation = matches[0]
    assert relation["tags"]["admin_level"] == "5"
    rings = {}
    for role in ["outer", "inner"]:
        lines = [
            LineString([(p["lon"], p["lat"]) for p in m["geometry"]])
            for m in relation["members"]
            if m["type"] == "way" and m["role"] == role and "geometry" in m
        ]
        if not lines:
            rings[role] = None
            continue
        polygons, cuts, dangles, invalid = polygonize_full(lines)
        assert cuts.is_empty and dangles.is_empty and invalid.is_empty, (
            city["id"],
            role,
            "incomplete rings",
        )
        rings[role] = unary_union(list(polygons.geoms))
    geometry = rings["outer"]
    if rings["inner"] is not None:
        geometry = geometry.difference(rings["inner"])
    assert geometry.is_valid and not geometry.is_empty
    assert geometry.covers(Point(city["coordinates"])), city["id"]
    simplified = geometry.simplify(0.0008, preserve_topology=True)
    assert simplified.covers(Point(city["coordinates"])) and simplified.is_valid
    if simplified.geom_type == "Polygon":
        simplified = MultiPolygon([simplified])
    geo = mapping(simplified)
    intersection = simplified.intersection(province)
    properties = {
        "land_bounds": list(intersection.bounds),
        "id": city["id"],
        "names": city["names"],
        "osm_relation": relation["id"],
        "admin_level": 5,
        "source": f"https://www.openstreetmap.org/relation/{relation['id']}",
        "license": "ODbL-1.0",
        "attribution": "© OpenStreetMap contributors",
        "simplification_degrees": 0.0008,
    }
    features.append({"type": "Feature", "properties": properties, "geometry": geo})
    intersection = simplified.intersection(province)
    checks.append(
        {
            "id": city["id"],
            "relation_id": relation["id"],
            "coordinate_inside_own_boundary": True,
            "valid": True,
            "land_bounds": list(intersection.bounds),
            "land_overlap_area_degrees2": intersection.area,
        }
    )
collection = {
    "type": "FeatureCollection",
    "name": "Liaoning prefecture-level city boundaries",
    "license": "https://opendatacommons.org/licenses/odbl/1-0/",
    "attribution": "© OpenStreetMap contributors",
    "source_timestamp": data.get("osm3s", {}).get("timestamp_osm_base"),
    "features": features,
}
encoded = json.dumps(collection, ensure_ascii=False, separators=(",", ":")) + "\n"
public = Path("apps/web/public/folkverse/maps/liaoning-cities.geojson")
client = Path("apps/web/src/lib/maps/liaoning-city-boundaries.json")
public.write_text(encoded)
client.write_text(encoded)
union = unary_union([shape(f["geometry"]) for f in features])
overlap = union.intersection(province)
proof = {
    "accessed_at": "2026-10-05",
    "source": "OpenStreetMap contributors",
    "license": collection["license"],
    "attribution": collection["attribution"],
    "query": Path(".local/liaoning-v2/overpass-query-v2.txt").read_text(),
    "endpoint": "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "timestamp_osm_base": collection["source_timestamp"],
    "raw_payload_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
    "public_path": str(public),
    "client_path": str(client),
    "sha256": hashlib.sha256(public.read_bytes()).hexdigest(),
    "city_count": len(features),
    "cities": checks,
    "natural_earth_land_coverage_fraction": overlap.area / province.area,
    "method": "Polygonize complete OSM outer member ways, subtract inner rings, topology-preserving 0.0008-degree simplification. Display clipped to original Natural Earth province outline. No hand-drawn or generated subdivision geometry.",
    "limits": "Generalized community mapping snapshot, not cadastral/legal boundaries. Independent province and city sources have small coastal/outer-edge differences; display is clipped to province.",
}
Path("report/evidence/phase02-map/atlas-v2/city-boundary-verification.json").write_text(
    json.dumps(proof, ensure_ascii=False, indent=2) + "\n"
)
print(
    "PASS",
    len(features),
    "valid sourced prefecture polygons; all city-centre points inside own boundary; bytes",
    len(public.read_bytes()),
    "province coverage",
    proof["natural_earth_land_coverage_fraction"],
)
