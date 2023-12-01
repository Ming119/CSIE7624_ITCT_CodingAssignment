import sys
import timeit

from modules.JPEG import JPEG

if __name__ == "__main__":
  if (len(sys.argv) < 2):
    print("Usage: python main.py <input>")
    exit(1)

  input_path = sys.argv[1]
  output_path = sys.argv[2] if len(sys.argv) > 2 else None
  if (not input_path.endswith(".jpg") and not input_path.endswith(".jpeg")):
    print("Input file must be a JPEG image")
    exit(1)
  
  start = timeit.default_timer()
  jpeg = JPEG(input_path, output_path)
  jpeg.decode()
  stop = timeit.default_timer()
  print("Decoding time: ", stop - start)
