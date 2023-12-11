import cv2

# Ask the user for the path to the AVI file
avi_file_path = input("Enter the full path to the AVI file: ")

# Open the AVI file
cap = cv2.VideoCapture(avi_file_path)

# Ask the user for the frame number
frame_number = int(input("Enter the frame number: "))

# Set the current frame position
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

# Read the frame
ret, frame = cap.read()

# If the frame was read successfully, save it as a PNG
if ret:
    # Save the frame as a PNG image
    cv2.imwrite('G:\\My Drive\\Research\\ThermalImaging\\FrustratedPlumesPaper\\Figures\\FinalFigures\\framerip.png', frame)

# Release the VideoCapture
cap.release()
