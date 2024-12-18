import os
import usb.core
import usb.util
import serial
import re
from flask import Flask, jsonify

app = Flask(__name__)

def find_usb_scale():
    """
    Finds the USB scale device based on its descriptors or serial connection.
    Returns the device object if found, else None.
    """
    if os.name == 'nt':  # Windows
        # On Windows, look for the COM ports
        for port in range(1, 256):
            try:
                ser = serial.Serial(f'COM{port}', baudrate=9600, timeout=1)
                if ser.is_open:
                    # Check if this matches the scale's serial protocol
                    ser.write(b'CHECK')  # Send a test command to the scale if needed
                    data = ser.readline().decode('utf-8').strip()
                    print(f"Found device on COM{port}: {data}")
                    return ser
            except serial.SerialException:
                continue
    else:  # Linux or Mac
        # On Linux, find devices under /dev/ttyUSB*
        for dev in os.listdir('/dev'):
            if dev.startswith('ttyUSB'):
                try:
                    serial_port = f'/dev/{dev}'
                    ser = serial.Serial(serial_port, baudrate=9600, timeout=1)
                    if ser.is_open:
                        # Check if this matches the scale's serial protocol
                        ser.write(b'CHECK')  # Send a test command to the scale if needed
                        data = ser.readline().decode('utf-8').strip()
                        print(f"Found device on {serial_port}: {data}")
                        return ser
                except serial.SerialException:
                    continue
    return None

def parse_scale_data(raw_data):
    """
    Parses raw data from the scale and extracts the weight and unit.
    Assumes the data format is like: "nter. 1665.0     g"
    """
    # Remove unwanted characters before the weight value
    cleaned_data = re.sub(r'^[^\d]*', '', raw_data)  # Remove everything before the first digit
    print(f"Cleaned data: {cleaned_data}")  # Debugging output
    
    # Remove any non-numeric characters except for the decimal point and unit
    cleaned_data = re.sub(r'[^0-9\.g]', '', cleaned_data)

    # Try to fix the format in case of misplaced decimal points
    cleaned_data = cleaned_data.strip()

    # Ensure only a single decimal point is present and valid
    match = re.match(r'([0-9]+(?:\.[0-9]+)?)\s*(g|kg|lb)?', cleaned_data)

    if match:
        weight = match.group(1)  # Extract the weight
        weight = weight.replace("..", ".")  # Fix any misplaced dots
        try:
            weight = float(weight)  # Convert to float
        except ValueError:
            return None, None  # Return None if the weight is still not valid

        unit = match.group(2) if match.group(2) else 'g'  # Extract the unit, default to 'g' if not found
        return weight, unit
    else:
        return None, None  # Return None if parsing fails

def read_usb_scale_data():
    """
    Connects to the USB scale and reads data.
    Returns scale reading and unit, or error message.
    """
    scale = find_usb_scale()
    if scale is None:
        return {"error": "USB scale not found"}, 404

    try:
        # Read data from the scale
        data = scale.readline().decode('utf-8').strip()
        print(f"Raw data from scale: {data}")  # Debugging output

        # Parse the raw data to extract the weight and unit
        weight, unit = parse_scale_data(data)
        
        if weight is not None:
            return {"weight": weight, "unit": unit}, 200
        else:
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
    app.run(host='0.0.0.0', port=5000)
