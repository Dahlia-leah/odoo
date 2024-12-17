from flask import Flask, jsonify
import serial
import time
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# USB scale configuration
SCALE_PORT = "/dev/ttyUSB0"  # Replace with the correct serial port (e.g., "COM3" on Windows)
BAUD_RATE = 9600            # Set baud rate as per your scale's specification

def read_scale_data():
    """
    Reads weight data from the scale over USB.
    """
    try:
        with serial.Serial(SCALE_PORT, BAUD_RATE, timeout=1) as ser:
            time.sleep(2)  # Allow scale to stabilize
            
            # Read data from the scale
            line = ser.readline().decode('ascii').strip()
            logging.debug(f"Raw scale data: {line}")
            
            # Parse weight and unit from the raw data
            if line:
                parts = line.split()
                weight = float(parts[0]) if parts[0].replace('.', '', 1).isdigit() else 0.0
                unit = parts[1] if len(parts) > 1 else "kg"  # Default unit is "kg"
                return {"weight": weight, "unit": unit}

            return {"weight": 0.0, "unit": "kg"}
    except Exception as e:
        logging.error(f"Error reading scale data: {e}")
        return {"weight": 0.0, "unit": "kg"}

@app.route('/get_weight', methods=['GET'])
def get_weight():
    """
    API endpoint to get live weight data from the scale.
    """
    data = read_scale_data()
    return jsonify(data)

if __name__ == "__main__":
    # Run the Flask server on localhost at port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
