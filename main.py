import sys
import numpy as np
from struct import unpack
import matplotlib.pyplot as plt

zigzag: np.ndarray = np.array([
   0,  1,  5,  6, 14, 15, 27, 28,
   2,  4,  7, 13, 16, 26, 29, 42,
   3,  8, 12, 17, 25, 30, 41, 43,
   9, 11, 18, 24, 31, 40, 44, 53,
  10, 19, 23, 32, 39, 45, 52, 54,
  20, 22, 33, 38, 46, 51, 55, 60,
  21, 34, 37, 47, 50, 56, 59, 61,
  35, 36, 48, 49, 57, 58, 62, 63
]).reshape((8, 8))

marker_mapping: dict = {
  0xFFD8: "Start of Image (SOI)",
  0xFFE0: "Application Segment 0 (APP0)",
  0xFFDB: "Define Quantization Table (DQT)",
  0xFFC0: "Start of Frame (SOF0)",
  0xFFC4: "Define Huffman Table (DHT)",
  0xFFDA: "Start of Scan (SOS)",
  0xFFD9: "End of Image (EOI)",
  
  0xFFFE: "Comment (COM)",
}

subsample_mapping: dict = {
  "11": "4:4:4",
  "21": "4:2:2",
  "22": "4:2:0",
  "41": "4:1:1",
}

def decodeNumber(code, bits):
  l = 2 ** (code - 1)
  if bits >= l: return bits
  return bits - (2 * l - 1)

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

class HuffmanTable:
  def __init__(self):
    self.root:     list = list()
    self.elements: list = list()
  
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
  
  def getHuffmanBits(self, lengths: int, elements: list) -> None:
    self.elements = elements
    
    ii = 0
    for i in range(len(lengths)):
      for _ in range(lengths[i]):
        self.bitsFromLengths(self.root, elements[ii], i)
        ii += 1

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

