import getopt
import picar_4wd as fc

def get_distance_from_ultrasonic(angle):
    print("detecting distance at ", angle, " degree")
    distance = fc.get_distance_at(angle)
    print("Object is ", distance, "cm away")

def main(argv):
    try:
      opts, args = getopt.getopt(argv,"f:p:")
    except getopt.GetoptError:
      print("test.py -f <function> -p <paramter>")
      sys.exit(2)

    for opt, arg in opts:
        if opt == "-f":
            test_function = arg
        elif opt == "-p":
            paramter = arg

    if test_function == "ultrasonic":
        get_distance_from_ultrasonic(paramter)

    return


if __name__ == '__main__':
    main(sys.argv[1:])