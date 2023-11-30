import numpy as np
from DCT import DCT
from utils import *
from Image import Image
from struct import unpack
from Stream import Stream
from HuffmanTable import HuffmanTable

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
      elif code > 0x0F:
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
