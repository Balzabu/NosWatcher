from flask import Flask, request, jsonify, render_template
import threading
import time
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
statuses = {}
status_file = 'statuses.json'
offline_timeout = timedelta(minutes=1)

# Function to load statuses from file
def load_statuses():
    global statuses
    if os.path.exists(status_file) and os.path.getsize(status_file) > 0:
        with open(status_file, 'r') as f:
            try:
                statuses = json.load(f)
            except json.JSONDecodeError:
                statuses = {}
        # Set all statuses to offline until they are updated
        for key in statuses:
            statuses[key]['client1'] = False
            statuses[key]['client2'] = False
            statuses[key]['last_update'] = None
    else:
        statuses = {}

# Function to save statuses to file
def save_statuses():
    with open(status_file, 'w') as f:
        json.dump(statuses, f)

@app.route('/update_status', methods=['POST'])
def update_status():
    """
    Endpoint to update the status of a client.
    Expects a JSON payload with client_id, client1, and client2 status.
    """
    try:
        data = request.json
        client_id = data['client_id']
        statuses[client_id] = {
            'client1': data['client1'],
            'client2': data['client2'],
            'last_update': datetime.utcnow().isoformat()
        }
        save_statuses()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        app.logger.error(f"Error in /update_status: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/remove_status', methods=['POST'])
def remove_status():
    """
    Endpoint to remove the status of a client.
    Expects a JSON payload with client_id.
    """
    try:
        data = request.json
        client_id = data['client_id']
        if client_id in statuses:
            del statuses[client_id]
            save_statuses()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        app.logger.error(f"Error in /remove_status: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/')
def index():
    """
    Endpoint to render the main HTML page with the current statuses.
    """
    try:
        return render_template('NosWatcher.html', statuses=statuses)
    except Exception as e:
        app.logger.error(f"Error in /: {str(e)}")
        return f"An error occurred: {str(e)}", 500

def check_offline_status():
    """
    Function to check if clients are offline.
    Runs in a separate thread and updates statuses every 30 seconds.
    """
    while True:
        now = datetime.utcnow()
        for client_id, status in statuses.items():
            if status['last_update']:
                last_update = datetime.fromisoformat(status['last_update'])
                if now - last_update > offline_timeout:
                    status['client1'] = False
                    status['client2'] = False
        save_statuses()
        time.sleep(30)

if __name__ == '__main__':
    load_statuses()
    # Start the offline status checker thread
    threading.Thread(target=check_offline_status, daemon=True).start()
    # Start the Flask server in the main thread
    app.run(host='0.0.0.0', port=5000, debug=True)
