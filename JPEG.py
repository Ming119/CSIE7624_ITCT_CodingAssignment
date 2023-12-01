import math
from utils import *
from typing import BinaryIO, List, Dict, Tuple

from PIL import Image as PILImage
from struct import unpack

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
    self.qt: Dict[int, QuantizationTable] = {}
    self.ht: Dict[Tuple[int, int], HuffmanTable] = {}

    self.sof: StartOfFrame = None
    self.sos: StartOfScan = None
  
  def _handleEOI(self):
    img = PILImage.new("RGB", (self.width, self.height))
    img.putdata(self.image)
    img.save(self.output_path or "output.bmp")

  def __removeStuffByte(self, fp: BinaryIO) -> bytearray:
    start_pos = fp.tell()
    fp.seek(0, 2)
    end_pos = fp.tell()
    fp.seek(start_pos)

    data = bytearray(fp.read(end_pos - start_pos))

    marker_pos = None
    marker_pos_diff = 0

    for i in range(len(data)-2, 0, -1):
      marker_code = data[i:i+2]

      if marker_code == b"\xFF\x00":
        data.pop(i+1)
        marker_pos_diff += 1

      elif marker_code > b"\xFF\x00":
        if b"\xFF\xD0" <= marker_code <= b"\xFF\xD7":
          print(f"Found RST marker at 0x{i:04X} ({i}), skipping")
          data.pop(i)
          marker_pos_diff += 1
        else:
          marker_pos = i
          marker_pos_diff = 0
    
    if marker_pos is None:
      print("Error: No marker found")
      exit(1)

    fp.seek(start_pos + marker_pos)
    return data[:marker_pos - marker_pos_diff]

  def _readMCU(self, fp: BinaryIO):
    mcu_height = self.sof.max_vsf * 8
    mcu_width  = self.sof.max_hsf * 8

    num_mcu_height = math.ceil(self.height / mcu_height)
    num_mcu_width  = math.ceil(self.width  / mcu_width)

    print(f"\tMCU size: {mcu_width} x {mcu_height}")
    print(f"\tNumber of MCU: {num_mcu_width} x {num_mcu_height}")
    print()

    scan_data = self.__removeStuffByte(fp)

    image_rgb = [[(0, 0, 0) for _ in range(self.width)] for _ in range(self.height)]
    current_bit = 0
    prediction = [0 for _ in range(self.sof.num_components)]

    for mcu_y in range(num_mcu_height):
      for mcu_x in range(num_mcu_width):
        print(f"\tMCU {mcu_x}, {mcu_y}")
        
        mcu_list = []
        for scanComponentIdx, scanComponent in self.sos.components.items():
          frameComponent = self.sof.components[scanComponent.selector]
          if frameComponent is None:
            print(f"Error: Component {scanComponent.selector} not defined in SOF")
            exit(1)
          
          qt = self.qt[frameComponent.qt_selector]
          dcht = self.ht[scanComponent.dc_table, 0]
          acht = self.ht[scanComponent.ac_table, 1]

          mcu = [[0 for _ in range(8 * frameComponent.hsf)] for _ in range(8 * frameComponent.vsf)]

          for _r in range(frameComponent.vsf):
            for _c in range(frameComponent.hsf):
             
              dcCode, length = dcht.getCode(scan_data, current_bit)
              current_bit += length

              additionalBits = dcht.bits_from_bytearray(scan_data, current_bit, dcCode)
              current_bit += dcCode

              diff = dcht.decode(dcCode, additionalBits)
              abs_diff = prediction[scanComponentIdx] + diff
              prediction[scanComponentIdx] = abs_diff

              dct_coeffs = [0 for _ in range(64)]
              dct_coeffs[0] = abs_diff

              k = 1
              while k < 64:
                acCode, length = acht.getCode(scan_data, current_bit)
                current_bit += length

                r = acCode >> 4
                s = acCode & 0x0F

                if s == 0:
                  if r == 15:
                    k += 15
                    continue
                  else: break

                k += r
                additionalBits = acht.bits_from_bytearray(scan_data, current_bit, s)
                current_bit += s

                acCoeff = acht.decode(acCode, additionalBits)
                dct_coeffs[k] = acCoeff
                k += 1
              
              dct_matrix = [[0 for _ in range(8)] for _ in range(8)]
              for i, coeff in enumerate(dct_coeffs):
                row, col = QuantizationTable.zigzag[i]
                dct_matrix[row][col] = coeff * qt[i]
              
              for y in range(8):
                for x in range(8):
                  val = 0
                  for u in range(8):
                    for v in range(8):
                      val += dct_matrix[u][v] * math.cos((2 * x + 1) * u * math.pi / 16) * math.cos((2 * y + 1) * v * math.pi / 16)
                  mcu[y + _r * 8][x + _c * 8] = val / 4
        
          hm = self.sof.max_hsf // frameComponent.hsf
          vm = self.sof.max_vsf // frameComponent.vsf

          if vm > 1 or hm > 1:
            mcu = [[val for val in row for _ in range(hm)] for row in mcu for _ in range(vm)]
          
          mcu_list.append(mcu)
        
        for y in range(mcu_height):
          if mcu_y * mcu_height + y >= self.height: break

          for x in range(mcu_width):
            if mcu_x * mcu_width + x >= self.width: break

            image_rgb[mcu_y * mcu_height + y][mcu_x * mcu_width + x] = ycbcr_to_rgb(mcu_list[0][y][x], mcu_list[1][y][x], mcu_list[2][y][x])

  def _handleDQT(self, fp: BinaryIO) -> None:
    for table in QuantizationTable.defineQT(fp):
      self.qt[table.id] = table

  def _handleSOF(self, fp: BinaryIO):
    self.sof = StartOfFrame.readSOF(fp)
    self.height = self.sof.height
    self.width = self.sof.width
    self.image = [0] * (self.height * self.width)

  def _handleDHT(self, fp: BinaryIO):
    for table in HuffmanTable.defineHT(fp):
      self.ht[table.id, table.tc] = table
    
  def _handleSOS(self, fp: BinaryIO):
    if self.sof is None:
      print("Error: SOF not defined")
      exit(1)
    
    self.sos = StartOfScan.readSOS(fp)
    self._readMCU(fp)
  
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
