import numpy as np
import pygame

# Класс для кривых
class Bezier:
    def TwoPoints(t, P1, P2):
        if not isinstance(P1, np.ndarray) or not isinstance(P2, np.ndarray):
            raise TypeError('Points must be an instance of the numpy.ndarray!')
        if not isinstance(t, (int, float)):
            raise TypeError('Parameter t must be an int or float!')

        Q1 = (1 - t) * P1 + t * P2
        return Q1

    def Points(t, points):
        newpoints = []
        for i1 in range(0, len(points) - 1):
            newpoints += [Bezier.TwoPoints(t, points[i1], points[i1 + 1])]
        return newpoints

    def Point(t, points):
        newpoints = points
        while len(newpoints) > 1:
            newpoints = Bezier.Points(t, newpoints)
        return newpoints[0]

    def Curve(t_values, points):
        if not hasattr(t_values, '__iter__'):
            raise TypeError("`t_values` Must be an ITERABLE of integers or floats, of length greater than 0 .")
        if len(t_values) < 1:
            raise TypeError("`t_values` Must be an iterable of integers or floats, of LENGTH greater than 0 .")
        if not isinstance(t_values[0], (int, float)):
            raise TypeError("`t_values` Must be an iterable of INTEGERS OR FLOATS, of length greater than 0 .")

        curve = np.array([[0.0] * len(points[0])])
        for t in t_values:
            curve = np.append(curve, [Bezier.Point(t, points)], axis=0)
        curve = np.delete(curve, 0, 0)
        return curve


