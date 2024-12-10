from odoo.addons.iot.models.iot_device import IoTDeviceDriver
import requests
import logging

_logger = logging.getLogger(__name__)

class AdamScaleDriver(IoTDeviceDriver):
    def __init__(self, device):
        super().__init__(device)
        self.endpoint = f"http://{device.connection['ip']}:5000/balance"

    def read(self):
        try:
            _logger.info(f"Fetching data from scale at {self.endpoint}")
            response = requests.get(self.endpoint, timeout=5)
            response.raise_for_status()
            data = response.json()
            return {'value': data['value'], 'unit': data['unit']}
        except Exception as e:
            _logger.error(f"Failed to read from scale: {e}")
            raise
