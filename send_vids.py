###paramiko version --> directly inputs password
###send to "/home/pi/python_camera/camera/camera_compressed" in rpi

import subprocess
import os
import paramiko
import netifaces
import argparse
from py_console import console
import yaml

# SFTP settings for Windows machine

"""
windows_hostname = "host_IP"
windows_port = 22
windows_username = 'dlc'
windows_password = 'dlc'

I'm just pretending that there is a .yaml file within the rpi that stores this information in this fomrat
# Configuration data
user: target-user
ip: ip-address
pass: target-password
port: target-port #default port is usually 22

Ok, I checked the send_ip repo and it seems that Matias set up a config.yaml file (yay!)

Path: home/config.yaml
"""


# Function to get the MAC address of the default interface
#Not sure what to do with this
def get_mac_address(interface):
    try:
        return netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
    except ValueError:
        return None

def read_config():

    yaml_path = os.path.join("home", "config.yaml")
    with open(yaml_path, 'r') as file:
        config = yaml.safe_load(file)
    user = config.get('user')
    ip = config.get('ip')
    password = config.get('pass')
    port = config.get('port')

    return user, ip, password, port

def copy_vids(remote_folder, local_folder):

    # Connect to the Windows machine over SFTP
    windows_username, windows_hostname, windows_password, windows_port = read_config()

    transport = paramiko.Transport((windows_hostname, windows_port))
    transport.connect(username=windows_username, password=windows_password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    #not great
    try:
        sftp.stat(remote_folder)
    except FileNotFoundError:
        sftp.mkdir(remote_folder)

    # Transfer files from local folder to remote folder
    existing_files = set(sftp.listdir(remote_folder)) #Test this later - could just make duplicates anyway

    for file_name in os.listdir(local_folder):
        if file_name not in existing_files:
            local_path = os.path.join(local_folder, file_name)
            remote_path = os.path.join(remote_folder, file_name)
            sftp.put(local_path, remote_path)

    # Close the SFTP connection
    sftp.close()
    transport.close()

if __name__ =="__main__":

    parser = argparse.ArgumentParser()
    # parser.add_argument("--start_date", help="Starting date for batch processing (format: YYYY-MM-DD)")
    parser.add_argument("--session_id", help="Session ID for constructing base path")
    parser.add_argument("--animal_id", required=True, help="Animal ID for constructing the base path")
    parser.add_argument("--local_folder", required=False, help="Full path of local folder (everything before `animal_id`) if not using default hard-coded one", default=None)
    parser.add_argument("--project_id", required=True, help="Project ID for constructing project path to send videos to", default=None)

    args = parser.parse_args()
    if args.base_folder is not None:
        local_folder = args.local_folder
        local_folder = os.path.join(local_folder, args.animal_id, args.session_id, "beh")
        console.info(f"Using User-Provided path: {local_folder}")
    else:
        # go with hardcoded
        local_folder = "/home/python_camera/camera"
        local_folder = os.path.join(local_folder, args.animal_id, args.session_id, "beh")
        console.warn(f"Using Hard-Coded path: {local_folder}")

    remote_folder = os.path.join(args.project_id, args.animal_id, args.session_id, "beh")
    copy_vids(remote_folder, local_folder)

    # Get the MAC address of the Ethernet interface
    mac_address = get_mac_address('wlan0')
    # project_path = "D:/Sasha/Video_Tracking"

    # # # Remote folder on Windows machine to receive files
    # # remote_folder = os.path.join(project_path, "videos", "raw", str(mac_address)[-5:].replace(":","_"))

    # # # Local folder containing files on Raspberry Pi
    # # local_folder = os.getcwd()
