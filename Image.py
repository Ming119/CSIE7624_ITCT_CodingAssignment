import numpy as np

class Image:
  def __init__(self, height: int, width: int):
    self.height: int = height
    self.width: int = width
    self.image = np.zeros((height, width, 3), dtype=np.uint8)
  
  def ycbcr2rgb(self):
    self.image[:, :, 0] += 128
    m = np.array([
      [1, 0, 1.402],
      [1, -0.34414, -0.71414],
      [1, 1.772, 0]
    ])
    rgb = np.dot(self.image, m.T)
    self.image = np.clip(rgb, 0, 255)
  
  def drawMatrix(self, y, x, l, cb, cr):
    x *= 8
    y *= 8
    self.image[y:y+8, x:x+8, 0] = l.reshape((8, 8))
    self.image[y:y+8, x:x+8, 1] = cb.reshape((8, 8))
    self.image[y:y+8, x:x+8, 2] = cr.reshape((8, 8))
