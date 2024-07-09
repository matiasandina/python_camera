import subprocess
import os
import argparse
import shutil
import re
import pandas as pd
from pathlib import Path
import datetime
import numpy as np

def get_bids_session(file_path, type = "str", format="%Y%m%dTH%M%S"):
    if isinstance(file_path, Path):
        file_path = str(file_path)

    pattern = r"ses-([a-zA-Z0-9]+)_"
    match = re.search(pattern, file_path)
    if match:
        if type == "str":
            timestamp_str = match.group(1)
            return timestamp_str
        if type == "dt":
            timestamp_dt = datetime.datetime.strptime(timestamp_str, format)
            return timestamp_dt
    else:
        raise ValueError(f"Cannot find pattern in {file_path}")

def get_session(file_path, data_type="str", format_in = "%Y-%m-%dT%H-%M-%S", format_out="%Y%m%dT%H%M%S"):
    '''
    Extracts datetime from the file name based on a specific format and converts it as specified.
    Assumes file names start with datetime pattern like "YYYY-MM-DDTHH-MM-SS_{animal_id}.extension".
    Format will coerce the datetime to a specific format example "%Y%m%dT%H%M%S".
    '''
    if isinstance(file_path, Path):
        file_path = file_path.name  # Directly get the file name with extension
    else:
        file_path = os.path.basename(str(file_path))  # Ensure we're working with the file name only

    # Regex pattern to match the datetime at the start of the file name
    pattern = r"^(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})"
    match = re.search(pattern, file_path)

    if not match:
        raise ValueError(f"Cannot find pattern {pattern} in {file_path}")

    timestamp_str = match.group(1)

    # Convert the timestamp based on the desired return type
    if data_type == "str":
        # Reformat the datetime string according to the specified format
        timestamp_dt = datetime.datetime.strptime(timestamp_str, format_in)
        return timestamp_dt.strftime(format_out)
    elif data_type == "dt":
        # Convert the string to a datetime object
        return datetime.datetime.strptime(timestamp_str, format_in)

def find_metadata_file(animal_id, directory):
    """
    Not recursive finds metadata in directory.
    :param directory: The directory path as a string or Path object where to start the search.
    :return: A Path to the metadata file.
    """
    # Convert directory to a Path object if it's not already one
    path = Path(directory)
    # Use the rglob method to find all .mp4 files recursively
    metadata_files = list(path.glob(f"sub-{animal_id}_metadata.parquet"))
    if metadata_files == []:
        print(directory)
        raise ValueError("Could not find metadata file. Please make sure it's on path")

    if len(metadata_files) > 1:
        print(f"Found these metadata files in {directory}")
        print(metadata_files)
        raise ValueError("Too many metadata files found. Check which one is correct")
    return metadata_files[0]



def read_metadata(parquet_path):
    df = pd.read_parquet(parquet_path)
    # TODO: this will get you the first row only.
    # We shouldn't have more than one, but it's not asserted
    return df.loc[0, :].to_dict()

def get_cropping_coords(metadata, session_id):
    coords = metadata["session_metadata"][session_id]["coords"]
    light_cage_coords = coords["light_cage"]
    dark_cage_coords =coords["dark_cage"]
    # Sample coordinates
    # light_cage_coords = [(110, 286), (200, 123), (463, 329)]
    # dark_cage_coords = [(397, 80), (396, 325), (497, 329), (501, 83)]
    y_px_tolerance = 10
    # Calculate encompassing Y-boundaries with a tolerance of 10 pixels
    stacked_coords = np.concatenate((light_cage_coords, dark_cage_coords), axis=0)

    y_coords = [coords[1] for coords in stacked_coords]

    min_y = min(y_coords)
    min_y = max(0, min_y - y_px_tolerance)

    max_y = max(y_coords)
    max_y = min(coords["frame_shape"][1], max_y + y_px_tolerance)

    range_y = max_y - min_y
    # this is data we already have but to be consistent with naming
    min_x = 0 # this is hardcoded though
    range_x = coords["frame_shape"][0]
    # maybe some assertions here to know we are not trying to get out of the frame
    print(range_x, range_y, min_x, min_y)
    return (range_x, range_y, min_x, min_y)

