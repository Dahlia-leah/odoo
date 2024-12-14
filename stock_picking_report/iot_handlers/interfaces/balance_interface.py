from odoo.addons.iot.models.device import AbstractDevice
from ..drivers.adam_scale_driver import ScaleDriver
import logging

_logger = logging.getLogger(__name__)

class ScaleInterface(AbstractDevice):
    """
    Interface for integrating the scale with Odoo's IoT framework.
    """

    def __init__(self, device, params):
        super().__init__(device, params)
        self.driver = ScaleDriver(
            serial_port=params.get('serial_port', 'com4'),
            baudrate=params.get('baudrate', 9600),
            timeout=params.get('timeout', 5)
        )

    def connect(self):
        """Connect to the scale."""
        self.driver.connect()

    def disconnect(self):
        """Disconnect from the scale."""
        self.driver.disconnect()

    def get_data(self):
        """Retrieve weight data from the scale."""
        try:
            data = self.driver.get_weight()
            _logger.info("Weight data retrieved: %s", data)
            return data
        except Exception as e:
            _logger.error("Error in ScaleInterface: %s", e)
            raise Exception("Failed to retrieve data from the scale.")