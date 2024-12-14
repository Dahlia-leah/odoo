import serial
import json
import logging

_logger = logging.getLogger(__name__)

class ScaleDriver:
    """
    A driver for managing communication with a serial-connected scale.
    """

    def __init__(self, serial_port='/dev/ttyUSB0', baudrate=9600, timeout=5):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None

    def connect(self):
        """Establish a serial connection to the scale."""
        try:
            self.serial_connection = serial.Serial(
                port=self.serial_port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            _logger.info("Connected to scale on port: %s", self.serial_port)
        except serial.SerialException as e:
            _logger.error("Error connecting to scale: %s", e)
            raise Exception("Failed to connect to the scale device.")

    def disconnect(self):
        """Close the serial connection."""
        if self.serial_connection:
            self.serial_connection.close()
            _logger.info("Disconnected from scale.")

    def get_weight(self):
        """Read and parse data from the scale."""
        if not self.serial_connection:
            self.connect()
        try:
            raw_data = self.serial_connection.readline().decode('utf-8').strip()
            _logger.info("Raw data from scale: %s", raw_data)
            data = json.loads(raw_data)
            return {
                'value': data.get('value', '0.0'),
                'unit': data.get('unit', 'g')
            }
        except json.JSONDecodeError:
            _logger.error("Invalid JSON format received from the scale.")
            raise Exception("Scale sent invalid data.")
        except Exception as e:
            _logger.error("Error reading data from scale: %s", e)
            raise Exception("Failed to read data from the scale.")
