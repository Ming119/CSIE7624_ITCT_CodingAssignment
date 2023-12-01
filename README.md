# 112-1 CSIE7624 ITCT Coding Assignment

#### R12944054 李浩銘

## Description
This is a simple JPEG baseline decoder implemented in pure Python. The program accepts a JPEG image as input, and outputs the decoded image in BMP format. The program is developed and tested on Ubuntu 20.04.6 LTS with Python 3.10.12 64-bit, and is not guaranteed to work on other platforms.

## Development Environment
- OS: Ubuntu 20.04.6 LTS
- Programming Language: Python 3.10.12 64-bit

## Requirements
This program is developed using pure Python, and the only package utilized is Pillow (PIL) for image output (refer to `requirements.txt`).
- Pillow (PIL) 10.1.0

## Installation
Use the following command to install the required dependencies:
``` bash
pip install -r requirements.txt
```
I highly recommend using a virtual environment to install the dependencies.
- Linux
  ``` bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

- Windows
  ``` bash
  python -m venv venv
  venv\Scripts\activate
  pip install -r requirements.txt
  ```


## Usage
The program accepts 1 to 2 arguments.
``` bash
python3 main.py <input_path> [<output_path>]
```
- `input_path`: Path to the input image. (required)
- `output_path`: Path to the output image. (optional)
- If `output_path` is not specified, the output image will be saved in the same directory as the input image, with the same name but different extension.

## Performance
Given the following images:
- `gig-sn01.jpg` (640x480)
- `gig-sn08.jpg` (640x480)
- `monalisa.jpg` (286x443)
- `teatime.jpg` (640x480)

The program takes the following time to decode the images:
| Image          | Time   |
| -------------- | ------ |
| `gig-sn01.jpg` | ~3.11s |
| `gig-sn08.jpg` | ~3.36s |
| `monalisa.jpg` | ~1.18s |
| `teatime.jpg`  | ~3.66s |

