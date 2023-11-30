import unittest

class Stream:
  def __init__(self, data: list):
    self.data: list = data
    self.position: int = 0

  def getBit(self):
    byte = self.data[self.position >> 3]
    bit = (byte >> (7 - (self.position & 0x07))) & 0x01
    self.position += 1
    if bit not in [0, 1]:
      raise ValueError(f"Invalid bit: {bit}")
    return bit

  def getBits(self, n: int):
    bits = 0
    for _ in range(n):
      bits = (bits << 1) | self.getBit()
    return bits

class TestStream(unittest.TestCase):
  def setUp(self):
    self.stream = Stream([])

  def test_getBit_with_valid_data(self):
    self.stream.data = bytearray([0b10101010])
    self.stream.position = 0
    self.assertEqual(self.stream.getBit(), 1)
    self.assertEqual(self.stream.getBit(), 0)
    self.assertEqual(self.stream.getBit(), 1)
    self.assertEqual(self.stream.getBit(), 0)
    self.assertEqual(self.stream.getBit(), 1)
    self.assertEqual(self.stream.getBit(), 0)
    self.assertEqual(self.stream.getBit(), 1)
    self.assertEqual(self.stream.getBit(), 0)

  def test_getBit_with_invalid_data(self):
    self.stream.data = bytearray([0b10101010])
    self.stream.position = 8
    with self.assertRaises(IndexError):
      self.stream.getBit()

  def test_getBit_with_no_data(self):
    self.stream.data = bytearray()
    self.stream.position = 0
    with self.assertRaises(IndexError):
      self.stream.getBit()

  def test_getBits_with_valid_data(self):
    self.stream.data = bytearray([0b10101010])
    self.stream.position = 0
    self.assertEqual(self.stream.getBits(1), 1)
    self.assertEqual(self.stream.getBits(1), 0)
    self.assertEqual(self.stream.getBits(1), 1)
    self.assertEqual(self.stream.getBits(1), 0)
    self.assertEqual(self.stream.getBits(1), 1)
    self.assertEqual(self.stream.getBits(1), 0)
    self.assertEqual(self.stream.getBits(1), 1)
    self.assertEqual(self.stream.getBits(1), 0)
  
  def test_getBits_with_invalid_data(self):
    self.stream.data = bytearray([0b10101010])
    self.stream.position = 8
    with self.assertRaises(IndexError):
      self.stream.getBits(1)
    
  def test_getBits_with_no_data(self):
    self.stream.data = bytearray()
    self.stream.position = 0
    with self.assertRaises(IndexError):
      self.stream.getBits(1)

if __name__ == '__main__':
  unittest.main()