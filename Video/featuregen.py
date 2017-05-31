"""Generate features."""
import math
import itertools
import numpy


def features_from_shape(shape):
    """Return features from shape."""
    landmarks = []
    for i in range(68):
        landmarks.append(shape.part(i).x)
        landmarks.append(shape.part(i).y)

    landmarks = numpy.array(landmarks)

    features = generate_features(landmarks)
    return numpy.asarray(features)


def find_ratio(points):
    """Find landmark ratios."""
    x_coor = [0] * 4
    y_coor = [0] * 4
    for i in range(4):
        x_coor[i] = points[(2 * i)]
        y_coor[i] = points[(2 * i) + 1]

    dist1 = math.sqrt((x_coor[0] - x_coor[1])**2 + (y_coor[0] - y_coor[1])**2)
    dist2 = math.sqrt((x_coor[2] - x_coor[3])**2 + (y_coor[2] - y_coor[3])**2)
    if dist2 == 0:
        return 0
    ratio = dist1 / dist2

    return ratio


# pylint: disable = R0914
def generate_features(landmark_coords):
    """Generate features from landmarks."""
    key_points = [18, 22, 23, 27, 37, 40, 43, 46, 28, 32,
                  34, 36, 5, 9, 13, 49, 55, 52, 58, 61, 63, 65, 67]
    combinations = itertools.combinations(key_points, 4)
    point1 = []
    point2 = []
    point3 = []
    point4 = []

    for combination in combinations:
        point1.append(combination[0])
        point2.append(combination[1])
        point3.append(combination[2])
        point4.append(combination[3])

        point1.append(combination[0])
        point2.append(combination[2])
        point3.append(combination[1])
        point4.append(combination[3])

        point1.append(combination[0])
        point2.append(combination[3])
        point3.append(combination[1])
        point4.append(combination[2])

    features = numpy.zeros((1, len(point1)))
    ratios = []

    for i in range(0, len(point1)):
        x_1 = landmark_coords[2 * (point1[i] - 1)]
        y_1 = landmark_coords[2 * point1[i] - 1]
        x_2 = landmark_coords[2 * (point2[i] - 1)]
        y_2 = landmark_coords[2 * point2[i] - 1]

        x_3 = landmark_coords[2 * (point3[i] - 1)]
        y_3 = landmark_coords[2 * point3[i] - 1]
        x_4 = landmark_coords[2 * (point4[i] - 1)]
        y_4 = landmark_coords[2 * point4[i] - 1]

        points = [x_1, y_1, x_2, y_2, x_3, y_3, x_4, y_4]
        ratios.append(find_ratio(points))

    features = numpy.asarray(ratios)

    return features
