from typing import List

MARKERS: List = [
  "SOF0", "SOF1", "SOF2", "SOF3", "DHT", "SOF5", "SOF6", "SOF7",
  "JPG", "SOF9", "SOF10", "SOF11", "DAC", "SOF13", "SOF14", "SOF15",
  "RST0", "RST1", "RST2", "RST3", "RST4", "RST5", "RST6", "RST7",
  "SOI", "EOI", "SOS", "DQT", "DNL", "DRI", "DHP", "EXP",
  "APP0", "APP1", "APP2", "APP3", "APP4", "APP5", "APP6", "APP7",
  "APP8", "APP9", "APP10", "APP11", "APP12", "APP13", "APP14", "APP15",
  "JPG0", "JPG1", "JPG2", "JPG3", "JPG4", "JPG5", "JPG6", "JPG7",
  "JPG8", "JPG9", "JPG10", "JPG11", "JPG12", "JPG13", "COM", "TEM",
  "[Invalid Marker]"
]

subsample_mapping: dict = {
  "11": "4:4:4",
  "21": "4:2:2",
  "22": "4:2:0",
  "41": "4:1:1",
}