def call_ffmpeg(input_file, crop_coords, animal_dir, output_file):
    # unpack cropping coords
    range_x, range_y, min_x, min_y = crop_coords
    cmd_command = [
            "ffmpeg",
            "-i", input_file,
            "-vf", f"crop={range_x}:{range_y}:{min_x}:{min_y},hue=s=0",
            "-c:v", "libx264",
            "-crf", f"{crf}",
            "-c:a", "copy",
            output_file]
    print("Calling ffmpeg with this command")
    print(cmd_command)
    subprocess.run(cmd_command)


def compress_videos(metadata, crf, base_folder, animal_dir):
    animal_id = metadata['animal_id']
    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})_.*" + re.escape(animal_id) + r".*")
    print(f"Checking for the existence of output folder: {animal_dir}")
    if not os.path.exists(animal_dir):
        print(f"Output folder not found. It will be created: {animal_dir}")
        os.makedirs(animal_dir)
    else:
        print("Output folder already exists")

    for file in sorted(os.listdir(base_folder)):
        match = pattern.match(file)
        if match:
            session_id = get_session(file)
            session_folder = os.path.join(animal_dir, session_id, 'beh')
            print(f"Checking for the existence of session folder: {session_folder}")
            if not os.path.exists(session_folder):
                print(f"Session folder not found. It will be created: {session_folder}")
                os.makedirs(session_folder)

            base_name = os.path.basename(file)
            file_name, file_extension = os.path.splitext(base_name)
            output_file = os.path.join(session_folder, f'sub-{animal_id}_ses-{session_id}_video{file_extension}')

            if file_extension == '.mp4':
                input_file = os.path.join(base_folder, file)
                crop_coords = get_cropping_coords(metadata, session_id=session_id)
                call_ffmpeg(input_file = input_file, crop_coords=crop_coords, animal_dir=animal_dir, output_file = output_file)

            elif file_extension == '.csv':
                output_csv = os.path.join(session_folder, f'sub-{animal_id}_ses-{session_id}_timestamps{file_extension}')
                print(f"CSV file will be copied from {os.path.join(base_folder, file)} to {output_csv}")
                shutil.copy(os.path.join(base_folder, file), output_csv)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--animal_id", required=True, help="Animal ID for constructing the base path. This script follows BIDS formatting `project/animal_id/session_id/beh/`. Files will be renamed `sub_\{animal_id\}_ses-...`")
    parser.add_argument("--crf", required= True, help="Compression factor for video downsizing. Check ffmpeg -h for details")
    parser.add_argument("--base_folder", required=False, help="Full path of base folder (everything before `animal_id`) if not using default hard-coded one", default=None)

    args = parser.parse_args()
    if args.base_folder is not None:
        base_folder = args.base_folder
        animal_dir = os.path.join(base_folder, args.animal_id)
        print(f"Using User-Provided path: {base_folder}")
    else:
        # go with hardcoded
        base_folder = "/home/pi/python_camera/camera/"
        animal_dir = os.path.join(base_folder, args.animal_id)
        print(f"Using Hard-Coded path: {base_folder}")

    # arg parsing
    animal_id = args.animal_id
    crf = args.crf

    print(f"Finding metadata on {animal_dir}")
    metadata_file = find_metadata_file(animal_id=animal_id, directory=animal_dir)
    print(f"Found metadata at {metadata_file}")
    metadata = read_metadata(metadata_file)
    print(metadata)
    input("PRESS ENTER KEY TO CONTINUE: >> ")
    compress_videos(metadata, crf, base_folder, animal_dir)
