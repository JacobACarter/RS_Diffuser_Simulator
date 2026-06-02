import cv2

# Returns a VideoCapture object for the given video path
def load_video(path="resources/video.mp4") -> cv2.VideoCapture:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print("Error opening video stream or file")
        return None
    return cap

if __name__ == "__main__":
    print("Running utility functions...")