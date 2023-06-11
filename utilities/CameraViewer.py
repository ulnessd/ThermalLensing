import cv2
from pylablib.devices import uc480

# List all cameras for the uc480 backend
camera_list = uc480.list_cameras(backend="uc480")
print(camera_list)

# Connect to the first available camera
cam = uc480.UC480Camera(backend="uc480")

# Set up the camera (configure exposure time, gain, etc.)
cam.set_exposure(100)  # Set exposure time in microseconds
cam.set_gains(1.0)  # Set gain

# Start the acquisition
cam.start_acquisition()

# Create a named window to display the images
window_name = 'Thorlabs Camera'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# Continuously capture and display images until the 'ESC' key is pressed
while True:
    image_data = cam.snap()

    # Convert the grayscale image to BGR
    image_data = cv2.cvtColor(image_data, cv2.COLOR_GRAY2BGR)

    # Add the text to the image
    cv2.putText(image_data, 'Hit ESC to exit', (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow(window_name, image_data)

    # Break the loop if the 'ESC' key is pressed
    if cv2.waitKey(1) == 27:
        break

# Release resources and close the window
cam.stop_acquisition()
cam.close()
cv2.destroyAllWindows()
