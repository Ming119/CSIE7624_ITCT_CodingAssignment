import math
from typing import List
from modules.QuantizationTable import QuantizationTable

class IDCT:
  idctTable = []
  for y in range(8):
    row = []
    for x in range(8):
      uv_matrix = []
      for u in range(8):
        uv_row = []
        for v in range(8):
          cu = 1.0 / math.sqrt(2) if u == 0 else 1.0
          cv = 1.0 / math.sqrt(2) if v == 0 else 1.0
          uv_row.append(cu * cv * math.cos((2 * x + 1) * u * math.pi / 16) * math.cos((2 * y + 1) * v * math.pi / 16))
        uv_matrix.append(uv_row)
      row.append(uv_matrix)
    idctTable.append(row)

  def __init__(self, qt: QuantizationTable):
    self.base = [[0 for _ in range(8)] for _ in range(8)]
    self.qt = qt
   
  def record(self, coeffs: List[int]):
    for i, coeff in enumerate(coeffs):
      row, col = QuantizationTable.zigzag[i]
      self.base[row][col] = coeff * self.qt.table[row][col]
  
  def perform_idct(self, mcu: List[List[int]], r: int, c: int) -> List[List[int]]:
    for y in range(8):
      for x in range(8):
        val = 0
        for u in range(8):
          for v in range(8):
            val += IDCT.idctTable[y][x][u][v] * self.base[v][u]
        mcu[(r * 8) + y][(c * 8) + x] = val / 4
    return mcu