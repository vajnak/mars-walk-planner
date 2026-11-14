"""Crop the real HiRISE DTM + orthoimage into the files the viewer needs.
Needs only:  pip install numpy pillow
Put these two files in the same folder as this script:
  DTEEC_048842_1985_048908_1985_U01.IMG   (elevation, PDS3 format)
  ESP_048842_1985_RED_C_01_ORTHO.JP2      (matching photo)
Run:  python prep_data.py
"""
import json, os
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None            # the photo is ~100 megapixels, allow it

DEM_FILE   = "DTEEC_048842_1985_048908_1985_U01.IMG"
ORTHO_FILE = "ESP_048842_1985_RED_C_01_ORTHO.JP2"
ROWS, COLS = 14775, 6955                 # from the DTM label (LINES, LINE_SAMPLES)
HEADER     = 27820                       # label size in bytes (RECORD_BYTES x 1 record)
PIXEL_M    = 1.0097                      # metres per pixel (MAP_SCALE in the label)

CROP_PX = 2000                           # crop is CROP_PX x CROP_PX pixels (about 2 km)
X0, Y0  = 1100, 6300                     # top-left corner of the crop, in pixels
N, TEX  = 1024, 4096                     # heightmap size and texture size in the viewer

dem = np.memmap(DEM_FILE, dtype="<f4", mode="r", offset=HEADER, shape=(ROWS, COLS))
z = np.array(dem[Y0:Y0 + CROP_PX, X0:X0 + CROP_PX], dtype="float32")
bad = ~np.isfinite(z) | (z < -1e30)      # NASA marks missing data with a huge negative number
print("missing-data pixels in crop: %.2f%%" % (bad.mean() * 100))
if bad.all():
    raise SystemExit("Crop has no data. Change X0, Y0.")
z[bad] = z[~bad].min()

zi = Image.fromarray(z, mode="F").resize((N, N), Image.BILINEAR)
h = np.asarray(zi, dtype="<f4")
os.makedirs("data", exist_ok=True)
h.tofile("data/height.bin")

ortho = Image.open(ORTHO_FILE).crop((X0, Y0, X0 + CROP_PX, Y0 + CROP_PX))
a = np.asarray(ortho, dtype="float32")
v = a[a > 0]
lo, hi = np.percentile(v, [2, 98]) if v.size else (0, 255)
a = np.clip((a - lo) / max(hi - lo, 1e-6), 0, 1)
Image.fromarray((a * 255).astype("uint8")).resize((TEX, TEX), Image.LANCZOS).save("data/terrain.jpg", quality=90)

json.dump({"n": N, "size_m": round(CROP_PX * PIXEL_M, 1),
           "zmin": float(h.min()), "zmax": float(h.max())}, open("data/meta.json", "w"))
print("Done. Size %.0f m, elevation %.0f to %.0f m (relief %.0f m)." % (CROP_PX * PIXEL_M, h.min(), h.max(), h.max() - h.min()))
