import numpy as np
import pygame
import math


# Class for bezier curves. It's math and I'm too bored to explain it.
class Bezier:
    @staticmethod
    def two_points(t, p1, p2):
        if not isinstance(p1, np.ndarray) or not isinstance(p2, np.ndarray):
            raise TypeError('Points must be an instance of the numpy.ndarray!')
        if not isinstance(t, (int, float)):
            raise TypeError('Parameter t must be an int or float!')

        q1 = (1 - t) * p1 + t * p2
        return q1

    @staticmethod
    def points(t, points):
        new_points = []
        for i in range(0, len(points) - 1):
            new_points += [Bezier.two_points(t, points[i], points[i + 1])]
        return new_points

    @staticmethod
    def point(t, points):
        while len(points) > 1:
            points = Bezier.points(t, points)
        return points[0]

    @staticmethod
    def curve(t_values, points):
        if not hasattr(t_values, '__iter__'):
            raise TypeError("`t_values` Must be an ITERABLE of integers or floats, of length greater than 0 .")
        if len(t_values) < 1:
            raise TypeError("`t_values` Must be an iterable of integers or floats, of LENGTH greater than 0 .")
        if not isinstance(t_values[0], (int, float)):
            raise TypeError("`t_values` Must be an iterable of INTEGERS OR FLOATS, of length greater than 0 .")

        curve = np.array([[0.0] * len(points[0])])
        for t in t_values:
            curve = np.append(curve, [Bezier.point(t, points)], axis=0)
        curve = np.delete(curve, 0, 0)
        return curve


# Class for animations
class Animation:
    # Makes a list of points to move along, based off key points. There are two options available:
    # 1. Linear movement
    # 2. Bezier curve movement
    # The first one is basic movement, which is broken into local movement and extended to fit the 1 animation per frame
    # format.
    # The second option uses the Bezier class to calculate those points, which are then broken into local movement
    # Why make those points into local movement? Well, it's more useful. You can't move the game object with a global
    # point animation, but you can do that with a local movement animation.
    @staticmethod
    def calculate_movement_points(t, key_points, curve_type):
        if curve_type == "LINE":
            movement_points = Animation.extend_linear_movement(Animation.global_points_to_local_movement(key_points), t)
            return movement_points
        elif curve_type == "BEZIER":
            # Create a numpy range for the bezier function
            t_points = np.arange(0, 1, 1 / t)
            # Transform the key points into a numpy array
            movement_points = np.array(key_points)
            # Apply the bezier curve function to the array
            movement_points = Bezier.curve(t_points, movement_points)
            # Transform the points into local movement
            movement_points = Animation.global_points_to_local_movement(movement_points)
            return movement_points

    # Transforms global points into local movement.
    # Example:
    # global points = [[0, 0], [10, 30], [0, 20], [-10, 0], [0, 0]]
    # local movement = [[0, 0], [10, 30], [-10, -10], [-10, -20], [10, 0]]
    # Why make points into local movement? Well, it's more useful. You can't move the game object around with a global
    # point animation, but you can do that with a local movement animation.
    @staticmethod
    def global_points_to_local_movement(points):
        final_points = []

        # Loop through all points aside from the last one
        for point in range(len(points) - 1):
            next_point = []
            # Loop through all values inside the point (usually 2)
            for p in range(len(points[point])):
                # If both this point's value and the next point's value is an integer or a float
                if type(points[point][p]) in [int, float] and type(points[point + 1][p]) in [int, float]:
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
    @staticmethod
    def extend_linear_movement(points, t=60):
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
            final_points.append([next_point, ] * time)

        return final_points

    # Generates an empty animation shell
    # Example:
    # length = 3
    # result = [[1, TempGameObject(), TempGameObject()], [1, TempGameObject(), TempGameObject()],
    # [1, TempGameObject(), TempGameObject()]]
    # This makes an empty animation, usually used for converting movement points into correct animation format.
    # Why use this? It's simply easier than typing it out yourself. Basically, syntax sugar.
    @staticmethod
    def generate_empty_animations(length):
        # Return the empty (and useless) animation element layout times desired length.
        return [[1, TempGameObject(), TempGameObject()], ] * length

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
    @staticmethod
    def points_to_animation(points, replaced_values, values_operations, animations=()):
        # Convert tuple to a list because tuples are immutable
        animations = list(animations)
        # In case we don't have enough animations we generate just enough empty new ones
        if len(animations) < len(points):
            animations += Animation.generate_empty_animations(length=len(points) - len(animations))

        # Go through the entire list of points
        for i in range(len(points)):
            # Go through each value of each element of points
            for j in range(len(points[i])):
                replaced_attribute = getattr(animations[i][1], replaced_values[j])
                value = GameObject.calculate_operations(replaced_attribute, points[i][j], values_operations[j])
                setattr(animations[i][1], replaced_values[j], value)
        # Convert back to tuple and return that
        return tuple(animations)


