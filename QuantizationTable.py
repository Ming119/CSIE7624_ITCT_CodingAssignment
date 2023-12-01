from typing import List, Tuple, BinaryIO
from struct import unpack

class QuantizationTable:
  zigzag: List[Tuple[int, int]] = [
    (0, 0), (0, 1), (1, 0), (2, 0), (1, 1), (0, 2), (0, 3), (1, 2),
    (2, 1), (3, 0), (4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (0, 5),
    (1, 4), (2, 3), (3, 2), (4, 1), (5, 0), (6, 0), (5, 1), (4, 2),
    (3, 3), (2, 4), (1, 5), (0, 6), (0, 7), (1, 6), (2, 5), (3, 4),
    (4, 3), (5, 2), (6, 1), (7, 0), (7, 1), (6, 2), (5, 3), (4, 4),
    (3, 5), (2, 6), (1, 7), (2, 7), (3, 6), (4, 5), (5, 4), (6, 3),
    (7, 2), (7, 3), (6, 4), (5, 5), (4, 6), (3, 7), (4, 7), (5, 6),
    (6, 5), (7, 4), (7, 5), (6, 6), (5, 7), (6, 7), (7, 6), (7, 7),
  ]

  def __init__(self):
    self.precision: int = None
    self.id:        int = None
    self.table: List[List[int]] = None
  
  @staticmethod
  def defineQT(fp: BinaryIO) -> List['QuantizationTable']:
    size, = unpack(">H", fp.read(2))
    size -= 2

    qts = []
    
    while size > 0:
      qt = QuantizationTable()
      qt.table = [[0 for _ in range(8)] for _ in range(8)]

      temp, = unpack(">B", fp.read(1))
      qt.precision = temp >> 4
      qt.id = temp & 0x0F

      element_bytes = 1 if qt.precision == 0 else 2

      for i in range(64):
        element, = unpack(f">B" * element_bytes, fp.read(element_bytes))
        row, col = QuantizationTable.zigzag[i]
        qt.table[row][col] = element
      size -= 1 + 64 * element_bytes
      qts.append(qt)

      print(f"\tTable ID: {qt.id} " + ("(L)" if qt.id == 0 else "(C)") + f"\tPrecision: {qt.precision}")
      for i in range(len(qt.table)):
          print(f"\t\t#{i}: " + " ".join(str(element).rjust(2) for element in qt.table[i]))
      print()

    return qts
