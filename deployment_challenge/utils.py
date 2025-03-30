import json
import subprocess
import urllib
from datetime import datetime
from pathlib import Path


def get_public_ip():
    try:
        # Make a request to a public IP service (ipify)
        with urllib.request.urlopen('https://api.ipify.org?format=json') as response:
            # Read the response and decode it to a string
            data = response.read().decode()
            # Parse the JSON response
            ip_info = json.loads(data)
            # Return the public IP
            return ip_info['ip']
    except urllib.error.URLError as e:
        print(f"Error: {e}")
        return None


def datetime_converter(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO format string
    raise TypeError(f"Type {type(obj)} not serializable")


def create_ssh_tunnel(local_port: int, remote_port: int, remote_server_ip: str, ssh_server_ip: str):
    print("SSH TUNNEL TO THE WEBSERVER OVER HTTP")
    while True:
        pem_file_location = input("Enter the PEM file location [./labsuser.pem]: ")
        if pem_file_location == "":
            pem_file_location = "./labsuser.pem"

        pem_file_location = Path(pem_file_location)

        if pem_file_location.is_file():
            break
        else:
            print(f"The PEM file location doesn't exist. ({str(pem_file_location.resolve())})")

    ssh_tunnel_command = [
        "ssh",
        "-oStrictHostKeyChecking=no",
        "-i", pem_file_location.resolve(),
        "-N", "-L", f"localhost:{str(local_port)}:{remote_server_ip}:{str(remote_port)}",
        f"ec2-user@{ssh_server_ip}"
    ]
    # I can't use .join :(
    ssh_tunnel_command_string = ""
    for word in ssh_tunnel_command:
        ssh_tunnel_command_string += str(word) + " "
    ssh_tunnel_command_string = ssh_tunnel_command_string.strip()
    print(f'RUN COMMAND: "{ssh_tunnel_command_string}"')

    # Run the command in the background using subprocess.Popen
    process = subprocess.Popen(ssh_tunnel_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    print("You can now access the private Web-Server Webpage")
    print(f"URL: http://localhost:8080")
    input("Press enter to exit...")

    try:
        process.terminate()
    except:
        process.kill()
