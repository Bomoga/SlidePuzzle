from __future__ import annotations

from pathlib import Path
from typing import Dict
from PIL import Image


try:
    _LANCZOS = Image.Resampling.LANCZOS  # Pillow >= 10.0
except AttributeError:  # pragma: no cover
    _LANCZOS = Image.LANCZOS  # Pillow < 10


def _open_image(path: Path) -> Image.Image:
    img = Image.open(path)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    return img


def prepare_image(path: str, grid_size: int, tile_pixels: int) -> Image.Image:
    source = _open_image(Path(path))
    width, height = source.size
    square = min(width, height)
    left = (width - square) // 2
    top = (height - square) // 2
    source = source.crop((left, top, left + square, top + square))
    target_pixels = grid_size * tile_pixels
    return source.resize((target_pixels, target_pixels), _LANCZOS)


def slice_image(path: str, grid_size: int = 3, tile_pixels: int = 150) -> Dict[int, Image.Image]:
    """Return a dict mapping tile id -> PIL image; tile id 0 is the blank tile."""
    prepared = prepare_image(path, grid_size, tile_pixels)
    tiles: Dict[int, Image.Image] = {}
    for idx in range(grid_size * grid_size - 1):
        row, col = divmod(idx, grid_size)
        left = col * tile_pixels
        top = row * tile_pixels
        tiles[idx + 1] = prepared.crop((left, top, left + tile_pixels, top + tile_pixels))
    blank = Image.new("RGB", (tile_pixels, tile_pixels), color=(30, 30, 30))
    tiles[0] = blank
    return tiles
