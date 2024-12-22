import os
import usb.core
import usb.util
import serial
import re
import subprocess
import sys
import requests
from flask import Flask, jsonify
import time

app = Flask(__name__)


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
    else:  # Linux or Mac
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

if __name__ == '__main__':
    print("Starting Flask app on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
