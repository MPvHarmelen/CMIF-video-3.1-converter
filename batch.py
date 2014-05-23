import os, sys, subprocess

from convert import convert

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

STOP_LOOP = False
MAX_FRAMES = 2
FOLDER = '../video_batch'
RJUST_VALUE = 5
FFMPEG_INSTALLATION_FOLDER = '../../FFMPEG-commandline'
FPS = 12
VIDEO_FORMAT = 'mp4'

def make_folder(folder, filename):
    output_folder = os.path.join(folder, filename.rsplit('.', 1)[0])
    os.mkdir(output_folder)
    img_file = os.path.join(folder, filename)
    return output_folder, img_file

sort_key = lambda a: a.rsplit('.', 1)[0].rjust(rjust_value, '0')
def serialise(folder, rjust_value=RJUST_VALUE):
    """Serialise filenames to consecutive numbers."""
    files = sorted(os.listdir(folder), key=sort_key)
    for i, name in enumerate(files):
        logger.debug('i, name: {}, {}'.format(i, name))
        ext = name.rsplit('.', 1)[1]
        old_name = os.path.join(folder, name)
        new_name = str(i + 1).rjust(rjust_value, '0') + '.' + ext
        new_name = os.path.join(folder, new_name)
        os.rename(old_name, new_name)

def run_ffmpeg(folder, img_file, installation_folder=FFMPEG_INSTALLATION_FOLDER,
               frame_rate=FPS, video_extension=VIDEO_FORMAT, n_digits=RJUST_VALUE):
    ffmpeg = os.path.join(installation_folder, 'bin', 'ffmpeg.exe')
    video_name = img_file.rsplit('.', 1)[0]
    args = [
        ffmpeg,
        '-r', str(frame_rate),
        '-f', 'image2',
        '-i', '{}{}%{}d.png'.format(folder, os.path.sep, n_digits),
        '{}{}{}.{}'.format(folder, os.path.sep, filename, video_extension)
    ]
    logger.debug(args)
    subprocess.call(args)

if __name__ == '__main__':
    folder = sys.argv[1] if len(sys.argv) > 1 else FOLDER
    rjust_value = sys.argv[2] if len(sys.argv) > 2 else RJUST_VALUE

    for filename in (name for name in os.listdir(folder) if not os.path.isdir(name)):
        logger.info('File: {}'.format(filename))

        # Make folder
        output_folder, img_file = make_folder(folder, filename)

        # Extract frames
        logger.info('Extracting frames.... Please wait. This takes approx 10 sec per frame.')
        convert(img_file, output_folder, stop_loop=STOP_LOOP, max_frames=MAX_FRAMES)

        # Serialise frames
        logger.info('Serialising images...')
        serialise(output_folder)

        # Run script
        logger.info('Running FFMPEG script...')
        run_ffmpeg(output_folder, filename)

        logger.info('Finished {}'.format(filename))
    logger.info('Done!')
