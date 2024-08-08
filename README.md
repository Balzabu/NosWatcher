# NosWatcher

NosWatcher is a client-server application for monitoring the execution status of specific processes on clients. The server collects updates from clients and displays them on a web page. Created for botters who manage hundreds of clients on as many virtual machines.

## Installation

### Requirements

- Python 3.x
- Flask
- psutil
- requests
- pystray
- Pillow

### Dependency Installation

Use `pip` to install the necessary dependencies:

```sh
pip install flask psutil requests pystray pillow
```

## Configuration

### Client

1. Create an `icons` folder and add your `NosWatcher.ico` icon inside it (or use the one provided).
2. Modify the `NosWatcher_client.py` file if necessary (e.g., to change the `use_hardcoded_client` flag and the `hardcoded_client_id`, `process_name` or `server_ip`).
3. Compile the client into an executable using PyInstaller:

```sh
pyinstaller --onefile --noconsole --icon=icons/NosWatcher.ico --add-data "icons/NosWatcher.ico;icons" NosWatcher_client.py
```

This will generate an `.exe` file in the `dist` folder that can be run directly without needing to install Python. 
Run the compiled executable on each machine you want to monitor.

**Note you can skip this step if you can avoid compiling the script to an `.exe` file is you decide to run the python script directly on the clients.**

### Server

1. Start the Flask server:

```sh
python NosWatcher_server.py
```

2. Visit the Flask app and enjoy :)


## Usage

### Client

When you start the client, you will be prompted to enter the `CLIENT_ID` if it is not already configured.
Once the `CLIENT_ID` is provided interactively or not, the value will be saved on the machine in a file named `client_id.txt`.
The client will send the process execution status to the server every 5 seconds.

In all subsequent runs, if the `client_id.txt` file is already present in the same path as the `.exe` file, a new `CLIENT_ID` will not be requested.

### Server

The server collects updates from the client statuses and saves them to `statuses.json`. The server periodically checks the status updates from clients and sets them to offline if they have not sent updates for more than a minute indicating that either the Clients or the VM itself stopped working.

## Project Structure

```
NosWatcher/
│
├── client/
│   ├── icons/
│   │   └── NosWatcher.ico
│   ├── NosWatcher_client.py
│
├── server/
│   ├── templates/
│   │   └── NosWatcher.html
│   ├── statuses.json
│   └── NosWatcher_server.py
│
└── README.md
│
└── LICENSE
```

## Contributing
I welcome contributions from the community! If you're interested in helping improve this script, feel free to:

- Open an issue to report bugs or suggest enhancements.
- Fork the repository, make your changes, and submit a pull request.

Your contributions make this project better for everyone. Thank you for your support!
