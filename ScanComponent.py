from typing import BinaryIO
from struct import unpack

class ScanComponent:
  def __init__(self):
    self.selector: int = None
    self.dc_table: int = None
    self.ac_table: int = None

  @staticmethod
  def readComponent(fp: BinaryIO) -> 'ScanComponent':
    component = ScanComponent()
    
    component.selector, table = unpack(">BB", fp.read(2))
    component.dc_table = table >> 4
    component.ac_table = table & 0x0F

    return component
