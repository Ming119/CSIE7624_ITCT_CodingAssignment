from typing import List, Tuple
from PIL import Image as PILImage

class Image:
  def __init__(self, height: int, width: int):
    self.height: int = height
    self.width: int = width
    self.image: List[List[Tuple[int, int, int]]] = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]
    self._rCoeff: float = 2 - 2 * 0.299
    self._bCoeff: float = 2 - 2 * 0.114
    self._gCoeff: List[float] = [0.587, -0.114, -0.299]
    self._offset: int = 128
  
  def _clamp(self, value: int, _min: int = 0, _max: int = 255) -> int:
    return min(max(value, _min), _max)
  
  def _ycbcr_to_rgb(self, l: float, cb: float, cr: float) -> Tuple[int, int, int]:
    red = self._clamp(round(self._offset + l + self._rCoeff * cr))
    blue = self._clamp(round(self._offset + l + self._bCoeff * cb))
    green = self._clamp(round(self._offset + l + self._gCoeff[0] * cb + self._gCoeff[1] * cr))
    return (red, green, blue)

  def draw(self, y: int, x: int, l: float, cb: float, cr: float) -> None:
    self.image[y][x] = self._ycbcr_to_rgb(l, cb, cr)

  def save(self, path: str) -> None:
    img = PILImage.new("RGB", (self.width, self.height))
    img.putdata([pixel for row in self.image for pixel in row])
    img.save(path)
    print(f"Saved image to {path}")