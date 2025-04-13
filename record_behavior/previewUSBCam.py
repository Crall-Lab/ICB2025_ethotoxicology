import cv2


def preview_webcam():
    # Initialize the USB webcam
    webcam = cv2.VideoCapture(0)

    while True:
        # Read a frame from the webcam
        ret, frame = webcam.read()

        # Display the frame in a window named "Webcam Preview"
        cv2.imshow("Webcam Preview", frame)

        # Wait for the user to press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close all windows
    webcam.release()
    cv2.destroyAllWindows()

# Call the function to start the webcam preview
preview_webcam()
