import math

from PIL import Image

from . import alphabet


def create_line(chars, onset=True, transpose=None, overlap=1,
                width=alphabet.vowel_line_length,
                height=alphabet.character_height):
    if len(chars) > 2:
        raise ValueError(
            'Consonant clusters cannot be longer than 2 characters')
    line_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    x = 0 if onset else width
    y = 0
    if not onset:
        chars.reverse()  # going to place chars in reverse order
    for char in chars:
        consonant = alphabet.consonants[char]
        char_img = consonant.image
        char_width, char_height = char_img.size
        if len(chars) == 1 and not consonant.end_char:
            # center the character
            box = (math.floor((width - char_width) / 2), y)
        elif onset:
            box = (x, y)
            x += char_width - overlap
        else:
            # (x1, y1, x2, y2)
            box = (x - char_width, y, x, height)
            x -= char_width - overlap
        line_img.paste(char_img, box, char_img)
    if transpose:
        line_img = line_img.transpose(transpose)
    return line_img


def create_syllable(onset, nucleus, coda):
    """
    Create a syllable image.

    :param onset: A list of consonant strings
    :param nucleus: A vowel string
    :param coda: A list of coda strings
    :return: An Image
    """

    # TODO if the last character in onset or first in coda descends, and
    #  the opposite side has one character, shift the single character
    vowel = alphabet.vowels[nucleus]
    syllable_img = vowel.image.copy()

    onset_img = create_line(onset, onset=True, transpose=vowel.onset_transpose)
    coda_img = create_line(coda, onset=False, transpose=vowel.coda_transpose)

    syllable_img.paste(onset_img, vowel.onset_pos, onset_img)
    syllable_img.paste(coda_img, vowel.coda_pos, coda_img)

    return syllable_img


def concat_images(im1, im2, vertical=False):
    if im1 is None:
        return im2
    if vertical:
        height = im1.height + im2.height
        width = max(im1.width, im2.width)
    else:
        height = max(im1.height, im2.height)
        width = im1.width + im2.width
    new_image = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    new_image.paste(im1)
    if vertical:
        new_image.paste(im2, (0, im1.height))
    else:
        new_image.paste(im2, (im1.width, 0))
    return new_image


def transcribe_syllable(text):
    onset, nucleus, coda = [], '', []
    i = 0
    while i < len(text):
        char = text[i]
        if char in alphabet.vowels:
            nucleus = char
            i += 1
            continue
        elif char == 'g' and text[i+1] == 'h':
            char += 'h'
            i += 1

        if nucleus:
            coda.append(char)
        else:
            onset.append(char)
        i += 1
    return create_syllable(onset, nucleus, coda)


def transcribe_line(text):
    image = None
    for syllable in text.split(' '):
        image = concat_images(image, transcribe_syllable(syllable))
    return image


def transcribe(text, filename):
    image = None
    for line in text.split('\n'):
        image = concat_images(image, transcribe_line(line), vertical=True)
    image.save(filename)


if __name__ == '__main__':
    import os
    if not os.path.isdir('tests'):
        os.mkdir('tests')

    anthem = (
        "ju 'ar so swit\n"
        "dan sin tu da bit\n"
        "derz 'a mit mar kit\n"
        "dawn da stit\n"
        "da bojz 'and da gilz\n"
        "wats its 'o der it")
    transcribe(anthem, 'tests/anthem.png')
