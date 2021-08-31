import Bezier
import numpy as np


# Makes a list of points to move along, based off key points. There are two options available:
# 1. Linear movement
# 2. Bezier curve movement
# The first one is basic movement, which is broken into local movement and extended to fit the 1 animation per frame
# format.
# The second option uses the Bezier class to calculate those points, which are then broken into local movement
# Why make those points into local movement? Well, it's more useful. You can't move the game object with a global
# point animation, but you can do that with a local movement animation.
def calculate_movement_points(t: int, key_points, curve_type: str):
    if curve_type == "LINE":
        movement_points = extend_linear_movement(
            global_points_to_local_movement(key_points), t
        )
        return movement_points
    elif curve_type == "BEZIER":
        # Create a numpy range for the bezier function
        t_points = np.arange(0, 1, 1 / t)
        # Transform the key points into a numpy array
        movement_points = np.array(key_points)
        # Apply the bezier curve function to the array
        movement_points = Bezier.curve(t_points, movement_points)
        # Transform the points into local movement
        movement_points = global_points_to_local_movement(movement_points)
        return movement_points


# Transforms global points into local movement.
# Example:
# global points = [[0, 0], [10, 30], [0, 20], [-10, 0], [0, 0]]
# local movement = [[0, 0], [10, 30], [-10, -10], [-10, -20], [10, 0]]
# Why make points into local movement? Well, it's more useful. You can't move the game object around with a global
# point animation, but you can do that with a local movement animation.
def global_points_to_local_movement(points):
    final_points = []

    # Loop through all points aside from the last one
    for point in range(len(points) - 1):
        next_point = []
        # Loop through all values inside the point (usually 2)
        for p in range(len(points[point])):
            # If both this point's value and the next point's value is an integer or a float
            if type(points[point][p]) in [int, float] and type(
                points[point + 1][p]
            ) in [int, float]:
                # We find the difference between them and save that value to next_point
                next_point.append(points[point + 1][p] - points[point][p])
            # Otherwise,
            else:
                # we simply append the next point's value to next_point.
                next_point.append(points[point + 1][p])
        # We then append next_point to the final list of movements
        final_points.append(next_point)
    # This effectively finds the difference between the next point and the current one for each of the points.
    return final_points


# Extends local movement linearly
# Example:
# points = [[0, 0], [10, 20], [20, -10], [-30, -10]]
# points extended by 2 = [[0, 0], [0, 0], [5, 10], [5, 10], [10, -5], [10, -5], [-15, -5], [-15, -5]]
# This makes animations slower and smoother.
# The t parameter corresponds to the desired final length of list of movements
def extend_linear_movement(points, t: int = 60):
    final_points = []

    # Find the extension number to divide and multiply by to achieve desired final list length
    # It must be an int, because we must multiply the lists of points by this number.
    time = int(t / len(points))

    # In case the desired list length is lower than current list length, we practically do nothing with the list.
    if time < 1:
        time = 1

    # Loop through the entire list of points
    for point in points:
        next_point = []
        # Loop through all the values of each point (usually 2)
        for p in point:
            # If we can divide that value,
            if type(p) in [int, float]:
                # we do, and append the result to the next_point list
                next_point.append(p / time)
            # Otherwise,
            else:
                # we simply append this value to next_point.
                next_point.append(p)
        # We then append next_point the number of times we divided it's contents
        final_points.append(
            [
                next_point,
            ]
            * time
        )

    return final_points


# Generates an empty animation shell
# Example:
# length = 3
# result = [Func(Events.animate_start, {'t': 1, 'before': TempGameObject(), 'after':
# Func(Events.animate_end, {'before': TempGameObject()})}), Func(Events.animate_start, {'t': 1, 'before':
# TempGameObject(), 'after': Func(Events.animate_end, {'before': TempGameObject()})}), Func(Events.animate_start,
# {'t': 1, 'before': TempGameObject(), 'after': Func(Events.animate_end, {'before': TempGameObject()})})]
# This makes an empty animation, usually used for converting movement points into correct animation format.
# Why use this? It's simply easier than typing it out yourself. Basically, syntax sugar.
def generate_empty_animations(length: int):
    # Return the empty (and useless) animation element layout times desired length.
    return [
               Func(
                   Events.animate_start,
                   {'t': 1, 'before': TempGameObject(), 'after': Func(Events.animate_end,
                                                                        {'before': TempGameObject()}
                                                                        )}
               ),
    ] * length


# Converts movement points into playable animations
# Example:
# points = [[10, 20], [20, -10], [-30, -10]]
# replaced_values = ['x', 'y']
# values__operations = ['+', '+']
# animations = ()
# returns ([1, TempGameObject(x=10, y=20, x_operation='+', y_operation='+'), TempGameObject()],
# [1, TempGameObject(x=20, y=-10, x_operation='+', y_operation='+'), TempGameObject()],
# [1, TempGameObject(x=-30, y=-10, x_operation='+', y_operation='+'), TempGameObject()])
# Why use this? It's just easier this way
def points_to_animation(points, replaced_values, values_operations, animations=()):
    # Convert tuple to a list because tuples are immutable
    animations = list(animations)
    # In case we don't have enough animations we generate just enough empty new ones
    if len(animations) < len(points):
        animations += generate_empty_animations(
            length=len(points) - len(animations)
        )

    # Go through the entire list of points
    for i in range(len(points)):
        # Go through each value of each element of points
        for j in range(len(points[i])):
            replaced_attribute = getattr(animations[i]['before'], replaced_values[j])
            value = GameObject.evaluate_operation_between_different_types(
                replaced_attribute, points[i][j], values_operations[j]
            )
            setattr(animations[i]['before'], replaced_values[j], value)
    # Convert back to tuple and return that
    return tuple(animations)
