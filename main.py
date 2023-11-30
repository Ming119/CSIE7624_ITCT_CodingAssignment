import sys
import numpy as np

def idct2d(input: np.ndarray) -> np.ndarray:
  l = image.shape[0]
  c = np.zeros((l, l))
  for k in range(l):
    for n in range(l):
      c[k, n] = np.sqrt(1/l) * np.cos(np.pi*k*(1/2+n)/l)
      if k != 0:
        c[k, n] *= np.sqrt(2)
  return (np.kron(c, c) @ input.flatten()).reshape((l, l))

def quantize(input: np.ndarray, q: np.ndarray) -> np.ndarray:
  return input // q

if __name__ == "__main__":
  if (len(sys.argv) != 2):
    print("Usage: python main.py <input>")
    exit(1)

  input = sys.argv[1]
  if (not input.endswith(".jpg") and not input.endswith(".jpeg")):
    print("Input file must be a JPEG image")
    exit(1)
  
  with open(input, "rb") as jpegfile:
    image = np.frombuffer(jpegfile.read(), dtype=np.uint8)
  