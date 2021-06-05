from copy import deepcopy
from xml.dom import minidom
from xml.etree import ElementTree

from alphabet import alphabet, Vowel


class SVG(ElementTree.Element):
    def __init__(self, x, y, width, height):
        super().__init__(
            'svg', attrib={
                'viewBox': f'{x} {y} {width} {height}',
                'xmlns': 'http://www.w3.org/2000/svg'})

    def to_file(self, filename):
        with open(filename, 'w') as f:
            f.write(pformat(self))


class Syllable(SVG):
    def __init__(self, string):
        super().__init__(0, 0, 31, 31)
        self.insert(1, transcribe_syllable(string).create_element())


def pformat(xml_element, indent='\t'):
    return minidom.parseString(ElementTree.tostring(xml_element)).toprettyxml(
        indent=indent)


def transcribe_syllable(text):
    onset, nucleus, coda = [], '', []
    i = 0
    digraphs = [char for char in alphabet if len(char) != 1]
    while i < len(text):
        char = text[i]
        if isinstance(alphabet[char], Vowel):
            nucleus = char
            i += 1
            continue
        else:
            for digraph in digraphs:
                if text[i:i+len(digraph)] == digraph:
                    char = digraph
                    i += len(digraph) - 1

        if nucleus:
            coda.append(char)
        else:
            onset.append(char)
        i += 1

    vowel = deepcopy(alphabet[nucleus])
    vowel.add_consonants(
        [deepcopy(alphabet[char]) for char in onset],
        [deepcopy(alphabet[char]) for char in coda],
        character_width=6, character_height=10)
    return vowel


if __name__ == '__main__':
    Syllable('test').to_file('tests/test.svg')
