import math

class IDCT:
  def __init__(self):
    self.base = [0] * 64

    self.zigzag = [
       0,  1,  5,  6, 14, 15, 27, 28,
       2,  4,  7, 13, 16, 26, 29, 42,
       3,  8, 12, 17, 25, 30, 41, 43,
       9, 11, 18, 24, 31, 40, 44, 53,
      10, 19, 23, 32, 39, 45, 52, 54,
      20, 22, 33, 38, 46, 51, 55, 60,
      21, 34, 37, 47, 50, 56, 59, 61,
      35, 36, 48, 49, 57, 58, 62, 63
    ]
    
    self.idctTable = [
      [ (self._normCoeff(y) * math.cos(((2.0 * x + 1.0) * y * math.pi) / 16.0))
        for x in range(8) ] for y in range(8) ]

  def _normCoeff(self, n):
    return math.sqrt(1.0/2.0) if n == 0 else 1.0
   
  def rearrange(self):
    for y in range(8):
      for x in range(8):
        self.zigzag[y][x] = self.base[self.zigzag[y][x]]
    return self.zigzag
  
  def performIDCT(self):
    out = [list(range(8)) for _ in range(8)]
    for x in range(8):
      for y in range(8):
        local_sum = 0
        for u in range(self.idctPrecision):
          for v in range(self.idctPrecision):
            local_sum += self.zigzag[v][u] * self.idctTable[u][x] * self.idctTable[v][y]
        out[y][x] = local_sum // 4
    self.base = out
