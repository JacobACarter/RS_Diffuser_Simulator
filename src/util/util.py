import cv2

# Returns a VideoCapture object for the given video path
def load_video(path="resources/video.mp4") -> cv2.VideoCapture | None:
    vid = cv2.VideoCapture(path)

    if not vid.isOpened():
        print("Error opening video stream or file")
        return None
    
    if vid.get(cv2.CAP_PROP_FPS) <= 0:
        print("Error: Video FPS must be > 0")
        return None
    
    if vid.get(cv2.CAP_PROP_FRAME_COUNT) <= 0:
        print("Error: Video frame count must be > 0")
        return None
    
    if vid.get(cv2.CAP_PROP_FRAME_WIDTH) <= 0 or vid.get(cv2.CAP_PROP_FRAME_HEIGHT) <= 0:
        print("Error: Video dimensions must be > 0")
        return None

    return vid

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