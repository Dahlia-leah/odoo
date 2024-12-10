from odoo.addons.iot.models.iot_interface import IoTInterface

class SerialInterface(IoTInterface):
    def __init__(self, device):
        super().__init__(device)
        self.driver = None

    def initialize_driver(self):
        """Initialize the appropriate driver."""
        from ..drivers.adam_scale import AdamScaleDriver
        self.driver = AdamScaleDriver(self.device)

    def read(self):
        """Read data from the device."""
        if not self.driver:
            self.initialize_driver()
        return self.driver.read()
