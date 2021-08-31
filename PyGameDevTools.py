import pygame
import math
import numpy as np
import Polygon
import Bezier


class Events:
    @staticmethod
    def pass_function(**dump):
        pass

    @staticmethod
    def animate_start(obj, kwargs: dict, **dump):
        obj.temporarily_change_variables(
            t=kwargs['t'],
            before=kwargs['before'],
            after=kwargs['after'],
        )

        obj.play_animation = False
        if obj.animations:
            animations = list(obj.animations)
            animations.append(animations.pop(0))
            obj.animations = tuple(animations)

    @staticmethod
    def animate_end(obj, kwargs: dict, **dump):
        GameObject.change_variables(obj, kwargs['before'])
        if kwargs['parent'] in obj.animations:
            obj.play_animation = True

    @staticmethod
    def move_shortcut(obj, **dump):
        try:
            if obj.pressed_controls[0]:
                obj.y -= obj.speed[0] * obj.speed_axis[0]
            if obj.pressed_controls[0]:
                obj.x -= obj.speed[1] * obj.speed_axis[1]
            if obj.pressed_controls[2]:
                obj.y += obj.speed[2] * obj.speed_axis[2]
            if obj.pressed_controls[3]:
                obj.x += obj.speed[3] * obj.speed_axis[3]
        except IndexError:
            pass

    @staticmethod
    def move(obj, kwargs: dict = None, **dump):
        for i in range(min(len(obj.pressed_controls), len(obj.on_pressed_controls))):
            if obj.pressed_controls[i]:
                obj.on_pressed_controls[i].execute(obj=obj, kwargs=kwargs)

    @staticmethod
    def move_0(obj, **dump):
        obj.y -= obj.speed[0] * obj.speed_axis[0]

    @staticmethod
    def move_1(obj, **dump):
        obj.x -= obj.speed[1] * obj.speed_axis[1]

    @staticmethod
    def move_2(obj, **dump):
        obj.y += obj.speed[2] * obj.speed_axis[2]

    @staticmethod
    def move_3(obj, **dump):
        obj.x += obj.speed[3] * obj.speed_axis[3]

    @staticmethod
    def move_rotated_shortcut(obj, **dump):
        cos = math.cos(obj.angle / 180 * math.pi)
        sin = math.sin(obj.angle / 180 * math.pi)
        if obj.pressed_controls[0]:
            obj.x -= sin * obj.speed[0] * obj.speed_axis[1]
            obj.y -= cos * obj.speed[0] * obj.speed_axis[0]
        if obj.pressed_controls[1]:
            obj.x -= sin * obj.speed[1] * obj.speed_axis[1]
            obj.y += cos * obj.speed[1] * obj.speed_axis[2]
        if obj.pressed_controls[2]:
            obj.x += sin * obj.speed[2] * obj.speed_axis[3]
            obj.y += cos * obj.speed[2] * obj.speed_axis[2]
        if obj.pressed_controls[3]:
            obj.x += sin * obj.speed[3] * obj.speed_axis[3]
            obj.y -= cos * obj.speed[3] * obj.speed_axis[0]

    @staticmethod
    def move_0_rotated(obj, **dump):
        cos = math.cos(obj.angle / 180 * math.pi)
        sin = math.sin(obj.angle / 180 * math.pi)
        obj.x -= sin * obj.speed[0] * obj.speed_axis[1]
        obj.y -= cos * obj.speed[0] * obj.speed_axis[0]

    @staticmethod
    def move_1_rotated(obj, **dump):
        cos = math.cos(obj.angle / 180 * math.pi)
        sin = math.sin(obj.angle / 180 * math.pi)
        obj.x -= sin * obj.speed[1] * obj.speed_axis[1]
        obj.y += cos * obj.speed[1] * obj.speed_axis[2]

    @staticmethod
    def move_2_rotated(obj, **dump):
        cos = math.cos(obj.angle / 180 * math.pi)
        sin = math.sin(obj.angle / 180 * math.pi)
        obj.x += sin * obj.speed[2] * obj.speed_axis[3]
        obj.y += cos * obj.speed[2] * obj.speed_axis[2]

    @staticmethod
    def move_3_rotated(obj, **dump):
        cos = math.cos(obj.angle / 180 * math.pi)
        sin = math.sin(obj.angle / 180 * math.pi)
        obj.x += sin * obj.speed[3] * obj.speed_axis[3]
        obj.y -= cos * obj.speed[3] * obj.speed_axis[0]


