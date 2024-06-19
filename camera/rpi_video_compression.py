import subprocess
import os
import argparse
import shutil
import re

def compress_videos(animal_id, crf, base_folder, out_folder):
    # Define a regex pattern to match filenames with a date and the animal_id
    # Assuming the session ID is the date-time part formatted as YYYY-MM-DDTHH-MM-SS
    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})_.*" + re.escape(animal_id) + r".*")

    # Ensure the output directory exists
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    # Process each file in the base folder
    for file in sorted(os.listdir(base_folder)):
        # Check if the file matches the expected pattern
        match = pattern.match(file)
        if match:
            session_id = match.group(1).replace('-', '').replace('T', '').replace(':', '')
            base_name = os.path.basename(file)
            file_name, file_extension = os.path.splitext(base_name)
            output_file = os.path.join(out_folder, f'sub-{animal_id}_ses-{session_id}{file_extension}')

            # Process .mp4 files
            if file_extension == '.mp4':
                output_file = os.path.join(out_folder, f'sub-{animal_id}_ses-{session_id}_video{file_extension}')
                cmd = f"ffmpeg -i {os.path.join(base_folder, file)} -c:v libx264 -crf {str(crf)} -c:a copy {output_file}"
                subprocess.run(cmd, shell=True, check=True)
                print(f"Video file compressed with crf {crf} and copied to folder {out_folder}")

            # Process .csv files
            elif file_extension == '.csv':
                output_file = os.path.join(out_folder, f'sub-{animal_id}_ses-{session_id}_timestamps{file_extension}')
                shutil.copy(os.path.join(base_folder, file), output_file)
                print(f"Timestamps file copied to folder {out_folder}")


"""
from `{timestamp}_{animal_id}.mp4` to `/animal_id/session_id/beh/sub-{animal_id}_ses-{session_id}_video.mp4`
from `{timestamp}_timestamp.csv` to `/animal_id/session_id/beh/sub-{animal_id}_ses-{session_id}_timestamps.csv
beh short for behavior
"""

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--animal_id", required=True, help="Animal ID for constructing the base path. This script follows BIDS formatting `project/animal_id/session_id/beh/`. Files will be renamed `sub_\{animal_id\}_ses-...`")
    parser.add_argument("--crf", required= True, help="Compression factor for video downsizing. Check ffmpeg -h for details")
    parser.add_argument("--base_folder", required=False, help="Full path of base folder (everything before `animal_id`) if not using default hard-coded one", default=None)
    args = parser.parse_args()
    if args.base_folder is not None:
        base_folder = args.base_folder
        out_folder = os.path.join(base_folder, args.animal_id, args.session_id, "beh")
        print(f"Using User-Provided path: {base_folder}")
    else:
        # go with hardcoded
        base_folder = "/home/pi/python_camera/camera/"
        out_folder = os.path.join(base_folder, args.animal_id, args.session_id, "beh")
        print(f"Using Hard-Coded path: {base_folder}")
    crf = args.crf
    compress_videos(animal_id, crf, base_folder, out_folder)

