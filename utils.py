from typing import List

MARKERS: List = [
  "SOF0", "SOF1", "SOF2", "SOF3", "DHT", "SOF5", "SOF6", "SOF7",
  "JPG", "SOF9", "SOF10", "SOF11", "DAC", "SOF13", "SOF14", "SOF15",
  "RST0", "RST1", "RST2", "RST3", "RST4", "RST5", "RST6", "RST7",
  "SOI", "EOI", "SOS", "DQT", "DNL", "DRI", "DHP", "EXP",
  "APP0", "APP1", "APP2", "APP3", "APP4", "APP5", "APP6", "APP7",
  "APP8", "APP9", "APP10", "APP11", "APP12", "APP13", "APP14", "APP15",
  "JPG0", "JPG1", "JPG2", "JPG3", "JPG4", "JPG5", "JPG6", "JPG7",
  "JPG8", "JPG9", "JPG10", "JPG11", "JPG12", "JPG13", "COM", "TEM",
  "[Invalid Marker]"
]

def bit_from_bytearray(data: bytearray, bit_idx: int) -> int:
  return (data[bit_idx // 8] & (0b1 << (7 - (bit_idx % 8)))) >> (7 - bit_idx % 8)
  
def bits_from_bytearray(data: bytearray, start_idx: int, length: int) -> int:
  out = 0
  for bit_idx in range(start_idx, start_idx + length):
    out = (out << 1) | bit_from_bytearray(data, bit_idx)
  return out

def get_signed_value(bits: int, length: int) -> int:
  if bits < 2 ** (length - 1):
    min_val = (-1 << length) + 1
    return bits + min_val
  return bits
