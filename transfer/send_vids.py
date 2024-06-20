###paramiko version --> directly inputs password
###send to "/home/pi/python_camera/camera/camera_compressed" in rpi

import subprocess
import os
import paramiko
import argparse
import yaml


def get_mac(interface = 'wlan0'):
    # This is good for Raspberry PIs, not good for other OS !
    # possible interfaces ['wlan0', 'eth0']
    try:
        mac = open('/sys/class/net/'+interface+'/address').readline()
    except:
        mac = "00:00:00:00:00:00"
    return mac[0:17]

def read_config(path):
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def copy_vids(local_folder, remote_folder, config):
    target_user = config.get('user')
    target_ip = config.get('ip')
    target_password = config.get('pass')
    target_port = config.get('port')

    transport = paramiko.Transport((target_ip, target_port))
    transport.connect(username=target_user, password=target_password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    #not great
    try:
        sftp.stat(remote_folder)
    except FileNotFoundError:
        # user must have write permissions
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
    parser.add_argument("--animal_id", required=True, help="Animal ID for constructing the base path")
    parser.add_argument("--local_folder", required=False, help="Full path of local folder (everything before `animal_id`) if not using default hard-coded one", default=None)
    parser.add_argument("--project_id", required=True, help="Project ID for constructing project path to send videos to. This will construct a project in the form of MLA/project_id", default=None)
    parser.add_argument("--config_path", required=True, help="Path to credentials to establish sftp connection to server/remote computer where data will be sent to.", default=None)
    args = parser.parse_args()
    if args.base_folder is not None:
        local_folder = args.local_folder
        local_folder = os.path.join(local_folder, args.animal_id)
        print(f"Using User-Provided path: {local_folder}")
    else:
        # go with hardcoded
        local_folder = "/home/python_camera/camera"
        local_folder = os.path.join(local_folder, args.animal_id)
        print(f"Using Hard-Coded path: {local_folder}")

    remote_folder = os.path.join("MLA", args.project_id, args.animal_id)
    print(f"Data will be sent to {remote_folder}")
    assert args.config_path is not None
    config = read_config(args.config_path)
    copy_vids(remote_folder, local_folder, config)

    # Get the MAC address of the Ethernet interface
    mac_address = get_mac('wlan0')