import numpy as np
import pygame


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
                # Copypasta, very annoying
                # I have to do this because putting all those values (animations[i][1].x, animations[i][1].y, etc.)
                # in a list will be useless, as those values will only be copied. Links will be made to the values, not
                # the names. That's why this very long, extremely annoying copypasta which is hard to maintain.
                # If anybody reading this knows how to avoid this mess, PLEASE tell me!!!
                if replaced_values[j] == 'x':
                    # If the operation is =, we set the value to the point
                    if values_operations[j] == '=':
                        animations[i][1].x = points[i][j]
                    # If the operation is +, we add the value to the point (negative numbers for subtraction)
                    elif values_operations[j] == '+':
                        animations[i][1].x += points[i][j]
                    # If the operation is *, we multiply the value by the point (floats between 0 and 1 for division)
                    elif values_operations[j] == '*':
                        animations[i][1].x *= points[i][j]
                elif replaced_values[j] == 'y':
                    if values_operations[j] == '=':
                        animations[i][1].y = points[i][j]
                    elif values_operations[j] == '+':
                        animations[i][1].y += points[i][j]
                    elif values_operations[j] == '*':
                        animations[i][1].y *= points[i][j]
                elif replaced_values[j] == 'width':
                    if values_operations[j] == '=':
                        animations[i][1].width = points[i][j]
                    elif values_operations[j] == '+':
                        animations[i][1].width += points[i][j]
                    elif values_operations[j] == '*':
                        animations[i][1].width *= points[i][j]
                elif replaced_values[j] == 'height':
                    if values_operations[j] == '=':
                        animations[i][1].height = points[i][j]
                    elif values_operations[j] == '+':
                        animations[i][1].height += points[i][j]
                    elif values_operations[j] == '*':
                        animations[i][1].height *= points[i][j]
                elif replaced_values[j] == 'x_offset':
                    if values_operations[j] == '=':
                        animations[i][1].x_offset = points[i][j]
                    elif values_operations[j] == '+':
                        animations[i][1].x_offset += points[i][j]
                    elif values_operations[j] == '*':
                        animations[i][1].x_offset *= points[i][j]
                elif replaced_values[j] == 'y_offset':
                    if values_operations[j] == '=':
                        animations[i][1].y_offset = points[i][j]
                    elif values_operations[j] == '+':
                        animations[i][1].y_offset += points[i][j]
                    elif values_operations[j] == '*':
                        animations[i][1].y_offset *= points[i][j]
                elif replaced_values[j] == 'width_offset':
                    if values_operations[j] == '=':
                        animations[i][1].width_offset = points[i][j]
                    elif values_operations[j] == '+':
                        animations[i][1].width_offset += points[i][j]
                    elif values_operations[j] == '*':
                        animations[i][1].width_offset *= points[i][j]
                elif replaced_values[j] == 'height_offset':
                    if values_operations[j] == '=':
                        animations[i][1].height_offset = points[i][j]
                    elif values_operations[j] == '+':
                        animations[i][1].height_offset += points[i][j]
                    elif values_operations[j] == '*':
                        animations[i][1].height_offset *= points[i][j]
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
    def __init__(self, x=0, y=0, width=10, height=10, x_offset=0, y_offset=0, width_offset=1, height_offset=1,
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
            self.counters = self.counters + (after_counter, )

    # Draws the game object on the surface
    # The surface usually should be a screen
    def draw(self, surface):
        # If we have an icon, we do the following
        if self.icon:
            # TODO: Rotation
            surface.blit(
                # 1. Transform the image according to our size times offset
                pygame.transform.scale(
                    self.icon, (self.width * self.width_offset, self.height * self.height_offset)
                ),
                # 2. Blit our image according to our coordinates plus offset
                (self.x + self.x_offset, self.y + self.y_offset)
            )
        # If we don't have an icon, we do the following
        else:
            try:
                pygame.draw.rect(
                    surface, self.color,
                    # 1. Create a rect object according to our size times offset, and our coordinates plus offset
                    pygame.Rect(
                        self.x + self.x_offset, self.y + self.y_offset,
                        self.width * self.width_offset, self.height * self.height_offset
                    )
                    # 2. Blit our rect to the surface
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
        # This copypasta again... I don't want to support this. I don't want to use this. Help me.
        # If this variable isn't an empty string,
        if object_replace_with.x != '':
            # And if it's operation for replacement is a plus,
            if object_replace_with.x_operation == '+':
                # We add it to the according variable of object replaced.
                object_replaced.x += object_replace_with.x
            # And if it's operation for replacement is multiplication,
            elif object_replace_with.x_operation == '*':
                # We multiply the according variable of object replaced by it.
                object_replaced.x *= object_replace_with.x
            # And if it's operation for replacement is equals,
            elif object_replace_with.x_operation == '=':
                # We set the according variable of object replaced to it.
                object_replaced.x = object_replace_with.x
        if object_replace_with.y != '':
            if object_replace_with.y_operation == '+':
                object_replaced.y += object_replace_with.y
            elif object_replace_with.y_operation == '*':
                object_replaced.y *= object_replace_with.y
            elif object_replace_with.y_operation == '=':
                object_replaced.y = object_replace_with.y
        if object_replace_with.width != '':
            if object_replace_with.width_operation == '+':
                object_replaced.width += object_replace_with.width
            elif object_replace_with.width_operation == '*':
                object_replaced.width *= object_replace_with.width
            elif object_replace_with.width_operation == '=':
                object_replaced.width = object_replace_with.width
        if object_replace_with.height != '':
            if object_replace_with.height_operation == '+':
                object_replaced.height += object_replace_with.height
            elif object_replace_with.height_operation == '*':
                object_replaced.height *= object_replace_with.height
            elif object_replace_with.height_operation == '=':
                object_replaced.height = object_replace_with.height
        if object_replace_with.x_offset != '':
            if object_replace_with.x_offset_operation == '+':
                object_replaced.x_offset += object_replace_with.x_offset
            elif object_replace_with.x_offset_operation == '*':
                object_replaced.x_offset *= object_replace_with.x_offset
            elif object_replace_with.x_offset_operation == '=':
                object_replaced.x_offset = object_replace_with.x_offset
        if object_replace_with.y_offset != '':
            if object_replace_with.y_offset_operation == '+':
                object_replaced.y_offset += object_replace_with.y_offset
            elif object_replace_with.y_offset_operation == '*':
                object_replaced.y_offset *= object_replace_with.y_offset
            elif object_replace_with.y_offset_operation == '=':
                object_replaced.y_offset = object_replace_with.y_offset
        if object_replace_with.width_offset != '':
            if object_replace_with.width_offset_operation == '+':
                object_replaced.width_offset += object_replace_with.width_offset
            elif object_replace_with.width_offset_operation == '*':
                object_replaced.width_offset *= object_replace_with.width_offset
            elif object_replace_with.width_offset_operation == '=':
                object_replaced.width_offset = object_replace_with.width_offset
        if object_replace_with.height_offset != '':
            if object_replace_with.height_offset_operation == '+':
                object_replaced.height_offset += object_replace_with.height_offset
            elif object_replace_with.height_offset_operation == '*':
                object_replaced.height_offset *= object_replace_with.height_offset
            elif object_replace_with.height_offset_operation == '=':
                object_replaced.height_offset = object_replace_with.height_offset
        if object_replace_with.controls != '':
            object_replaced.controls = object_replace_with.controls
        if object_replace_with.pressed_controls != '':
            object_replaced.pressed_controls = list(object_replace_with.pressed_controls)
        if object_replace_with.speed != '':
            if object_replace_with.speed_operation == '+':
                new_speed = []
                for i in range(len(object_replaced.speed)):
                    new_speed.append(object_replaced.speed[i] + object_replace_with.speed[i])
                object_replaced.speed = tuple(new_speed)
            elif object_replace_with.speed_operation == '*':
                new_speed = []
                for i in range(len(object_replaced.speed)):
                    new_speed.append(object_replaced.speed[i] * object_replace_with.speed[i])
                object_replaced.speed = tuple(new_speed)
            elif object_replace_with.speed_operation == '=':
                object_replaced.speed = object_replace_with.speed
        if object_replace_with.icon != '':
            object_replaced.icon = object_replace_with.icon
        if object_replace_with.color != '':
            if object_replace_with.color_operation == '+':
                new_color = []
                for i in range(len(object_replaced.color)):
                    new_color.append(object_replaced.color[i] + object_replace_with.color[i])
                object_replaced.color = tuple(new_color)
            elif object_replace_with.color_operation == '*':
                new_color = []
                for i in range(len(object_replaced.color)):
                    new_color.append(object_replaced.color[i] * object_replace_with.color[i])
                object_replaced.color = tuple(new_color)
            elif object_replace_with.color_operation == '=':
                object_replaced.color = object_replace_with.color
        if object_replace_with.sound != '':
            object_replaced.sound = object_replace_with.sound
        if object_replace_with.animations != '':
            object_replaced.animations = object_replace_with.animations
        if object_replace_with.play_animation != '':
            object_replaced.play_animation = object_replace_with.play_animation
        if object_replace_with.counters != '':
            object_replaced.counters = object_replace_with.counters

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
    def collide_rectangles(movable_rect, static_rect):
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


# class for temporary game objects. Mostly used for temporary variable changes, and animations.
class TempGameObject(GameObject):
    # All the variables serve the same function as game object variables. They can also be empty strings, if we wish not
    # to replace that value. The _operation variables give directions to change_variables function, the operation
    # corresponding to the operation
    def __init__(self, x='', y='', width='', height='', x_offset='', y_offset='', width_offset='', height_offset='',
                 controls='', pressed_controls='', speed='',
                 icon='', color='', sound='',
                 animations='', play_animation='', counters='',
                 x_operation='+', y_operation='+', width_operation='+', height_operation='+',
                 x_offset_operation='+', y_offset_operation='+', width_offset_operation='+',
                 height_offset_operation='+',
                 speed_operation='+', color_operation='+'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.width_offset = width_offset
        self.height_offset = height_offset

        self.controls = controls
        self.pressed_controls = pressed_controls
        # We have to turn the pressed controls variable into a tuple because of some bug that happens when it's mutable.
        self.pressed_controls = tuple(self.pressed_controls)
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

        # The initialized variable makes the temporary game object update if it's true. This is only useful for
        # temporary game objects that update, and are in animations.
        self.initialized = False

    def update(self):
        if self.initialized:
            super().update()


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
    man = GameObject(controls=[pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d], width=70, height=50)

    blok = GameObject(controls=[pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT], width=50, height=30,
                      color=(0, 255, 255))
    players = [man, blok]
    drawablethings = [man, blok]
    things = [man, blok]
    screen = Screen()
    pygame.init()

    while GameObject.check_events(players):
        update_things(things)
        screen.window.fill(screen.color)
        draw_things(drawablethings, screen.window)
        pygame.display.update()
        clock.tick(60)
    pygame.quit()
