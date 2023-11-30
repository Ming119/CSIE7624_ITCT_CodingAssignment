import sys
import matplotlib.pyplot as plt

from JPEG import JPEG

if __name__ == "__main__":
  if (len(sys.argv) != 2):
    print("Usage: python main.py <input>")
    exit(1)

  input = sys.argv[1]
  if (not input.endswith(".jpg") and not input.endswith(".jpeg")):
    print("Input file must be a JPEG image")
    exit(1)
  
  jpeg = JPEG(input)
  jpeg.decode()
  plt.imsave("out.png", jpeg.decodeedImage)
