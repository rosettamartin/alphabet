from PIL import Image


img_consonants = 'consonants.png'
img_vowels = 'vowels.png'
consonant_order = [
    'p', 'b', 'm', 'f', 'v',
    't', 'd', 'n', 's', 'z',
    'l', 'k', 'g', 'x', 'gh',
    "'", 'h', 'j', 'w', 'r']
vowel_order = [
    'i', 'u', 'e', 'o', 'a']

vowel_line_length = 19
character_height = 13
c_box_width = 11
c_box_height = 15
v_box_width = 33
v_box_height = 33


def get_images(image, characters, box_width, box_height, transparent=True):
    images = []
    box_interval = box_width - 1  # horizontal distance between boxes
    with Image.open(image) as img:
        for i in range(len(characters)):
            x1 = (box_interval * i) + 1
            x2 = x1 + box_interval - 1
            y1 = 1
            y2 = box_height - 1
            cropped = img.crop((x1, y1, x2, y2))
            if transparent:
                cropped = color_to_alpha(cropped)
            images.append(cropped)
    return dict(zip(characters, images))


def color_to_alpha(image, color=(255, 255, 255)):
    new_data = []
    for r, g, b, a in image.getdata():
        if (r, g, b) == color:
            new_data.append((r, g, b, 0))
        else:
            new_data.append((r, g, b, a))
    img = image.copy()
    img.putdata(new_data)
    return img


class Consonant:
    consonant_images = get_images(
        img_consonants, consonant_order, c_box_width, c_box_height)

    def __init__(self, char,
                 end_char=False, descends=True, tall=True, wide=True):
        """
        Information about a consonant character

        :param char: Character string
        :param end_char: If True, this character should be at the end of
            a line when possible, rather than centered
        :param descends: If True, this character descends below the center line
        :param tall: If True, this character is tall
        :param wide: If True, this character is wide
        """

        self.image = Consonant.consonant_images[char]
        self.end_char = end_char
        self.descends = descends
        self.tall = tall
        self.wide = wide


class Vowel:
    vowel_images = get_images(
        img_vowels, vowel_order, v_box_width, v_box_height, transparent=False)

    def __init__(
            self, char,
            onset_transpose, coda_transpose, onset_pos, coda_pos):
        """
        Information about a vowel character

        :param char: Character string
        :param onset_transpose: Image transpose method for the onset
        :param coda_transpose: Image transpose method for the coda
        :param onset_pos: 2-tuple of (x, y) position to paste the onset
        :param coda_pos: 2-tuple of (x, y) position to paste the coda
        """

        self.image = Vowel.vowel_images[char]
        self.onset_transpose = onset_transpose
        self.coda_transpose = coda_transpose
        self.onset_pos = onset_pos
        self.coda_pos = coda_pos


vowels = {
    'i': Vowel('i', Image.ROTATE_90, None, (0, 6), (6, 0)),
    'u': Vowel('u', None, Image.ROTATE_270, (6, 0), (18, 6)),
    'e': Vowel('e', Image.TRANSPOSE, Image.FLIP_TOP_BOTTOM, (0, 6), (6, 18)),
    'o': Vowel('o', Image.FLIP_TOP_BOTTOM, Image.TRANSVERSE, (6, 18), (18, 6)),
    'a': Vowel('a', Image.TRANSPOSE, Image.FLIP_TOP_BOTTOM, (0, 6), (6, 18))}

consonants = {
    'p': Consonant('p'),
    'b': Consonant('b'),
    'm': Consonant('m'),
    'f': Consonant('f'),
    'v': Consonant('v'),
    't': Consonant('t', descends=False),
    'd': Consonant('d'),
    'n': Consonant('n'),
    's': Consonant('s'),
    'z': Consonant('z'),
    'l': Consonant('l'),
    'k': Consonant('k', end_char=True, descends=False),
    'g': Consonant('g', end_char=True),
    'x': Consonant('x'),
    'gh': Consonant('gh'),
    "'": Consonant("'"),
    'h': Consonant('h'),
    'j': Consonant('j'),
    'w': Consonant('w'),
    'r': Consonant('r')}
