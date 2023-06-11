import cv2

# Trackbar callback function
def on_trackbar(val):
    cap.set(cv2.CAP_PROP_POS_FRAMES, val)

# Open the video file
cap = cv2.VideoCapture('output0.avi')

# Get the total frames
frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Create a named window
cv2.namedWindow('Video Viewer', cv2.WINDOW_NORMAL)

# Create trackbar/slider
cv2.createTrackbar('Frame', 'Video Viewer', 0, frames - 1, on_trackbar)

# Window size (you can set it according to your preference)
cv2.resizeWindow('Video Viewer', 800, 600)

# State variable for play/pause functionality
play = True

while True:
    if play:
        ret, frame = cap.read()

        if not ret:
            break

        # Add text overlay to the frame
        cv2.putText(frame, "Press 'p' to Pause/Play", (180, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, "Press 'Esc' to exit", (600, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        # Display the frame
        cv2.imshow('Video Viewer', frame)

        # Update the position of the trackbar
        position = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        cv2.setTrackbarPos('Frame', 'Video Viewer', position)

    # Check for user input
    key = cv2.waitKey(1)
    if key & 0xFF == 27:  # Exit if ESC key is pressed
        break
    elif key == ord('p'):  # Play/Pause toggle
        play = not play

# Release everything and destroy window
cap.release()
cv2.destroyAllWindows()
