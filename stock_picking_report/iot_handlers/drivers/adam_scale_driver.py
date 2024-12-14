from odoo.addons.hw_drivers.driver import Driver
import serial
import logging

_logger = logging.getLogger(__name__)

class ScaleDriver(Driver):
    connection_type = 'serial'
    device_type = 'scale'
    device_connection = 'serial_connection'
    device_name = 'Adam Equipment Serial'

    def __init__(self, identifier, device, serial_port='COM5', baudrate=9600, timeout=5):
        super().__init__(identifier, device)
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.status = "Disconnected"

    def connect(self):
        """Establish a serial connection to the scale."""
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
            raise Exception("Failed to connect to the scale device.")

    def get_status(self):
        """Return the current status of the scale connection."""
        return self.status

    def get_weight(self):
        """Retrieve weight from the scale."""
        if self.serial_connection:
            try:
                raw_data = self.serial_connection.readline().decode('utf-8').strip()
                _logger.info("Raw data from scale: %s", raw_data)
                # Assuming the data is in JSON format
                data = json.loads(raw_data)
                return {
                    'value': data.get('value', '0.0'),
                    'unit': data.get('unit', 'g')
                }
            except Exception as e:
                _logger.error("Error reading from scale: %s", e)
                return {'value': '0.0', 'unit': 'g'}
        return {'value': '0.0', 'unit': 'g'}
