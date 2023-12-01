from typing import List, Tuple, BinaryIO
from ScanComponent import ScanComponent
from struct import unpack

class StartOfScan:
  def __init__(self):
    self.num_components:           int = None
    self.successive_approximation: int = None
    self.components: List[ScanComponent] = []
    self.spectral_selection: Tuple[int, int] = ()

  @staticmethod
  def readSOS(fp: BinaryIO) -> 'StartOfScan':
    size, = unpack(">H", fp.read(2))
    
    sos = StartOfScan()
    sos.num_components, = unpack(">B", fp.read(1))

    for _ in range(sos.num_components):
      sos.components.append(ScanComponent.readComponent(fp))
    
    sos.spectral_selection = unpack(">BB", fp.read(2))
    sos.successive_approximation, = unpack(">B", fp.read(1))

    print(f"\tNumber of image components: {sos.num_components}")
    for i, component in enumerate(sos.components):
        print(f"\t\tComponent #{i+1}: selector={component.selector}, "
              f"table={component.dc_table}(DC), {component.ac_table}(AC)")
    print(f"\tSpectral selection: {sos.spectral_selection[0]} .. {sos.spectral_selection[1]}")
    print(f"\tSuccessive approximation: 0x{sos.successive_approximation:02X}")
    print()

    return sos