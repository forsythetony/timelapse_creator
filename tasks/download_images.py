#!/usr/bin/env python3
import glob
import os
from os import path
from datetime import datetime
import logging as log
from shutil import copyfile
import boto3

BASE_FOLDER = "/Users/forsythetony/Documents/Coding/projects/timelapse/"
IMAGE_INPUT_FOLDER = path.join(BASE_FOLDER, "raw_images")
IMAGE_OUTPUT_FOLDER = path.join(BASE_FOLDER, "output_images")

LOG_OUTPUT_FORMAT = "%(asctime)s: %(message)s"
DATETIME_FORMAT = "%d-%m-%Y_%H-%M-%S"

BUCKET_NAME = "forsythetony-construction-timelapse"

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

def disable_boto_logging():
    for name in log.Logger.manager.loggerDict.keys():
        if ('boto' in name) or ('urllib3' in name):
            log.getLogger(name).setLevel(log.WARNING)

def get_files_in_bucket():
    bucket_files = []
    s3 = boto3.client('s3')
    my_bucket = s3.list_objects(Bucket=BUCKET_NAME, Prefix='raw_images/run_2')

    for content in my_bucket.get('Contents', []):
        image_file_name = content['Key']

        bucket_files.append(image_file_name)

    return bucket_files

def pull_base_names(file_entries):
    base_names = []

    for entry in file_entries:
        base_names.append(entry['base_name'])

    return base_names

def filter_out_pulled_files(files_in_bucket, files_downloaded):
    filtered_files = []

    for bucket_file in files_in_bucket:
        bucket_base_name = path.basename(bucket_file)

        if bucket_base_name not in files_downloaded:
            filtered_files.append(bucket_file)

    return filtered_files

def build_output_file_name(download_key):
    base_name = path.basename(download_key)

    return path.join(IMAGE_INPUT_FOLDER, base_name)

def download_files(s3_download_keys):

    #   First construct a file name from the download key
    
    s3 = boto3.client('s3')

    for key in s3_download_keys:
        target_file_name = build_output_file_name(key)

        log.info("Downloading key {} to target file {}".format(key, target_file_name))

        s3.download_file(BUCKET_NAME, key, target_file_name)

def log_strings(strin_arr):
    for str in strin_arr:
        log.info(str)

def setup_logging():
    log.basicConfig( 
        format=LOG_OUTPUT_FORMAT, 
        level=log.DEBUG,
        datefmt="%H:%M:%S"
    )

    disable_boto_logging()

def setup():
    setup_logging()

def main():
    setup()

    pulled_files = pull_base_names(gather_files())

    files_in_bucket = get_files_in_bucket()

    files_to_download = filter_out_pulled_files(files_in_bucket, pulled_files)

    download_count = len(files_to_download)

    if download_count < 1:
        log.info("No files to download.")
    else:
        log.info("Currently missing {} files on local machine. Downloading now.".format(download_count))
        download_files(files_to_download)
    
if __name__ == "__main__":
    main()