# This class is applied to any object of the game. It has the abilities of a player, anything static, anything moving,
# basically any object you would need for your game.
class GameObject(object):
    # Initiates the object
    # Variables:

    # x: x coordinate of the object

    # y: y coordinate of the object

    # width: width of the object

    # height: height of the object

    # x_offset: the offset, in pixels, from the actual x coordinate to where the object will be displayed. Useful for
    # keeping the hitbox the same while moving the sprite around.

    # y_offset: the offset, in pixels, from the actual y coordinate to where the object will be displayed. Useful for
    # keeping the hitbox the same while moving the sprite around.

    # width_offset: the offset, in pixels, from the actual width of object, to how wide the object will be displayed.
    # Useful for keeping the hitbox the same while making the sprite expand and shrink.

    # height_offset: the offset, in pixels, from the actual height of object, to how high the object will be displayed.
    # Useful for keeping the hitbox the same while making the sprite expand and shrink.

    # angle: The angle at which the image or rectangle will be displayed at. Useful for... Making a sprite rotate.

    # controls: which keys can be pressed to control the object. Useful for making a player object.

    # pressed_controls: the bridge between pressing a key and moving the player. When value of an element is set to
    # True, it will move the player accordingly. The default directions are UP, LEFT, DOWN, RIGHT

    # speed: how much the player will move in each direction per frame, when pressed_controls are True accordingly

    # icon: the icon of the object. Any image. Will be displayed according to width and height of the object.

    # color: the color of the object, in case it doesn't have an icon. If there is no icon, a rectangle of this color
    # will be displayed instead

    # sound: the sound which the object will play every second. Only useful if very indiscreet or quiet, OR when used
    # in "animations".

    # animations: a tuple, containing lists of recurring temporal variable changes. This can include: x, y, width,
    # height, x_offset, etc.; ALL the variables of the object. They rely on counters for their functionality.

    # counters: a tuple, containing objects of class Counter. Count down each second. Very useful while simple. Can hold
    # an additional value to help animations,
    def __init__(self, x=0, y=0, width=10, height=10, x_offset=0, y_offset=0, width_offset=0, height_offset=0,
                 x_offset_op='+', y_offset_op='+', width_offset_op='+', height_offset_op='+',
                 angle=0, rotation_mode='Idk', hit_box=(), origin=(),
                 controls=(None, None, None, None), pressed_controls=(False, False, False, False), speed=(1, 1, 1, 1),
                 icon=None, color=(255, 0, 0), sound=None,
                 animations=(), counters=()):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.width_offset = width_offset
        self.height_offset = height_offset

        self.x_offset_op = x_offset_op
        self.y_offset_op = y_offset_op
        self.width_offset_op = width_offset_op
        self.height_offset_op = height_offset_op

        if not hit_box:
            self.hit_box = (
                (
                    GameObject.evaluate_operation(self.x, self.x_offset, self.x_offset_op),
                    GameObject.evaluate_operation(self.y, self.y_offset, self.y_offset_op)
                ),
                (
                    GameObject.evaluate_operation(self.x, self.x_offset, self.x_offset_op),
                    GameObject.evaluate_operation(self.y, self.y_offset, self.y_offset_op) +
                    GameObject.evaluate_operation(self.height, self.height_offset, self.height_offset_op)
                ),
                (
                    GameObject.evaluate_operation(self.x, self.x_offset, self.x_offset_op) +
                    GameObject.evaluate_operation(self.width, self.width_offset, self.width_offset_op),
                    GameObject.evaluate_operation(self.y, self.y_offset, self.y_offset_op) +
                    GameObject.evaluate_operation(self.height, self.height_offset, self.height_offset_op)
                ),
                (
                    GameObject.evaluate_operation(self.x, self.x_offset, self.x_offset_op) +
                    GameObject.evaluate_operation(self.width, self.width_offset, self.width_offset_op),
                    GameObject.evaluate_operation(self.y, self.y_offset, self.y_offset_op)
                ),
            )
        else:
            self.hit_box = hit_box
        if not origin:
            self.origin = (self.x, self.y)
        else:
            self.origin = origin

        self.angle = angle
        self.rotation_mode = rotation_mode

        # Controls can be of any length due to how the checking of events is done,
        self.controls = controls
        # and thus, this construction is needed
        # If the passed in pressed_controls aren't a tuple or a list (which they always should be)
        if type(pressed_controls) not in (tuple, list):
            # And if controls ARE a tuple or a list,
            if type(controls) in (tuple, list):
                # We make a list of the same length than that of controls.
                self.pressed_controls = [False, ] * len(controls)
            # And if controls aren't a tuple nor a list,
            else:
                # we make pressed_controls an empty list instead.
                self.pressed_controls = []
        # if they ARE a tuple or a list, we make them a list (because it's easier that way to change them)
        else:
            self.pressed_controls = list(pressed_controls)
        self.speed = speed

        self.icon = icon
        self.color = color
        self.sound = sound

        self.animations = animations
        # play_animation is used for animations only (recurring temporal variable changes). It makes the selected
        # animation play only once until the next animation comes. This is extremely important.
        self.play_animation = True
        self.counters = counters

    # Method to update the game object. Mostly useful for player movement, counters and animation. Should be called
    # every frame for each game object.
    def update(self):
        self.move_rotated()
        self.evaluate_boxes()
        self.update_counters()
        self.animate()

    def move(self):
        # Useful for player (and not only player) movement. If we actually have a non-empty pressed_controls list,
        # we will do the following:
        if self.pressed_controls:
            # Try moving the player according to UP, LEFT, DOWN, RIGHT controls
            try:
                if self.pressed_controls[0]:
                    self.y -= self.speed[0]
                if self.pressed_controls[1]:
                    self.x -= self.speed[1]
                if self.pressed_controls[2]:
                    self.y += self.speed[2]
                if self.pressed_controls[3]:
                    self.x += self.speed[3]
            # If the list is for whatever reason less than 4 elements long, we just ignore that error.
            except IndexError:
                pass
            # Or if the object is actually Temporary Game object, and some of the used variables are empty strings, we
            # just ignore that error.
            except TypeError:
                pass

    def move_rotated(self):
        if self.pressed_controls:
            # Try moving the player according to UP, LEFT, DOWN, RIGHT controls
            try:
                cos = math.cos(self.angle / 180 * math.pi)
                sin = math.sin(self.angle / 180 * math.pi)
                if self.pressed_controls[0]:
                    self.x -= sin * self.speed[0]
                    self.y -= cos * self.speed[0]
                if self.pressed_controls[1]:
                    self.x -= cos * self.speed[3]
                    self.y += sin * self.speed[3]
                if self.pressed_controls[2]:
                    self.x += sin * self.speed[2]
                    self.y += cos * self.speed[2]
                if self.pressed_controls[3]:
                    self.x += cos * self.speed[3]
                    self.y -= sin * self.speed[3]
            # If the list is for whatever reason less than 4 elements long, we just ignore that error.
            except IndexError:
                pass
            # Or if the object is actually Temporary Game object, and some of the used variables are empty strings, we
            # just ignore that error.
            except TypeError:
                pass

    def evaluate_boxes(self):
        x = GameObject.evaluate_operation(self.x, self.x_offset, self.x_offset_op)
        y = GameObject.evaluate_operation(self.y, self.y_offset, self.y_offset_op)
        width = GameObject.evaluate_operation(self.width, self.width_offset, self.width_offset_op)
        height = GameObject.evaluate_operation(self.height, self.height_offset, self.height_offset_op)

        origin = (x, y)
        if self.rotation_mode == 'AROUND':
            box = [pygame.math.Vector2(p) for p in [(0, 0), (width, 0), (width, -height), (0, -height)]]
            box_rotate = [p.rotate(self.angle) for p in box]
            min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
            max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])
            origin = (x + min_box[0], y - max_box[1])
            self.hit_box = (
                (x + box_rotate[0][0], y + box_rotate[0][1] * -1),
                (x + box_rotate[1][0], y + box_rotate[1][1] * -1),
                (x + box_rotate[2][0], y + box_rotate[2][1] * -1),
                (x + box_rotate[3][0], y + box_rotate[3][1] * -1),
            )
        elif self.rotation_mode == 'CENTER':
            box = [pygame.math.Vector2(p) for p in [
                (0, 0),
                (width, 0),
                (width, -height),
                (0, -height)
            ]]
            box_rotate = [p.rotate(self.angle) for p in box]

            min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
            max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])

            pivot = pygame.math.Vector2(width / 2, -height / 2)
            pivot_rotate = pivot.rotate(self.angle)
            pivot_move = pivot_rotate - pivot

            origin = (
                x + min_box[0] - pivot_move[0],
                y - max_box[1] + pivot_move[1]
            )

            or1x = origin[0] + box_rotate[0][0]
            or1y = origin[1] + box_rotate[0][1] * -1

            if self.angle // 90 % 2 != 0:
                width, height = height, width
                angle_sin = math.sin((self.angle - 90) / 180 * math.pi)
                angle_cos = math.cos((self.angle - 90) / 180 * math.pi)
            else:
                angle_sin = math.sin(self.angle / 180 * math.pi)
                angle_cos = math.cos(self.angle / 180 * math.pi)
            angle_sin = abs(angle_sin)
            angle_cos = abs(angle_cos)
            point1 = (
                or1x,
                or1y + angle_sin * width
            )
            point2 = (
                or1x + angle_cos * width,
                or1y
            )
            point3 = (
                or1x + angle_cos * width + angle_sin * height,
                or1y + angle_cos * height
            )
            point4 = (
                or1x + angle_sin * height,
                or1y + angle_sin * width + angle_cos * height
            )
            self.hit_box = (
                point1,
                point2,
                point3,
                point4
            )
        else:
            if self.angle // 90 % 2 != 0:
                width, height = height, width
                angle_sin = math.sin((self.angle - 90) / 180 * math.pi)
                angle_cos = math.cos((self.angle - 90) / 180 * math.pi)
            else:
                angle_sin = math.sin(self.angle / 180 * math.pi)
                angle_cos = math.cos(self.angle / 180 * math.pi)
            angle_sin = abs(angle_sin)
            angle_cos = abs(angle_cos)
            point1 = (
                x,
                y + angle_sin * width
            )
            point2 = (
                x + angle_cos * width,
                y
            )
            point3 = (
                x + angle_cos * width + angle_sin * height,
                y + angle_cos * height
            )
            point4 = (
                x + angle_sin * height,
                y + angle_sin * width + angle_cos * height
            )
            self.hit_box = (
                point1,
                point2,
                point3,
                point4
            )

        self.origin = origin

    def update_counters(self):
        # If we have any current counters, we do the following
        if self.counters:
            for counter in self.counters:
                # We update the counter
                counter.update()
                # If this counter is actually used by temporary_variable_change, and has already reached one of it's
                # limits, we do the following
                if (counter.count == counter.range[0] or counter.count == counter.range[1]) and type(
                        counter.value) == TempGameObject:
                    # Assign it's value to a temporary variable c for simplicity
                    c = counter.value
                    # Change this object's variables according to c
                    GameObject.change_variables(self, c)

                    # If this was actually all part of our animations list, we make the animations progress
                    for sublist in self.animations:
                        if c in sublist:
                            self.play_animation = True

                    # If our counters variable hasn't been changed by c, and we still have counter in our counters
                    if counter in self.counters and c.counters == '':
                        # We convert counters to a temporary list
                        counters = list(self.counters)
                        # We remove the counter from our temporary list
                        counters.remove(counter)
                        # We convert our temporary list back to a tuple and assign our counters to it
                        self.counters = tuple(counters)
                        # We then delete the now useless object counter. I don't know if this is needed, or if python's
                        # garbage collector would've cleaned it up the same regardless.
                        del counter
                    # We then delete the now useless object c. I don't know if this is needed, or if python's
                    # garbage collector would've cleaned it up the same regardless.
                    del c

    def animate(self):
        # If we do have current animations (which, if we ever have animations, and none of our animations change our
        # animations, we always should have), we do the following
        if self.animations:
            # If it's time to play the animation, we do the following
            if self.play_animation:
                # Our animation is always the first animation in a list, because it's easy that way, without having to
                # keep track of an additional variable.
                # We call the function to temporarily change our variables, with time being as the first element of our
                # animation element list, the immediate variable change as second element of our animation, and the
                # change after counter ticks down as third element of our animation.
                self.temporarily_change_variables(t=self.animations[0][0], before=self.animations[0][1],
                                                  after=self.animations[0][2])
                # We then set the animation to not play anymore.
                self.play_animation = False
                # And if our animations haven't been overwritten by our animation already to contain nothing,
                if self.animations:
                    # We make them into a temporary list to make them mutable
                    animations = list(self.animations)
                    # We move the first element o the last element
                    animations.insert(len(animations), animations.pop(0))
                    # We make that temporary list into a tuple and set out animations to it
                    self.animations = tuple(animations)

    # Function to temporarily change object variables. Any of them.
    # t is time, in frames, for how long the counter will last. At the end of the counter, this game object will be
    # assigned values from after. At the immediate start of the timer, it will be assigned values from before.
    def temporarily_change_variables(self, t, before, after):
        # We make the temporary game object initialized, so it can update. It won't update unless you intentionally
        # update it.
        after.initialized = True
        # We make a counter for the value after, which will tick down after t frames.
        after_counter = Counter(count=t, change_range=[0, t + 1], change_per_second=1, value=after)
        # We change our variables with the object before
        GameObject.change_variables(self, before)
        # And discard it because we don't need it anymore.
        del before

        # If we don't have that counter in our counters, we add it to our counters.
        # How would we even have that counter in our counters? Well, that's in case before changed our counters to
        # include this exact timer, for whatever reason.
        if after_counter not in self.counters:
            self.counters = self.counters + (after_counter,)

    # Draws the game object on the surface
    # The surface usually should be a screen
    def draw(self, surface):
        width = GameObject.evaluate_operation(self.width, self.width_offset, self.width_offset_op)
        height = GameObject.evaluate_operation(self.height, self.height_offset, self.height_offset_op)
        # If we have an icon, we do the following
        if self.icon:
            image = pygame.transform.scale(
                self.icon, (width, height)
            )
            image = pygame.transform.rotate(image, self.angle)
            image = pygame.Surface.convert_alpha(image)

            # 2. Blit our image according to our coordinates plus offset and rotation
            surface.blit(
                image, self.origin
            )
        # If we don't have an icon, we do the following
        if True:
            try:
                # Draw lines from the hitbox
                pygame.draw.line(surface, self.color, self.hit_box[0], self.hit_box[1], 3)
                pygame.draw.line(surface, self.color, self.hit_box[1], self.hit_box[2], 3)
                pygame.draw.line(surface, self.color, self.hit_box[2], self.hit_box[3], 3)
                pygame.draw.line(surface, self.color, self.hit_box[3], self.hit_box[0], 3)
            # If the object is actually Temporary Game object, and some of the used variables are empty strings, we just
            # ignore that error.
            except TypeError:
                pass
            except ValueError:
                self.color = (0, 0, 0)

    # Method to change variables with a lot of options.
    # object_replaced: Game object
    # object_replace_with: Temporary Game object
    @staticmethod
    def change_variables(object_replaced, object_replace_with):
        all_game_object_values = ('x', 'y', 'width', 'height', 'x_offset', 'y_offset', 'width_offset', 'height_offset',
                                  'x_offset_op', 'y_offset_op', 'width_offset_op', 'height_offset_op',
                                  'angle', 'rotation_mode', 'hit_box', 'origin',
                                  'controls', 'pressed_controls', 'speed',
                                  'icon', 'color', 'sound',
                                  'animations', 'counters')
        for name in all_game_object_values:
            if getattr(object_replace_with, name) != '':
                value = getattr(object_replace_with, name)
                if hasattr(object_replace_with, name + '_operation'):
                    value = GameObject.calculate_operations(
                        getattr(object_replaced, name),
                        value,
                        getattr(object_replace_with, name + '_operation')
                    )
                setattr(
                    object_replaced,
                    name,
                    value
                )

    # A function to check events for players. It will check if the window is closed, and return False accordingly,
    # and if control buttons are pressed, and set the pressed controls values accordingly
    # players: iterable of game objects or temporary game objects with controls.
    @staticmethod
    def check_events(players):
        # Get pygame events
        for event in pygame.event.get():
            # Check if the window is attempted to be closed,
            if event.type == pygame.QUIT:
                # return False if so.
                return False
            # Check if some buttons are pressed or unpressed,
            elif event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
                # go through all players.
                for player in players:
                    # Go through all of player's controls.
                    for k in range(0, len(player.controls)):
                        # Check if the un/pressed key is the control key,
                        if event.key == player.controls[k]:
                            try:
                                # If the player is game object,
                                if type(player.pressed_controls) == list:
                                    # We set the pressed value accordingly
                                    player.pressed_controls[k] = True if event.type == pygame.KEYDOWN else False
                                # If the player is temporary game object, so his pressed controls are a tuple,
                                elif type(player.pressed_controls) == tuple:
                                    # We convert them to a temporary list,
                                    pressed_controls = list(player.pressed_controls)
                                    # set the value to the according place in the list
                                    pressed_controls[k] = True if event.type == pygame.KEYDOWN else False
                                    # Convert the list back into a tuple and set pressed controls to it.
                                    player.pressed_controls = tuple(pressed_controls)
                            # If the player is temporary game object and some of the used variables are empty strings,
                            # we just ignore that error.
                            except TypeError:
                                pass

        # If the window wasn't closed, we return True in the end.
        return True

    # Function to find the minimal collision of rectangles. Useful for basic object collision.
    # movable_rect: any game object. Will be the one moved
    # static_rect: any other game object. Will not be the one moved. You can still deduce where to move it if you like,
    # by diving the cost by two, and moving both objects in opposite directions.
    @staticmethod
    def collide_not_rotated_rectangles(movable_rect, static_rect):
        # Check if both rectangles are colliding at all
        if pygame.Rect(movable_rect.x, movable_rect.y, movable_rect.width, movable_rect.height).colliderect(
                pygame.Rect(static_rect.x, static_rect.y, static_rect.width, static_rect.height)):

            # We find the difference between the bottom of the static rect and the top of the movable rect
            cost_down = static_rect.y + static_rect.height - movable_rect.y
            # We find the difference between the bottom of the movable rect and the top of the static rect
            cost_up = movable_rect.y + movable_rect.height - static_rect.y
            # We find the difference between the right of the static rect and the left of the movable rect
            cost_right = static_rect.x + static_rect.width - movable_rect.x
            # We find the difference between the right of the movable rect and the left of the static rect
            cost_left = movable_rect.x + movable_rect.width - static_rect.x

            # Find the minimal cost of moving each direction, to get realistic collision
            minimal_cost = min(cost_down, cost_up, cost_right, cost_left)
            # Check which direction takes minimal effort and return values accordingly
            if minimal_cost == cost_left:
                return ["LEFT", cost_left]
            if minimal_cost == cost_right:
                return ["RIGHT", cost_right]
            if minimal_cost == cost_up:
                return ["UP", cost_up]
            if minimal_cost == cost_down:
                return ["DOWN", cost_down]
        return False

    @staticmethod
    def is_point_colliding_with_any_rectangle(rectangle_points, point):
        if point not in rectangle_points:
            ab = math.sqrt(((rectangle_points[0][0] - rectangle_points[1][0]) ** 2) +
                           ((rectangle_points[0][1] - rectangle_points[1][1]) ** 2))
            bc = math.sqrt(((rectangle_points[1][0] - rectangle_points[2][0]) ** 2) +
                           ((rectangle_points[1][1] - rectangle_points[2][1]) ** 2))
            cd = math.sqrt(((rectangle_points[2][0] - rectangle_points[3][0]) ** 2) +
                           ((rectangle_points[2][1] - rectangle_points[3][1]) ** 2))
            da = math.sqrt(((rectangle_points[3][0] - rectangle_points[0][0]) ** 2) +
                           ((rectangle_points[3][1] - rectangle_points[0][1]) ** 2))

            ap = math.sqrt(((rectangle_points[0][0] - point[0]) ** 2) +
                           ((rectangle_points[0][1] - point[1]) ** 2))
            bp = math.sqrt(((rectangle_points[1][0] - point[0]) ** 2) +
                           ((rectangle_points[1][1] - point[1]) ** 2))
            cp = math.sqrt(((rectangle_points[2][0] - point[0]) ** 2) +
                           ((rectangle_points[2][1] - point[1]) ** 2))
            dp = math.sqrt(((rectangle_points[3][0] - point[0]) ** 2) +
                           ((rectangle_points[3][1] - point[1]) ** 2))

            if ((ap + bp > ab)
                    and (ap + ab > bp)
                    and (bp + ab > ap)) \
                    and ((bp + cp > bc)
                         and (bp + bc > cp)
                         and (cp + bc > bp)) \
                    and ((cp + dp > cd)
                         and (cp + cd > dp)
                         and (dp + cd > cp)) \
                    and ((dp + ap > da)
                         and (dp + da > ap)
                         and (ap + da > dp)):
                abp_perimeter = (ab + bp + ap) / 2
                bcp_perimeter = (bc + cp + bp) / 2
                cdp_perimeter = (cd + dp + cp) / 2
                dap_perimeter = (da + ap + dp) / 2
                abp_area = math.sqrt(abp_perimeter *
                                     (abp_perimeter - ab) *
                                     (abp_perimeter - bp) *
                                     (abp_perimeter - ap))
                bcp_area = math.sqrt(bcp_perimeter *
                                     (bcp_perimeter - bc) *
                                     (bcp_perimeter - cp) *
                                     (bcp_perimeter - bp))
                cdp_area = math.sqrt(cdp_perimeter *
                                     (cdp_perimeter - cd) *
                                     (cdp_perimeter - dp) *
                                     (cdp_perimeter - cp))
                dap_area = math.sqrt(dap_perimeter *
                                     (dap_perimeter - da) *
                                     (dap_perimeter - ap) *
                                     (dap_perimeter - dp))

                if abp_area + bcp_area + cdp_area + dap_area <= ab * bc:
                    return True
        return False

    @staticmethod
    def which_rectangle_inside_another(rectangle_points1, rectangle_points2):
        for point in rectangle_points1:
            if GameObject.is_point_colliding_with_any_rectangle(rectangle_points2, point):
                return 1
        for point in rectangle_points2:
            if GameObject.is_point_colliding_with_any_rectangle(rectangle_points1, point):
                return 2
        return False

    @staticmethod
    def point_on_line_perpendicular_to_point(line_point1, line_point2, point):
        if line_point1[0] != line_point2[0] and line_point1[1] != line_point2[1]:
            m = (line_point2[1] - line_point1[1]) / (line_point2[0] - line_point1[0])
            b = line_point1[1] - (m * line_point1[0])
            pm = -(1 / m)
            pb = point[1] - (pm * point[0])
            x = (pb - b) / (m - pm)
            y = (m * x) + b
        elif line_point1[0] == line_point2[0] and line_point1[1] != line_point2[1]:
            x = line_point1[0]
            y = point[1]
        elif line_point1[1] == line_point2[1] and line_point1[0] != line_point2[0]:
            x = point[0]
            y = line_point1[1]
        else:
            x = line_point1[0]
            y = line_point1[1]
        return x, y

    @staticmethod
    def distance_between_two_points(p1, p2):
        return math.sqrt(((p2[0] - p1[0]) ** 2) + ((p2[1] - p1[1]) ** 2))

    @staticmethod
    def all_perpendiculars_on_a_rectangle_of_a_point(rectangle_points, point):
        if GameObject.is_point_colliding_with_any_rectangle(rectangle_points, point):
            return_list = [
                GameObject.point_on_line_perpendicular_to_point(rectangle_points[0], rectangle_points[1], point),
                GameObject.point_on_line_perpendicular_to_point(rectangle_points[1], rectangle_points[2], point),
                GameObject.point_on_line_perpendicular_to_point(rectangle_points[2], rectangle_points[3], point),
                GameObject.point_on_line_perpendicular_to_point(rectangle_points[3], rectangle_points[0], point)
            ]
            return return_list
        return False

    @staticmethod
    def collide_rotated_rectangles(movable_rect, static_rect):
        which = GameObject.which_rectangle_inside_another(movable_rect, static_rect)
        if which == 1:
            del which
            all_perpendiculars = []
            viable_perpendiculars = []
            for point in movable_rect:
                perpendicular_points = GameObject.all_perpendiculars_on_a_rectangle_of_a_point(static_rect, point)
                if perpendicular_points:
                    for i in range(len(perpendicular_points)):
                        all_perpendiculars.append((perpendicular_points[i][0] - point[0],
                                                   perpendicular_points[i][1] - point[1]))
            for point in all_perpendiculars:
                temp_movable_rect = list(movable_rect)
                for tp in range(len(temp_movable_rect)):
                    tpx = temp_movable_rect[tp][0] + point[0]
                    tpy = temp_movable_rect[tp][1] + point[1]
                    temp_movable_rect[tp] = (tpx, tpy)
                if not GameObject.which_rectangle_inside_another(temp_movable_rect, static_rect):
                    viable_perpendiculars.append(point)

            viable_perpendiculars = sorted(viable_perpendiculars, key=lambda x: abs(x[0]) + abs(x[1]))
            return viable_perpendiculars
        elif which == 2:
            del which
            all_perpendiculars = []
            viable_perpendiculars = []
            for point in static_rect:
                perpendicular_points = GameObject.all_perpendiculars_on_a_rectangle_of_a_point(movable_rect, point)
                if perpendicular_points:
                    for i in range(len(perpendicular_points)):
                        all_perpendiculars.append((point[0] - perpendicular_points[i][0],
                                                   point[1] - perpendicular_points[i][1]))
            for point in all_perpendiculars:
                temp_movable_rect = list(movable_rect)
                for tp in range(len(temp_movable_rect)):
                    tpx = temp_movable_rect[tp][0] + point[0]
                    tpy = temp_movable_rect[tp][1] + point[1]
                    temp_movable_rect[tp] = (tpx, tpy)
                if not GameObject.which_rectangle_inside_another(temp_movable_rect, static_rect):
                    viable_perpendiculars.append(point)

            viable_perpendiculars = sorted(viable_perpendiculars, key=lambda x: abs(x[0]) + abs(x[1]))
            return viable_perpendiculars
        return False

    @staticmethod
    def evaluate_operation(val1, val2, operator):
        if operator == '+':
            return val1 + val2
        elif operator == '*':
            return val1 * val2
        elif operator == '=':
            return val2
        else:
            return val1

    @staticmethod
    def calculate_operations(val1, val2, operator):
        val1_type = type(val1)
        val2_type = type(val2)
        iters = (tuple, list)
        ints = (int, float)
        return_value = val1

        if val1_type in iters:
            if val2_type in iters:
                return_value = list(val1)
                for i in range(len(val1)):
                    return_value[i] = GameObject.evaluate_operation(return_value[i], val2[i], operator)

                if val1_type == tuple:
                    return_value = tuple(return_value)
            elif val2_type in ints:
                return_value = [GameObject.evaluate_operation(value, val2, operator) for value in val1]

                if val1_type == tuple:
                    return_value = tuple(return_value)
        elif val1_type in ints:
            if val2_type in iters:
                return_value = GameObject.evaluate_operation(val1, val2[0], operator)
            elif val2_type in ints:
                return_value = GameObject.evaluate_operation(val1, val2, operator)
        return return_value


