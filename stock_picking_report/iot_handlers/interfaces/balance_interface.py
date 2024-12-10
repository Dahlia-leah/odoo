from odoo.addons.iot.models.iot_device import IoTDeviceDriver

class BalanceInterface(IoTDeviceDriver):
    def read(self):
        return self.device.call('adam_scale_driver.read')
