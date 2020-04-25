#!/usr/bin/env python3
import logging as log
import tasks.download_images as download_images
import tasks.process_images as process_images
import os
from os import path
from datetime import datetime


LOG_OUTPUT_FORMAT = "%(asctime)s: %(message)s"
VIDEO_OUTPUT_FOLDER = path.join(os.path.dirname(os.path.realpath(__file__)), "timelapses")
INPUT_IMAGES_PATH = path.join(os.path.dirname(os.path.realpath(__file__)), "output_images")

DATETIME_FORMAT = "%d-%m-%Y_%H-%M-%S"

def create_video_output_folder():
    if not path.exists(VIDEO_OUTPUT_FOLDER):
        log.info("{} is not a directory. Creating now...".format(VIDEO_OUTPUT_FOLDER))
        os.mkdir(VIDEO_OUTPUT_FOLDER)
    else:
        log.info("{} already exists. Will not create.".format(VIDEO_OUTPUT_FOLDER))

def get_new_timelapse_file_path():
    timestamp = datetime.now().strftime(DATETIME_FORMAT)
    return "timelapse_{}.mp4".format(timestamp)

def create_timelapse():
    file_path = get_new_timelapse_file_path()
    full_file_path = path.join(VIDEO_OUTPUT_FOLDER, get_new_timelapse_file_path())

    command = "ffmpeg -pattern_type glob -i \"{}/*.jpg\" -c:v libx264 -pix_fmt yuv420p {}".format(INPUT_IMAGES_PATH, full_file_path)

    os.system(command)

def setup_logging():
    log.basicConfig( 
        format=LOG_OUTPUT_FORMAT, 
        level=log.DEBUG,
        datefmt="%H:%M:%S"
    )

def setup():
    setup_logging()
    create_video_output_folder()

def main():
    setup()
    download_images.main()
    process_images.main()
    create_timelapse()

    
if __name__ == "__main__":
    main()