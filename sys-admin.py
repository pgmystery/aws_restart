import os
import subprocess


os.system("ls")

try:
    subprocess.run(["ls"])
except FileNotFoundError:
    pass

try:
    subprocess.run(["ls","-l"])
except FileNotFoundError:
    pass

command="uname"
commandArgument="-a"
print(f'Gathering system information with command: {command} {commandArgument}')
try:
    subprocess.run([command,commandArgument])
except FileNotFoundError:
    pass

command="ps"
commandArgument="-x"
print(f'Gathering active process information with command: {command} {commandArgument}')
try:
    subprocess.run([command,commandArgument])
except FileNotFoundError:
    subprocess.run(["powershell", command])
