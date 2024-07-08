import tkinter as tk
from tkinter import messagebox, filedialog
import datetime
from tkcalendar import DateEntry
from tkinter import messagebox, font
from rich import print
import subprocess
import sys
import pandas as pd
from pathlib import Path
from video_selector import VideoSelector
import re
import os

class ExperimentMetadataApp:
    def __init__(self, master):
        self.master = master
        master.title("Experiment Metadata Collection")        
        # Set the window size
        master.geometry("600x700")         
        # Styling
        self.style_app()
        # Initializing variables
        self.sessions = {}
        self.sex_var = tk.StringVar()
        self.metadata = None
        # Set the base path using os.path, assuming your script's location is stable within the project structure
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'python_camera', 'camera'))
        # Setup UI
        self.setup_ui()
    
    def style_app(self):
        # Font and Color Scheme
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=12, family="Helvetica")
        self.master.option_add("*Font", default_font)
        self.master.configure(bg="#FFFFFF")  # white background
        self.button_style = {'activebackground': '#CDDC39', 'bg': '#E0E0E0', 'bd': 0, 'fg': '#212121', 'padx': 10, 'pady': 5, 'relief': 'flat'}
        self.entry_style = {'relief': 'flat', 'bd': 1, 'insertbackground': '#212121'}

    # Define a function to update the button's style on hover
    def on_enter(self, e, btn):
        btn['background'] = '#CDDC39'  # Green shade for hover

    def on_leave(self, e, btn):
        btn['background'] = '#E0E0E0'  # Default background

    # Update button creation to use this new style
    def create_button(self, text, command):
        btn = tk.Button(self.master, text=text, command=command, bg='#E0E0E0', fg='black',
                        padx=20, pady=5, relief='flat', borderwidth=0)
        btn.bind("<Enter>", lambda e, b=btn: self.on_enter(e=e, btn=b))
        btn.bind("<Leave>", lambda e, b=btn: self.on_leave(e=e, btn=b))
        return btn
   
    def setup_ui(self):
        self.main_background = "#FFFFFF"
        row_options = {'padx': 20, 'pady': 10}
        # Animal ID
        tk.Label(self.master, text="Animal ID:", bg="#FFFFFF").grid(row=0, column=0, **row_options)
        self.animal_id_entry = tk.Entry(self.master, **self.entry_style)
        self.animal_id_entry.grid(row=0, column=1, **row_options)

        # Date of Birth
        tk.Label(self.master, text="Date of Birth (mm/dd/yy):", bg="#FFFFFF").grid(row=1, column=0, **row_options)
        self.dob_cal = DateEntry(self.master, width=12, background='white', foreground='black', borderwidth=2,
                         headerbackground='#E0E0E0', selectbackground='#CDDC39', selectforeground='black')
        self.dob_cal.grid(row=1, column=1, **row_options)

        # Sex
        tk.Label(self.master, text="Sex:", bg="#FFFFFF").grid(row=2, column=0, **row_options)
        sex_menu = tk.OptionMenu(self.master, self.sex_var, "Male", "Female")
        sex_menu.config(**self.button_style)
        sex_menu.grid(row=2, column=1, **row_options)

        # MAC Address
        tk.Label(self.master, text="MAC Address:", bg="#FFFFFF").grid(row=3, column=0, **row_options)
        self.mac_label = tk.Label(self.master, text=self.get_mac(), bg="#FFFFFF")
        self.mac_label.grid(row=3, column=1, **row_options)

        # FED
        tk.Label(self.master, text="FED:", bg="#FFFFFF").grid(row=4, column=0, **row_options)
        self.fed_entry = tk.Entry(self.master, **self.entry_style)
        self.fed_entry.grid(row=4, column=1, **row_options)

        # Session Management
        self.session_frame = tk.LabelFrame(self.master, text="Sessions", bg="#FFFFFF", fg="black")
        self.session_frame.grid(row=5, columnspan=3, sticky='ew', **row_options)

        # Input for adding new sessions
        self.session_name_label = tk.Label(self.session_frame, text="Session Name:", bg="#FFFFFF")
        self.session_name_label.grid(row=6, column=0, **row_options)
        self.session_name_entry = tk.Entry(self.session_frame)
        self.session_name_entry.grid(row=6, column=1, padx=10, pady=10)

        # Placeholder where dynamic session widgets will be placed
        self.dynamic_session_frame = tk.Frame(self.session_frame)
        self.dynamic_session_frame.grid(row=7, columnspan=2, sticky='ew')
        # Buttons
        # Submit Button
        self.add_button = self.create_button("Add/Edit Session", self.add_or_edit_session)
        self.add_button.grid(row=6, column=0, padx=10, pady=10)
        # Load button
        self.load_button = self.create_button("Load Metadata", command=self.load_metadata)
        self.load_button.grid(row=6, column=1, columnspan=1, pady=20)
        self.submit_button = self.create_button("Save Metadata", self.submit_form)
        self.submit_button.grid(row=6, column=2, columnspan=1, pady=20)
        self.trigger_main_button = self.create_button(text="✔ Record", command=self.trigger_main_py)
        self.trigger_main_button.grid(row=7, column=1, columnspan=1, pady=20)
        # Crop ROIs button
        self.crop_roi_button = self.create_button("Crop ROIs", command=self.collect_session_metadata)
        self.crop_roi_button.grid(row=9,column=1, columnspan=1, pady=50)

    def trigger_main_py(self):
        if self.metadata is not None:
            record_name = self.metadata['animal_id'][0]
            try:
                # Prepare command with arguments
                args_dict = {
                    #"--device_name": cameraDeviceName,
                    #"--resolution": resolution,
                    "--fps": str(15),
                    #"--flip": flip,
                    #"--use_pi_camera": usePiCamera,
                    #"--record_duration": record_duration,
                    "--record_name": record_name
                }

                # Construct command list and filter out empty arguments
                cmd = [sys.executable, "main.py"]
                for key, value in args_dict.items():
                    if value not in [None, "", False]:
                        cmd.append(key)
                        if value is not True:  # For boolean flags, don't add the value part
                            cmd.append(str(value))

                # Print formatted command arguments
                print("Launching 'main.py' with the following arguments:")
                for key, value in args_dict.items():
                    print(f"  {key}: {value}")

                # Launch main.py with collected parameters
                subprocess.run(cmd)

            except subprocess.CalledProcessError as e:
                print(f"An error occurred while executing main.py: {e}")
        else:
            print("Animal ID is missing or not specified.")

    def get_mac(self, interface='wlan0'):
        try:
            return open('/sys/class/net/' + interface + '/address').readline().strip()
        except:
            return "00:00:00:00:00:00"

    def add_or_edit_session(self):
        session_name = self.session_name_entry.get().strip()
        if not session_name:
            messagebox.showerror("Invalid Input", "Session name cannot be empty.")
            return
        if session_name in self.sessions:
            messagebox.showerror("Duplicate Session", "This session name already exists.")
            return
        self.create_session_ui(session_name)
    
    def load_sessions_from_metadata(self):
        exp_dates = self.metadata.get('exp_dates', {})
        for session_name, dates in exp_dates.items():
            start, stop = dates[0], dates[1]
            self.create_session_ui(session_name, start, stop)

    def create_session_ui(self, session_name, start=None, stop=None):
        frame = tk.Frame(self.dynamic_session_frame, bg=self.main_background) 
        frame.pack(fill='x', expand=True, pady=5)
        
        tk.Label(frame, text=session_name, bg=self.main_background).pack(side='left', padx=10)
        
        start_cal = DateEntry(frame, width=8, background='black', foreground='white', borderwidth=2,
                              normalbackground='#FFFFFF', normalforeground='black', 
                              headerbackground='lightgrey', selectbackground='lightblue', selectforeground='black')
        start_cal.pack(side='left', padx=8)
        start_time = tk.Entry(frame, width=10)
        start_time.pack(side='left', padx=2)
        if start:
            start_cal.set_date(start.date())
            start_time.insert(0, start.strftime("%H:%M:%S"))
        else:
            start_time.insert(0, "HH:MM:SS")
        
        stop_cal = DateEntry(frame, width=8, background='black', foreground='white', borderwidth=2,                               
                             normalbackground='#FFFFFF', normalforeground='black', 
                             headerbackground='lightgrey', selectbackground='lightblue', selectforeground='black')
        stop_cal.pack(side='left', padx=8)
        stop_time = tk.Entry(frame, width=10, background=self.main_background)
        stop_time.pack(side='left', padx=2)

        if stop:
            stop_cal.set_date(stop.date())
            stop_time.insert(0, stop.strftime("%H:%M:%S"))
        else:       
            stop_time.insert(0, "HH:MM:SS")
        
        # Button to finalize session
        save_button = tk.Button(frame, text="Confirm", 
                                command=lambda: self.save_session(session_name, frame, start_cal, start_time, stop_cal, stop_time))
        save_button.pack(side='left', padx=10)
        self.session_name_entry.delete(0, 'end')

    def save_session(self, session_name, frame, start_cal, start_time, stop_cal, stop_time):
        try:
            print(f"Collecting info for session {session_name}")
            start_datetime = self.combine_date_time(start_cal.get_date(), start_time.get())
            stop_datetime = self.combine_date_time(stop_cal.get_date(), stop_time.get())
            self.sessions[session_name] = (start_datetime, stop_datetime)
            print(f"Session {session_name} was saved successfully. Showing all sessions below")
            print(self.sessions)
            frame.config(bg='lightgreen')  # Set to light green on successful save
        except ValueError as e:
            messagebox.showerror("Invalid Time", str(e))
            frame.config(bg='lightcoral')  # Set to light red on error


    def combine_date_time(self, date, time_str):
        try:
            time_parts = [int(part) for part in time_str.split(':')]
            time = datetime.time(*time_parts)
        except ValueError:
            raise ValueError("Time must be in HH:MM:SS format and valid.")
        return datetime.datetime.combine(date, time)


    def populate_dictionary(self, animal_dir, animal_id, exp_dates, dob = [], sex = [], mac = [], fed = [], session_metadata = {}):
        d = {}
        d["animal_id"] = animal_id
        #must be datetime object
        d["exp_dates"] = exp_dates
        d["dob"] = dob
        d["sex"] = sex
        d["mac"] = mac
        d["fed"] = fed
        if session_metadata == {}:
            session_metadata['info'] = "Dictionary containing cropping coordinates for each video file on each session."
        d['session_metadata'] = session_metadata
        return d


    def validate_fields(self):
        errors = []
        if not self.animal_id_entry.get().strip():
            errors.append("Animal ID is required.")
        if not self.sessions:
            errors.append("At least one session with start and stop dates is required.")
        if self.dob_cal.get_date() >= datetime.date.today():
            errors.append("Date of birth assigned to today (or the future!). This is likely an error.")
        if not self.sex_var.get().strip():
            errors.append("Sex is required.")
        if not self.fed_entry.get().strip():
            errors.append("Fed details are required.")
        return errors

    def populate_form(self):

        self.animal_id_entry.delete(0, 'end')
        self.animal_id_entry.insert(0, self.metadata['animal_id'])        
        #self.animal_id_entry.set(self.metadata['animal_id'])
        self.dob_cal.set_date(self.metadata['dob'])
        self.sex_var.set(self.metadata['sex'])
        # we are not going to check mac
        self.fed_entry.delete(0, 'end')
        self.fed_entry.insert(0, ', '.join(map(str, self.metadata['fed'].ravel())))
        self.load_sessions_from_metadata()

    def submit_form(self):
        errors = self.validate_fields()
        if errors:
            messagebox.showerror("Validation Errors", "\n".join(errors))
            return
        
        animal_id = self.animal_id_entry.get()
        dob = self.dob_cal.get_date()
        sex = self.sex_var.get()
        mac = self.get_mac()
        fed = self.fed_entry.get()
        # things are passed as a list to match requirements from rest of the code
        if self.metadata is None:
            print("Creating new metadata!")
            self.metadata = self.populate_dictionary(animal_dir = "", animal_id=animal_id, exp_dates=self.sessions, dob=dob, sex = sex, mac=mac, fed=[fed])
            print(self.metadata) 
        else: 
            print("Saving existing metadata")
            print(self.metadata) 

        self.dict_to_parquet()
        messagebox.showinfo("Metadata Saved", "Metadata was successfully save to file")


    def flatten_dict(self, data):
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

    # Loading of metadata
    def dict_to_parquet(self):
        # TODO: manage /animal_id folder creation for user

        ##get animal_id -> camera/MLA___?
        out_folder = os.path.join(self.base_path, self.metadata["animal_id"])
        
        # Ensure the directory exists
        if not os.path.exists(out_folder):
            print(f"Output folder not found. It will be created: {out_folder}")
            os.makedirs(out_folder, exist_ok=True)
        # Open a file dialog to select the parquet file
        file_path = filedialog.asksaveasfilename(
            title="Create a Parquet file",
            initialdir=out_folder,
            initialfile=f"sub-{self.metadata['animal_id']}_metadata.parquet",
            filetypes=[("Parquet files", "*.parquet")]
        )
        
        if file_path:  # Proceed only if a file was selected
            flattened_data = self.flatten_dict(self.metadata)
            df = pd.DataFrame([flattened_data])
            df.to_parquet(file_path)
            # try:
            #     # Assuming original_metadata_path is the path of the original file you want to delete
            #     os.remove(self.original_metadata_path)
            #     print("Original metadata file has been successfully removed.")
            # except OSError as e:
            #     print(f"Error: {e.strerror}. File {e.filename} could not be removed.")
            print("[green]success! [/green]")

    def load_metadata(self):
        # Open a file dialog to select the parquet file
        file_path = filedialog.askopenfilename(
            title="Select a Parquet file",
            filetypes=[("Parquet files", "*.parquet")]
        )
        
        if file_path:  # Proceed only if a file was selected
            self.metadata = self.read_metadata(file_path)
            print(self.metadata)  # Display metadata 
            # update the GUI accordingly
            self.populate_form()

    def read_metadata(self, parquet_path):
        df = pd.read_parquet(parquet_path)
        # TODO: this will get you the first row only.
        # We shouldn't have more than one, but it's not asserted
        return df.loc[0, :].to_dict()

    def check_in_range(self, target_dt):
        exp_dates = self.metadata["exp_dates"]
        for session_type, span in exp_dates.items(): 
            # we assume exclusive session types (target_date only belongs to one)
            if min(span) <= target_dt <= max(span):
                # then it actually belongs to session_type
                return session_type

    def get_bids_session(self, video_path, data_type = "str"):
        if isinstance(video_path, Path):
            video_path = str(video_path)

        pattern = r"ses-([a-zA-Z0-9]+)_"
        match = re.search(pattern, video_path)
        if match:
            timestamp_str = match.group(1)
            timestamp_dt = datetime.datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
            # Create a new datetime object
            #timestamp_dt = datetime.datetime(timestamp_dt.year, timestamp_dt.month, timestamp_dt.day)
            if type == "str":
                return timestamp_str
            if type == "dt":
                timestamp_dt
                return timestamp_dt
        else:
            raise ValueError(f"Cannot find pattern in {video_path}")

    def get_session(self, file_path, data_type="str", format_in = "%Y-%m-%dT%H-%M-%S", format_out="%Y%m%dT%H%M%S"):
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


    def find_mp4_videos(self, directory):
        """
        Recursive finds all .mp4 video files within the given directory.
        :param directory: The directory path as a string or Path object where to start the search.
        :return: A list of Paths to the .mp4 files.
        """
        # Convert directory to a Path object if it's not already one
        path = Path(directory)
        # Use the rglob method to find all .mp4 files recursively
        mp4_files = list(path.rglob(f"*{self.metadata['animal_id']}*.mp4"))
        return mp4_files

    def collect_session_metadata(self):
        if self.metadata is None:
            messagebox.showwarning("Metadata is missing", "Metadata has to be entered manually or loaded")
            return

        animal_dir = filedialog.askdirectory()
        if animal_dir:
            video_path_list = self.find_mp4_videos(animal_dir)
        else: 
            messagebox.showinfo("Select Directory", "A directory needs to be selected to be able to find videos")
            return
        print("video paths", video_path_list)
        data = []
        # trigger matching
        for video_path in video_path_list:
            # files from camera get generated as %Y-%m-%dT%H-%M-%S
            # we will coerce to %Y%m%dT%H%M%S
            session_id = self.get_session(video_path, data_type = "str", format_in = "%Y-%m-%dT%H-%M-%S")
            session_dt = self.get_session(video_path, data_type = "dt", format_in = "%Y-%m-%dT%H-%M-%S")
            session_type = self.check_in_range(session_dt)
            # create session metadata dictionary
            self.metadata['session_metadata'][session_id] = {
                'filepath': str(video_path), # parquet cannot store PosixPath()
                'session_type': session_type,
                'coords': {}
            }

            # this is easier for data aggregation
            data.append({
                'session_id': session_id,
                'session_dt': session_dt,
                'session_type': session_type,
                'filepath': str(video_path) # coerce from path to str
                })

        df = pd.DataFrame(data)
        # Group by 'session_type' and get the index of the minimum 'session_dt' for each group
        idx = df.groupby('session_type')['session_dt'].idxmin()
        # Use these indices to get the corresponding rows from the original DataFrame
        min_sessions_df = df.loc[idx]
        print(min_sessions_df)
        regions = {}

        for index, row in min_sessions_df.iterrows():
            session_type = row['session_type']
            video_path = row['filepath']
            # get the coords for a particular session type
            regions[session_type] = self.get_cropping_coords(video_path)
            print(f"Adding coords for session_type = `{session_type}`")
            for key in self.metadata['session_metadata'].keys():
                if key != 'info' and self.metadata['session_metadata'][key]['session_type'] == session_type:
                    self.metadata['session_metadata'][key]['coords'] = regions[session_type]
        return

    def get_cropping_coords(self, filepath):
    
        selector = VideoSelector(filepath)
        selector.select_areas()
        # light_cage_coords, dark_cage_coords = selector.get_coords()
        regions = selector.regions
        regions['frame_shape'] = selector.get_shape()
        selector.release()
        return regions

if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentMetadataApp(root)
    root.mainloop()