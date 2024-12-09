from odoo.addons.hw_drivers.driver import Driver
from odoo.addons.hw_drivers.event_manager import event_manager
import serial
import logging
import time

_logger = logging.getLogger(__name__)

class ScaleDriver(Driver):
    connection_type = 'serial'
    
    def __init__(self, identifier, device):
        super(ScaleDriver, self).__init__(identifier, device)
        self.device_type = 'scale'
        self.device_connection = 'serial'
        self.device_name = 'Adam Scale'
        self.port = device.get('port', 'COM4')
        self.baudrate = device.get('baudrate', 9600)
        self.serial_connection = None
        self._actions.update({
            'read_weight': self._read_weight,
        })
        self._connect_serial()
        
    def _connect_serial(self):
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            _logger.info(f"Connected to scale on {self.port}")
        except Exception as e:
            _logger.error(f"Failed to connect to scale: {str(e)}")
            
    def _read_weight(self, data=None):
        """Read weight from serial scale"""
        try:
            if not self.serial_connection or not self.serial_connection.is_open:
                self._connect_serial()
                
            # Clear input buffer
            self.serial_connection.reset_input_buffer()
            
            # Send command to request weight (adjust based on your scale's protocol)
            self.serial_connection.write(b'P\r\n')  # Common command for Adam scales
            time.sleep(0.1)  # Give scale time to respond
            
            response = self.serial_connection.readline().decode().strip()
            
            # Parse the response (adjust based on your scale's output format)
            weight = float(response.split()[0])  # Assuming format: "weight unit"
            unit = response.split()[1] if len(response.split()) > 1 else 'kg'
            
            self.data = {
                'value': weight,
                'unit': unit
            }
            event_manager.device_changed(self)
            return True
            
        except Exception as e:
            _logger.error(f"Failed to read scale: {str(e)}")
            return False
            
    @classmethod
    def supported(cls, device):
        """Check if device is supported by this driver"""
        return (device.get('manufacturer', '').lower() == 'adam' and 
                device.get('type') == 'scale' and 
                device.get('connection') == 'serial')