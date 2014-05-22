from sys import argv
from ast import literal_eval
from itertools import chain
from math import ceil
import png

# Initialize logging / debuging
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class EncodingError(Exception):
    pass

RED_BITS, GREEN_BITS = 3, 2
rgb_tup = ((0, RED_BITS), (RED_BITS, RED_BITS + GREEN_BITS), (RED_BITS + GREEN_BITS, 8))
normalize = lambda number, tup: round(number * 255 / (2 ** (tup[1] - tup[0]) - 1))
def rgb_from_bytes(bytes, encoding):
    """Return rgb values read from bytes."""
    if encoding != 'rgb8':
        raise EncodingError("Only rgb8 encoding is supported, got {}."
                            "".format(encoding))

    n_bits = int(encoding[3:])
    bits = '{0:b}'.format(bytes)[:n_bits].rjust(n_bits, '0')
    get_b = lambda a: int(bits[a[0]:a[1]], 2)
    rgb = map(get_b, rgb_tup)
    return map(normalize, rgb, rgb_tup)

def chop(li, length):
    """Chop a list into pieces."""
    n_rows = ceil(len(li) / length)
    out = []
    for x in range(n_rows):
        out.append(li[x * length : (x + 1) * length])
    return out
    # if len(li) > length:
    #     newli = chop(li[:-length], length)
    #     newli.append(li[-length:])
    #     return newli
    # return [li]

if __name__ == '__main__':
    FILENAME = '../video/obscure.v'
    FILE_MODE = 'rb'
    ENCODING_NAME = 'CMIF video 3.1'
    EOF_MARKER = '/////CMIF/////'

    filename = argv[1] if len(argv) > 1 else FILENAME

    with open(filename, FILE_MODE) as f:
        # First line should be our encoding name
        if f.readline().decode() != ENCODING_NAME + '\n':
            raise EncodingError("This file isn't using {}".format(ENCODING_NAME))

        encoding = literal_eval(f.readline().decode())
        logger.info("Encoding: {}".format(encoding))

        width, hight, unknown2 = literal_eval(f.readline().decode())
        logger.debug("Width, hight: {}, {}".format(width, hight))


        eof_marker = (EOF_MARKER + '\n').encode()
        for line in f:
            if line == eof_marker:
                logger.debug('EOF reached.')
                break

            line = line.decode().strip()
            if line:
                timestamp, line_length, unknown3 = literal_eval(line)
            else:
                continue

            if width * hight != line_length:
                raise EncodingError("Line length isn't width * hight.")
            else:
                logger.debug("Line length: {}".format(line_length))

            bytes = f.read(line_length)

            get_rgb = lambda a: rgb_from_bytes(a, encoding[0])
            rgbs = list(map(get_rgb, bytes))
            rows = chop(rgbs, width)
            for i, row in enumerate(rows):
                rows[i] = list(chain(*row))
            rows.reverse()
            img = png.from_array(rows, 'RGB')
            img.save('../video/{}.png'.format(timestamp))
            logger.debug("{}, {}".format(bytes[:10], timestamp))

