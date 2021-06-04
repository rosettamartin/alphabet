import math
from abc import ABC, abstractmethod
from xml.etree import ElementTree


class Shape(ABC):
    @abstractmethod
    def __init__(self):
        self.center = None

    @abstractmethod
    def create_element(self):
        pass

    @abstractmethod
    def rotate(self, degrees, around_point=None):
        pass

    @abstractmethod
    def flip_horizontal(self, x=None):
        pass

    @abstractmethod
    def flip_vertical(self, y=None):
        pass

    def attach_center(self, x, y):
        """
        Transform this object's `points` such that the center of this
        object is located at (`x`, `y`).
        """

        center_x, center_y = self.center
        self.translate(x - center_x,  y - center_y)

    @abstractmethod
    def translate(self, x, y):
        pass


class Polyline(Shape):
    def __init__(self, *points, center_x=None, center_y=None, **attrs):
        """
        Create a Polyline.
        If `center_x` and/or `center_y` are None (default), the center
        of the shape will be calculated automatically. These values only
        need to be specified if the shape is asymmetrical.

        :param points: List of points to draw the polyline
        :param center_x: Horizontal center of the shape
        :param center_y: Vertical center of the shape
        :param attrs: SVG polyline attributes
        """

        super().__init__()
        self.points = points
        self.attrib = {'fill': 'none', 'stroke': 'black', **attrs}

        # find center
        if center_x is None or center_y is None:
            try:
                min_x, min_y = max_x, max_y = points[0]
            except IndexError:  # no points given
                min_x, min_y = max_x, max_y = (0, 0)
            for x, y in points:
                min_x, min_y = min(min_x, x), min(min_y, y)
                max_x, max_y = max(max_x, x), max(max_y, y)
            if center_x is None:
                center_x = min_x + ((max_x - min_x) / 2)
            if center_y is None:
                center_y = min_y + ((max_y - min_y) / 2)
        self.center = (center_x, center_y)

    def create_element(self):
        """
        Create an XML Element for this shape.
        :return: An instance of xml.etree.ElementTree.Element
        """

        return ElementTree.Element(
            'polyline',
            attrib={
                # 'x1,y1 x2,y2' instead of ((x1, y1), (x2, y2))
                'points': ' '.join([
                    ','.join((str(x), str(y)))
                    for x, y in self.points]),
                **self.attrib})

    def rotate(self, degrees, around_point=None):
        """
        Rotate by `degrees` clockwise around `around_point`. If a point
        is not specified, rotate around the center of the object.

        :param degrees: Degrees to rotate the object
        :param around_point: A point to rotate around
        """

        if around_point is None:
            around_point = self.center

        # rotate points
        self.points = [
            rotate_point(point, around_point, degrees)
            for point in self.points]

        self.center = rotate_point(self.center, around_point, degrees)

    def flip_horizontal(self, x=None):
        """
        Flip the shape across the `x` value. If `x` is None, flip across
        the center of the shape.

        :param x: an x coordinate
        """

        if x is None:
            x = self.center[0]

        self.points = [
            (flip_coordinate(old_x, x), old_y)
            for old_x, old_y in self.points]

        center_x, center_y = self.center
        self.center = (flip_coordinate(center_x, x), center_y)

    def flip_vertical(self, y=None):
        """
        Flip the shape across the `y` value. If `y` is None, flip across
        the center of the shape.

        :param y: a y coordinate
        """

        if y is None:
            y = self.center[1]

        self.points = [
            (old_x, flip_coordinate(old_y, y))
            for old_x, old_y in self.points]

        center_x, center_y = self.center
        self.center = (center_x, flip_coordinate(center_y, y))

    def translate(self, x, y):
        """Move this object by `x` and `y`."""
        self.points = [
            (old_x + x, old_y + y)
            for old_x, old_y in self.points]
        center_x, center_y = self.center
        self.center = (center_x + x, center_y + y)


