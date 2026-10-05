"""Shared numerical source preparation for derived elevation products."""

import concurrent.futures
import hashlib
import json
import math
import urllib.request
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image


def load_grid():
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
    return elevation, longitudes, latitudes, [w, s, e, n], manifest
