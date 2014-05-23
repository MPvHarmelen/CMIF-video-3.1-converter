import os, sys, math, ast
from itertools import chain

import png

# Initialize logging / debuging
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Constants
FILE_MODE = 'rb'
ENCODING_NAME = 'CMIF video 3.1'
EOF_MARKER = '/////CMIF/////'
RED_BITS, GREEN_BITS = 3, 2
STOP_LOOP = False
MAX_FRAMES = 4

class EncodingError(Exception):
    pass

rgb_tup = ((0, RED_BITS), (RED_BITS, RED_BITS + GREEN_BITS), (RED_BITS + GREEN_BITS, 8))
normalize = lambda number, tup: round(number * 255 / (2 ** (tup[1] - tup[0]) - 1))
def rgb_from_bytes(bytes, encoding):
    """Return rgb values read from bytes."""
    if encoding != 'rgb8':
        raise EncodingError("Only rgb8 encoding is supported, got {}."
                            "".format(encoding))

    n_bits = int(encoding[3:])
    # bits = '{0:b}'.format(bytes)[:n_bits].rjust(n_bits, '0')
    # get_b = lambda a: int(bits[a[0]:a[1]], 2)
    get_b = lambda a: get_bits(bytes, a[0], a[1], n_bits)
    rbg = map(get_b, rgb_tup)

    # Some idiot flipped the green and blue to be blue and green, so they
    # somehow used rbg8 in stead of rgb8.
    red, blue, green = map(normalize, rbg, rgb_tup)
    return (red, green, blue)

def get_bits(bits, start, end, length=8):
    return (bits >> length - end) % 2 ** (end - start)

def chop(li, length):
    """Chop a list into pieces."""
    n_rows = math.ceil(len(li) / length)
    return [li[x * length : (x + 1) * length] for x in range(n_rows)]
    # if len(li) > length:
    #     newli = chop(li[:-length], length)
    #     newli.append(li[-length:])
    #     return newli
    # return [li]


def convert(filename, output_folder, eof_marker=EOF_MARKER, file_mode=FILE_MODE,
            encoding_name=ENCODING_NAME, stop_loop=STOP_LOOP,
            max_frames=MAX_FRAMES):
    """Convert filename to separate png frames."""
    with open(filename, file_mode) as f:
        # First line should be our encoding name
        if f.readline().decode() != encoding_name + '\n':
            raise EncodingError("This file isn't using {}".format(encoding_name))

        # Second line should be the encoding
        encoding = ast.literal_eval(f.readline().decode())
        logger.debug("Encoding: {}".format(encoding))

        # Third line should be the width and hight and ehhh.. another something
        width, hight, unknown = ast.literal_eval(f.readline().decode())
        logger.debug("Width, hight: {}, {}".format(width, hight, unknown))

        eof_marker = (eof_marker + '\n').encode()

        # Loop over file
        if stop_loop:
            iterations = 0
        for line in f:
            # Check for eof
            if line == eof_marker:
                logger.debug('EOF reached.')
                break

            if stop_loop:
                if iterations == max_frames:
                    break
                else:
                    iterations += 1


            # Get line information
            line = line.decode().strip()
            if line:
                timestamp, line_length, unknown2 = ast.literal_eval(line)
            else:
                continue

            # if width * hight != line_length:
            #     raise EncodingError("Line length isn't width * hight.")
            # else:
            #     logger.debug("Line length: {}".format(line_length))

            # Read image bytes
            bytes = f.read(line_length)

            # Get rgb data
            get_rgb = lambda a: rgb_from_bytes(a, encoding[0])
            rgbs = list(map(get_rgb, bytes))

            # Cleanup
            rows = chop(rgbs, width)
            for i, row in enumerate(rows):
                rows[i] = list(chain(*row))
            rows.reverse()

            # Save
            img = png.from_array(rows, 'RGB')
            img.save(os.path.join(output_folder,'{}.png'.format(timestamp)))
            logger.info('Finished frame with timestamp: {}'.format(timestamp))

if __name__ == '__main__':
    OUTPUT_FOLDER = '../video/Champ/'
    FILENAME = OUTPUT_FOLDER + 'obscure.v'
    sys.argv_len = len(sys.argv)
    if sys.argv_len > 1:
        filename = sys.argv[1]
        if sys.argv_len > 2:
            output_folder = sys.argv[2]
        else:
            output_folder = os.path.split(filename)[0]
    else:
        filename, output_folder = FILENAME, OUTPUT_FOLDER

    convert(filename, output_folder)

