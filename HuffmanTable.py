from typing import Dict, List, Tuple, BinaryIO
from collections import defaultdict
from struct import unpack

class HuffmanTable:
  id: int = None
  tc: int = None
  counts: List[int] = []
  huffmanData: Dict[Tuple[int, int], int] = {}

  @staticmethod
  def defineHT(fp: BinaryIO) -> List['HuffmanTable']:
    size, = unpack(">H", fp.read(2))
    size -= 2
    hts = []

    while size > 0:
      ht = HuffmanTable()
      ht.counts = [0 for _ in range(16)]
      ht.huffmanData = {}

      temp, = unpack(">B", fp.read(1))
      ht.tc = temp >> 4
      ht.id = temp & 0x0F

      for i in range(16):
        ht.counts[i], = unpack(">B", fp.read(1))
     
      length_code_map = defaultdict(list)
      code = 0
      for length, count in enumerate(ht.counts):
        for _ in range(count):
          huffman_byte, = unpack(">B", fp.read(1))
          ht.huffmanData[(length + 1, code)] = huffman_byte
          length_code_map[length + 1].append(huffman_byte)
          code += 1
        code <<= 1
      
      size -= (1 + 16 + sum(ht.counts))

      hts.append(ht)

      print(f"\tTable ID: {ht.id}\tClass: {ht.tc} " + ("(DC)" if ht.tc == 0 else "(AC)"))
      for i in range(16):
          print(f"\t\tCodes of length {i+1} bits ({ht.counts[i]} total): ", end="")
          for huffman_byte in length_code_map[i+1]:
              print(f"{huffman_byte:02X} ", end="")
          print()
      print(f"\tTotal number of codes: {sum(ht.counts)}")
      print()
  
    return hts