class JPEG:
  def __init__(self, image_path: str):
    with open(image_path, "rb") as jpegfile:
      self.image_data = jpegfile.read()

    self.decodedImage: np.ndarray = None
    self.height: int = 0
    self.width: int = 0
    self.quantizationTabel: dict = {}
    self.huffmanTables: dict = {}
    self.numComponents: int = 0

    self.horizantalSubsamplingFactor: list = []
    self.verticalSubsamplingFactor: list = []
    self.quantizationTabelMapping: list = []
  
  def _buildMatrix(self, stream: Stream, dcTableId: int, acTableId: int, quantizationTable: list, oldDcCoefficient: int) -> tuple:
    i = DCT()

    code = self.huffmanTables[0b00 | dcTableId].getCode(stream)
    bits = stream.getBits(code)
    dcCoeff = decodeNumber(code, bits) + oldDcCoefficient
    i.base[0] = dcCoeff

    l = 1
    while l < 64:
      code = self.huffmanTables[0b10 | acTableId].getCode(stream)
      if code == 0: break
      if code == 0xF0:
        l += 16
        continue
      elif code > 15:
        l += code >> 4
        code &= 0x0F
      
      bits = stream.getBits(code)

      if l < 64:
        i.base[l] = decodeNumber(code, bits)
        l += 1
    
    i.base = np.multiply(i.base, quantizationTable)
    i.rearrange()
    i.idct()

    return i, dcCoeff

  def decodeQuantizationTable(self, data: np.ndarray):
    offset = 0
    while offset < len(data):
      identifier = int.from_bytes(data[offset:offset+1], "big")
      self.quantizationTabel[identifier] = [int(byte) for byte in data[offset + 1: offset + 65]]
      offset += 65

  def decodeSOF(self, data: np.ndarray):
    precision = int.from_bytes(data[:1], "big")
    self.height = int.from_bytes(data[1:3], "big")
    self.width = int.from_bytes(data[3:5], "big")
    self.numComponents = int.from_bytes(data[5:6], "big")

    for i in range(self.numComponents):
      identifier = int.from_bytes(data[6 + 3*i:7 + 3*i], "big")
      subsamplingFactor = int.from_bytes(data[7 + 3*i:8 + 3*i], "big")
      self.quantizationTabelMapping.append(int.from_bytes(data[8 + 3*i:9 + 3*i], "big"))
      self.horizantalSubsamplingFactor.append(subsamplingFactor >> 4)
      self.verticalSubsamplingFactor.append(subsamplingFactor & 0x0F)

  def decodeHuffmanTable(self, data: np.ndarray):
    offset = 0

    while offset < len(data):
      tcth = int.from_bytes(data[offset:offset+1], "big")
      tableClass = tcth >> 4
      tableIdentifier = tcth & 0x0F
      offset += 1

      lengths = [int(byte) for byte in data[offset:offset+16]]
      offset += 16

      elements = []
      for length in lengths:
        elements.extend([int(byte) for byte in data[offset:offset+length]])
        offset += length
      
      huffmanTable = HuffmanTable()
      huffmanTable.getHuffmanBits(lengths, elements)
      self.huffmanTables[tableClass << 1 | tableIdentifier] = huffmanTable

  def decodeSOS(self, data: np.ndarray):
    ls = int.from_bytes(data[:1], "big")
    ns = int.from_bytes(data[1:3], "big")
    csj = unpack("BB"*ns, data[3:3+2*ns])
    
    dcTableMapping = []
    acTableMapping = []
    for i in range(ns):
      dcTableMapping.append(csj[2*i+1] >> 4)
      acTableMapping.append(csj[2*i+1] & 0x0F)
    data = data[6+2*ns:]

    i = 0
    while i < len(data) - 1:
      m = int.from_bytes(data[i:i+2], "big")
      if m == 0xFF00:
        data = data[:i+1] + data[i+2:]
      i += 1
    
    image = Image(self.height, self.width)
    stream = Stream(data)
    oldlumaDcCoefficient, oldCbDcCoefficient, oldCrDcCoefficient = 0, 0, 0
    for y in range(self.height // 8):
      for x in range(self.width // 8):
        matLuma, oldlumaDcCoefficient = self._buildMatrix(
          stream, dcTableMapping[0], acTableMapping[0],
          self.quantizationTabel[self.quantizationTabelMapping[0]],
          oldlumaDcCoefficient)
        matCb, oldCbDcCoefficient = self._buildMatrix(
          stream, dcTableMapping[1], acTableMapping[1],
          self.quantizationTabel[self.quantizationTabelMapping[1]],
          oldCbDcCoefficient)
        matCr, oldCrDcCoefficient = self._buildMatrix(
          stream, dcTableMapping[2], acTableMapping[2],
          self.quantizationTabel[self.quantizationTabelMapping[2]],
          oldCrDcCoefficient)
        image.drawMatrix(y, x, matLuma.base, matCb.base, matCr.base)
    image.ycbcr2rgb()
    self.decodeedImage = image.image

  def decode(self):
    data = self.image_data
    while len(data) > 0:
      marker = int.from_bytes(data[:2], "big")
      print(f"{marker_mapping[marker]}")

      if marker == 0xFFD8:    # SOI
        data = data[2:]
      
      elif marker == 0xFFDA:  # SOS
        self.decodeSOS(data[2:-2])
        data = data[-2:]
      
      elif marker == 0xFFD9:  # EOI
        return
      
      else:
        length = int.from_bytes(data[2:4], "big")
        chunk = data[4:2+length]
        data = data[2+length:]

        if marker == 0xFFDB:  # DQT
          self.decodeQuantizationTable(chunk)
        elif marker == 0xFFC0:  # SOF0
          self.decodeSOF(chunk)
        elif marker == 0xFFC4:    # DHT
          self.decodeHuffmanTable(chunk)
        else:
          print(f"\tSkpped {length} bytes")

# def quantize(input: np.ndarray, q: np.ndarray) -> np.ndarray:
#   return input // q

if __name__ == "__main__":
  if (len(sys.argv) != 2):
    print("Usage: python main.py <input>")
    exit(1)

  input = sys.argv[1]
  if (not input.endswith(".jpg") and not input.endswith(".jpeg")):
    print("Input file must be a JPEG image")
    exit(1)
  
  jpeg = JPEG(input)
  jpeg.decode()
  plt.imsave("out.png", jpeg.decodeedImage)
