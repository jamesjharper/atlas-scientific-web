import unittest
from unittest.mock import Mock, call, patch
from datetime import datetime, timezone

from atlas_scientific_web.hardware.device import AtlasScientificDeviceBus
from atlas_scientific_web.hardware.i2c import I2CBusIo
from atlas_scientific_web.api import create_app

date_time_patch = 'atlas_scientific_web.hardware.device.get_datetime_now'

class DevicesTests(unittest.TestCase):
 
    def setUp(self):
        self.i2cbus = I2CBusIo()
        self.i2cbus.read = Mock()
        self.i2cbus.write = Mock()
        self.i2cbus.ping = Mock()

        self.app = create_app(self.i2cbus).test_client()
 
    def test_can_return_empty_list_of_devices(self):
        # Arrange
        # as there are no devices present, then every call will return an error
        def i2cbus_ping(address):
            return False
        self.i2cbus.ping.side_effect = i2cbus_ping

        # Act
        response = self.app.get('/api/device', follow_redirects=True)

        # Assert
        # expect a scan from address 0 to 128
        expected_calls = (call(addr) for addr in range(0, 128))
        self.i2cbus.ping.assert_has_calls(expected_calls, any_order=True)

        # expect a empty json list 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[]\n', response.data)

    @patch('time.sleep', return_value=None)
    def test_can_return_a_connected_atlas_scientific_orp_device(self, patched_time_sleep):

        # Arrange
        device_address = 98
        def i2cbus_ping(address):
            return address == device_address

        self.i2cbus.ping.side_effect = i2cbus_ping

        def i2cbus_write(address, value):
            if address != device_address:
                raise Exception('Sorry i wasn\'t expecting this call.')

        self.i2cbus.write.side_effect = i2cbus_write

        def i2cbus_read(address):
            if address != device_address:
                raise Exception('Sorry i wasn\'t expecting this call.')
            return b'\x01?i,ORP,1.97\00'

        self.i2cbus.read.side_effect = i2cbus_read

        # Act
        response = self.app.get('/api/device', follow_redirects=True)

        # Assert
        # expect a scan from address 0 to 128
        expected_calls = (call(addr) for addr in range (0,128))
        self.i2cbus.ping.assert_has_calls(expected_calls, any_order=True)

        # expect 'i' to be written
        self.i2cbus.write.assert_called_once_with(device_address, b'i\00')

        # expect to wait for result to be ready
        patched_time_sleep.assert_called_once_with(0.3)

        # expect device info to be read from bus
        self.i2cbus.read.assert_called_once_with(device_address)

        # expect a json list with a single device
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"address": 98, "device_type": "ORP", "vendor": "atlas-scientific", "firmware_version": "1.97"}]\n', response.data)
 
    @patch('time.sleep', return_value=None)
    def test_can_return_a_connected_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 99
        def i2cbus_ping(address):
            return address == device_address

        self.i2cbus.ping.side_effect = i2cbus_ping

        def i2cbus_write(address, value):
            if address != device_address:
                raise Exception('Sorry i wasn\'t expecting this call.')

        self.i2cbus.write.side_effect = i2cbus_write

        def i2cbus_read(address):
            if address != device_address:
                raise Exception('Sorry i wasn\'t expecting this call.')
            return b'\x01?i,pH,1.98\00'

        self.i2cbus.read.side_effect = i2cbus_read

        # Act
        response = self.app.get('/api/device', follow_redirects=True)

        # Assert
        # expect a scan from address 0 to 128
        expected_calls = (call(addr) for addr in range (0,128))
        self.i2cbus.ping.assert_has_calls(expected_calls, any_order=True)

        # expect 'i' to be written
        self.i2cbus.write.assert_called_once_with(device_address, b'i\00')

        # expect to wait for result to be ready
        patched_time_sleep.assert_called_once_with(0.3)

        # expect device info to be read from bus
        self.i2cbus.read.assert_called_once_with(device_address)

        # expect a json list with a single device
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"address": 99, "device_type": "pH", "vendor": "atlas-scientific", "firmware_version": "1.98"}]\n', response.data)
 

    @patch('time.sleep', return_value=None)
    def test_can_return_multiple_atlas_scientific_devices(self, patched_time_sleep):

        # Arrange
        device1_address = 97
        device2_address = 105
        def i2cbus_ping(address):
            return address == device1_address or address == device2_address

        self.i2cbus.ping.side_effect = i2cbus_ping

        def i2cbus_write(address, value):
            if address != device1_address and address != device2_address:
                raise Exception('Sorry i wasn\'t expecting this call.')

        self.i2cbus.write.side_effect = i2cbus_write

        def i2cbus_read(address):
            if address == device1_address:
                return b'\x01?i,DO,1.98\00'
            elif address == device2_address:
                return b'\x01?i,CO2,1.00\00'
            else:   
                raise Exception('Sorry i wasn\'t expecting this call.')
            
        self.i2cbus.read.side_effect = i2cbus_read

        # Act
        response = self.app.get('/api/device', follow_redirects=True)

        # Assert
        # expect a scan from address 0 to 128
        expected_ping_calls = (call(addr) for addr in range (0,128))
        self.i2cbus.ping.assert_has_calls(expected_ping_calls, any_order=True)

        # expect 'i' to be written to both devices
        expected_write_calls = [call(device1_address, b'i\00'), call(device2_address, b'i\00')]
        self.i2cbus.write.assert_has_calls(expected_write_calls, any_order=True)

        # expect to wait for result to be ready
        expected_sleep_calls = [call(0.3), call(0.3)]
        patched_time_sleep.assert_has_calls(expected_sleep_calls, any_order=True)

        # expect device info to be read from bus
        expected_read_calls = [call(device1_address), call(device2_address)]
        self.i2cbus.read.assert_has_calls(expected_read_calls, any_order=True)

        # expect a json response with both devices
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"address": 97, "device_type": "DO", "vendor": "atlas-scientific", "firmware_version": "1.98"}, {"address": 105, "device_type": "CO2", "vendor": "atlas-scientific", "firmware_version": "1.00"}]\n', response.data)
 
if __name__ == '__main__':
    unittest.main()