class Circle(Shape):
    def __init__(self, center_x, center_y, radius, **attrs):
        """
        Create a circle.

        :param center_x: The x-coordinate of the center of the circle
        :param center_y: The y-coordinate of the center of the circle
        :param radius: The radius of the circle
        :param attrs: SVG circle attributes
        """

        super().__init__()
        self.radius = radius
        self.center = (center_x, center_y)
        self.attrib = {'fill': 'none', 'stroke': 'black', **attrs}

    def create_element(self):
        """
        Create an XML Element for this shape.
        :return: An instance of xml.etree.ElementTree.Element
        """

        return ElementTree.Element(
            'circle',
            attrib={
                'cx': str(self.center[0]),
                'cy': str(self.center[1]),
                'r': str(self.radius),
                **self.attrib})

    def rotate(self, degrees, around_point=None):
        """
        Rotate by `degrees` clockwise around `around_point`.

        :param degrees: Degrees to rotate the object
        :param around_point: A point to rotate around
        """

        if around_point is None:
            # I could rotate the circle around its center,
            # or I could just not do that
            return

        self.center = rotate_point(self.center, around_point, degrees)

    def flip_horizontal(self, x=None):
        """
        Flip the shape across the `x` value. If `x` is None, flip across
        the center of the shape.

        :param x: an x coordinate
        """

        if x is None:
            return
        center_x, center_y = self.center
        self.center = (flip_coordinate(center_x, x), center_y)

    def flip_vertical(self, y=None):
        """
        Flip the shape across the `y` value. If `y` is None, flip across
        the center of the shape.

        :param y: a y coordinate
        """

        if y is None:
            return
        center_x, center_y = self.center
        self.center = (center_x, flip_coordinate(center_y, y))

    def translate(self, x, y):
        """Move this object by `x` and `y`."""
        center_x, center_y = self.center
        self.center = (center_x + x, center_y + y)


class Path(Shape):
    def __init__(self, *commands, center_x=None, center_y=None, **attrs):
        """
        Create a Path.
        If `center_x` and/or `center_y` are None (default), the center
        of the shape will be calculated automatically. These values only
        need to be specified if the shape is asymmetrical.

        :param commands: tuples of the form (command, *args)
        :param center_x: Horizontal center of the shape
        :param center_y: Vertical center of the shape
        :param attrs: SVG path attributes
        """

        super().__init__()
        self.commands = [c for c in commands if c]
        self.attrib = {'fill': 'none', 'stroke': 'black', **attrs}

        # find center
        if center_x is None or center_y is None:
            x, y = self.get_center()
            if center_x is None:
                center_x = x
            if center_y is None:
                center_y = y
        self.center = (center_x, center_y)

    def get_center(self):
        """
        Find the center of the shape, based on the coordinates in the
        commands.

        :return: The (x, y) coordinates of the center
        """

        try:
            c, min_x, min_y = c, max_x, max_y = self.commands[0]
        except IndexError:  # no commands given
            return 0, 0
        for command in self.commands:
            if command[0].lower() == 'v':
                # vertical line, only has y coordinate
                y = command[1]
                x = None
            else:
                try:
                    x = command[1]
                    try:
                        y = command[2]
                    except IndexError:
                        y = None
                except IndexError:
                    x, y = None, None
            if x is not None:
                min_x, max_x = min(min_x, x), max(max_x, x)
            if y is not None:
                min_y, max_y = min(min_y, y), max(max_y, y)
        return (
            min_x + ((max_x - min_x) / 2),
            min_y + ((max_y - min_y) / 2))

    def create_element(self):
        """
        Create an XML Element for this shape.
        :return: An instance of xml.etree.ElementTree.Element
        """

        return ElementTree.Element(
            'path',
            attrib={
                # 'M x1,y1 Lx2,y2' instead of (('M', x1, y1), ('L', x2, y2))
                'd': ' '.join(
                    '{c} {coords}'.format(
                        c=command[0],
                        coords=','.join([str(c) for c in command[1:]]))
                    for command in self.commands),
                **self.attrib})

    def rotate(self, degrees, around_point=None):
        """
        Rotate by `degrees` clockwise around `around_point`. If a point
        is not specified, rotate around the center of the object.

        :param degrees: Degrees to rotate the object
        :param around_point: A point to rotate around
        """

        if around_point is None:
            around_point = self.center

        # rotate the x and y coordinates in all commands
        new_commands = []
        x = 0
        y = 0
        for command in self.commands:
            c = command[0]
            if c.lower() == 'v':
                # vertical line, only has y coordinate
                y = command[1]
                # keep the previous x
            else:
                try:
                    x = command[1]
                    try:
                        y = command[2]
                    except IndexError:
                        print('TEST1')
                        pass  # keep the previous y
                except IndexError:
                    print('test2')
                    pass  # keep the previous x
            point = (x, y)
            new_point = rotate_point(point, around_point, degrees)
            if c.lower() == 'v':
                new_point = new_point[1:]  # exclude x coordinate
            # make sure the new command has the same length
            new_commands.append((c, *new_point)[:len(command)])
        self.commands = new_commands

        self.center = rotate_point(self.center, around_point, degrees)

    def flip_horizontal(self, x=None):
        """
        Flip the shape across the `x` value. If `x` is None, flip across
        the center of the shape.

        :param x: an x coordinate
        """

        if x is None:
            x = self.center[0]

        # flip across the x value in all commands
        new_commands = []
        for command in self.commands:
            c = command[0]
            if c.lower() == 'v':
                # only has y value, don't alter command
                new_commands.append(command)
            else:
                try:
                    old_x = command[1]
                    command[1] = flip_coordinate(old_x, x)
                    new_commands.append(command)
                except IndexError:
                    # no coordinates, don't alter command
                    new_commands.append(command)
        self.commands = new_commands

        center_x, center_y = self.center
        self.center = (flip_coordinate(center_x, x), center_y)

    def flip_vertical(self, y=None):
        """
        Flip the shape across the `y` value. If `y` is None, flip across
        the center of the shape.

        :param y: a y coordinate
        """

        if y is None:
            y = self.center[1]

        # flip across the y value in all commands
        new_commands = []
        for command in self.commands:
            c = command[0]
            if c.lower() == 'v':
                # only has y value, flip
                old_y = command[1]
                command[1] = flip_coordinate(old_y, y)
            else:
                try:
                    old_y = command[2]
                    command[2] = flip_coordinate(old_y, y)
                    new_commands.append(command)
                except IndexError:
                    # no coordinates, don't alter command
                    new_commands.append(command)
        self.commands = new_commands

        center_x, center_y = self.center
        self.center = (center_x, flip_coordinate(center_y, y))

    def translate(self, x, y):
        """Move this object by `x` and `y`."""
        new_commands = []
        for command in self.commands:
            command = list(command)
            c = command[0]
            if c.lower() == 'v':
                command[1] += y
            else:
                try:
                    command[1] += x
                    try:
                        command[2] += y
                    except IndexError:
                        pass
                except IndexError:
                    pass
            new_commands.append(command)
        self.commands = new_commands

        center_x, center_y = self.center
        self.center = (center_x + x, center_y + y)


