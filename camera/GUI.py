import tkinter as tk
from tkinter import messagebox
import datetime
from tkcalendar import DateEntry
from tkinter import messagebox, font



# def populate_dictionary(animal_dir, animal_id, exp_dates, dob = [], sex = [], mac = [], fed = [], session_metadata = {}, coords_by_session = None):
#     d = {}
#     d["animal_id"] = animal_id
#     #must be datetime object
#     d["exp_dates"] = exp_dates
#     d["dob"] = dob
#     d["sex"] = sex
#     d["mac"] = mac
#     d["fed"] = fed
#     #if session_metadata == {}:
#         #session_metadata = get_session_metadata(animal_dir, exp_dates, coords_by_session)
#     #d['session_metadata'] = session_metadata
#     return d


# def validate_fields():
#     errors = []
#     if not animal_id_entry.get().strip():
#         errors.append("Animal ID is required.")
#     if not exp_dates:
#         errors.append("At least one session with start and stop dates is required.")
#     if dob_cal.get_date() == datetime.date.today():
#         errors.append("Please select the date of birth.")
#     if not sex_var.get().strip():
#         errors.append("Sex is required.")
#     if not fed_entry.get().strip():
#         errors.append("Fed details are required.")
#     return errors


# def get_mac(interface = 'wlan0'):
#     # This is good for Raspberry PIs, not good for other OS !
#     # possible interfaces ['wlan0', 'eth0']
#     try:
#         mac = open('/sys/class/net/'+interface+'/address').readline()
#     except:
#         mac = "00:00:00:00:00:00"
#     return mac[0:17]




# def submit_form():
#     errors = validate_fields()
#     if errors:
#         messagebox.showerror("Validation Errors", "\n".join(errors))
#         return
    
#     animal_id = animal_id_entry.get()
#     dob = dob_cal.get_date()
#     sex = sex_var.get()
#     mac = get_mac()
#     fed = fed_entry.get()
#     exp_dates = {}

#     exp_dates_list = []
#     for session_name, (start_cal, stop_cal) in sessions.items():
#         if start_cal.get_date() and stop_cal.get_date():
#             start_datetime = datetime.datetime.combine(start_cal.get_date(), datetime.datetime.min.time())
#             stop_datetime = datetime.datetime.combine(stop_cal.get_date(), datetime.datetime.min.time())
#             exp_dates_list.append({session_name: [start_datetime, stop_datetime]})
   
#     metadata = populate_dictionary(animal_dir = "", animal_id=animal_id, exp_dates=exp_dates_list, dob=[dob], sex = [sex], mac=[mac], fed=[fed])

#     messagebox.showinfo("Form Submitted", "Metadata submitted successfully.")
#     print(metadata)
    
#     # Placeholder to call a script if needed
#     # os.system(f"python main.py --arg {animal_id} --another-arg {dob}")
#     print(metadata)
#     messagebox.showinfo("Form Submitted", "Metadata submitted successfully.")


class ExperimentMetadataApp:
    def __init__(self, master):
        self.master = master
        master.title("Experiment Metadata Collection")
        
        # Styling
        self.style_app()

        # Initializing variables
        self.sessions = {}
        self.sex_var = tk.StringVar()

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
    def on_enter(e, btn):
        btn['background'] = '#CDDC39'  # Green shade for hover

    def on_leave(e, btn):
        btn['background'] = '#E0E0E0'  # Default background

    # Update button creation to use this new style
    def create_button(self, text, command):
        btn = tk.Button(self.master, text=text, command=command, bg='#E0E0E0', fg='black',
                        padx=10, pady=5, relief='flat', borderwidth=0)
        btn.bind("<Enter>", lambda e, b=btn: on_enter(e, b))
        btn.bind("<Leave>", lambda e, b=btn: on_leave(e, b))
        return btn
   
    def setup_ui(self):
        row_options = {'padx': 15, 'pady': 5}
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
        self.session_frame.grid(row=5, columnspan=2, sticky='ew', **row_options)

        tk.Label(self.session_frame, text="Session Name:", bg="#FFFFFF").pack(side='left', padx=10, pady=10)
        self.session_name_entry = tk.Entry(self.session_frame, **self.entry_style)
        self.session_name_entry.pack(side='left', padx=10, pady=10)

        add_button = self.create_button("Add/Edit Session", self.add_or_edit_session)
        add_button.pack(side='left', padx=10, pady=10)

        # Submit Button
        self.submit_button = self.create_button("Submit", self.submit_form)
        self.submit_button.grid(row=6, columnspan=2, pady=20)


    def get_mac(self, interface='wlan0'):
        try:
            return open('/sys/class/net/' + interface + '/address').readline().strip()
        except:
            return "00:00:00:00:00:00"

    def add_or_edit_session(self):
        session_name = self.session_name_entry.get()
        if not session_name:
            messagebox.showerror("Invalid Input", "Session name cannot be empty.")
            return

        if session_name in self.sessions:
            messagebox.showerror("Duplicate Session", "This session name already exists. Please edit the existing one.")
            return

        frame = tk.Frame(self.session_frame)
        frame.pack(fill='x', expand=True, pady=5)

        tk.Label(frame, text=session_name).pack(side='left', padx=10)
        
        start_cal = DateEntry(frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        start_cal.pack(side='left', padx=5)
        stop_cal = DateEntry(frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        stop_cal.pack(side='left', padx=5)

        self.sessions[session_name] = (start_cal, stop_cal)
        self.session_name_entry.delete(0, 'end')

    def submit_form(self):
        # Implement validation and submission logic
        pass  # Placeholder for your existing logic

if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentMetadataApp(root)
    root.mainloop()