import math

from shapes import Circle, Group, Path, Polyline


class Consonant(Group):
    def __init__(self, *items, descends=True, end_char=False):
        super().__init__(*items)
        self.descends = descends
        self.end_char = end_char


class Vowel(Group):
    def __init__(self, start_point, middle_point, end_point, *items,
                 flip_onset=False, rotate_onset=0,
                 flip_coda=False, rotate_coda=0):
        self.items = None
        self.start_point = start_point
        self.middle_point = middle_point
        self.end_point = end_point
        self.flip_onset = flip_onset
        self.rotate_onset = rotate_onset
        self.flip_coda = flip_coda
        self.rotate_coda = rotate_coda
        super().__init__(
            Polyline(start_point, middle_point, end_point),
            *items)

    def add_consonants(self, onset, coda, character_width, character_height):
        # flip and rotate each shape if necessary
        for shape in onset:
            if self.flip_onset:
                shape.flip_vertical()
            if self.rotate_onset:
                shape.rotate(self.rotate_onset)
        for shape in coda:
            if shape.end_char:
                # end_chars are always opposite direction in coda
                shape.flip_horizontal()
            if self.flip_coda:
                shape.flip_vertical()
            if self.rotate_coda:
                shape.rotate(self.rotate_coda)

        onset_empty_space = get_distance(
            self.start_point, self.middle_point)
        coda_empty_space = get_distance(
            self.middle_point, self.end_point)

        # subtract the space taken up by characters
        onset_empty_space -= character_width * len(onset)
        coda_empty_space -= character_width * len(coda)

        # take away some space if the characters on the other side
        # will get in the way
        if onset and onset[-1].descends:
            if coda[0].descends:
                coda_empty_space -= character_height / 2
        if coda and coda[0].descends:
            if onset[-1].descends:
                onset_empty_space -= character_height / 2

        onset_num_spaces = len(onset) + 1
        coda_num_spaces = len(coda) + 1
        if onset and onset[0].end_char:
            onset_num_spaces -= 1
        if coda and coda[-1].end_char:
            coda_num_spaces -= 1
        onset_padding = onset_empty_space / onset_num_spaces
        coda_padding = coda_empty_space / coda_num_spaces

        point_marker = self.start_point
        for i, cons in enumerate(onset):
            if i == 0 and cons.end_char:
                point_marker = travel_towards(
                    point_marker, self.middle_point,
                    character_width / 2)
            else:
                point_marker = travel_towards(
                    point_marker, self.middle_point,
                    onset_padding + (character_width / 2))
            cons.attach_center(*point_marker)
            point_marker = travel_towards(
                point_marker, self.middle_point,
                (character_width / 2))
            if i == 0 and cons.end_char:
                # add a point to the base vowel shape
                # instead of adding the consonant
                add_points = cons.items[0].points[:0:-1]
                self.items[0].points = (*add_points, *self.items[0].points)
            else:
                self.items = (*self.items, cons)

        # add coda consonants in reverse order
        point_marker = self.end_point
        for i, cons in enumerate(coda[::-1]):
            if i == 0 and cons.end_char:
                point_marker = travel_towards(
                    point_marker, self.middle_point,
                    character_width / 2)
            else:
                point_marker = travel_towards(
                    point_marker, self.middle_point,
                    coda_padding + (character_width / 2))
            cons.attach_center(*point_marker)
            point_marker = travel_towards(
                point_marker, self.middle_point,
                (character_width / 2))
            if i == 0 and cons.end_char:
                # add a point to the base vowel shape
                # instead of adding the consonant
                add_points = cons.items[0].points[1:]
                self.items[0].points = (*self.items[0].points, *add_points)
            else:
                self.items = (*self.items, cons)


def get_distance(point_a, point_b):
    xa, ya = point_a
    xb, yb = point_b
    horizontal = xa - xb
    vertical = ya - yb
    # pythagorean theorem
    return math.sqrt((horizontal ** 2) + (vertical ** 2))


def get_middle_point(point_a, point_b, percentage=0.5):
    xa, ya = point_a
    xb, yb = point_b
    return (
        xa + ((xb - xa) * percentage),
        ya + ((yb - ya) * percentage))


def travel_towards(point_a, point_b, distance):
    return get_middle_point(
        point_a, point_b,
        percentage=distance/get_distance(point_a, point_b))


alphabet = {
    'p': Consonant(
        Polyline((0, 10), (0, 0), (6, 0), (6, 10))),
    'b': Consonant(
        Polyline((0, 0), (0, 10), (6, 10), (6, 0))),
    'm': Consonant(
        Path(('M', 0, 0), ('L', 0, 6), ('L', 6, 6), ('L', 6, 0), ('Z',))),
    'f': Consonant(
        Polyline((6, 0), (0, 0), (0, 10), (6, 10))),
    'v': Consonant(
        Polyline((0, 0), (6, 0), (6, 10), (0, 10))),
    't': Consonant(
        Polyline((0, 0), (6, 0), center_y=5),
        descends=False),
    'd': Consonant(
        Polyline((0, 10), (6, 10), center_y=5)),
    'n': Consonant(
        Polyline((0, 0), (6, 0)),
        Polyline((0, 10), (6, 10))),
    's': Consonant(
        Polyline((0, 10), (6, 0))),
    'z': Consonant(
        Polyline((0, 0), (6, 10))),
    'l': Consonant(
        Polyline((0, 2), (6, 8)),
        Polyline((0, 8), (6, 2))),
    'k': Consonant(
        Polyline((0, 5), (6, 2), center_y=5),
        end_char=True, descends=False),
    'g': Consonant(
        Polyline((0, 5), (6, 8), center_y=5),
        end_char=True),
    'x': Consonant(
        Polyline((5, 0), (0, 5), (5, 10), center_x=3)),
    'gh': Consonant(
        Polyline((1, 0), (6, 5), (1, 10), center_x=3)),
    "'": Consonant(
        Polyline((1, 0), (1, 10)),
        Polyline((5, 0), (5, 10))),
    'h': Consonant(
        Polyline((0, 0), (6, 0), (0, 10), (6, 10))),
    'j': Consonant(
        Polyline((3, 0), (3, 10))),
    'w': Consonant(
        Circle(3, 5, 3)),
    'r': Consonant(
        Circle(3, 5, 3),
        Polyline((0, 10), (6, 0))),
    'i': Vowel(
        (6, 24), (6, 6), (24, 6),
        rotate_onset=270),
    'u': Vowel(
        (6, 6), (24, 6), (24, 24),
        rotate_coda=90),
    'e': Vowel(
        (6, 6), (6, 24), (24, 24),
        flip_onset=True, rotate_onset=90, flip_coda=True),
    'o': Vowel(
        (6, 24), (24, 24), (24, 6),
        flip_onset=True, flip_coda=True, rotate_coda=270),
    'a': Vowel(
        (6, 6), (6, 24), (24, 24),
        Polyline((1, 24), (1, 29), (6, 29), center_x=15, center_y=15),
        flip_onset=True, rotate_onset=90, flip_coda=True)}
