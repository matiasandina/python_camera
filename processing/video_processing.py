#Changes to be made:
# - Grayscale (waiting on whether we need to train 1 or 2 models)
# - Downsize from 640x480 to 320x240. Check [Downsizing videos for prediction](https://www.notion.so/Downsizing-videos-for-prediction-5458158f73c544278e1f7995032d5c96?pvs=21)
# - Optionally reduce fps (max 15 FPS)

import os
import subprocess
import shutil

def process_vids(input_folder, output_folder, fps = None, width = None, height = None):

    # Iterate through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.mp4'):
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)

            if os.path.exists(output_file_path):
                print(f"Skipping {input_file_path} as {output_file_path} already exists")
                continue

            cmd = f"ffmpeg -i {input_file_path} -vf scale={width}:{height},format=gray,fps={fps}:round=near -c:v libx264 -c:a copy {output_file_path}"

            subprocess.run(cmd, check=True)

            print(f"Processed {input_file_path} and saved as {output_file_path}")



def main(source_folder, target_folder, width, height, fps):

    for folder_name in os.listdir(source_folder):
        folder_path = os.path.join(source_folder, folder_name)
        if os.path.isdir(folder_path):
            # Create target folder if it doesn't exist
            target_folder_path = os.path.join(target_folder, folder_name)

            if not os.path.exists(target_folder_path):
                os.makedirs(target_folder_path)

            # Process videos in the folder
            process_vids(folder_path, target_folder_path, fps, width, height)


if __name__ == "__main__":

    # Set the desired width and height for resizing
    width = 320
    height = 240
    #select desired fps
    fps = 15

    # Source and target directories
    source_folder = os.path.join('D:/Sasha/Video_Tracking', 'videos', 'raw')
    target_folder = os.path.join('D:/Sasha/Video_Tracking', 'videos', 'downsized')
