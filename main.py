import sys
import numpy as np

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
  
  print(image)
  print(image.shape)
