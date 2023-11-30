import sys
import numpy as np

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

class Stream:
  def __init__(self, data: np.ndarray):
    self.data: np.ndarray = data
    self.pos: int = 0

  def getBit(self):
    byte = self.data[self.pos >> 3]
    bit = (byte >> (7 - (self.pos & 0x07))) & 0x01
    self.pos += 1
    return bit

  def getBits(self, n: int):
    res = 0
    for _ in range(n):
      res = (res << 1) | self.getBit()
    return res

class HuffmanTable:
  def __init__(self):
    self.root:     list = list()
    self.elements: list = list()
  
  def bitsFromLengths(self, root: list, element: list, pos: int) -> bool:
    if isinstance(root, list):
      if pos == 0:
        if len(root) < 2:
          root.append([element])
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
  
  def getcode(self, stream: Stream) -> int:
    while True:
      res: int = self.find(stream)
      if res == 0: return 0
      if res != -1: return res

class JPEG:
  def __init__(self, image_path: str):
    with open(image_path, "rb") as jpegfile:
      self.image_data = jpegfile.read()

    self.quantizationTabel: dict = {}
    self.height: int = 0
    self.width: int = 0
    self.numComponents: int = 0
    self.horizantalSubsamplingFactor: list = []
    self.verticalSubsamplingFactor: list = []
    self.quantizationTabelMapping: list = []

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
    # print("Huffman Table")
    pass

  def decodeSOS(self, data: np.ndarray):
    # print("Start of Scan")
    pass

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

# def idct2d(input: np.ndarray) -> np.ndarray:
#   l = input.shape[0]
#   c = np.zeros((l, l))
#   for k in range(l):
#     for n in range(l):
#       c[k, n] = np.sqrt(1/l) * np.cos(np.pi*k*(1/2+n)/l)
#       if k != 0:
#         c[k, n] *= np.sqrt(2)
#   return (np.kron(c, c) @ input.flatten()).reshape((l, l))

# def quantize(input: np.ndarray, q: np.ndarray) -> np.ndarray:
#   return input // q

# def decodeNumber(code, bits):
#   l = 2 ** (code - 1)
#   if bits >= l: return bits
#   return bits - (2 * l - 1)

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