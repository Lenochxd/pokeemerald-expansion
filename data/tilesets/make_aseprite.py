#!/usr/bin/env python3
"""Build a tileset.aseprite file from porytiles_src layer PNGs.

Usage: make_aseprite.py <porytiles_src_dir> <output.aseprite>

Writes one RGBA frame with three layers (bottom, middle, top), matching the
layer names used by the existing tilesets. Requires Pillow (pip install pillow).
"""
import struct
import sys
import zlib
from pathlib import Path

from PIL import Image

LAYERS = ["bottom", "middle", "top"]


def chunk(chunk_type, body):
    return struct.pack("<IH", len(body) + 6, chunk_type) + body


def layer_chunk(name):
    encoded = name.encode("utf-8")
    body = struct.pack("<HHHHHHB3xH", 3, 0, 0, 0, 0, 0, 255, len(encoded))
    return chunk(0x2004, body + encoded)


def cel_chunk(index, image):
    width, height = image.size
    pixels = zlib.compress(image.tobytes())
    body = struct.pack("<HhhBHh5xHH", index, 0, 0, 255, 2, 0, width, height)
    return chunk(0x2005, body + pixels)


def build(src_dir, out_path):
    images = []
    for name in LAYERS:
        path = Path(src_dir) / f"{name}.png"
        if not path.exists():
            raise SystemExit(f"Missing layer PNG: {path}")
        images.append(Image.open(path).convert("RGBA"))

    width, height = images[0].size
    for image in images:
        if image.size != (width, height):
            raise SystemExit("All layer PNGs must have the same size.")

    chunks = [layer_chunk(name) for name in LAYERS]
    chunks += [cel_chunk(i, image) for i, image in enumerate(images)]
    frame_body = b"".join(chunks)
    frame = struct.pack("<IHHH2xI", 16 + len(frame_body), 0xF1FA, len(chunks), 100, len(chunks)) + frame_body

    header = struct.pack("<IHHHHHIHII", 0, 0xA5E0, 1, width, height, 32, 1, 100, 0, 0)
    header += struct.pack("<B3xH", 0, 0)
    header += struct.pack("<BBhhHH", 1, 1, 0, 0, 16, 16)
    header += bytes(84)
    assert len(header) == 128

    data = header + frame
    data = struct.pack("<I", len(data)) + data[4:]
    Path(out_path).write_bytes(data)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    build(sys.argv[1], sys.argv[2])
