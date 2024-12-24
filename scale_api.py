import os
import subprocess
import sys
import time
from flask import Flask, jsonify
import re
import serial

app = Flask(__name__)

def start_serveo():
    """
    Starts Serveo and retrieves the public URL.
    """
    try:
        serveo_process = subprocess.Popen(
            ["ssh", "-R", "80:localhost:5000", "serveo.net"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("Starting Serveo tunnel...")
        time.sleep(5)  # Wait for Serveo to establish the connection

        output = serveo_process.stdout.readline().decode('utf-8').strip()
        url_match = re.search(r'https://[a-zA-Z0-9.-]+\.serveo\.net', output)
        if url_match:
            return url_match.group(0)
        else:
            raise Exception("Failed to retrieve Serveo URL.")
    except Exception as e:
        print(f"Error starting Serveo: {e}")
        sys.exit(1)

def find_usb_scale():
    """
    Finds the USB scale device based on its descriptors or serial connection.
    Returns the device object if found, else None.
    """
    print("Searching for USB scale...")
    if os.name == 'nt':  # Windows
        for port in range(1, 256):
            try:
                ser = serial.Serial(f'COM{port}', baudrate=9600, timeout=1)
                if ser.is_open:
                    ser.write(b'CHECK')
                    data = ser.readline().decode('utf-8').strip()
                    print(f"Found USB scale at COM{port}")
                    return ser
            except serial.SerialException:
                continue
    else:  # Linux or macOS
        for dev in os.listdir('/dev'):
            if dev.startswith('ttyUSB'):
                try:
                    serial_port = f'/dev/{dev}'
                    ser = serial.Serial(serial_port, baudrate=9600, timeout=1)
                    if ser.is_open:
                        ser.write(b'CHECK')
                        data = ser.readline().decode('utf-8').strip()
                        print(f"Found USB scale at /dev/{dev}")
                        return ser
                except serial.SerialException:
                    continue
    return None

def parse_scale_data(raw_data):
    """
    Parses raw data from the scale and extracts the weight and unit.
    """
    cleaned_data = re.sub(r'^[^\d]*', '', raw_data)
    cleaned_data = re.sub(r'[^0-9\.g]', '', cleaned_data)
    cleaned_data = cleaned_data.strip()

    match = re.match(r'([0-9]+(?:\.[0-9]+)?)\s*(g|kg|lb)?', cleaned_data)

    if match:
        weight = match.group(1)
        try:
            weight = float(weight)
        except ValueError:
            return None, None
        unit = match.group(2) if match.group(2) else 'g'
        return weight, unit
    return None, None

def read_usb_scale_data():
    """
    Connects to the USB scale and reads data.
    """
    scale = find_usb_scale()
    if scale is None:
        return {"error": "USB scale not found"}, 404

    try:
        data = scale.readline().decode('utf-8').strip()
        weight, unit = parse_scale_data(data)
        if weight is not None:
            return {"weight": weight, "unit": unit}, 200
        return {"error": "Failed to parse weight from scale data"}, 500
    except Exception as e:
        return {"error": f"Error reading scale: {str(e)}"}, 500

@app.route('/read-scale', methods=['GET'])
def read_scale():
    """
    Endpoint to read data from the USB scale.
    """
    result, status = read_usb_scale_data()
    return jsonify(result), status

def start_flask():
    """
    Starts the Flask app in a separate thread.
    """
    from threading import Thread

    def run():
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

    flask_thread = Thread(target=run)
    flask_thread.start()

if __name__ == '__main__':
    print("Starting Flask app...")
    start_flask()

    public_url = start_serveo()
    print(f"Your Flask app is now exposed to the internet at: {public_url}")
