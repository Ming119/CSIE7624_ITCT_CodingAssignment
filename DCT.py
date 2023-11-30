import numpy as np

class DCT:
  def __init__(self):
    self.base = np.zeros(64)
    self.zigzag = np.array([
      [ 0,  1,  5,  6, 14, 15, 27, 28],
      [ 2,  4,  7, 13, 16, 26, 29, 42],
      [ 3,  8, 12, 17, 25, 30, 41, 43],
      [ 9, 11, 18, 24, 31, 40, 44, 53],
      [10, 19, 23, 32, 39, 45, 52, 54],
      [20, 22, 33, 38, 46, 51, 55, 60],
      [21, 34, 37, 47, 50, 56, 59, 61],
      [35, 36, 48, 49, 57, 58, 62, 63]
    ]).flatten()
    
    l = 8
    self._dct = np.zeros((l, l))
    for k in range(l):
      for n in range(l):
        self._dct[k, n] = np.sqrt(1/l) * np.cos(np.pi*k*(1/2+n)/l)
        if k != 0:
          self._dct[k, n] *= np.sqrt(2)
  
  def dct(self):
    self.base = np.kron(self._dct, self._dct) @ self.base
  
  def idct(self):
    self.base = np.kron(self._dct.T, self._dct.T) @ self.base
  
  def rearrange(self):
    newIdx = np.ones(64).astype('int8')
    for i in range(64):
      newIdx[list(self.zigzag).index(i)] = i
    self.base = self.base[newIdx]