class Group(Shape):
    def __init__(self, *items):
        """
        Create a group of Shapes.

        :param items: A list of Shape Objects.
        """

        super().__init__()
        self.items = items

        # set center to the average of each item's center
        x_centers = []
        y_centers = []
        for item in items:
            x, y = item.center
            x_centers.append(x)
            y_centers.append(y)
        self.center = (
            sum(x_centers) / len(x_centers),
            sum(y_centers) / len(y_centers))

    def create_element(self):
        g = ElementTree.Element('g')
        for item in self.items:
            g.insert(1, item.create_element())
        return g

    def rotate(self, degrees, around_point=None):
        """
        Rotate by `degrees` clockwise around `around_point`. If a point
        is not specified, rotate around the center of the object.

        :param degrees: Degrees to rotate the object
        :param around_point: A point to rotate around
        """

        if around_point is None:
            around_point = self.center

        for item in self.items:
            item.rotate(degrees, around_point=around_point)

        self.center = rotate_point(self.center, around_point, degrees)

    def flip_horizontal(self, x=None):
        """
        Flip the shape across the `x` value. If `x` is None, flip across
        the center of the shape.

        :param x: an x coordinate
        """

        if x is None:
            x = self.center[0]

        for item in self.items:
            item.flip_horizontal(x)

        center_x, center_y = self.center
        self.center = (flip_coordinate(center_x, x), center_y)

    def flip_vertical(self, y=None):
        """
        Flip the shape across the `y` value. If `y` is None, flip across
        the center of the shape.

        :param y: a y coordinate
        """

        if y is None:
            y = self.center[1]

        for item in self.items:
            item.flip_vertical(y)

        center_x, center_y = self.center
        self.center = (center_x, flip_coordinate(center_y, y))

    def translate(self, x, y):
        """Move this object by `x` and `y`."""
        for item in self.items:
            item.translate(x, y)
        center_x, center_y = self.center
        self.center = (center_x + x, center_y + y)


def flip_coordinate(coord_a, coord_b):
    """
    Flip `coord_a` to the other side of `coord_b`.

    :param coord_a: an int coordinate
    :param coord_b: an int coordinate
    :return: the new value of coord_a
    """

    difference = coord_b - coord_a
    return coord_a + (2 * difference)


def rotate_point(point_a, point_b, degrees):
    """
    Rotate `point_a` around `point_b` and return the new coordinates of
    `point_a`.

    :param point_a: A 2-tuple of x and y coordinates
    :param point_b:  A 2-tuple of x and y coordinates
    :param degrees: Degrees to rotate the point
    :return: A 2-tuple of the new coordinates
    """

    if point_a == point_b:
        return point_a

    x, y = point_a
    around_x, around_y = point_b
    radians = math.radians(degrees)
    cos_radians = round(math.cos(radians), 2)
    sin_radians = round(math.sin(radians), 2)
    # subtract point b to get coordinates relative to point b
    relative_x, relative_y = x - around_x, y - around_y
    # rotate x around center
    new_relative_x = relative_x * cos_radians - relative_y * sin_radians
    # rotate y around center
    new_relative_y = relative_x * sin_radians + relative_y * cos_radians
    # add center back
    return new_relative_x + around_x, new_relative_y + around_y
