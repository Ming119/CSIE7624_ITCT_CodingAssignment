from IDCT import IDCT
from utils import *
from Image import Image
from struct import unpack
from Stream import Stream
from HuffmanTable import HuffmanTable
from PIL import Image as PILImage

class JPEG:
  def __init__(self, image_path: str):
    with open(image_path, "rb") as jpegfile:
      self.image_data = jpegfile.read()

    self.height: int = 0
    self.width:  int = 0

    self.qt: dict = {}
    self.qtMap: list = []

    self.huffmanTables: dict = {}
  
  def _removeFF00(self, data: list) -> list:
    d = []
    i = 0

    while True:
      byte, nextByte = unpack("BB", data[i:i+2])
      if byte == 0xFF:
        if nextByte != 0x00: break
        d.append(data[i])
        i += 2
      else:
        d.append(data[i])
        i += 1
  
    return d, i
  
  def _decodeNumber(self, code, bits) -> int:
    l = 2 ** (code - 1)
    return bits - (2 * l - 1) if bits < l else bits

  def _buildMatrix(self, stream: Stream, idx: int, qt: list, oldCoefficient: int) -> tuple:
    i = IDCT()

    code = self.huffmanTables[0b00 | idx].getCode(stream)
    bits = stream.getBits(code)
    dcCoeff = self._decodeNumber(code, bits) + oldCoefficient
    i.base[0] = dcCoeff * qt[0]

    l = 1
    while l < 64:
      code = self.huffmanTables[0b10 | idx].getCode(stream)
      if code == 0: break
      if code > 0x0F:
        l += code >> 4
        code &= 0x0F
      
      bits = stream.getBits(code)
      if l < 64:
        acCoeff = self._decodeNumber(code, bits)
        i.base[l] = acCoeff * qt[l]
        l += 1
    
    i.rearrange()
    i.performIDCT()

    return i, dcCoeff

  def decodeQuantizationTable(self, data: list):
    while (len(data) > 0):
      header, = unpack("B", data[:1])
      tableId = header & 0x0F
      if header >> 4 == 0:
        self.qt[tableId] = unpack("B"*64, data[1:65])
        data = data[65:]
      else:
        self.qt[tableId] = unpack(">H"*64, data[1:129])
        data = data[129:]

  def decodeSOF(self, data: list):
    header, self.height, self.width, components = unpack(">BHHB", data[:6])
    self.image = [0] * self.height * self.width

    for i in range(components):
      componentId, samplingFactor, quantizationTableId = unpack("BBB", data[6+3*i:9+3*i])
      self.qtMap.append(quantizationTableId)

  def decodeHuffmanTable(self, data: list):
    while len(data) > 0:
      offset = 0
      header, = unpack("B", data[offset:offset+1])
      offset += 1

      lengths = unpack("B"*16, data[offset:offset+16])
      offset += 16

      elements = []
      for length in lengths:
        elements += unpack("B"*length, data[offset:offset+length])
        offset += length
      
      huffmanTable = HuffmanTable()
      huffmanTable.getHuffmanBits(lengths, elements)
      self.huffmanTables[header] = huffmanTable

      data = data[offset:]

  def decodeSOS(self, data: list, headerLength: int) -> int:
    data, length = self._removeFF00(data[headerLength:])

    stream = Stream(data)
    oldlumaDcCoefficient, oldCbDcCoefficient, oldCrDcCoefficient = 0, 0, 0
    image = Image(self.height, self.width)
    for y in range(self.height // 8):
      for x in range(self.width // 8):
        matL,  oldlumaDcCoefficient = self._buildMatrix(stream, 0, self.qt[self.qtMap[0]], oldlumaDcCoefficient)
        matCr, oldCrDcCoefficient   = self._buildMatrix(stream, 1, self.qt[self.qtMap[1]], oldCrDcCoefficient)
        matCb, oldCbDcCoefficient   = self._buildMatrix(stream, 1, self.qt[self.qtMap[1]], oldCbDcCoefficient)  
        image.drawMatrix(y, x, matL, matCb, matCr)
    self.image = image.image

    return length + headerLength

  def decode(self):
    data = self.image_data
    while len(data) > 0:
      marker, = unpack(">H", data[:2])
      print(f"{marker_mapping[marker]}")

      if marker == 0xFFD8:    # SOI
        length = 2
      
      elif marker == 0xFFD9:  # EOI
        break
      
      else:
        length, = unpack(">H", data[2:4])
        length += 2
        chunk = data[4:length]
        if marker == 0xFFDB:  # DQT
          self.decodeQuantizationTable(chunk)
        elif marker == 0xFFC0:  # SOF
          self.decodeSOF(chunk)
        elif marker == 0xFFC4:  # DHT
          self.decodeHuffmanTable(chunk)
        elif marker == 0xFFDA:  # SOS
          length = self.decodeSOS(data, length)
        else:
          print(f"\tSkpped {length} bytes")
        
      data = data[length:]

  def save(self, output_path: str):
    img = PILImage.new("RGB", (self.width, self.height))
    img.putdata(self.image)
    img.save(output_path)