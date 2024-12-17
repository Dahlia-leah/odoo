from flask import Flask, jsonify
import serial
import time
import logging

app = Flask(__name__)

# USB Scale configuration (adjust the serial port and baud rate based on your scale)
SCALE_SERIAL_PORT = "/dev/ttyUSB0"  # Change this to your scale's serial port
BAUD_RATE = 9600  # Adjust the baud rate if necessary

# Set up logging for better visibility
logging.basicConfig(level=logging.DEBUG)

# Function to read data from the scale
def read_scale_data():
    try:
        # Open the serial connection
        with serial.Serial(SCALE_SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            time.sleep(2)  # Allow scale to stabilize
            line = ser.readline().decode('ascii').strip()  # Read the line from scale
            logging.debug(f"Raw scale data: {line}")  # Debugging: Print the raw data

            if line:
                # Split the scale data into components (e.g., "166 kg" or "166")
                parts = line.split()

                # Try to extract the weight and unit
                if len(parts) == 1:
                    # If only weight is given (e.g., "166"), assume unit is kg
                    weight = float(parts[0]) if parts[0].replace('.', '', 1).isdigit() else 0.0
                    unit = "kg"  # Default unit
                elif len(parts) >= 2:
                    # If both weight and unit are given (e.g., "166 kg")
                    weight = float(parts[0]) if parts[0].replace('.', '', 1).isdigit() else 0.0
                    unit = parts[1]  # Extract unit from second part

                logging.debug(f"Parsed data - Weight: {weight}, Unit: {unit}")  # Debugging: Print parsed data

                return {"weight": weight, "unit": unit}

            # If no data is found, return default values
            logging.warning("No valid scale data found, returning default values.")
            return {"weight": 0.0, "unit": "kg"}

    except serial.SerialException as e:
        logging.error(f"Error reading from serial port: {e}")
        return {"weight": 0.0, "unit": "kg"}  # Return default values in case of error

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"weight": 0.0, "unit": "kg"}  # Return default values in case of other errors

@app.route("/get_weight", methods=["GET"])
def get_weight():
    """API endpoint to fetch live weight from the scale"""
    data = read_scale_data()
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
