import numpy as np


def two_points(t, p1, p2):
    if not isinstance(p1, np.ndarray) or not isinstance(p2, np.ndarray):
        raise TypeError("Points must be an instance of the numpy.ndarray!")
    if not isinstance(t, (int, float)):
        raise TypeError("Parameter t must be an int or float!")

    q1 = (1 - t) * p1 + t * p2
    return q1


def get_points(t, points):
    new_points = []
    for i in range(0, len(points) - 1):
        new_points += [two_points(t, points[i], points[i + 1])]
    return new_points


def get_point(t, points):
    while len(points) > 1:
        points = get_points(t, points)
    return points[0]


def curve(t_values, points):
    if not hasattr(t_values, "__iter__"):
        raise TypeError(
            "`t_values` Must be an ITERABLE of integers or floats, of length greater than 0 ."
        )
    if len(t_values) < 1:
        raise TypeError(
            "`t_values` Must be an iterable of integers or floats, of LENGTH greater than 0 ."
        )
    if not isinstance(t_values[0], (int, float)):
        raise TypeError(
            "`t_values` Must be an iterable of INTEGERS OR FLOATS, of length greater than 0 ."
        )

    curve = np.array([[0.0] * len(points[0])])
    for t in t_values:
        curve = np.append(curve, [get_point(t, points)], axis=0)
    curve = np.delete(curve, 0, 0)

    curve = curve.tolist()

    return curve
