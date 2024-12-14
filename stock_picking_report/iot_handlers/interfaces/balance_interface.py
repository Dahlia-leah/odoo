# iot_handlers/interfaces/scale_interface.py
from odoo.addons.hw_drivers.interface import Interface
from ..drivers.adam_scale_driver import ScaleDriver
import logging
import serial
import serial.tools.list_ports

_logger = logging.getLogger(__name__)

class ScaleInterface(Interface):
    connection_type = 'serial'  # Use serial connection type to detect connected devices

    def get_devices(self):
        """Detect connected scale devices and return their details."""
        devices = {}

        # List available serial ports
        available_ports = serial.tools.list_ports.comports()

        for port in available_ports:
            # Try to communicate with the scale on each port
            try:
                # Create a ScaleDriver instance and try to connect
                scale_driver = ScaleDriver(identifier=port.device, device=None)
                scale_driver.serial_port = port.device
                scale_driver.connect()

                # If connection is successful, add to devices dictionary
                devices[port.device] = {
                    'serial_port': port.device,
                    'baudrate': 9600,  # Use default baudrate for communication
                    'timeout': 5       # Timeout for serial communication
                }
                _logger.info("Detected scale on port: %s", port.device)

                # Disconnect after detection
                scale_driver.serial_connection.close()

            except Exception as e:
                _logger.warning("No scale detected on port %s: %s", port.device, str(e))

        if not devices:
            _logger.warning("No scale devices detected.")
        
        return devices
