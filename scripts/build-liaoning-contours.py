"""Export numerical elevation contours without changing protected artwork or boundaries."""

import hashlib
import json
from itertools import pairwise
from pathlib import Path

import matplotlib
from liaoning_elevation import load_grid

matplotlib.use("Agg")
import matplotlib.pyplot as plt

elevation, longitudes, latitudes, bounds, source_tiles = load_grid()
w, s, e, n = bounds
levels = [50, 200, 500, 1000]
# An explicit downsample retains the source DEM resolution; no invented high-frequency detail.
contour = plt.contour(
    longitudes[::4], latitudes[::4], elevation[::4, ::4], levels=levels
)


# Clip each numerical line to nine independent SVG tiles; no raster upscaling.
def clip(a, b, bounds):
    x0, y0, x1, y1 = bounds
    dx, dy = b[0] - a[0], b[1] - a[1]
    lo, hi = 0.0, 1.0
    for p, q in [(-dx, a[0] - x0), (dx, x1 - a[0]), (-dy, a[1] - y0), (dy, y1 - a[1])]:
        if p == 0:
            if q < 0:
                return None
        elif p < 0:
            lo = max(lo, q / p)
        else:
            hi = min(hi, q / p)
    if lo > hi:
        return None
    return (a[0] + lo * dx, a[1] + lo * dy), (a[0] + hi * dx, a[1] + hi * dy)


folder = Path("apps/web/public/folkverse/maps/contours")
folder.mkdir(exist_ok=True)
tiles = []
for row in range(3):
    for col in range(3):
        x, y, size = col * 1000 / 3, row * 1000 / 3, 1000 / 3
        content = []
        for level, segments, color in zip(
            levels, contour.allsegs, ["#d5dcbb", "#ead49b", "#f6b877", "#fff4df"]
        ):
            commands = []
            for segment in segments:
                points = [
                    ((lon - w) / (e - w) * 1000, (n - lat) / (n - s) * 1000)
                    for lon, lat in segment
                ]
                previous = None
                for a, b in pairwise(points):
                    clipped = clip(a, b, (x, y, x + size, y + size))
                    if clipped is None:
                        previous = None
                        continue
                    start, end = clipped
                    if previous != start:
                        commands.append(f"M{start[0]:.2f},{start[1]:.2f}")
                    commands.append(f"L{end[0]:.2f},{end[1]:.2f}")
                    previous = end
            content.append(
                f'<path d="{" ".join(commands)}" fill="none" stroke="{color}" stroke-width="1" vector-effect="non-scaling-stroke"/>'
            )
        payload = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {size} {size}">{"".join(content)}</svg>\n'
        name = f"{row}-{col}.svg"
        (folder / name).write_text(payload)
        tiles.append(
            {
                "x": x,
                "y": y,
                "size": size,
                "src": f"/folkverse/maps/contours/{name}",
                "sha256": hashlib.sha256(payload.encode()).hexdigest(),
            }
        )
output = {
    "bounds": [w, s, e, n],
    "coordinateSize": 1000,
    "metres": levels,
    "tiles": tiles,
    "source": "Mapzen Terrain Tiles, zoom 8 Terrarium elevation",
    "method": "Numerical contours sampled every fourth cell on the existing equirectangular grid and clipped to nine vector tiles. Approximate reference, not survey or navigation data.",
    "sourceTiles": source_tiles,
}
Path("apps/web/src/lib/maps/liaoning-contours.json").write_text(
    json.dumps(output, separators=(",", ":")) + "\n"
)
plt.close("all")
print(
    "Exported nine sourced SVG contour tiles at four elevation levels with source and output hashes; original artwork unchanged."
)
