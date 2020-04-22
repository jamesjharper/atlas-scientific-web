import unittest
from unittest.mock import Mock, call, patch

from atlas_scientific.device import AtlasScientificDeviceBus
from datetime import datetime, timezone
import api

from i2c import I2CBus

class PhDeviceTests(unittest.TestCase):
 
    def setUp(self):
        self.i2cbus = I2CBus()
        self.i2cbus.read = Mock()
        self.i2cbus.write = Mock()
        self.i2cbus.ping = Mock() 
        
        self.app = api.create_app(self.i2cbus).test_client()

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_should_retry_sample_atlas_scientific_ph_device_if_receive_device_not_ready_response(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
                b'\x01?i,pH,1.98\00', # first call should be for the device info            
                b'\xfe\00',            # second call return 'still processing, not ready'
                b'\x019.560\00'       # third call should succeed and return sample
            ]

        # Act
        response = self.app.get('/api/device/99/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'), # expect 'i' for read info
                call(device_address, b'r\00')  # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), 
                call(0.9),
                call(0.3) # wait only 0.3 to resample
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address), # expect another attempt to read output
                call(device_address) 
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "pH", "timestamp": "2020-02-25 23:08:13+00:00", "value": "9.56", "value_type": "float"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_should_return_device_not_ready_error_if_sample_atlas_scientific_ph_device_if_receive_device_not_ready_response_for_more_then_four_tries(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
                b'\x01?i,pH,1.98\00', # first call should be for the device info            
                b'\xfe\00',            # 'still processing, not ready'
                b'\xfe\00',            # 'still processing, not ready'
                b'\xfe\00',            # 'still processing, not ready'
                b'\xfe\00',            # 'still processing, not ready'
            ]

        # Act
        response = self.app.get('/api/device/99/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'), # expect 'i' for read info
                call(device_address, b'r\00')  # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), 
                call(0.9),
                call(0.3), # wait only 0.3 to resample
                call(0.3),
                call(0.3),
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address), # expect another attempt to read output
                call(device_address), 
                call(device_address),
                call(device_address),
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(b'{"message": "Device did not return the expected response in a timely mannor.", "error_code": "DEVICE_NOT_READY"}\n', response.data)

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_should_return_error_if_sample_atlas_scientific_ph_device_returns_syntax_error(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
                b'\x01?i,pH,1.98\00', # first call should be for the device info            
                b'\x02\00',            # second call return 'still processing, not ready'
            ]

        # Act
        response = self.app.get('/api/device/99/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
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
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address), 
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(b'{"message": "Device has rejected your request, please confrim the request is supported by the device and the device has the latest firmware.", "error_code": "COMMAND_ERROR"}\n', response.data)

if __name__ == '__main__':
    unittest.main()
