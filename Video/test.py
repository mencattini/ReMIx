"""Detect emotion from webacam stream."""
import time

import cv2
import dlib
import imutils
from imutils.video import VideoStream
from imutils import face_utils

from sklearn.externals import joblib
# from sklearn.svm import SVC

from featuregen import features_from_shape
# pylint: disable=E1101


if __name__ == '__main__':
    # emotion list
    EMOTIONS = ["anger",
                "disgust",
                "fear",
                "happy",
                "neutral",
                "sadness",
                "surprise"]
    # detector
    DETECTOR = dlib.get_frontal_face_detector()
    # predictor
    PREDICTOR = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    # classifier
    CLASSIFIER = joblib.load('classifier.pkl')

    # initialize the video stream and allow the cammera sensor to warmup
    print("[INFO] camera sensor warming up...")

    VIDEOSTREAM = VideoStream().start()
    time.sleep(2.0)

    EMOTION = 0

    # counter = 0

    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream, resize it to
        # have a maximum width of 400 pixels, and convert it to
        # grayscale
        FRAME = VIDEOSTREAM.read()
        FRAME = imutils.resize(FRAME, width=400)
        GRAY = cv2.cvtColor(FRAME, cv2.COLOR_BGR2GRAY)
        # detect faces in the grayscale frame
        RECTS = DETECTOR(GRAY, 0)

        # loop over the face detections
        for rect in RECTS:
            shape = PREDICTOR(GRAY, rect)
            vector = features_from_shape(shape)
            EMOTION = CLASSIFIER.predict([vector])[0]

            shape = face_utils.shape_to_np(shape)
            # loop over the (x, y)-coordinates for the facial landmarks
            # and draw them on the image
            for (x, y) in shape:
                cv2.circle(FRAME, (x, y), 1, (0, 0, 255), -1)
        # show the frame
        cv2.putText(FRAME,
                    EMOTIONS[EMOTION],
                    (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)

        cv2.imshow("Frame", FRAME)

        KEY = cv2.waitKey(1) & 0xFF
        if KEY == ord("q"):
            break

    # do a bit of cleanup
    cv2.destroyAllWindows()
    VIDEOSTREAM.stop()