# class for temporary game objects. Mostly used for temporary variable changes, and animations.
class TempGameObject(GameObject):
    # All the variables serve the same function as game object variables. They can also be empty strings, if we wish not
    # to replace that value. The _operation variables give directions to change_variables function, the operation
    # corresponding to the operation
    def __init__(self, x='', y='', width='', height='', x_offset='', y_offset='', width_offset='', height_offset='',
                 x_offset_op='', y_offset_op='', width_offset_op='', height_offset_op='',
                 angle='', rotation_mode='', hit_box='', origin='',
                 controls='', pressed_controls='', speed='',
                 icon='', color='', sound='',
                 animations='', play_animation='', counters='',
                 x_operation='+', y_operation='+', width_operation='+', height_operation='+',
                 x_offset_operation='+', y_offset_operation='+', width_offset_operation='+',
                 height_offset_operation='+',
                 speed_operation='+', color_operation='+',
                 angle_operation='+'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.width_offset = width_offset
        self.height_offset = height_offset

        self.x_offset_op = x_offset_op
        self.y_offset_op = y_offset_op
        self.width_offset_op = width_offset_op
        self.height_offset_op = height_offset_op

        self.angle = angle
        self.rotation_mode = rotation_mode

        self.hit_box = hit_box
        self.origin = origin

        self.controls = controls
        # We have to turn the pressed controls variable into a tuple because of some bug that happens when it's mutable.
        self.pressed_controls = tuple(pressed_controls) if pressed_controls != '' else ''
        self.speed = speed

        self.icon = icon
        self.color = color
        self.sound = sound

        self.animations = animations
        self.play_animation = play_animation
        self.counters = counters

        self.x_operation = x_operation
        self.y_operation = y_operation
        self.width_operation = width_operation
        self.height_operation = height_operation
        self.x_offset_operation = x_offset_operation
        self.y_offset_operation = y_offset_operation
        self.width_offset_operation = width_offset_operation
        self.height_offset_operation = height_offset_operation
        self.speed_operation = speed_operation
        self.color_operation = color_operation
        self.angle_operation = angle_operation

        # The initialized variable makes the temporary game object update if it's true. This is only useful for
        # temporary game objects that update, and are in animations.
        self.initialized = False

    def update(self):
        if self.initialized:
            super().update()

    def draw(self, surface):
        if self.initialized:
            super().draw(surface)


# This class is for counting down. It's really simple, but useful.
class Counter(object):
    # count: the count that the counter starts on
    # change_range: list of 2 numbers, determining the minimum and maximum of the counter
    # change_per_second: the number which will be deducted each frame
    # value: variable to hold anything if needed. Useful for temporary variable changes and animations.
    def __init__(self, count, change_range, change_per_second, value):
        self.count = count
        self.range = change_range
        self.decrease = change_per_second
        self.value = value

    # Function to update the count. Should be called every frame.
    def update(self):
        if self.range[0] < self.count < self.range[1]:
            self.count -= self.decrease


# Class for a screen object. Really simple, but pretty useful to hold those variables together.
class Screen(object):
    # width: width of the window
    # height: height of the window
    # color: the background color of the window
    def __init__(self, width=300, height=300, color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.color = color
        # Create a pygame window
        self.window = pygame.display.set_mode((self.width, self.height))


# function for drawing all things on a surface. Simple, but very useful.
# things: list of game objects or temporary game objects
# surface: the screen window
def draw_things(things, surface):
    for thing in things:
        thing.draw(surface)


# function for updating all things. Simple, but very useful.
# things: list of game objects or temporary game objects
def update_things(things):
    for thing in things:
        thing.update()


if __name__ == "__main__":
    clock = pygame.time.Clock()
    man = GameObject(controls=[pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d], width=70, height=50,
                     icon=pygame.image.load('a.png'), angle=90)

    blok = GameObject(controls=[pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT], width=100, height=70,
                      color=(0, 10, 10), x=10, y=10, angle=0)

    players = [man, blok]
    drawablethings = [man, blok]
    things = [man, blok]
    screen = Screen(700, 600)
    pygame.init()
    while GameObject.check_events(players):
        update_things(things)
        screen.window.fill(screen.color)
        draw_things(drawablethings, screen.window)
        pygame.display.update()
        p = GameObject.collide_rotated_rectangles(blok.hit_box, man.hit_box)
        if p:
            man.x -= p[0][0]
            man.y -= p[0][1]

        clock.tick(60)
    pygame.quit()
