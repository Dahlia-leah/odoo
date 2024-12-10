from odoo.addons.iot.models.iot_device import IoTDeviceDriver

class AdamScaleDriver(IoTDeviceDriver):
    def __init__(self, device):
        super().__init__(device)
        self.serial_connection = None

    def connect(self):
        """Establish a connection with the scale."""
        if not self.device.connection:
            raise Exception("No connection string found for the device.")

        import serial
        self.serial_connection = serial.Serial(
            port=self.device.connection['port'],
            baudrate=9600,
            timeout=1
        )

    def disconnect(self):
        """Close the connection."""
        if self.serial_connection:
            self.serial_connection.close()

    def read(self):
        """Fetch data from the scale."""
        if not self.serial_connection:
            raise Exception("Device is not connected.")
        
        self.serial_connection.write(b'R\n')  # Replace with actual scale command
        response = self.serial_connection.readline().decode('utf-8').strip()
        
        value, unit = response.split()
        return {'value': value, 'unit': unit}
