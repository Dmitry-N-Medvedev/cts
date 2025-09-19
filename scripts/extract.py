#!/usr/bin/env python3
"""Split a binary float matrix file (startup.$516) into per-column text files.

- Input: a raw binary matrix of f32 or f64 (you set which), laid out row-major.
- Output: creates (or recreates) an "extracted" directory next to the input and
  writes one file per column named "startup.$516.<1..N>", one value per line.
"""

from __future__ import annotations
import os
import sys
import shutil

import numpy as np  # pylint: disable=import-error

# === Configuration (hardcoded) ===
FILE_PATH = "data/startup.$516"   # <-- adjust if needed
ROWS = 30002
COLS = 223
FLOAT_TYPE = "f32"                # choose: "f32" or "f64"

# Mapping for dtype (little-endian, big-endian)
DTYPE_MAP = {
    "f32": ("<f4", ">f4"),
    "f64": ("<f8", ">f8"),
}

def read_matrix(path: str, rows: int, cols: int, float_type: str) -> np.ndarray:
    """Read a raw binary float matrix from *path* as shape (rows, cols).

    Tries little-endian first, then big-endian for the given *float_type*.
    Raises ValueError if the byte size doesn't match the expected count.
    """
    if float_type not in DTYPE_MAP:
        raise ValueError(f"Invalid FLOAT_TYPE '{float_type}'. Use 'f32' or 'f64'.")

    expected_count = rows * cols
    le, be = DTYPE_MAP[float_type]

    # Try little-endian
    arr = np.fromfile(path, dtype=le)
    if arr.size == expected_count:
        return arr.reshape(rows, cols)

    # Try big-endian
    arr_be = np.fromfile(path, dtype=be)
    if arr_be.size == expected_count:
        return arr_be.reshape(rows, cols)

    itemsize = np.dtype(le).itemsize
    byte_size = os.path.getsize(path)
    have_vals = byte_size // itemsize
    raise ValueError(
        "Binary size mismatch: "
        f"{byte_size} bytes -> {have_vals} values, "
        f"expected {expected_count} ({rows}×{cols}, {float_type})."
    )

def main() -> None:
    """Entry point: load the matrix, recreate 'extracted/', and write columns."""
    in_path = FILE_PATH
    if not os.path.isfile(in_path):
        print(f"ERROR: file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    try:
        data = read_matrix(in_path, ROWS, COLS, FLOAT_TYPE)
    except (ValueError, OSError) as exc:
        print(f"ERROR: failed to read matrix from '{in_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    rows, cols = data.shape
    if rows != ROWS or cols != COLS:
        print(f"ERROR: parsed shape {data.shape}, expected ({ROWS}, {COLS}).", file=sys.stderr)
        sys.exit(1)

    base_dir = os.path.dirname(in_path)
    base_name = os.path.basename(in_path)

    # Recreate "extracted" directory
    out_dir = os.path.join(base_dir, "extracted")
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)

    print(f"Splitting {in_path} ({FLOAT_TYPE}, {rows}×{cols}) into {cols} columns...")

    for c in range(cols):
        out_name = f"{base_name}.{c+1}"
        out_path = os.path.join(out_dir, out_name)
        # Text output (human-readable); keep as requested
        np.savetxt(out_path, data[:, c], fmt="%.9g")
        print(f"  [{c+1:3}/{cols}] wrote {out_name}")

    print(f"Done: wrote {cols} files into {out_dir}")

if __name__ == "__main__":
    main()

