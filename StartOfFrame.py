from typing import List, BinaryIO
from struct import unpack
from FrameComponent import FrameComponent

class StartOfFrame:
  def __init__(self):
    self.precision:      int = None
    self.height:         int = None
    self.width:          int = None
    self.num_components: int = None
    self.components: List[FrameComponent] = []

  @staticmethod
  def readSOF(fp: BinaryIO) -> 'StartOfFrame':
    size, = unpack(">H", fp.read(2))
    size -= 2

    sof = StartOfFrame()
    sof.precision, sof.height, sof.width, sof.num_components = unpack(">BHHB", fp.read(6))

    for _ in range(sof.num_components):
      sof.components.append(FrameComponent.readComponent(fp))

    print(f"\tPrecision: {sof.precision}\tImage size: {sof.width} x {sof.height}")
    print(f"\tNumber of image components: {sof.num_components}")
    for i, component in enumerate(sof.components):
        print(f"\t\tComponent #{i+1}: ID = {component.id}, "
              f"Vertical sampling factor = {component.ver_sampling_factor}, "
              f"Horizontal sampling factor = {component.hor_sampling_factor}, "
              f"Quantization table = {component.qt_selector}")
    print()

    return sof
