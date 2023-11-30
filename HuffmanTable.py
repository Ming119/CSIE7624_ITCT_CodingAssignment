from Stream import Stream

class HuffmanTable:
  def __init__(self):
    self.root:     list = list()
    self.elements: list = list()
  
  def bitsFromLengths(self, root: list, element: list, pos: int) -> bool:
    if isinstance(root, list):
      if pos == 0:
        if len(root) < 2:
          root.append(element)
          return True
        return False
      
      for i in [0, 1]:
        if len(root) == i:
          root.append([])
        if self.bitsFromLengths(root[i], element, pos - 1):
          return True
    return False
  
  def getHuffmanBits(self, lengths: int, elements: list) -> None:
    self.elements = elements
    
    ii = 0
    for i in range(len(lengths)):
      for _ in range(lengths[i]):
        self.bitsFromLengths(self.root, elements[ii], i)
        ii += 1

  def find(self, stream: Stream) -> int:
    root = self.root
    while isinstance(root, list):
      root = root[stream.getBit()]
    return root
  
  def getCode(self, stream: Stream) -> int:
    while True:
      res: int = self.find(stream)
      if res == 0: return 0
      if res != -1: return res
