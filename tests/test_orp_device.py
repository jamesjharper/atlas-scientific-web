import unittest
from unittest.mock import Mock, call, patch

from atlas_scientific.device import AtlasScientificDeviceBus
from datetime import datetime, timezone
import api
from api import i2cbus


class OrpDeviceTests(unittest.TestCase):
 
    def setUp(self):
        self.app = api.create_app().test_client()
        i2cbus.read = Mock()
        i2cbus.write = Mock()
        i2cbus.ping = Mock()
 
    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_orp_device(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 98

        i2cbus.read.side_effect = [ 
                b'\x01?I,ORP,1.97\00', # first call should be for the device info
                b'\x01209.6\00'  # second call should be for reading the device sample
            ]

        # Act
        response = self.app.get('/api/device/98/sample', follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'), # expect 'i' for read info
                call(device_address, b'r\00')  # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), 
                call(0.9)  
            ], 
            any_order=False)

        # expect device info to be read from bus
        i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)  
            ], 
            any_order=False)

        # expect a empty json list 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "mV", "timestamp": "2020-02-25 23:08:13+00:00", "value": "209.6", "value_type": "float"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    def test_can_resolve_supported_outputs_atlas_scientific_orp_device(self, patched_time_sleep):

        # Arrange
        device_address = 98

        i2cbus.read.side_effect = [
                b'\x01?I,ORP,1.97\00', # first call should be for the device info
            ]

        # Act
        response = self.app.get('/api/device/98/sample/output', follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'), # expect 'i' for read info
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3)
            ], 
            any_order=False)

        # expect device info to be read from bus
        i2cbus.read.assert_has_calls([
                call(device_address), 
            ], 
            any_order=False)

        # expect a empty json list
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"is_enable": true, "symbol": "mV", "unit": "millivolt", "value_type": "float"}]\n', response.data)



    @patch('time.sleep', return_value=None)
    def test_can_calibrate_low_point_in_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        i2cbus.read.side_effect = [
            b'\x01?i,pH,1.98\00', # first call should be for the device info             
            b'\x01\00',            # call should be to read the result from setting the calibration point
        ]

        request_body = {
            'actual_value': '225'
        }

        response = self.app.put('/api/device/99/sample/calibration', json=request_body, follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'Cal,225\00'), # expect 'Cal,225' for setting the calibration point
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.9), # "Cal,225"
            ], 
            any_order=False)

        # expect device info to be read from bus
        i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)

# TODO: add test to ignore any compensation params given

# TODO add test to fail when attempting to read with temp comp, as this is not supported for this device
