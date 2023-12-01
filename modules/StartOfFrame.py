from typing import BinaryIO, Dict
from struct import unpack
from modules.FrameComponent import FrameComponent

class StartOfFrame:
  def __init__(self):
    self.precision:      int = None
    self.height:         int = None
    self.width:          int = None
    self.max_hsf:        int = -1
    self.max_vsf:        int = -1
    self.num_components: int = None
    self.components: Dict[int, FrameComponent] = {}

  @staticmethod
  def readSOF(fp: BinaryIO) -> 'StartOfFrame':
    size, = unpack(">H", fp.read(2))
    size -= 2

    sof = StartOfFrame()
    sof.precision, sof.height, sof.width, sof.num_components = unpack(">BHHB", fp.read(6))

    for _ in range(sof.num_components):
      component = FrameComponent.readComponent(fp)
      sof.components[component.id] = component
      sof.max_hsf = max(sof.max_hsf, component.hsf)
      sof.max_vsf = max(sof.max_vsf, component.vsf)

    print(f"\tPrecision: {sof.precision}\tImage size: {sof.width} x {sof.height}")
    print(f"\tNumber of image components: {sof.num_components}")
    for id, component in sof.components.items():
        print(f"\t\tComponent ID = {id}, "
              f"Vertical sampling factor = {component.vsf}, "
              f"Horizontal sampling factor = {component.hsf}, "
              f"Quantization table = {component.qt_selector}")
    print()

    return sof
