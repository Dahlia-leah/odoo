import logging
import serial
from odoo.addons.hw_drivers.driver import Driver
import websocket

# Set up logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)  # Set your desired log level

class AdamScaleDriver(Driver):
    connection_type = 'serial'

    def __init__(self, identifier, device):
        super(AdamScaleDriver, self).__init__(identifier, device)
        self.device_type = 'scale'
        self.device_connection = device.get('port')
        self.device_name = device.get('device_name')

    @classmethod
    def supported(cls, device):
        """
        Check if the device is an Adam scale connected via serial.
        """
        return device.get('manufacturer') == 'Adam' and device.get('device_type') == 'scale'

    def read_weight(self):
        """
        Read weight data from the scale over serial connection.
        """
        try:
            ser = serial.Serial(self.device_connection, 9600, timeout=5)
            data = ser.readline().decode('utf-8').strip()  # Read the data from the scale
            weight, unit = data.split()  # Assuming data format: "5.0 kg"
            return {'weight': weight, 'unit': unit}
        except serial.SerialException as e:
            _logger.error(f"Error communicating with the scale on {self.device_connection}: {e}")
            return None

# Enable WebSocket trace logging
websocket.enableTrace(True)
