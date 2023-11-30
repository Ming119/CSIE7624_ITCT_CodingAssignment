import numpy as np

zigzag: np.ndarray = np.array([
   0,  1,  5,  6, 14, 15, 27, 28,
   2,  4,  7, 13, 16, 26, 29, 42,
   3,  8, 12, 17, 25, 30, 41, 43,
   9, 11, 18, 24, 31, 40, 44, 53,
  10, 19, 23, 32, 39, 45, 52, 54,
  20, 22, 33, 38, 46, 51, 55, 60,
  21, 34, 37, 47, 50, 56, 59, 61,
  35, 36, 48, 49, 57, 58, 62, 63
]).reshape((8, 8))

marker_mapping: dict = {
  0xFFD8: "Start of Image (SOI)",
  0xFFE0: "Application Segment 0 (APP0)",
  0xFFDB: "Define Quantization Table (DQT)",
  0xFFC0: "Start of Frame (SOF0)",
  0xFFC4: "Define Huffman Table (DHT)",
  0xFFDA: "Start of Scan (SOS)",
  0xFFD9: "End of Image (EOI)",
  
  0xFFFE: "Comment (COM)",
}

subsample_mapping: dict = {
  "11": "4:4:4",
  "21": "4:2:2",
  "22": "4:2:0",
  "41": "4:1:1",
}

def decodeNumber(code, bits):
  l = 2 ** (code - 1)
  if bits >= l: return bits
  return bits - (2 * l - 1)
