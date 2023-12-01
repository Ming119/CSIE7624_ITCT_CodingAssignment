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

  def _draw_pixel(self, y: int, x: int, l: float, cb: float, cr: float) -> None:
    self.image[y][x] = self._ycbcr_to_rgb(l, cb, cr)

  def draw_mcu(self, mcu_y: int, mcu_x: int, mcu_h: int, mcu_w: int, mcu: List[List[List[float]]]) -> None:
    for y in range(mcu_h):
      image_y = mcu_y * mcu_h + y
      if image_y >= self.height: break
      for x in range(mcu_w):
        image_x = mcu_x * mcu_w + x
        if image_x >= self.width: break
        self._draw_pixel(image_y, image_x, mcu[0][y][x], mcu[1][y][x], mcu[2][y][x])

  def save(self, path: str) -> None:
    img = PILImage.new("RGB", (self.width, self.height))
    img.putdata([pixel for row in self.image for pixel in row])
    img.save(path)
    print(f"Saved image to {path}")