# Класс для любого объекта игры
class Player(object):
    def __init__(self, x=0, y=0, width=10, height=10, x_off=0, y_off=0, width_off=1, height_off=1,
                 controls=[None, None, None, None], pressedValue=[0, 0, 0, 0], speed=[1, 1, 1, 1],
                 icon=None, color=(255, 0, 0), sound=None,
                 animations=[], counters=[]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.x_off = x_off
        self.y_off = y_off
        self.width_off = width_off
        self.height_off = height_off

        self.controls = controls
        if type(pressedValue) != list:
            if type(controls) == list:
                self.pressedValue = [0, ] * len(controls)
            else:
                self.pressedValue = None
        else:
            self.pressedValue = pressedValue
        self.speed = speed

        if icon:
            self.icon = icon
        else:
            self.icon = None
        self.color = color
        self.sound = sound

        self.animations = animations
        self.selectedAnimation = 0
        self.playAnimation = 1
        self.counters = counters

    def update(self):
        if self.pressedValue:
            try:
                if self.pressedValue[0]:
                    self.y -= self.speed[0]
                if self.pressedValue[1]:
                    self.x -= self.speed[1]
                if self.pressedValue[2]:
                    self.y += self.speed[2]
                if self.pressedValue[3]:
                    self.x += self.speed[3]
            except IndexError:
                pass
        if self.counters:
            for counter in self.counters:
                counter.update()
                if (counter.count == counter.range[0] or counter.count == counter.range[1]) and type(counter.value) == TempPlayer:
                    c = counter.value
                    if c.x != '':
                        if c.xSorO[0] == 'S':
                            if c.xSorO[1] == 'P':
                                self.x += c.x
                            else:
                                self.x *= c.x
                        else:
                            self.x = c.x
                    if c.y != '':
                        if c.ySorO[0] == 'S':
                            if c.ySorO[1] == 'P':
                                self.y += c.y
                            else:
                                self.y *= c.y
                        else:
                            self.y = c.y
                    if c.width != '':
                        if c.widthSorO[0] == 'S':
                            if c.widthSorO[1] == 'P':
                                self.width += c.width
                            else:
                                self.width *= c.width
                        else:
                            self.width = c.width
                    if c.height != '':
                        if c.heightSorO[0] == 'S':
                            if c.heightSorO[1] == 'P':
                                self.height += c.height
                            else:
                                self.height *= c.height
                        else:
                            self.height = c.height
                    if c.x_off != '':
                        if c.x_offSorO[0] == 'S':
                            if c.x_offSorO[1] == 'P':
                                self.x_off += c.x_off
                            else:
                                self.x_off *= c.x_off
                        else:
                            self.x_off = c.x_off
                    if c.y_off != '':
                        if c.y_offSorO[0] == 'S':
                            if c.y_offSorO[1] == 'P':
                                self.y_off += c.y_off
                            else:
                                self.y_off *= c.y_off
                        else:
                            self.y_off = c.y_off
                    if c.width_off != '':
                        if c.width_offSorO[0] == 'S':
                            if c.width_offSorO[1] == 'P':
                                self.width_off += c.width_off
                            else:
                                self.width_off *= c.width_off
                        else:
                            self.width_off = c.width_off
                    if c.height_off != '':
                        if c.height_offSorO[0] == 'S':
                            if c.height_offSorO[1] == 'P':
                                self.height_off += c.height_off
                            else:
                                self.height_off *= c.height_off
                        else:
                            self.height_off = c.height_off
                    if c.controls != '':
                        self.controls = c.controls
                    if c.pressedValue != '':
                        self.pressedValue = c.pressedValue
                    if c.speed != '':
                        if c.speedSorO[0] == 'S':
                            if c.speedSorO[1] == 'P':
                                self.speed = [self.speed[0] + c.speed[0], self.speed[1] + c.speed[1],
                                              self.speed[2] + c.speed[2], self.speed[3] + c.speed[3]]
                            else:
                                self.speed = [self.speed[0] * c.speed[0], self.speed[1] * c.speed[1],
                                              self.speed[2] * c.speed[2], self.speed[3] * c.speed[3]]
                        else:
                            self.speed = c.speed
                    if c.icon != '':
                        self.icon = c.icon
                    if c.color != '':
                        if c.colorSorO[0] == 'S':
                            if c.colorSorO[1] == 'P':
                                self.color = (self.color[0] + c.color[0], self.color[1] + c.color[1], self.color[2] + c.color[2])
                            else:
                                self.color = (self.color[0] * c.color[0], self.color[1] * c.color[1], self.color[2] * c.color[2])
                        else:
                            self.color = c.color
                    if c.sound != '':
                        self.sound = c.sound
                    if c.animations != '':
                        self.animations = c.animations
                    if c.selectedAnimation != '':
                        self.selectedAnimation = c.selectedAnimation
                    if c.playAnimation != '':
                        self.playAnimation = c.playAnimation
                    if c.counters != '':
                        self.counters = c.counters
                    else:
                        self.counters.remove(counter)
                    del counter
                    del c

    def tempvarchange(self, t, x='', y='', width='', height='', x_off='', y_off='', width_off='', height_off='',
                 controls='', pressedValue='', speed='',
                 icon='', color='', sound='',
                 animations='', selectedAnimation='', playAnimation='', counters='',
                 xSorO='SP', ySorO='SP', widthSorO='SP', heightSorO='SP', x_offSorO='SP', y_offSorO='SP', width_offSorO='SP', height_offSorO='SP', speedSorO='SP', colorSorO='SP',
                 bx='', by='', bwidth='', bheight='', bx_off='', by_off='', bwidth_off='', bheight_off='',
                 bcontrols='', bpressedValue='', bspeed='',
                 bicon='', bcolor='', bsound='',
                 banimations='', bselectedAnimation='', bplayAnimation='', bcounters='',
                 bxSorO='SP', bySorO='SP', bwidthSorO='SP', bheightSorO='SP', bx_offSorO='SP', by_offSorO='SP', bwidth_offSorO='SP', bheight_offSorO='SP', bspeedSorO='SP', bcolorSorO='SP',):
        temp = Counter(count=t, changeRange=[0, t+1], changePerSecond=1, value=TempPlayer(x=bx, y=by,
                 width=bwidth, height=bheight, x_off=bx_off, y_off=by_off, width_off=bwidth_off, height_off=bheight_off,
                 controls=bcontrols, pressedValue=bpressedValue, speed=bspeed,
                 icon=bicon, color=bcolor, sound=bsound,
                 animations=banimations, selectedAnimation=bselectedAnimation, playAnimation=bplayAnimation, counters=bcounters,
                 xSorO=bxSorO, ySorO=bySorO, widthSorO=bwidthSorO, heightSorO=bheightSorO, x_offSorO=bx_offSorO, y_offSorO=by_offSorO, width_offSorO=bwidth_offSorO, height_offSorO=bheight_offSorO, speedSorO=bspeedSorO, colorSorO=bcolorSorO))
        if x != '':
            if xSorO[0] == 'S':
                if xSorO[1] == 'P':
                    self.x += x
                else:
                    self.x *= x
            else:
                self.x = x
        if y != '':
            if ySorO[0] == 'S':
                if ySorO[1] == 'P':
                    self.y += y
                else:
                    self.y *= y
            else:
                self.y = y
        if width != '':
            if widthSorO[0] == 'S':
                if widthSorO[1] == 'P':
                    self.width += width
                else:
                    self.width *= width
            else:
                self.width = width
        if height != '':
            if heightSorO[0] == 'S':
                if heightSorO[1] == 'P':
                    self.height += height
                else:
                    self.height *= height
            else:
                self.height = height
        if x_off != '':
            if x_offSorO[0] == 'S':
                if x_offSorO[1] == 'P':
                    self.x_off += x_off
                else:
                    self.x_off *= x_off
            else:
                self.x_off = x_off
        if y_off != '':
            if y_offSorO[0] == 'S':
                if y_offSorO[1] == 'P':
                    self.y_off += y_off
                else:
                    self.y_off *= y_off
            else:
                self.y_off = y_off
        if width_off != '':
            if width_offSorO[0] == 'S':
                if width_offSorO[1] == 'P':
                    self.width_off += width_off
                else:
                    self.width_off *= width_off
            else:
                self.width_off = width_off
        if height_off != '':
            if height_offSorO[0] == 'S':
                if height_offSorO[1] == 'P':
                    self.height_off += height_off
                else:
                    self.height_off *= height_off
            else:
                self.height_off = height_off
        if controls != '':
            self.controls = controls
        if pressedValue != '':
            self.pressedValue = pressedValue
        if speed != '':
            self.speed = speed

        if icon != '':
            self.icon = icon
        if color != '':
            self.color = color
        if sound != '':
            self.sound = sound

        if animations != '':
            self.animations = animations
        if selectedAnimation != '':
            self.selectedAnimation = selectedAnimation
        if playAnimation != '':
            self.playAnimation = playAnimation
        if counters != '':
            self.counters = counters
        self.counters += [temp]

    def draw(self, surface):
        if self.icon:
            surface.blit(pygame.transform.scale(self.icon, (self.width * self.width_off, self.height * self.height_off)), (self.x + self.x_off, self.y + self.y_off))
        else:
            pygame.draw.rect(surface, self.color, pygame.Rect(self.x + self.x_off, self.y + self.y_off, self.width * self.width_off, self.height * self.height_off))


class TempPlayer(Player):
    def __init__(self, x='', y='', width='', height='', x_off='', y_off='', width_off='', height_off='',
                 controls='', pressedValue='', speed='',
                 icon='', color='', sound='',
                 animations='', selectedAnimation='', playAnimation='', counters='',
                 xSorO='SP', ySorO='SP', widthSorO='SP', heightSorO='SP', x_offSorO='SP', y_offSorO='SP', width_offSorO='SP', height_offSorO='SP', speedSorO='SP', colorSorO='SP'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.x_off = x_off
        self.y_off = y_off
        self.width_off = width_off
        self.height_off = height_off

        self.controls = controls
        self.pressedValue = pressedValue
        self.speed = speed

        self.icon = icon
        self.color = color
        self.sound = sound

        self.animations = animations
        self.selectedAnimation = selectedAnimation
        self.playAnimation = playAnimation
        self.counters = counters

        self.xSorO = xSorO
        self.ySorO = ySorO
        self.widthSorO = widthSorO
        self.heightSorO = heightSorO
        self.x_offSorO = x_offSorO
        self.y_offSorO = y_offSorO
        self.width_offSorO = width_offSorO
        self.height_offSorO = height_offSorO
        self.speedSorO = speedSorO
        self.colorSorO = colorSorO

        self.initialized = False

    def update(self):
        if self.initialized:
            super().update()


class Screen(object):
    def __init__(self, width=300, height=300, color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.color = color
        self.window = pygame.display.set_mode((self.width, self.height))


class Animation(object):
    def __init__(self, points, curve_type="LINE"):
        self.points = points
        self.curve_type = curve_type

    def calc_points(self, t=60):
        movementpoints = []
        if self.curve_type == "LINE" or self.curve_type == "SPRITE":
            movementpoints = extend_linear_movement(global_points2local_movement(self.points), t=t)
        elif self.curve_type == "BEZIER":
            t_points = np.arange(0, 1, 1/t)
            points1 = np.array(self.points)
            points = Bezier.Curve(t_points, points1)
            points = points - points[0]
            for p in range(len(points)-1):
                nextpoint = [points[p+1][0] - points[p][0], points[p+1][1] - points[p][1]]
                movementpoints.append(nextpoint)
        return movementpoints


class Counter(object):
    def __init__(self, count, changeRange, changePerSecond, value):
        self.count = count
        self.range = changeRange
        self.decrease = changePerSecond
        self.value = value

    def update(self):
        if self.range[0] < self.count < self.range[1]:
            self.count -= self.decrease


def global_points2local_movement(points):
    finalpoints = []

    for point in range(len(points) - 1):
        nextpoint = []
        for p in range(len(points[point])):
            if type(points[point][p]) in [int, float] and type(points[point + 1][p]) in [int, float]:
                nextpoint.append(points[point + 1][p] - points[point][p])
            else:
                nextpoint.append(points[point + 1][p])
        finalpoints.append(nextpoint)
    return finalpoints


def extend_linear_movement(points, t=60):
    finalpoints = []

    time = int(t/len(points))

    if time < 1:
        time = 1

    for point in points:
        nextpoint = []
        for p in point:
            if type(p) in [int, float]:
                nextpoint.append(p/time)
            else:
                nextpoint.append(p)
        for i in range(time):
            finalpoints.append(nextpoint)

    return finalpoints


def check_events(players):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
            for player in players:
                for k in range(0, len(player.controls)):
                    if event.key == player.controls[k]:
                        player.pressedValue[k] = 1 if event.type == pygame.KEYDOWN else 0
                        break
    return True


def draw_things(things, surface):
    for thing in things:
        thing.draw(surface)


def update_things(things):
    for thing in things:
        thing.update()


def collide_rectangles(movable_rect, static_rect):
    if pygame.Rect(movable_rect.x, movable_rect.y, movable_rect.width, movable_rect.height).colliderect(pygame.Rect(static_rect.x, static_rect.y, static_rect.width, static_rect.height)):

        cost_down = static_rect.y + static_rect.height - movable_rect.y
        cost_up = movable_rect.y + movable_rect.height - static_rect.y
        cost_right = static_rect.x + static_rect.width - movable_rect.x
        cost_left = movable_rect.x + movable_rect.width - static_rect.x
        cost_min = min(cost_down, cost_up, cost_right, cost_left)
        if cost_min == cost_left:
            return ["LEFT", cost_left]
        if cost_min == cost_right:
            return ["RIGHT", cost_right]
        if cost_min == cost_up:
            return ["UP", cost_up]
        if cost_min == cost_down:
            return ["DOWN", cost_down]


if __name__ == "__main__":
    clock = pygame.time.Clock()
    man = Player(controls=[pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d], width=70, height=50, icon=pygame.image.load("1.png"))
    blok = Player(controls=[pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT], width=50, height=30, color=(0, 255, 255), animations=[Animation(points=[[0, 0], [50, -10], [20, 0], [10, 20], [60, 100], [0, -5]], curve_type="BEZIER"), Animation(points=[[0, 0], [30, 15], [-15, 30], [0, 5], [1, 1]], curve_type="LINE")])
    players = [man, blok]
    drawablethings = [man, blok]
    things = [man, blok]
    screen = Screen()
    pygame.init()

    while check_events(players):
        update_things(things)
        screen.window.fill(screen.color)
        draw_things(drawablethings, screen.window)
        pygame.display.update()
        clock.tick(60)
    pygame.quit()
