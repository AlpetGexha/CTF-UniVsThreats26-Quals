from PIL import Image
import numpy as np

infile = "matrix_1white_0black2.txt"
outfile = "matrix_rendered2.png"
scale = 20   # pixel size per cell
quiet = 4    # white border (QR quiet zone)

with open(infile, "r", encoding="ascii") as f:
    rows = [line.strip() for line in f if line.strip()]

w = len(rows[0])
assert all(len(r) == w for r in rows)

arr = np.array([[255 if c == "1" else 0 for c in r] for r in rows], dtype=np.uint8)
arr = np.pad(arr, quiet, constant_values=255)

img = Image.fromarray(arr, mode="L").resize(
    (arr.shape[1] * scale, arr.shape[0] * scale),
    Image.NEAREST
)
img.save(outfile)
