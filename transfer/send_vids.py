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
        stdin, stdout, stderr = client.exec_command(f'mkdir -p {remote_folder}')
        stderr_output = stderr.read()  # Wait for the directory creation command to complete
        if stderr_output:
            print(f"Error during directory creation: {stderr_output}")
        else:
            print(f"Remote directory is ready at {remote_folder}")

        # Use rsync to sync the data directory
        print("Trying to send data via rsync")
        rsync_command = f"rsync -avz -e 'ssh -p {nas_port}' {local_folder}/ {nas_user}@{nas_ip}:{remote_folder}"
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
    parser.add_argument("--project_id", required=True, help="Project ID for constructing project path to send videos to. This will construct a project in the form of MLA/project_id. Do not end this with a '/'", default=None)
    parser.add_argument("--config_path", required=True, help="Path to credentials to establish sftp connection to server/remote computer where data will be sent to.", default=None)
    args = parser.parse_args()

    if args.local_folder is not None:
        local_folder = args.local_folder
        local_folder = os.path.join(local_folder, args.animal_id)
        print(f"Using User-Provided path: {local_folder}")
    else:
        # go with hardcoded
        local_folder = "/home/python_camera/camera"
        local_folder = os.path.join(local_folder, args.animal_id)
        print(f"Using Hard-Coded path: {local_folder}")

    remote_folder = os.path.join("volume1", "MLA", args.project_id, args.animal_id)
    print(f"Data will be sent to {remote_folder}")
    assert args.config_path is not None
    config = read_config(args.config_path)
    sync(local_folder=local_folder, remote_folder=remote_folder, config=config)