class Func(object):
    def __init__(self, func, kwargs: dict = None):
        if kwargs is None:
            kwargs = {}
        self.func = func
        self.kwargs = kwargs

    def execute(self, obj, kwargs: dict = None):
        if kwargs is None:
            kwargs = self.kwargs

        if 'after' in kwargs:
            kwargs['after'].kwargs['parent'] = self

        self.func(obj=obj, kwargs=kwargs)


class Animations:
    # Makes a list of points to move along, based off key points. There are two options available:
    # 1. Linear movement
    # 2. Bezier curve movement
    # The first one is basic movement, which is broken into local movement and extended to fit the 1 animation per frame
    # format.
    # The second option uses the Bezier class to calculate those points, which are then broken into local movement
    # Why make those points into local movement? Well, it's more useful. You can't move the game object with a global
    # point animation, but you can do that with a local movement animation.
    @staticmethod
    def calculate_movement_points(t: int, key_points, curve_type: str):
        if curve_type == "LINE":
            movement_points = Animations.extend_linear_movement(
                Animations.global_points_to_local_movement(key_points), t
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
            movement_points = Animations.global_points_to_local_movement(movement_points)
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
    @staticmethod
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
    @staticmethod
    def generate_empty_animations(length: int):
        # Return the empty (and useless) animation element layout times desired length.
        return_list = []
        for i in range(length):
            return_list.append(Func(
                       Events.animate_start,
                       {'t': 1, 'before': TempGameObject(), 'after': Func(Events.animate_end,
                                                                          {'before': TempGameObject()}
                                                                          )}
                   ))
        return return_list

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
            animations += Animations.generate_empty_animations(
                length=len(points) - len(animations)
            )

        # Go through the entire list of points
        for i in range(len(points)):
            # Go through each value of each element of points
            for j in range(len(points[i])):

                replaced_attribute = getattr(animations[i].kwargs['before'], replaced_values[j])
                value = GameObject.evaluate_operation_between_different_types(
                    replaced_attribute, points[i][j], values_operations[j]
                )
                setattr(animations[i].kwargs['before'], replaced_values[j], value)
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
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        width: float = 10.0,
        height: float = 10.0,
        x_offset: float = 0.0,
        y_offset: float = 0.0,
        width_offset: float = 0.0,
        height_offset: float = 0.0,
        x_offset_op: str = '+',
        y_offset_op: str = '+',
        width_offset_op: str = '+',
        height_offset_op: str = '+',
        angle: float = 0.0,
        rotation_mode: str = 'CENTER',
        hit_box=(),
        origin=(),
        controls=(None, None, None, None),
        pressed_controls=(False, False, False, False),
        speed=(1.0, 1.0, 1.0, 1.0),
        speed_axis=(1.0, 1.0, 1.0, 1.0),
        icon=None,
        hit_box_color=(255, 0, 0),
        sound=None,
        sound_volume: float = 1.0,
        sound_channel: int = 0,
        sound_loop_mode: int = 0,
        sound_fade_in_ms: int = 0,
        weight: float = 0.5,
        animations=(),
        counters=(),
        other_events=()
    ):
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

        self.speed_axis = speed_axis

        self.sound = sound
        self.sound_volume = sound_volume
        self.sound_channel = sound_channel
        self.sound_loop_mode = sound_loop_mode
        self.sound_fade_in_ms = sound_fade_in_ms
        self.played_sound = False

        self.speed = speed

        self.icon = icon
        self.hit_box_color = hit_box_color

        self.weight = weight

        self.animations = animations
        # play_animation is used for animations only (recurring temporal variable changes). It makes the selected
        # animation play only once until the next animation comes. This is extremely important.
        self.play_animation = True
        self.counters = counters

        self.other_events = other_events

        if not hit_box:
            self.original_hit_box = (
                (0, 0),
                (0, self.height),
                (self.width, self.height),
                (self.width, 0),
            )
        else:
            self.original_hit_box = hit_box
        if not origin:
            self.image_origin = (self.x, self.y)
        else:
            self.image_origin = origin
        self.angle = angle
        self.rotation_mode = rotation_mode
        self.rotated_hit_box = self.original_hit_box
        self.moved_rotated_hit_box = self.rotated_hit_box
        self.bounding_box = (
            (self.x, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height),
            (self.x + self.width, self.y)
        )

        # Controls can be of any length due to how the checking of events is done,
        self.controls = controls
        # and thus, this construction is needed
        # If the passed in pressed_controls aren't a tuple or a list (which they always should be)
        if type(pressed_controls) not in (tuple, list):
            # And if controls ARE a tuple or a list,
            if type(controls) in (tuple, list):
                # We make a list of the same length than that of controls.
                self.pressed_controls = [
                    False,
                ] * len(controls)
            # And if controls aren't a tuple nor a list,
            else:
                # we make pressed_controls an empty list instead.
                self.pressed_controls = []
        # if they ARE a tuple or a list, we make them a list (because it's easier that way to change them)
        else:
            self.pressed_controls = list(pressed_controls)

    # Method to update the game object. Mostly useful for player movement, counters and animation. Should be called
    # every frame for each game object.
    def update(self):
        for event in self.other_events:
            event(self)
        self.move_rotated()
        self.evaluate_image_rotation()
        self.bounding_box = Polygon.get_bounding_box(self.moved_rotated_hit_box)
        self.evaluate_hit_box_rotation()
        self.evaluate_hit_box_movement()
        self.update_counters()
        self.animate()
        self.play_sound()

    def play_sound(self):
        if type(self.sound) == pygame.mixer.Sound:
            if not pygame.mixer.Channel(0).get_busy() and (
                not self.played_sound or self.sound_loop_mode == 2
            ):
                self.played_sound = True
                if self.sound_loop_mode != 1:
                    pygame.mixer.Channel(self.sound_channel).play(
                        self.sound, fade_ms=self.sound_fade_in_ms
                    )
                else:
                    pygame.mixer.Channel(self.sound_channel).play(
                        self.sound, fade_ms=self.sound_fade_in_ms, loops=True
                    )
                pygame.mixer.Channel(self.sound_channel).set_volume(self.sound_volume)

    def move_unrotated(self):
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
                    self.x -= cos * self.speed[1]
                    self.y += sin * self.speed[1]
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

    def evaluate_hit_box_movement(self):
        self.moved_rotated_hit_box = tuple((point[0] + self.x, point[1] + self.y) for point in self.rotated_hit_box)

    def evaluate_hit_box_rotation(self):
        if self.rotation_mode == "AROUND":
            self.rotated_hit_box = Polygon.rotate_points_around_point(
                (0, 0), self.original_hit_box, math.radians(-self.angle)
            )
        elif self.rotation_mode == "CENTER":
            self.rotated_hit_box = Polygon.rotate_points_around_point(
                (self.width / 2, self.height / 2),
                self.original_hit_box,
                math.radians(-self.angle),
            )
        elif False:
            # Please don't use this ever. I beg you. It's utterly useless and incomplete,
            # it won't ever work and it shouldn't.
            rotated_hit_box = Polygon.rotate_points_around_point(
                (0, 0), self.original_hit_box, math.radians(-self.angle)
            )
            global_rotated_hit_box = []
            if 0 <= self.angle <= 90:
                origin = (
                    self.x,
                    self.y + math.sin(math.radians(self.angle)) * self.width,
                )
            elif 90 <= self.angle <= 180:
                origin = (
                    self.x + math.sin(math.radians(self.angle - 90)) * self.width,
                    self.y + self.width,
                )
            elif 180 <= self.angle <= 270:
                origin = (
                    self.x + self.width,
                    self.y + math.sin(math.radians(self.angle)) * self.width,
                )
            else:
                pass

    def evaluate_image_rotation(self):
        x = GameObject.evaluate_operation(self.x, self.x_offset, self.x_offset_op)
        y = GameObject.evaluate_operation(self.y, self.y_offset, self.y_offset_op)
        width = GameObject.evaluate_operation(
            self.width, self.width_offset, self.width_offset_op
        )
        height = GameObject.evaluate_operation(
            self.height, self.height_offset, self.height_offset_op
        )

        origin = (x, y)
        if self.rotation_mode == "AROUND":
            box = [
                pygame.math.Vector2(p)
                for p in [(0, 0), (width, 0), (width, -height), (0, -height)]
            ]
            box_rotate = [p.rotate(self.angle) for p in box]
            min_box = (
                min(box_rotate, key=lambda p: p[0])[0],
                min(box_rotate, key=lambda p: p[1])[1],
            )
            max_box = (
                max(box_rotate, key=lambda p: p[0])[0],
                max(box_rotate, key=lambda p: p[1])[1],
            )
            origin = (x + min_box[0], y - max_box[1])
        elif self.rotation_mode == "CENTER":
            box = [
                pygame.math.Vector2(p)
                for p in [(0, 0), (width, 0), (width, -height), (0, -height)]
            ]
            box_rotate = [p.rotate(self.angle) for p in box]
            min_box = (
                min(box_rotate, key=lambda p: p[0])[0],
                min(box_rotate, key=lambda p: p[1])[1],
            )
            max_box = (
                max(box_rotate, key=lambda p: p[0])[0],
                max(box_rotate, key=lambda p: p[1])[1],
            )
            pivot = pygame.math.Vector2(width / 2, -height / 2)
            pivot_rotate = pivot.rotate(self.angle)
            pivot_move = pivot_rotate - pivot
            origin = (x + min_box[0] - pivot_move[0], y - max_box[1] + pivot_move[1])
        else:
            pass

        self.image_origin = origin

    def update_counters(self):
        # If we have any current counters, we do the following
        if self.counters:
            for counter in self.counters:
                # We update the counter
                counter.update()
                # If this counter is actually used by temporary_variable_change, and has already reached one of it's
                # limits, we do the following
                if (
                    counter.count == counter.range[0]
                    or counter.count == counter.range[1]
                ):
                    # Assign it's value to a temporary variable c for simplicity
                    c = counter.value

                    if type(c) == Func:
                        c.execute(self)

                    # If we still have counter in our counters
                    if counter in self.counters:
                        # We convert counters to a temporary list
                        counters = list(self.counters)
                        # We remove the counter from our temporary list
                        counters.remove(counter)
                        # We convert our temporary list back to a tuple and assign our counters to it
                        self.counters = tuple(counters)

                        # We then delete the now useless object counter and it's value c. I don't know if this is
                        # needed, or if python's garbage collector would've cleaned it up the same regardless.
                        del counter
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
                self.animations[0].execute(self)

    # Function to temporarily change object variables. Any of them.
    # t is time, in frames, for how long the counter will last. At the end of the counter, this game object will be
    # assigned values from after. At the immediate start of the timer, it will be assigned values from before.
    def temporarily_change_variables(self, t: int, before, after):
        # We make the temporary game object initialized, so it can update. It won't update unless you intentionally
        # update it.
        after.initialized = True
        # We make a counter for the value after, which will tick down after t frames.
        after_counter = Counter(
            count=t, change_range=[0, t + 1], change_per_second=1, value=after
        )
        # We change our variables with the object before
        GameObject.change_variables(self, before)
        # And discard it because we don't need it anymore.
        del before

        self.counters = self.counters + (after_counter,)

    # Draws the game object on the surface
    # The surface usually should be a screen
    def draw(self, surface):
        width = GameObject.evaluate_operation(
            self.width, self.width_offset, self.width_offset_op
        )
        height = GameObject.evaluate_operation(
            self.height, self.height_offset, self.height_offset_op
        )
        # If we have an icon, we do the following
        if self.icon:
            image = pygame.transform.scale(self.icon, (width, height))
            image = pygame.transform.rotate(image, self.angle)
            image = pygame.Surface.convert_alpha(image)

            # 2. Blit our image according to our coordinates plus offset and rotation
            surface.blit(image, self.image_origin)
        if True:
            try:
                pygame.draw.polygon(
                    surface, self.hit_box_color, self.moved_rotated_hit_box, 1
                )
            # If the object is actually Temporary Game object, and some of the used variables are empty strings, we just
            # ignore that error.
            except TypeError:
                pass

    # Method to change variables with a lot of options.
    # object_replaced: Game object
    # object_replace_with: Temporary Game object
    @staticmethod
    def change_variables(object_replaced, object_replace_with):
        all_game_object_variables = [
            "angle",
            "animations",
            "controls",
            "counters",
            "height",
            "height_offset",
            "height_offset_op",
            "hit_box_color",
            "icon",
            "image_origin",
            "original_hit_box",
            "play_animation",
            "played_sound",
            "pressed_controls",
            "rotated_hit_box",
            "rotation_mode",
            "sound",
            "sound_channel",
            "sound_fade_in_ms",
            "sound_loop_mode",
            "sound_volume",
            "speed",
            "width",
            "width_offset",
            "width_offset_op",
            "x",
            "x_offset",
            "x_offset_op",
            "y",
            "y_offset",
            "y_offset_op",
        ]
        for var in all_game_object_variables:
            if getattr(object_replace_with, var) != "":
                value = getattr(object_replace_with, var)
                if hasattr(object_replace_with, var + "_operation"):
                    value = GameObject.evaluate_operation_between_different_types(
                        getattr(object_replaced, var),
                        value,
                        getattr(object_replace_with, var + "_operation"),
                    )
                setattr(object_replaced, var, value)

    # A function to check events for players. It will check if the window is closed, and return False accordingly,
    # and if control buttons are pressed, and set the pressed controls values accordingly
    # players: iterable of game objects or temporary game objects with controls.
    @staticmethod
    def check_player_events(players):
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
                                    player.pressed_controls[k] = (
                                        True if event.type == pygame.KEYDOWN else False
                                    )
                                # If the player is temporary game object, so his pressed controls are a tuple,
                                elif type(player.pressed_controls) == tuple:
                                    # We convert them to a temporary list,
                                    pressed_controls = list(player.pressed_controls)
                                    # set the value to the according place in the list
                                    pressed_controls[k] = (
                                        True if event.type == pygame.KEYDOWN else False
                                    )
                                    # Convert the list back into a tuple and set pressed controls to it.
                                    player.pressed_controls = tuple(pressed_controls)
                            # If the player is temporary game object and some of the used variables are empty strings,
                            # we just ignore that error.
                            except TypeError:
                                pass

        # If the window wasn't closed, we return True in the end.
        return True

    @staticmethod
    def evaluate_operation(val1, val2, operator):
        if operator == '+':
            return val1 + val2
        if operator == '*':
            return val1 * val2
        if operator == '=':
            return val2
        return val1

    # Function for evaluating the operation between different types of variables. Mainly used for changing variables.
    #
    # Supported types:
    # (numbers):
    #   bool = True
    #   int = 12
    #   float = 3.1
    # (iterables):
    #   tuple = (1, 'hi', TempGameObject())
    #   list = [4, '+', GameObject()]
    #
    # Please note: True is treated as the number 1, and False is treated as the number 0.
    # However, only the number 0, empty strings and tuples are treated as False and anything else is treated as True.
    #
    # Supported operations:
    # num + num:
    #   1 + 1 = 2
    # num + iter: (the first element will always be taken)
    #   1 + [5, 1, 4, 2] = 1 + 5 = 6
    #
    # num * num:
    #   4 * 4 = 16
    # num * iter: (the first element will always be taken)
    #   3 * (0, 12, 4, 3) = 3 * 0 = 0
    #
    # iter + iter:
    #   [1, 5, 3, 4] + [2, 6, 3] = [1 + 2, 5 + 6, 3 + 3, 4] = [3, 11, 6, 4]
    # iter + num:
    #   [1, 2, 6, 2] + 14 = [1 + 14, 2 + 14, 6 + 14, 2 + 14] = [15, 16, 20, 16]
    # iter * iter:
    #   [1, 5, 3, 4] * [2, 6, 3] = [1 * 2, 5 * 6, 3 * 3, 4] = [2, 30, 9, 4]
    # iter * num:
    #   [1, 2, 6, 2] * 14 = [1 * 14, 2 * 14, 6 * 14, 2 * 14] = [14, 28, 84, 28]
    #
    # iter extend iter:
    #   [3, '+', TempGameObject(), GameObject()] extend [1, 5, '*', GameObject()] =
    #   [3, '+', TempGameObject(), GameObject(), 1, 5, '*', GameObject()]
    # iter replace iter:
    #   [3, '+', TempGameObject(), GameObject()] replace [1, 5, '*', GameObject()] =
    #   [1, 5, '*', GameObject()]
    @staticmethod
    def evaluate_operation_between_different_types(val1, val2, operator: str):

        if val1 == '':
            val1 = 0

        val1_type = type(val1)
        val2_type = type(val2)
        iters = (tuple, list)
        nums = (int, float, bool)

        return_value = val1

        if val1_type == bool:
            val1 = int(val1 == True)
        if val2_type == bool:
            val2 = int(val2 == True)



        if val1_type in iters:
            return_value = list(return_value)
            if val2_type in iters:
                if operator == "extend":
                    return_value.extend(val2)
                elif operator == "replace":
                    return_value = val2
                else:
                    for i in range(min(len(val1), len(val2))):
                        return_value[i] = GameObject.evaluate_operation(
                            return_value[i], val2[i], operator
                        )
            elif val2_type in nums:
                return_value = [
                    GameObject.evaluate_operation(val, val2, operator) for val in val1
                ]
            if val1_type == tuple:
                return_value = tuple(return_value)
        elif val1_type in nums:
            if val2_type in iters:
                return_value = GameObject.evaluate_operation(val1, val2[0], operator)
            elif val2_type in nums:
                return_value = GameObject.evaluate_operation(val1, val2, operator)
        if val1_type == bool:
            return_value = bool(return_value)

        return return_value


