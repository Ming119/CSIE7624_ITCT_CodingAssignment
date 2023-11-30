import numpy as np

class Stream:
  def __init__(self, data: np.ndarray):
    self.data: np.ndarray = data
    self.position: int = 0

  def getBit(self):
    byte = self.data[self.position >> 3]
    bit = (byte >> (7 - (self.position & 0x07))) & 0x01
    self.position += 1
    return bit

  def getBits(self, n: int):
    bits = 0
    for _ in range(n):
      bits = (bits << 1) | self.getBit()
    return bits
