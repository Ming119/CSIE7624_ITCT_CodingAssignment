from typing import BinaryIO
from struct import unpack

class FrameComponent:
  def __init__(self):
    self.id:  int = None
    self.hsf: int = None
    self.vsf: int = None
    self.qt_selector: int = None

  @staticmethod
  def readComponent(fp: BinaryIO) -> 'FrameComponent':
    comp = FrameComponent()

    comp.id, sampling_factors, comp.qt_selector = unpack(">BBB", fp.read(3))
    comp.hsf = sampling_factors >> 4
    comp.vsf = sampling_factors & 0x0F

    return comp
