#!/usr/bin/env python3
import glob
import os
from os import path
from datetime import datetime
import logging as log
from shutil import copyfile
import time

BASE_FOLDER = "/Users/forsythetony/Documents/Coding/projects/timelapse/"
IMAGE_INPUT_FOLDER = path.join(BASE_FOLDER, "raw_images")
IMAGE_OUTPUT_FOLDER = path.join(BASE_FOLDER, "output_images")

LOG_OUTPUT_FORMAT = "%(asctime)s: %(message)s"
DATETIME_FORMAT = "%d-%m-%Y_%H-%M-%S"

def get_raw_files_in_dir(directory):
    return glob.glob("{}/*.jpg".format(directory))

def get_date_from_file_name(file_basename: str):

    file_basename = file_basename.replace(".jpg", "")

    return datetime.strptime(file_basename, DATETIME_FORMAT)

def print_file_entries(file_entries):

    for entry in file_entries:
        print("""
        Basename:\t{}
        Full Path:\t{}
        Timestamp:\t{}
        """.format(
            entry['base_name'],
            entry['full_path'],
            entry['datetime']
        ))

def gather_files():
    all_files = []

    raw_files = get_raw_files_in_dir(IMAGE_INPUT_FOLDER)

    for full_file_path in raw_files:
        base_name = path.basename(full_file_path)
        datetime = get_date_from_file_name(base_name)
        
        file_entry = {
            'base_name' : base_name,
            'datetime' : datetime,
            'full_path' : full_file_path
        }

        all_files.append(file_entry)

    return all_files

def create_sorted_directory():
    if not path.exists(IMAGE_OUTPUT_FOLDER):
        log.info("{} is not a directory. Creating now...".format(IMAGE_OUTPUT_FOLDER))
        os.mkdir(IMAGE_OUTPUT_FOLDER)
    else:
        log.info("{} already exists. Will not create.".format(IMAGE_OUTPUT_FOLDER))

    log.info("Will now clear the sorted directory")

    files = glob.glob("{}/*".format(IMAGE_OUTPUT_FOLDER))

    for f in files:
        os.remove(f)

def get_iterated_image_file_name(i):
    return "tl_{:05d}.jpg".format(i)

def copy_ordered_images(file_entries):

    counter = 1

    for entry in file_entries:
        target_file_name = get_iterated_image_file_name(counter)

        target_path = path.join(IMAGE_OUTPUT_FOLDER, target_file_name)
        source_path = entry['full_path']

        log.info("Copying file at {} to {}".format(source_path, target_path))

        copyfile(entry['full_path'], target_path)

        counter += 1

def setup_logging():
    log.basicConfig( 
        format=LOG_OUTPUT_FORMAT, 
        level=log.DEBUG,
        datefmt="%H:%M:%S"
    )

def setup():
    setup_logging()
    create_sorted_directory()

def main():
    setup()

    file_entries = gather_files()
    file_entries.sort(key=lambda x: x['datetime'])

    copy_ordered_images(file_entries)
    
if __name__ == "__main__":
    main()