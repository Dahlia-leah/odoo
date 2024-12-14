from odoo.addons.hw_drivers.interface import Interface
from ..drivers.balance_interface import ScaleDriver
import logging
import serial.tools.list_ports

_logger = logging.getLogger(__name__)

class ScaleInterface(Interface):
    connection_type = 'serial'

    def get_devices(self):
        """Detect connected scale devices."""
        devices = []
        ports = serial.tools.list_ports.comports()
        for port in ports:
            _logger.info("Detected serial port: %s", port.device)
            if 'scale' in port.device.lower():  # Looking for scale devices
                devices.append(port.device)
        return devices

    def get_data(self):
        """Fetch data from the scale."""
        scale_driver = ScaleDriver(self.identifier, self.device)
        scale_driver.connect()
        return scale_driver.get_weight()
