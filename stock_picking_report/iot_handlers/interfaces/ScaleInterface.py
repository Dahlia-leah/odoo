from odoo.addons.hw_drivers.interface import Interface
import serial.tools.list_ports

class ScaleInterface(Interface):
    connection_type = 'serial'
    
    def get_devices(self):
        """Return connected scale devices"""
        devices = {}
        
        # List all COM ports
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            if port.device == 'COM4':  # Your scale's port
                devices['scale_1'] = {
                    'type': 'scale',
                    'manufacturer': 'Adam',
                    'connection': 'serial',
                    'port': port.device,
                    'identifier': 'scale_1',
                    'baudrate': 9600
                }
                
        return devices 