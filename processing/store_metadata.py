import pandas as pd
import os
import datetime as dt
import re
from datetime import datetime
from video_selector import VideoSelector
import subprocess

def dict_skeleton():
    return {"animal_id": [], "exp_dates": [{}], 'dob': [], 'sex':[], 'mac':[], 'FED':[], 'session_metadata':[{}]}

def get_session(video_path, type = "str", format = "%Y%m%d%H%M%S"):
    pattern = r"ses-([a-zA-Z0-9]+)_"
    match = re.search(pattern, video_path)
    if match:
        timestamp_str = match.group(1)
        timestamp_dt = datetime.strptime(timestamp_str, format=format)
        # Create a new datetime object
        timestamp_dt = datetime(timestamp_dt.year, timestamp_dt.month, timestamp_dt.day)

        timestamp_str = datetime.strftime(timestamp_dt, "%Y%m%d")
        if type == "str":
            return timestamp_str
        if type == "dt":
            timestamp_dt
            return timestamp_dt
    else:
        raise ValueError()

def get_session_type(exp_dates, target_date):

    date_to_exp_type = {date: key for key, date_list in exp_dates.items() for date in date_list}
    return date_to_exp_type[target_date]


def get_cropping_coords(filepath):
    selector = VideoSelector(filepath)
    selector.select_areas()
    # light_cage_coords, dark_cage_coords = selector.get_coords()
    regions = selector.regions
    regions['frame_shape'] = selector.get_shape()
    selector.release()


    return regions

def get_session_metadata(animal_dir, exp_dates, coords_by_session):
    files = os.listdir(animal_dir)
    session_metadata = {}
    for file in files:
        if file.endswith(".mp4"):
            session = {}
            name = get_session(file, type = "str")
            filepath = os.path.join(animal_dir, file)
            session['filepath'] = filepath
            session_datetime = get_session(file, type = "dt")
            session['date'] = session_datetime
            #expects exp_dates to be datetime objects
            session_type = get_session_type(exp_dates, session_datetime)
            session["session_type"] = session_type
            if coords_by_session == None:
                coords = get_cropping_coords(filepath)
            session["coords"] = coords_by_session[session_type]
            session_metadata[name] = session

    return session_metadata

def crop_coords_by_session(exp_dates, animal_dir):
    videos = [video for video in os.listdir(animal_dir) if video.endswith(".mp4")]
    # print(get_session(video, type = "dt"))
    fasted = [video for video in videos if get_session_type(exp_dates,  get_session(video, type = "dt")) == "fasted"]
    baseline = [video for video in videos if get_session_type(exp_dates,  get_session(video, type = "dt")) == "baseline"]

    if fasted:
        fasted_coords = get_cropping_coords(os.path.join(animal_dir, fasted[0]))
    else:
        fasted_coords = None

    if baseline:
        baseline_coords = get_cropping_coords(os.path.join(animal_dir, baseline[0]))
    else:
        baseline = None

    return {"fasted": fasted_coords, "baseline": baseline_coords}

def populate_dictionary(animal_dir, animal_id, exp_dates, dob = [], sex = [], mac = [], fed = [], session_metadata = {}, coords_by_session = None):
    d = {}
    d["animal_id"] = animal_id
    #must be datetime object
    d["exp_dates"] = exp_dates
    d["dob"] = dob
    d["sex"] = sex
    d["mac"] = mac
    d["fed"] = fed
    if session_metadata == {}:
        session_metadata = get_session_metadata(animal_dir, exp_dates, coords_by_session)
    d['session_metadata'] = session_metadata
    return d

def flatten_dict(data):
    flattened_data = {
        'animal_id': data['animal_id'],
        'exp_dates': data['exp_dates'],
        'dob': data['dob'],
        'sex': data['sex'],
        'mac': data['mac'],
        'fed': data['fed'],
        'session_metadata': data['session_metadata']
    }
    return flattened_data

def write_parquet(animal_dir, data):
    animal_id = data["animal_id"]
    flattened_data = flatten_dict(data)
    df = pd.DataFrame([flattened_data])
    filename = f"sub-{animal_id}_metadata.parquet"
    filepath = os.path.join(animal_dir, filename)
    df.to_parquet(filepath)


def dict_to_parquet(data, parquet_path):
    flattened_data = flatten_dict(data)
    df = pd.DataFrame([flattened_data])
    df.to_parquet(parquet_path)


def read_metadata(parquet_path):
    df = pd.read_parquet(parquet_path)
    # TODO: this will get you the first row only.
    # We shouldn't have more than one, but it's not asserted
    return df.loc[0, :].to_dict()


if __name__ == "__main__":

    video_dir = "VideoTracking/videos/downsized"
    exp_dates =  {"fasted": ["20240620", "20240621"], "baseline": ["20240617", "20240618"]}
    #convert dates to datetime
    exp_dates_dt = {k: [datetime.strptime(val, "%Y%m%d") for val in v] for k, v in exp_dates.items()}
    animal_list = ["MLA163"]


    for animal_id in animal_list:
        animal_dir = os.path.join(video_dir, animal_id)

        coords_by_session = crop_coords_by_session(exp_dates_dt, animal_dir)
        metadata = populate_dictionary(animal_dir, animal_id, exp_dates_dt, coords_by_session = coords_by_session)
        write_parquet(animal_dir, metadata)

        for file in os.listdir(animal_dir):

            if file.endswith(".mp4"):
                name = get_session(file, type = "str")
                coords = metadata["session_metadata"][name]["coords"]
                light_cage_coords = coords["light_cage"]
                dark_cage_coords =coords["dark_cage"]
                # Sample coordinates
                # light_cage_coords = [(110, 286), (200, 123), (463, 329)]
                # dark_cage_coords = [(397, 80), (396, 325), (497, 329), (501, 83)]
                y_px_tolerance = 10
                # Calculate encompassing Y-boundaries with a tolerance of 10 pixels
                min_y = min(coord[1] for coord in light_cage_coords + dark_cage_coords) - y_px_tolerance
                max_y = max(coord[1] for coord in light_cage_coords + dark_cage_coords) + y_px_tolerance
                range_y = max_y - min_y
                # this is data we already have but to be consistent with naming
                min_x = 0 # this is hardcoded though
                range_x = coords["frame_shape"][0]
                # maybe some assertions here to know we are not trying to get out of the frame

                print(range_x, range_y, min_x, min_y)

                input_video_path = os.path.join(animal_dir, file)

                root, ext = os.path.splitext(file)
                    # but maybe also some overengineering
                output_video_path = os.path.join(animal_dir,f"{root}_cropped.mp4")

                cmd_command=command = [
                        "ffmpeg",
                        "-i", input_video_path,
                        "-vf", f"crop={range_x}:{range_y}:{min_x}:{min_y}",
                        "-c:v", "libx264",
                        "-crf", "18",
                        "-c:a", "copy",
                        output_video_path]

                subprocess.run(cmd_command)
