import tkinter as tk
from tkinter import messagebox
import datetime
from tkcalendar import DateEntry
from tkinter import messagebox, font
from rich import print
import subprocess
import sys

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
        self.submit_button = self.create_button("Save Metadata", self.submit_form)
        self.submit_button.grid(row=6, column=1, columnspan=1, pady=20)
        self.trigger_main_button = self.create_button(text="✔ Record", command=self.trigger_main_py)
        self.trigger_main_button.grid(row=6, column=2, columnspan=1, pady=20)


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

    def create_session_ui(self, session_name):
        frame = tk.Frame(self.dynamic_session_frame, bg=self.main_background) 
        frame.pack(fill='x', expand=True, pady=5)
        
        tk.Label(frame, text=session_name, bg=self.main_background).pack(side='left', padx=10)
        
        start_cal = DateEntry(frame, width=8, background='black', foreground='white', borderwidth=2,
                              normalbackground='#FFFFFF', normalforeground='black', 
                              headerbackground='lightgrey', selectbackground='lightblue', selectforeground='black')
        start_cal.pack(side='left', padx=8)
        start_time = tk.Entry(frame, width=10)
        start_time.pack(side='left', padx=2)
        start_time.insert(0, "HH:MM:SS")
        
        stop_cal = DateEntry(frame, width=8, background='black', foreground='white', borderwidth=2,                               
                             normalbackground='#FFFFFF', normalforeground='black', 
                             headerbackground='lightgrey', selectbackground='lightblue', selectforeground='black')
        stop_cal.pack(side='left', padx=8)
        stop_time = tk.Entry(frame, width=10, background=self.main_background)
        stop_time.pack(side='left', padx=2)
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
            print("Session {session_name} was saved successfully. Showing all sessions below")
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


    def populate_dictionary(self, animal_dir, animal_id, exp_dates, dob = [], sex = [], mac = [], fed = [], session_metadata = {}, coords_by_session = None):
        d = {}
        d["animal_id"] = animal_id
        #must be datetime object
        d["exp_dates"] = exp_dates
        d["dob"] = dob
        d["sex"] = sex
        d["mac"] = mac
        d["fed"] = fed
        #d['session_metadata'] = session_metadata
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
        self.metadata = self.populate_dictionary(animal_dir = "", animal_id=[animal_id], exp_dates=self.sessions, dob=[dob], sex = [sex], mac=[mac], fed=[fed])

        messagebox.showinfo("Metadata Saved", "Metadata was successfully save to file")
        print(self.metadata)
        
        # Placeholder to call a script if needed
        # os.system(f"python main.py --arg {animal_id} --another-arg {dob}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentMetadataApp(root)
    root.mainloop()