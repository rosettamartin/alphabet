import os
from xml.etree import ElementTree
from xml.dom import minidom

from .shapes import Circle, Group, Path, Polyline


class Consonant(Group):
    def __init__(self, *items):
        # TODO add more kwargs when necessary
        super().__init__(*items)


class Vowel(Group):
    def __init__(self, *items):
        # TODO specify points where letters should be attached
        super().__init__(*items)


def pformat(xml_element, indent='\t'):
    return minidom.parseString(ElementTree.tostring(xml_element)).toprettyxml(
        indent=indent)


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
        Polyline((0, 0), (6, 0), center_y=5)),
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
        Polyline((0, 5), (6, 2), center_y=5)),
    'g': Consonant(
        Polyline((0, 5), (6, 8), center_y=5)),
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
        Polyline((6, 24), (6, 6), (24, 6))),
    'u': Vowel(
        Polyline((6, 6), (24, 6), (24, 24))),
    'e': Vowel(
        Polyline((6, 6), (6, 24), (24, 24))),
    'o': Vowel(
        Polyline((6, 24), (24, 24), (24, 6))),
    'a': Vowel(
        Polyline((6, 24), (6, 6), (24, 6)),
        Polyline((1, 24), (1, 29), (6, 29)))}

if __name__ == '__main__':
    # import copy

    i = alphabet['i']
    # p = alphabet['p']
    # p2 = copy.copy(p)
    p = alphabet['nTEST']
    p2 = alphabet['l']

    p.rotate(90)
    p.attach_center(0, 9)
    p2.attach_center(9, 0)

    group = Group(p, i, p2)
    group.translate(6, 6)

    svg = ElementTree.Element(
        'svg', attrib={
            'viewbox': '0 0 31 31',
            'xmlns': 'http://www.w3.org/2000/svg'})
    svg.insert(1, group.create_element())

    if not os.path.isdir('tests'):
        os.mkdir('tests')
    with open('tests/test.svg', 'w') as f:
        f.write(pformat(svg))
