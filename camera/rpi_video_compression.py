import subprocess
import os
import argparse
import shutil
import re

def compress_videos(animal_id, crf, base_folder):
    out_folder = os.path.join(base_folder, animal_id)
    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})_.*" + re.escape(animal_id) + r".*")

    print(f"Checking for the existence of output folder: {out_folder}")
    if not os.path.exists(out_folder):
        print(f"Output folder not found. It will be created: {out_folder}")
        # os.makedirs(out_folder)

    for file in sorted(os.listdir(base_folder)):
        match = pattern.match(file)
        if match:
            session_id = match.group(1).replace('-', '').replace('T', '')
            session_folder = os.path.join(out_folder, session_id, 'beh')
            print(f"Checking for the existence of session folder: {session_folder}")
            if not os.path.exists(session_folder):
                print(f"Session folder not found. It will be created: {session_folder}")
                # os.makedirs(session_folder)

            base_name = os.path.basename(file)
            file_name, file_extension = os.path.splitext(base_name)
            output_file = os.path.join(session_folder, f'sub-{animal_id}_ses-{session_id}_video{file_extension}')
            
            if file_extension == '.mp4':
                input_file = os.path.join(base_folder, file)
                cmd = f"ffmpeg -i {input_file} -c:v libx264 -crf {str(crf)} -c:a copy {output_file}"
                print(f"Command to be run: {cmd}")
                print(f"Output video file would be saved to: {output_file}")
                # subprocess.run(cmd, shell=True, check=True)

            elif file_extension == '.csv':
                output_csv = os.path.join(session_folder, f'sub-{animal_id}_ses-{session_id}_timestamps{file_extension}')
                print(f"CSV file will be copied from {os.path.join(base_folder, file)} to {output_csv}")
                # shutil.copy(os.path.join(base_folder, file), output_csv)

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
        out_folder = os.path.join(base_folder, args.animal_id)
        print(f"Using User-Provided path: {base_folder}")
    else:
        # go with hardcoded
        base_folder = "/home/pi/python_camera/camera/"
        out_folder = os.path.join(base_folder, args.animal_id)
        print(f"Using Hard-Coded path: {base_folder}")

    crf = args.crf
    animal_id = args.animal_id
    compress_videos(animal_id, crf, base_folder, out_folder)
