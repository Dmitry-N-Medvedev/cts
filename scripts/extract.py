#!/usr/bin/env python3

import os
import sys
import shutil
import numpy as np

# === Configuration (hardcoded) ===
FILE_PATH   = "data/startup.$516"   # <-- adjust if needed
ROWS        = 30002
COLS        = 223
FLOAT_TYPE  = "f32"                 # choose: "f32" or "f64"

# Mapping for dtype
DTYPE_MAP = {
    "f32": ("<f4", ">f4"),   # little-endian, big-endian
    "f64": ("<f8", ">f8"),
}

def read_matrix(path: str, rows: int, cols: int, float_type: str) -> np.ndarray:
    if float_type not in DTYPE_MAP:
        raise ValueError(f"Invalid FLOAT_TYPE '{float_type}'. Use 'f32' or 'f64'.")

    expected_count = rows * cols
    le, be = DTYPE_MAP[float_type]

    # Try little-endian first
    arr = np.fromfile(path, dtype=le)
    if arr.size == expected_count:
        return arr.reshape(rows, cols)

    # Then try big-endian
    arr_be = np.fromfile(path, dtype=be)
    if arr_be.size == expected_count:
        return arr_be.reshape(rows, cols)

    raise ValueError(
        f"Binary size mismatch. File has {os.path.getsize(path)} bytes -> "
        f"{os.path.getsize(path)//np.dtype(le).itemsize} values; "
        f"expected {expected_count} ({rows}×{cols}). "
        f"Check ROWS/COLS or FLOAT_TYPE."
    )

def main():
    in_path = FILE_PATH
    if not os.path.isfile(in_path):
        print(f"ERROR: file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    try:
        data = read_matrix(in_path, ROWS, COLS, FLOAT_TYPE)
    except Exception as e:
        print(f"ERROR: failed to read matrix from '{in_path}': {e}", file=sys.stderr)
        sys.exit(1)

    rows, cols = data.shape
    print(f"Parsed matrix shape: {rows}×{cols} ({FLOAT_TYPE})")

    base_dir = os.path.dirname(in_path)
    base_name = os.path.basename(in_path)

    # Recreate "extracted" directory
    out_dir = os.path.join(base_dir, "extracted")
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)

    print(f"Splitting {in_path} into {cols} columns...")

    for c in range(cols):
        out_name = f"{base_name}.{c+1}"
        out_path = os.path.join(out_dir, out_name)
        np.savetxt(out_path, data[:, c], fmt="%.9g")
        print(f"  [{c+1:3}/{cols}] wrote {out_name}")

    print(f"Done: wrote {cols} files into {out_dir}")

if __name__ == "__main__":
    main()

