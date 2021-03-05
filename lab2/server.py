if __name__ == '__main__':
    main(sys.argv[1:])

    Initialize PiCamera
    Initialize TensorFlow Interpreter
    while moving:
        Get a frame from PiCamera
        Detect objects in the frame using TensorFlow
        if (stop sign detected):
            stop
        