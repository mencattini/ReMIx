"""SVC training for 7 emotions."""
import glob
import random

import cv2
import numpy as np
import dlib

from sklearn.svm import SVC
from sklearn.externals import joblib

from featuregen import features_from_shape


# emotion list
EMOTIONS = ["anger",
            "disgust",
            "fear",
            "happy",
            "neutral",
            "sadness",
            "surprise"]

# cache
CACHE = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
# detector
DETECTOR = dlib.get_frontal_face_detector()
# predictor
PREDICTOR = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Set the classifier as a support vector machines with polynomial kernel
CLASSIFIER = SVC(C=10, kernel='linear')


def get_files(emotion):
    """Define function to get file list, shuffle it and split 80/20."""
    files = glob.glob("dataset/sorted_set/%s/*" % emotion)
    random.shuffle(files)
    training = files
    return training


def get_landmarks(image):
    """Get facial landmarks."""
    detections = DETECTOR(image, 1)
    for _, detected in enumerate(detections):
        shape = PREDICTOR(image, detected)
        landmarks_vectorised = features_from_shape(shape)

    if len(detections) < 1:
        landmarks_vectorised = "error"
    return landmarks_vectorised


def make_sets():
    """Build training and predcition set."""
    data = []
    labels = []
    for emotion in EMOTIONS:
        training = get_files(emotion)
        # Append data to training and prediction list, and generate labels 0-7
        for item in training:
            image = cv2.imread(item)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            clahe_image = CACHE.apply(gray)
            landmarks_vectorised = get_landmarks(clahe_image)
            if landmarks_vectorised == "error":
                pass
            else:
                data.append(landmarks_vectorised)
                labels.append(EMOTIONS.index(emotion))

    return data, labels


print("Making sets ")

DATA, LABELS = make_sets()

for i in range(0, 10):
    npar_train = np.array(DATA)
    npar_trainlabs = np.array(LABELS)
    print("training SVM linear %d" % i)
    CLASSIFIER.fit(npar_train, npar_trainlabs)

joblib.dump(CLASSIFIER, 'classifier.pkl')
