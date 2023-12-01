from typing import List, Tuple
from PIL import Image as PILImage

class Image:
  def __init__(self, height: int, width: int):
    self.height: int = height
    self.width: int = width
    self.image: List[List[Tuple[int, int, int]]] = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]
  
  def _clamp(self, value: int, _min: int = 0, _max: int = 255) -> int:
    return min(max(value, _min), _max)
  
  def _ycbcr_to_rgb(self, l, cb, cr) -> Tuple[int, int, int]:
    red = cr * (2 - 2 * 0.299) + l + 128
    blue = cb * (2 - 2 * 0.114) + l + 128
    green = (l - 0.114 * blue - 0.299 * red) / 0.587 + 128
    return (self._clamp(red), self._clamp(green), self._clamp(blue))

  def draw(self, y: int, x: int, l: int, cb: int, cr: int) -> None:
    self.image[y][x] = self._ycbcr_to_rgb(l, cb, cr)

  def save(self, path: str) -> None:
    img = PILImage.new("RGB", (self.width, self.height))
    img.putdata([pixel for row in self.image for pixel in row])
    print(f"Saved image to {path}")