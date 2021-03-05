import cv2
import getopt
import numpy as np
import sys

def render(input_path, output_path):
    factor = 30
    input_image = cv2.imread(input_path, cv2.IMREAD_COLOR)
    rows = input_image.shape[0]
    cols = input_image.shape[1]
    output_image = np.zeros((rows * factor, cols * factor, 3))

    empty = cv2.imread(".\empty.jpg")
    travelled = cv2.imread(".\\travelled.jpg")
    detected = cv2.imread(".\detected.jpg")
    expanded = cv2.imread(".\expanded.jpg")

    for i in range(input_image.shape[0]):
        for j in range(input_image.shape[1]):
            i_start = i * factor
            i_end = i_start + factor
            j_start = j * factor
            j_end = j_start + factor

            if (input_image[i][j][0] == 255):
                output_image[i_start:i_end, j_start:j_end:] = empty
            elif(input_image[i][j][0] == 0):
                output_image[i_start:i_end, j_start:j_end:] = detected
            elif(input_image[i][j][0] == 128):
                output_image[i_start:i_end, j_start:j_end:] = expanded
            elif(input_image[i][j][0] == 20):
                output_image[i_start:i_end, j_start:j_end:] = travelled
            else:
                print("Need mapping")

    cv2.imwrite(output_path, output_image)


def main(argv):
    try:
      opts, args = getopt.getopt(argv,"i:o:")
    except getopt.GetoptError:
      print("render.py -i <input> -p <output>")
      sys.exit(2)

    input_path = ".\drivingPath_simple.bmp"
    output_path = ".\\rendered simple routing.jpg"
    for opt, arg in opts:
        if opt == "-i":
            input_path = arg
        elif opt == "-o":
            output_path = arg

    render(input_path, output_path)
    
    return

if __name__ == '__main__':
    main(sys.argv[1:])