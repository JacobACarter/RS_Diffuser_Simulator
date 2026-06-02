import cv2

# Returns a VideoCapture object for the given video path
def load_video(path="resources/video.mp4") -> cv2.VideoCapture:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print("Error opening video stream or file")
        return None
    return cap

# Returns the properties of the video as a dictionary
def get_video_properties(vid: cv2.VideoCapture):
    width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = vid.get(cv2.CAP_PROP_FPS)
    frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    
    properties = {
        "width": width,
        "height": height,
        "fps": fps,
        "frames": frames
    }
    return properties

if __name__ == "__main__":
    print("Running utility functions...")