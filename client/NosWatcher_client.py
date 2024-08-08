import psutil
import requests
import time
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
import sys
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image

# Use hardcoded CLIENT_ID or not?
use_hardcoded_client = False  # False will ask for the CLIENT_ID

# General variables
hardcoded_client_id = 'VM2_Client'  # Hardcoded CLIENT_ID
client_id_file = 'client_id.txt'  # Filename where CLIENT_ID will be saved
process_name = 'NosTale.exe'  # Process name we will have to look for
server_ip = "127.0.0.1"  # Server IP
server_port = "5000"  # Server PORT
server_endpoint = "update_status"  # Server METHOD
use_https = False  # Use HTTPS when connecting to the Server IP


def get_client_id():
    """
    Retrieves the CLIENT_ID either from a hardcoded value, a file, or through user input.
    Returns the CLIENT_ID as a string.
    """
    if use_hardcoded_client:
        return hardcoded_client_id

    if os.path.exists(client_id_file):
        with open(client_id_file, 'r') as f:
            client_id = f.read().strip()
            if client_id:
                return client_id

    client_id = None
    if getattr(sys, 'frozen', False):  # If the file is compiled as an executable
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        # Set the Tkinter icon
        icon_path = os.path.join(base_path, "icons/NosWatcher.ico")
        root.iconbitmap(default=icon_path)

        # Show the input dialog
        client_id = simpledialog.askstring("Input", "Enter the CLIENT_ID for this machine:", parent=root)
        if not client_id:
            messagebox.showerror("Error", "CLIENT_ID not specified. Exiting...", parent=root)
            sys.exit(1)
        root.destroy()  # Close the main window after input
    else:  # If the file is run from terminal
        client_id = input("Enter the CLIENT_ID for this machine: ").strip()

    if client_id:
        with open(client_id_file, 'w') as f:
            f.write(client_id)
    return client_id


def get_process_ids(process_name):
    """
    Retrieves the process IDs for a given process name.
    Returns a list of process IDs.
    """
    pids = [proc.pid for proc in psutil.process_iter(['pid', 'name']) if proc.info['name'] == process_name]
    return pids


def check_process(pid):
    """
    Checks if a process with a given PID exists.
    Returns True if the process exists, False otherwise.
    """
    return psutil.pid_exists(pid)


def send_status(client_id, process_name):
    """
    Sends the status of the specified processes to a server.
    """
    pids = get_process_ids(process_name)

    status = {
        'client_id': client_id,
        'client1': check_process(pids[0]) if len(pids) > 0 else False,
        'client2': check_process(pids[1]) if len(pids) > 1 else False
    }

    protocol = "https" if use_https else "http"
    server_url = f"{protocol}://{server_ip}:{server_port}/{server_endpoint}"

    try:
        requests.post(server_url, json=status)
    except Exception as e:
        print(f"Error sending status: {str(e)}")


def on_quit(icon, item):
    """
    Handles the quit action from the system tray icon.
    """
    icon.stop()
    os._exit(0)


def setup(icon):
    """
    Sets up the system tray icon.
    """
    icon.visible = True


def monitor_processes(client_id, process_name):
    """
    Continuously monitors the specified processes and sends their status every 5 seconds.
    """
    while True:
        send_status(client_id, process_name)
        time.sleep(5)


if __name__ == '__main__':
    # Determine the base path
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    icon_path = os.path.join(base_path, "icons/NosWatcher.ico")

    # Determine if we are in interactive mode
    interactive_mode = False
    if getattr(sys, 'frozen', False):  # If the file is compiled as an executable
        interactive_mode = True
    else:
        interactive_mode = False

    # If we are running in interactive mode configure a taskbar element using our icon
    if interactive_mode:
        icon = pystray.Icon("name")
        icon.menu = pystray.Menu(item('Quit', on_quit))
        icon.icon = Image.open(icon_path)  # Specify the path to your icon.ico file
        icon.title = "NosWatcher"

    client_id = get_client_id()  # Request the client_id once at the beginning

    # Start monitoring the processes in a separate thread
    monitor_thread = threading.Thread(target=monitor_processes, args=(client_id, process_name))
    monitor_thread.daemon = True
    monitor_thread.start()

    # If we are running in interactive mode, show the taskbar element we created previously
    if interactive_mode:
        icon.run(setup)
    # Else, keep the program alive
    else:
        while True:
            time.sleep(1)
