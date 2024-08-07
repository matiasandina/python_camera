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

def sync(local_folder, remote_folder, config):
    nas_user = config.get('user')
    nas_ip = config.get('ip')
    nas_password = config.get('pass')
    nas_port = config.get('nas_port')

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {nas_user}@{nas_ip} at port {nas_port}")
        client.connect(nas_ip, port=nas_port, username=nas_user, password=nas_password, timeout=10)

        # Determine the remote directory path, creating it if necessary
        print(f"Checking if remote directory {remote_folder} exists")
        if not os.path.isdir(remote_folder):
            print(f"Creating remote directory {remote_folder}")
            stdin, stdout, stderr = client.exec_command(f'mkdir -p {remote_folder}')
            stderr.read()  # Wait for the directory creation command to complete
            print(f"Created {remote_folder}")
        else:
            print(f"{remote_folder} already exists")

        # Use rsync to sync the data directory
        rsync_command = f"rsync -avz {local_folder}/ {nas_user}@{nas_ip}:{remote_folder}"
        print("Trying to send data via rsync. Command to execute")
        print(f'{rsync_command}')
        os.system(rsync_command)

        client.close()
    except paramiko.SSHException as ssh_err:
        print(f"An SSH error occurred: {ssh_err}")
    except Exception as e:
        print(f"An error occurred during data synchronization: {e}")

if __name__ =="__main__":

    parser = argparse.ArgumentParser()
    # parser.add_argument("--start_date", help="Starting date for batch processing (format: YYYY-MM-DD)")
    parser.add_argument("--animal_id", required=True, help="Animal ID for constructing the base path")
    parser.add_argument("--local_folder", required=False, help="Full path of local folder (everything before `animal_id`) if not using default hard-coded one", default=None)
    parser.add_argument("--project_id", required=True, help="Project ID for constructing project path to send videos to. This will construct a project in the form of /volume1/MLA/pilots/project_id. Do not end this with a '/'", default=None)
    parser.add_argument("--config_path", required=False, help="Path to credentials to establish sftp connection to server/remote computer where data will be sent to.", default=None)
    parser.add_argument("--remote_folder", required=False, default=None, help="Remote path to direct the files. Resulting will be {remote_path}/{project_id}")
    args = parser.parse_args()

    if args.local_folder is not None:
        local_folder = args.local_folder
        local_folder = os.path.join(local_folder, args.animal_id)
        print(f"Using User-Provided path: {local_folder}")
    else:
        # go with hardcoded
        local_folder = "/home/pi/python_camera/camera"
        local_folder = os.path.join(local_folder, args.animal_id)
        print(f"Using Hard-Coded local path: {local_folder}")

    if args.remote_folder is None:
        remote_folder = os.path.join("/volume1", "MLA", 'pilots', args.project_id, args.animal_id)
        print(f"Using Hard-Coded remote path: {remote_folder}")
    else:
        remote_folder = args.remote_folder
        print(f"Using User-Provided remote path: {remote_folder}")

    if args.config_path is not None:
        config_path = args.config_path
        print(f"Using User-Provided path: {config_path}")
    else:
        config_path = "/home/pi/python_camera/transfer/.config.yaml"
        print(f"Using hard-coded config path: {config_path}")


    print(f"Data will be sent to {remote_folder}")
    # assert args.config_path is not None
    config = read_config(config_path)
    sync(local_folder=local_folder, remote_folder=remote_folder, config=config)