# class for temporary game objects. Mostly used for temporary variable changes, and animations.
class TempGameObject(GameObject):
    # All the variables serve the same function as game object variables. They can also be empty strings, if we wish not
    # to replace that value. The _operation variables give directions to change_variables function, the operation
    # corresponding to the operation
    def __init__(
            self,
            x='',               # int
            y='',               # int
            width='',               # int
            height='',               # int
            x_offset='',               # int
            y_offset='',               # int
            width_offset='',               # int
            height_offset='',               # int
            x_offset_op='',               # str
            y_offset_op='',               # str
            width_offset_op='',               # str
            height_offset_op='',               # str
            speed_axis='',               # tuple
            sound='',               # NoneType
            sound_volume='',               # float
            sound_channel='',               # int
            sound_loop_mode='',               # int
            sound_fade_in_ms='',               # int
            played_sound='',               # bool
            speed='',               # tuple
            icon='',               # pygame.Surface
            hit_box_color='',               # tuple
            weight='',               # float
            animations='',               # tuple
            play_animation='',               # bool
            counters='',               # tuple
            other_events='',               # tuple
            original_hit_box='',               # tuple
            image_origin='',               # tuple
            angle='',               # float
            rotation_mode='',               # str
            rotated_hit_box='',               # list
            moved_rotated_hit_box='',               # tuple
            bounding_box='',               # list
            controls='',               # tuple
            pressed_controls='',               # list
            x_operation='+',
            y_operation='+',
            width_operation='+',
            height_operation='+',
            x_offset_operation='+',
            y_offset_operation='+',
            width_offset_operation='+',
            height_offset_operation='+',
            speed_axis_operation='+',
            sound_volume_operation='+',
            sound_channel_operation='+',
            sound_loop_mode_operation='+',
            sound_fade_in_ms_operation='+',
            played_sound_operation='+',
            speed_operation='+',
            hit_box_color_operation='+',
            weight_operation='+',
            animations_operation='+',
            play_animation_operation='+',
            counters_operation='+',
            other_events_operation='+',
            original_hit_box_operation='+',
            image_origin_operation='+',
            angle_operation='+',
            rotated_hit_box_operation='+',
            moved_rotated_hit_box_operation='+',
            bounding_box_operation='+',
            controls_operation='+',
            pressed_controls_operation='+',
    ):
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
        self.speed_axis = speed_axis
        self.sound = sound
        self.sound_volume = sound_volume
        self.sound_channel = sound_channel
        self.sound_loop_mode = sound_loop_mode
        self.sound_fade_in_ms = sound_fade_in_ms
        self.played_sound = played_sound
        self.speed = speed
        self.icon = icon
        self.hit_box_color = hit_box_color
        self.weight = weight
        self.animations = animations
        self.play_animation = play_animation
        self.counters = counters
        self.other_events = other_events
        self.original_hit_box = original_hit_box
        self.image_origin = image_origin
        self.angle = angle
        self.rotation_mode = rotation_mode
        self.rotated_hit_box = rotated_hit_box
        self.moved_rotated_hit_box = moved_rotated_hit_box
        self.bounding_box = bounding_box
        self.controls = controls
        self.pressed_controls = pressed_controls
        self.x_operation = x_operation
        self.y_operation = y_operation
        self.width_operation = width_operation
        self.height_operation = height_operation
        self.x_offset_operation = x_offset_operation
        self.y_offset_operation = y_offset_operation
        self.width_offset_operation = width_offset_operation
        self.height_offset_operation = height_offset_operation
        self.speed_axis_operation = speed_axis_operation
        self.sound_volume_operation = sound_volume_operation
        self.sound_channel_operation = sound_channel_operation
        self.sound_loop_mode_operation = sound_loop_mode_operation
        self.sound_fade_in_ms_operation = sound_fade_in_ms_operation
        self.played_sound_operation = played_sound_operation
        self.speed_operation = speed_operation
        self.hit_box_color_operation = hit_box_color_operation
        self.weight_operation = weight_operation
        self.animations_operation = animations_operation
        self.play_animation_operation = play_animation_operation
        self.counters_operation = counters_operation
        self.other_events_operation = other_events_operation
        self.original_hit_box_operation = original_hit_box_operation
        self.image_origin_operation = image_origin_operation
        self.angle_operation = angle_operation
        self.rotated_hit_box_operation = rotated_hit_box_operation
        self.moved_rotated_hit_box_operation = moved_rotated_hit_box_operation
        self.bounding_box_operation = bounding_box_operation
        self.controls_operation = controls_operation
        self.pressed_controls_operation = pressed_controls_operation

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


