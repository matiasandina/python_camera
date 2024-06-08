import subprocess
import os
import argparse
import shutil

def compress_videos(crf, base_folder, out_folder):
    path_parts = out_folder.split(os.sep)
    animal_id = path_parts[1]
    session_id = path_parts[2]
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    for file in sorted(os.listdir(base_folder)):
        ###might want to extract date instead of session_id
        base_name = os.path.basename(file) ###might not be necessary
        file_name, file_extension = os.path.splitext(base_name)
        output_file = os.path.join(out_folder, 'sub-{}_ses-{}.{}'.format(animal_id, session_id, file_extension))
        input_file = os.path.join(base_folder, file)
        if file_extension == '.mp4':
            output_file = os.path.join(out_folder, 'sub-{}_ses-{}_video.{}'.format(animal_id, session_id, file_extension))

            cmd = f"ffmpeg -i {input_file} -c:v libx264 -crg {str(crf)} -c:a copy {output_file}"
            # cmd = ["ffmpeg", "-i", input_file, "-c:v", "libx264", "-crf", str(crf), "-c:a", "copy", output_file]
            subprocess.run(cmd, check=True)
            print(f"Video file compressed with crf {crf} and copied to folder {out_folder}")
            ###might need to be subprocess.check_call(cmd)
        elif file_extension == '.csv':
            output_file = os.path.join(out_folder, 'sub-{}_ses-{}_timestamps.{}'.format(animal_id, session_id, file_extension))
            shutil.copy(input_file, output_file)
            print(f"Timestamps file copied to folder {out_folder}")


"""
from `{timestamp}_{animal_id}.mp4` to `/animal_id/session_id/beh/sub-{animal_id}_ses-{session_id}_video.mp4`
from `{timestamp}_timestamp.csv` to `/animal_id/session_id/beh/sub-{animal_id}_ses-{session_id}_timestamps.csv
beh short for behavior
"""

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--crf", required= True, help="Compression factor for video downsizing. Check ffmpeg -h for details")
    parser.add_argument("--animal_id", required=True, help="Animal ID for constructing the base path. This script follows BIDS formatting `project/animal_id/session_id/beh/`. Files will be renamed `sub_\{animal_id\}_ses-...`")
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
    compress_videos(crf, base_folder, out_folder, animal_id)

