import concurrent.futures
import hashlib
import json
import math
import urllib.request
from io import BytesIO
from pathlib import Path

import matplotlib
import numpy as np
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource, LinearSegmentedColormap

geo = json.loads(Path("apps/web/src/lib/maps/liaoning-geography.json").read_text())
w, s, e, n = geo["bounds"]
z = 8
size = 256
scale = 2**z
fx = lambda lon: (lon + 180) / 360 * scale
fy = lambda lat: (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * scale
xmin, xmax = math.floor(fx(w)), math.floor(fx(e))
ymin, ymax = math.floor(fy(n)), math.floor(fy(s))
cache = Path(".local/liaoning-v2/elevation")
cache.mkdir(exist_ok=True)
manifest = []


def load(pair):
    x, y = pair
    url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
    path = cache / f"{z}-{x}-{y}.png"
    if not path.exists():
        path.write_bytes(urllib.request.urlopen(url, timeout=30).read())
    payload = path.read_bytes()
    rgb = np.asarray(Image.open(BytesIO(payload)).convert("RGB")).astype(float)
    height = rgb[:, :, 0] * 256 + rgb[:, :, 1] + rgb[:, :, 2] / 256 - 32768
    return x, y, height, {"url": url, "sha256": hashlib.sha256(payload).hexdigest()}


canvas = np.zeros(((ymax - ymin + 1) * size, (xmax - xmin + 1) * size))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for x, y, height, record in pool.map(
        load, [(x, y) for x in range(xmin, xmax + 1) for y in range(ymin, ymax + 1)]
    ):
        canvas[
            (y - ymin) * size : (y - ymin + 1) * size,
            (x - xmin) * size : (x - xmin + 1) * size,
        ] = height
        manifest.append(record)
# Resample the elevation grid to the exact north-up longitude/latitude extent used by the atlas.
width = 1536
height = 1408
longitudes = np.linspace(w, e, width)
latitudes = np.linspace(n, s, height)
xpixels = np.clip(
    np.rint((np.array([fx(v) for v in longitudes]) - xmin) * size).astype(int),
    0,
    canvas.shape[1] - 1,
)
ypixels = np.clip(
    np.rint((np.array([fy(v) for v in latitudes]) - ymin) * size).astype(int),
    0,
    canvas.shape[0] - 1,
)
elevation = canvas[ypixels[:, None], xpixels[None, :]]
cmap = LinearSegmentedColormap.from_list(
    "liaoning", ["#91a47a", "#7c9568", "#627c55", "#686d4f", "#9b9879", "#c2b894"]
)
land = LightSource(azdeg=315, altdeg=45).shade(
    np.maximum(elevation, 0),
    cmap=cmap,
    vmin=0,
    vmax=1500,
    vert_exag=2.5,
    dx=(e - w) * 111000 * math.cos(math.radians((n + s) / 2)) / width,
    dy=(n - s) * 111000 / height,
    blend_mode="soft",
)
land[elevation < 0] = [0.075, 0.18, 0.22, 1]
fig = plt.figure(figsize=(width / 128, height / 128), dpi=128)
ax = fig.add_axes([0, 0, 1, 1])
ax.imshow(land, extent=[w, e, s, n], aspect="auto")
ax.axis("off")
output = Path("report/evidence/phase02-map/atlas-v2/liaoning-elevation-reference.png")
fig.savefig(output, dpi=128, pad_inches=0)
plt.close(fig)
proof = {
    "accessed_at": "2026-10-05",
    "dataset": "Mapzen Terrain Tiles, zoom 8 Terrarium elevation",
    "source": "https://registry.opendata.aws/terrain-tiles/",
    "attribution": "Mapzen; SRTM/GMTED2010 courtesy of USGS; ETOPO1 NOAA",
    "licensing": "https://github.com/tilezen/joerd/blob/master/docs/attribution.md",
    "bounds": geo["bounds"],
    "reference_path": str(output),
    "reference_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    "tiles": sorted(manifest, key=lambda a: a["url"]),
    "method": "Decode numerical elevation; resample to exact atlas equirectangular bounds; hypsometric tint and shaded relief. This is a numerical geographic reference plot, not generated artwork.",
}
Path("report/evidence/phase02-map/atlas-v2/elevation-provenance.json").write_text(
    json.dumps(proof, indent=2) + "\n"
)
print(
    "Rendered sourced elevation reference:",
    output,
    "tiles",
    len(manifest),
    "range",
    float(elevation.min()),
    float(elevation.max()),
)