class ConvexPolygon:
    @staticmethod
    def collide(p1, p2):
        """
        Return True and the MPV if the shapes collide. Otherwise, return False and
        None.

        p1 and p2 are lists of ordered pairs, the vertices of the polygons in the
        counterclockwise direction.
        """

        p1 = [np.array(v, "float64") for v in p1]
        p2 = [np.array(v, "float64") for v in p2]

        edges = ConvexPolygon.edges_of(p1)
        edges += ConvexPolygon.edges_of(p2)
        orthogonals = [ConvexPolygon.orthogonal(e) for e in edges]

        push_vectors = []
        for o in orthogonals:
            separates, pv = ConvexPolygon.is_separating_axis(o, p1, p2)

            if separates:
                # they do not collide and there is no push vector
                return False, None
            else:
                push_vectors.append(pv)

        # they do collide and the push_vector with the smallest length is the MPV
        mpv = min(push_vectors, key=(lambda v: np.dot(v, v)))

        # assert mpv pushes p1 away from p2
        d = ConvexPolygon.centers_displacement(p1, p2)  # direction from p1 to p2
        if np.dot(d, mpv) > 0:  # if it's the same direction, then invert
            mpv = -mpv

        return True, mpv

    @staticmethod
    def centers_displacement(p1, p2):
        """
        Return the displacement between the geometric center of p1 and p2.
        """
        # geometric center
        c1 = np.mean(np.array(p1), axis=0)
        c2 = np.mean(np.array(p2), axis=0)
        return c2 - c1

    @staticmethod
    def edges_of(vertices):
        """
        Return the vectors for the edges of the polygon p.

        p is a polygon.
        """
        edges = []
        N = len(vertices)

        for i in range(N):
            edge = vertices[(i + 1) % N] - vertices[i]
            edges.append(edge)

        return edges

    @staticmethod
    def orthogonal(v):
        """
        Return a 90 degree clockwise rotation of the vector v.
        """
        return np.array([-v[1], v[0]])

    @staticmethod
    def is_separating_axis(o, p1, p2):
        """
        Return True and the push vector if o is a separating axis of p1 and p2.
        Otherwise, return False and None.
        """
        min1, max1 = float("+inf"), float("-inf")
        min2, max2 = float("+inf"), float("-inf")

        for v in p1:
            projection = np.dot(v, o)

            min1 = min(min1, projection)
            max1 = max(max1, projection)

        for v in p2:
            projection = np.dot(v, o)

            min2 = min(min2, projection)
            max2 = max(max2, projection)

        if max1 >= min2 and max2 >= min1:
            d = min(max2 - min1, max1 - min2)
            # push a bit more than needed so the shapes do not overlap in future
            # tests due to float precision
            d_over_o_squared = d / np.dot(o, o) + 1e-10
            pv = d_over_o_squared * o
            return False, pv
        else:
            return True, None

    @staticmethod
    def collide_objects_with_weight(objects):
        indexes = range(len(objects))
        for obj_i_1 in indexes:
            obj_1 = objects[obj_i_1]
            for obj_i_2 in indexes[obj_i_1 + 1 :]:
                obj_2 = objects[obj_i_2]
                if Polygon.do_boxes_overlap(obj_1.bounding_box, obj_2.bounding_box):
                    movement = ConvexPolygon.collide(
                        obj_1.moved_rotated_hit_box, obj_2.moved_rotated_hit_box
                    )
                    if movement[0]:
                        total_percent = obj_1.weight + obj_2.weight
                        percent_1 = obj_1.weight / total_percent
                        percent_2 = obj_2.weight / total_percent
                        obj_1.x += float(movement[1][0]) * percent_1
                        obj_1.y += float(movement[1][1]) * percent_1
                        obj_2.x -= float(movement[1][0]) * percent_2
                        obj_2.y -= float(movement[1][1]) * percent_2


