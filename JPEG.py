from PIL import Image as PILImage
from utils import *
from struct import unpack
from typing import BinaryIO, List, Tuple

from StartOfScan import StartOfScan
from StartOfFrame import StartOfFrame
from HuffmanTable import HuffmanTable
from QuantizationTable import QuantizationTable

class JPEG:
  def __init__(self, input_path: str, output_path: str = None):
    self.input_path: str = input_path
    self.output_path: str = output_path

    self.height: int = 0
    self.width:  int = 0
    self.image: List[int] = []
    self.qt: dict = {}
    self.ht: dict = {}

    self.sof: StartOfFrame = None
    self.sos: StartOfScan = None
  
  def _handleEOI(self):
    img = PILImage.new("RGB", (self.width, self.height))
    img.putdata(self.image)
    img.save(self.output_path or "output.bmp")

  # def _removeFF00(self, data: list) -> list:
  #   d = []
  #   i = 0

  #   while True:
  #     byte, nextByte = unpack("BB", data[i:i+2])
  #     if byte == 0xFF:
  #       if nextByte != 0x00: break
  #       d.append(data[i])
  #       i += 2
  #     else:
  #       d.append(data[i])
  #       i += 1
  
  #   return d, i
  
  # def _getArray(self, fmt: str, data: bytes, length: int) -> list:
  #   return list(unpack(fmt*length, data[:length]))

  # def _decodeNumber(self, code, bits) -> int:
  #   l = 2 ** (code - 1)
  #   return bits - (2 * l - 1) if bits < l else bits

  # def _buildMatrix(self, stream: Stream, idx: int, qt: list, oldCoefficient: int) -> tuple:
  #   i = IDCT()

  #   code = self.ht[0 + idx].getCode(stream)
  #   bits = stream.getBits(code)
  #   dcCoeff = self._decodeNumber(code, bits) + oldCoefficient
  #   i.base[0] = dcCoeff * qt[0]

  #   l = 1
  #   ht = self.ht[16 + idx]
    
  #   while l < 64:
  #     print(ht.root)
  #     print(ht.elements)
  #     code = ht.getCode(stream)
  #     # code = self.ht[16 + idx].getCode(stream)
  #     if code == 0: break
  #     if code > 0x0F:
  #       l += code >> 4
  #       code &= 0x0F
      
  #     bits = stream.getBits(code)
  #     if l < 64:
  #       acCoeff = self._decodeNumber(code, bits)
  #       i.base[l] = acCoeff * qt[l]
  #       l += 1
    
  #   i.rearrange()
  #   i.performIDCT()

  #   return i, dcCoeff

  def _readMCU(self):
    pass

  def _handleDQT(self, fp: BinaryIO) -> None:
    for table in QuantizationTable.defineQT(fp):
      self.qt[table.id] = table.table

  def _handleSOF(self, fp: BinaryIO):
    self.sof = StartOfFrame.readSOF(fp)
    self.height = self.sof.height
    self.width = self.sof.width
    self.image = [0] * (self.height * self.width)

  def _handleDHT(self, fp: BinaryIO):
    for table in HuffmanTable.defineHT(fp):
      self.ht[table.id, table.tc] = table.huffmanData
    
  def _handleSOS(self, fp: BinaryIO):
    if self.sof is None:
      print("Error: SOF not defined")
      exit(1)
    
    self.sos = StartOfScan.readSOS(fp)
    self._readMCU()
  
  def decode(self):
    with open(self.input_path, "rb") as fp:
      marker_bytes = fp.read(2)
      while marker_bytes:
        marker = int.from_bytes(marker_bytes, "big")
        pos = fp.tell() - 2

        if marker < 0xFFC0:
          print("Error: Not a valid JPEG file")
          exit(1)

        print(f"@0x{pos:04X} ({pos}) READ MARKER 0x{marker:04X} ({MARKERS[marker - 0xFFC0]})")

        if marker == 0xFFD8:    # SOI
          pass
        elif marker == 0xFFD9:  # EOI
          self._handleEOI()
          break
        elif marker == 0xFFDB:  # DQT
          self._handleDQT(fp)
        elif marker == 0xFFC4:  # DHT
          self._handleDHT(fp)
        elif marker == 0xFFC0 or marker == 0xFFC1:  # SOF0 or SOF1
          self._handleSOF(fp)
        elif marker == 0xFFDA:  # SOS
          self._handleSOS(fp)
        else:
          size, = unpack(">H", fp.read(2))
          fp.seek(size - 2, 1)
          print(f"\tSkipping {size} bytes\n")

        marker_bytes = fp.read(2)
