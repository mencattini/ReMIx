"""Main entry point for video stream."""
import multiprocessing

import cv2
import dlib
import imutils
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np

from sklearn.externals import joblib
# from sklearn.svm import SVC
from Video.featuregen import features_from_shape
# pylint: disable = E1101, R0902
from Video.constants import EMOTIONS

# Emotion list
EMOTIONS = ["anger",
            "disgust",
            "fear",
            "happy",
            "neutral",
            "sadness",
            "surprise"]


class VideoEmotion(multiprocessing.Process):
    """Simple process to extract facial emotion."""

    def __init__(self, classifier, shared_value, flag, demo=False):
        """Initialize class."""
        multiprocessing.Process.__init__(self)
        self.shared = shared_value
        self.flag = flag
        self.demo = demo
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(
            "Video/shape_predictor_68_face_landmarks.dat")
        self.classifier = joblib.load(classifier)
        self.emotion = 4
        self.video_stream = None
        self.exit = multiprocessing.Event()

    def run(self):
        """Exec the process to identify the emotion in real time."""
        self.video_stream = VideoStream().start()
        frames = []
        n_frames = 100
        while not self.exit.is_set():
            frame = self.video_stream.read()
            frame = imutils.resize(frame, width=400)
            # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frames.append(frame)
            if len(frames) == n_frames:
                super_frame = cv2.addWeighted(
                    frames[0], 0.5, frames[1], 0.5, 0)
                for i in range(2, n_frames):
                    super_frame = cv2.addWeighted(
                        super_frame, 0.5, frames[i], 0.5, 0)
                frames = []
                gray = cv2.cvtColor(super_frame, cv2.COLOR_BGR2GRAY)
                # detect faces in the grayscale frame
                rects = self.detector(gray, 0)

                # loop over the face detections
                for rect in rects:
                    shape = self.predictor(gray, rect)
                    vector = features_from_shape(shape)
                    self.emotion = self.classifier.predict([vector])[0]

                    shape = face_utils.shape_to_np(shape)
                    # loop over the (x, y)-coordinates for the facial landmarks
                    # and draw them on the image
                    for (cor_x, cor_y) in shape:
                        cv2.circle(super_frame,
                                   (cor_x, cor_y), 1, (0, 0, 255), -1)
                if self.demo:
                    if np.random.rand() > 0.8:
                        self.shared.value = np.random.randint(0, len(EMOTIONS))
                else:
                    self.shared.value = self.emotion
                self.flag.value = True

                # show the frame
                cv2.putText(super_frame,
                            EMOTIONS[self.emotion],
                            (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)

                cv2.imshow("Frame", super_frame)

        # do a bit of cleanup
        cv2.destroyAllWindows()
        self.video_stream.stop()

    def shutdown(self):
        """Way to be notified when the process needs to stop."""
        self.exit.set()


if __name__ == "__main__":
    SH_VALUE = multiprocessing.Value('d', 4.0)
    FLAG_VALUE = multiprocessing.Value('b', 4.0)
    VIDEO = VideoEmotion(classifier="classifier.pkl",
                         shared_value=SH_VALUE, flag=FLAG_VALUE)
    VIDEO.run()