# function for drawing all things on a surface. Simple, but very useful.
# things: list of game objects or temporary game objects
# surface: the screen window
def draw_objects(objects, surface):
    for obj in objects:
        obj.draw(surface)


# function for updating all things. Simple, but very useful.
# things: list of game objects or temporary game objects
def update_objects(objects):
    for obj in objects:
        obj.update()


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    clock = pygame.time.Clock()
    man = GameObject(
        controls=[pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d],
        width=70,
        height=40,
        angle=0,
        rotation_mode="CENTER",
        # hit_box=((0, 0), (0, 60), (70, 60), (70, 30), (60, 30), (60, 50), (40, 50), (40, 30), (40, 10), (70, 10), (70, 0)),
        animations=(
            Func(
                Events.animate_start,
                {'t': 1, 'before': TempGameObject(), 'after': Func(Events.animate_end,
                                                                     {'before': TempGameObject(x=1)}
                                                                     )}
            ),
        ),
        weight=0.5,
    )

    blok = GameObject(
        controls=[pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT],
        width=100,
        height=70,
        hit_box_color=(0, 250, 200),
        angle=0,
        rotation_mode="AROUND",
        # hit_box=((0, 0), (0, 70), (75, 35), (100, 70), (100, 0)),
        animations=(
            Func(
                Events.animate_start,
                {'t': 1, 'before': TempGameObject(), 'after': Func(Events.animate_end,
                                                                   {'before': TempGameObject()}
                                                                   )}
            ),
        ),
        weight=1,
    )

    players = [man, blok]
    drawable_things = [man, blok]
    things = [man, blok]
    screen = Screen(700, 600)
    blok.animations = (
        Animations.points_to_animation(
        points=Animations.calculate_movement_points(60, ((0, 0), (50, 5), (10, 10), (0, 20), (-5, -10), (0, 0)), 'BEZIER'),
        replaced_values=('x', 'y'),
        values_operations=('+', '+'),
        animations=blok.animations
    ))

    while GameObject.check_player_events(players):
        update_objects(things)

        ConvexPolygon.collide_objects_with_weight([blok, man])

        screen.window.fill(screen.color)
        draw_objects(drawable_things, screen.window)
        pygame.display.update()

        clock.tick(60)
    pygame.quit()
