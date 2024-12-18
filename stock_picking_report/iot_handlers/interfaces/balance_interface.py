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
        
        if not devices:
            _logger.warning("No scale devices detected.")
        return devices

    def get_data(self):
        """Fetch data from the scale."""
        scale_driver = ScaleDriver(self.identifier, self.device)
        
        try:
            # Attempt to connect to the scale device
            scale_driver.connect()
            
            # Fetch weight data
            data = scale_driver.get_weight()
            _logger.info("Weight data retrieved: %s", data)
            
        except Exception as e:
            _logger.error("Error fetching data from the scale: %s", e)
            data = {'value': '0.0', 'unit': 'g'}  # Default fallback data
        
        finally:
            # Ensure the scale connection is closed after use
            scale_driver.disconnect()

        return data
