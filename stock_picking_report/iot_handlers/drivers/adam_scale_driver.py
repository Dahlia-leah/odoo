from odoo.addons.hw_drivers.driver import Driver
import serial
import logging
import json  # Ensure this is imported for JSON parsing

_logger = logging.getLogger(__name__)

class ScaleDriver(Driver):
    connection_type = 'serial'
    device_type = 'scale'
    device_connection = 'serial_connection'
    device_name = 'Adam Equipment Serial'

    def __init__(self, identifier, device, serial_port='COM5', baudrate=9600, timeout=5):
        """
        Initialize the scale driver with serial connection parameters.
        """
        super().__init__(identifier, device)
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.status = "Disconnected"

    def connect(self):
        """
        Establish a serial connection to the scale.
        """
        try:
            self.serial_connection = serial.Serial(
                port=self.serial_port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.status = "Connected"
            _logger.info("Connected to scale on port: %s", self.serial_port)
        except serial.SerialException as e:
            self.status = "Error"
            _logger.error("Error connecting to scale: %s", e)
            raise Exception("Failed to connect to the scale device. Please check the connection and configuration.")

    def disconnect(self):
        """
        Disconnect the serial connection to the scale.
        """
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.status = "Disconnected"
            _logger.info("Disconnected from scale on port: %s", self.serial_port)

    def get_status(self):
        """
        Return the current status of the scale connection.
        """
        return self.status

    def get_weight(self):
        """
        Retrieve weight from the scale.
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            _logger.warning("Attempted to read weight while scale is not connected.")
            return {'value': '0.0', 'unit': 'g'}

        try:
            raw_data = self.serial_connection.readline().decode('utf-8').strip()
            _logger.info("Raw data from scale: %s", raw_data)
            
            # Parse JSON if applicable
            try:
                data = json.loads(raw_data)
                value = data.get('value', '0.0')
                unit = data.get('unit', 'g')
                return {'value': value, 'unit': unit}
            except json.JSONDecodeError:
                _logger.error("Failed to parse weight data as JSON. Raw data: %s", raw_data)
                return {'value': '0.0', 'unit': 'g'}

        except serial.SerialException as e:
            _logger.error("Serial communication error while reading weight: %s", e)
        except Exception as e:
            _logger.error("Unexpected error while reading weight: %s", e)

        return {'value': '0.0', 'unit': 'g'}
