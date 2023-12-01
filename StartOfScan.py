from typing import Dict, Tuple, BinaryIO
from ScanComponent import ScanComponent
from struct import unpack

class StartOfScan:
  def __init__(self):
    self.num_components:           int = None
    self.successive_approximation: int = None
    self.components: Dict[int, ScanComponent] = {}
    self.spectral_selection: Tuple[int, int] = ()

  @staticmethod
  def readSOS(fp: BinaryIO) -> 'StartOfScan':
    size, = unpack(">H", fp.read(2))
    
    sos = StartOfScan()
    sos.num_components, = unpack(">B", fp.read(1))

    for _ in range(sos.num_components):
      component = ScanComponent.readComponent(fp)
      sos.components[component.selector] = component
    
    sos.spectral_selection = unpack(">BB", fp.read(2))
    sos.successive_approximation, = unpack(">B", fp.read(1))

    print(f"\tNumber of image components: {sos.num_components}")
    for id, component in sos.components.items():
        print(f"\t\tComponent selector={id}, "
              f"table={component.dc_table}(DC), {component.ac_table}(AC)")
    print(f"\tSpectral selection: {sos.spectral_selection[0]} .. {sos.spectral_selection[1]}")
    print(f"\tSuccessive approximation: 0x{sos.successive_approximation:02X}")
    print()

    return sos