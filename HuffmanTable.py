import unittest
from Stream import Stream

class HuffmanTable:
  def __init__(self):
    self.root:     list = []
    self.elements: list = []
  
  def bitsFromLengths(self, root: list, element: list, pos: int) -> bool:
    if isinstance(root, list):
      if pos == 0:
        if len(root) < 2:
          root.append(element)
          return True
        return False
      
      for i in [0, 1]:
        if len(root) == i:
          root.append([])
        if self.bitsFromLengths(root[i], element, pos - 1):
          return True
    return False
  
  def getHuffmanBits(self, lengths: list, elements: list) -> None:
    self.elements = elements
    
    j = 0
    for idx, length in enumerate(lengths):
      for _ in range(length):
        self.bitsFromLengths(self.root, elements[j], idx)
        j += 1

  def find(self, stream: Stream) -> int:
    root = self.root
    while isinstance(root, list):
      root = root[stream.getBit()]
    return root
  
  def getCode(self, stream: Stream) -> int:
    while True:
      res: int = self.find(stream)
      if res == 0: return 0
      if res != -1: return res

class TestHuffmanTable(unittest.TestCase):
  def setUp(self):
    self.huffman_table = HuffmanTable()

  def test_bitsFromLengths(self):
    root = []
    element = [1, 2, 3]
    pos = 2
    self.assertTrue(self.huffman_table.bitsFromLengths(root, element, pos))
    self.assertEqual(root, [[], [1, 2, 3]])

  def test_getHuffmanBits(self):
    lengths = [1, 2, 3]
    elements = [1, 2, 3, 4, 5, 6]
    self.huffman_table.getHuffmanBits(lengths, elements)
    self.assertEqual(self.huffman_table.root, [[1], [[2], [3, 4, 5]]])

  def test_find(self):
    stream = Stream([])
    stream.data = bytearray([0b10101010])
    stream.position = 0
    self.huffman_table.root = [[1], [[2], [3, 4, 5]]]
    self.assertEqual(self.huffman_table.find(stream), 1)

  def test_getCode(self):
    stream = Stream([])
    stream.data = bytearray([0b10101010])
    stream.position = 0
    self.huffman_table.root = [[1], [[2], [3, 4, 5]]]
    self.assertEqual(self.huffman_table.getCode(stream), 1)

if __name__ == '__main__':
  unittest.main()