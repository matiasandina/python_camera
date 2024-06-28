import pandas as pd
import os
import datetime as dt
import re
from datetime import datetime
from video_selector import VideoSelector
import subprocess

def dict_skeleton():
    return {"animal_id": [], "exp_dates": [{}], 'dob': [], 'sex':[], 'mac':[], 'FED':[], 'session_metadata':[{}]}

def get_session(video_path, type = "str"):
    pattern = r"ses-([a-zA-Z0-9]+)_"
    match = re.search(pattern, video_path)
    if match:
        timestamp_str = match.group(1)
        timestamp_dt = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
        # Create a new datetime object
        timestamp_dt = datetime(timestamp_dt.year, timestamp_dt.month, timestamp_dt.day)

        timestamp_str = datetime.strftime(timestamp_dt, "%YYYY%mm%dd")


        if type == "str":
            return timestamp_str
        if type == "dt":
            timestamp_dt
            return timestamp_dt
    else:
        raise ValueError()

def get_session_type(exp_dates, target_date):

    print(target_date, "target")
    print(exp_dates, "exp_dates")
    date_to_exp_type = {date: key for key, date_list in exp_dates.items() for date in date_list}
    return date_to_exp_type[target_date]


def get_cropping_coords(filepath):
    selector = VideoSelector(filepath)
    selector.select_areas()
    # light_cage_coords, dark_cage_coords = selector.get_coords()
    regions = selector.regions
    regions['frame_shape'] = selector.get_shape()
    selector.release()

    return selector.regions

def get_session_metadata(animal_dir, exp_dates):

    files = os.listdir(animal_dir)
    session_metadata = {}
    for file in files:
        filepath = os.path.join(animal_dir, file)
        session_metadata['filepath'] = filepath
        session_datetime = get_session(file, type = "dt")


        session_metadata['date'] = session_datetime

        #expects exp_dates to be datetime objects
        session_metadata["session_type"] = get_session_type(exp_dates, session_datetime)
        session_metadata["coords"] = get_cropping_coords(filepath)

    return session_metadata


def populate_dictionary(animal_dir, animal_id, exp_dates, dob = [], sex = [], mac = [], fed = [], session_metadata = {}):

    d = {}
    d["animal_id"] = animal_id
    #must be datetime object
    d["exp_dates"] = exp_dates
    d["dob"] = dob
    d["sex"] = sex
    d["mac"] = mac
    d["fed"] = fed

    session_metadata = get_session_metadata(animal_dir, exp_dates)
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

    return df.loc[0, :].to_dict()




if __name__ == "__main__":

    # video_dir = "processing/animal_dir"
    animal_dir = "processing/animal_dir"
    exp_dates =  {"fasted": ["20240620", "20240621"], "baseline": ["20240617", "20240618"]}
    #convert dates to datetime
    exp_dates_dt = {k: [datetime.strptime(val, "%Y%m%d") for val in v] for k, v in exp_dates.items()}

    # val_dict = populate_dictionary(animal_dir, "MLA163", exp_dates_dt)
    # write_parquet(animal_dir, val_dict)

    md_dict = read_metadata("processing/animal_dir/MLA163_metadata.parquet")
    print(md_dict)
