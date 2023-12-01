from typing import BinaryIO
from struct import unpack

class FrameComponent:
  def __init__(self):
    self.id:                  int = None
    self.hor_sampling_factor: int = None
    self.ver_sampling_factor: int = None
    self.qt_selector:         int = None

  @staticmethod
  def readComponent(fp: BinaryIO) -> 'FrameComponent':
    comp = FrameComponent()

    comp.id, sampling_factors, comp.qt_selector = unpack(">BBB", fp.read(3))
    comp.hor_sampling_factor = sampling_factors >> 4
    comp.ver_sampling_factor = sampling_factors & 0x0F

    return comp
