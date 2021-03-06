import unittest
from unittest.mock import Mock, call, patch
from datetime import datetime, timezone

from atlas_scientific_web.hardware.device import AtlasScientificDeviceBus, get_datetime_now
from atlas_scientific_web.hardware.i2c import I2CBusIo
from atlas_scientific_web.api import create_app

date_time_patch = 'atlas_scientific_web.hardware.device.get_datetime_now'

class AnyDeviceErrorTests(unittest.TestCase):
 
    def setUp(self):
        self.i2cbus = I2CBusIo()
        self.i2cbus.read = Mock()
        self.i2cbus.write = Mock()
        self.i2cbus.ping = Mock() 
        
        self.app = create_app(self.i2cbus).test_client()

    @patch('time.sleep', return_value=None)
    @patch(date_time_patch, return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_should_retry_sample_atlas_scientific_ph_device_if_receive_device_not_ready_response(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
                b'\x01?i,pH,1.98\00', # first call should be for the device info            
                b'\xfe\00',            # second call return 'still processing, not ready'
                b'\x019.56\00'       # third call should succeed and return sample
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
        self.assertEqual(b'[{"symbol": "", "timestamp": "2020-02-25 23:08:13+00:00", "value": "9.56", "value_type": "float", "unit_code": "PH"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    @patch(date_time_patch, return_value = datetime.fromtimestamp(1582672093, timezone.utc))
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
    @patch(date_time_patch, return_value = datetime.fromtimestamp(1582672093, timezone.utc))
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

    @patch('time.sleep', return_value=None)
    @patch(date_time_patch, return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_should_return_device_not_found_error_if_no_device_exists_at_address(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 110 # nothing at this address

        def i2cbus_ping(address):
            return address != device_address

        self.i2cbus.ping.side_effect = i2cbus_ping

        # Act
        response = self.app.get('/api/device/110/sample', follow_redirects=True)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(b'{"message": "No device is connected to the given address.", "error_code": "DEVICE_NOT_FOUND"}\n', response.data)

    @patch('time.sleep', return_value=None)
    @patch(date_time_patch, return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_should_return_device_not_recognized_error_when_device_response_is_novel(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
                b'\x01?i,NEW,1.98\00', # first call should be for a new device released by atlas scientific not yet supported
            ]

        # Act
        response = self.app.get('/api/device/99/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'), # expect 'i' for read info
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), 
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(b'{"message": "Detected unsupported atlas scientific device.", "error_code": "UNSUPPORTED_DEVICE"}\n', response.data)

    @patch('time.sleep', return_value=None)
    @patch(date_time_patch, return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_should_return_device_not_supported_error_when_response_does_not_match_any_known_device(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
                b'Novel response\00', # Unexpected response
            ]

        # Act
        response = self.app.get('/api/device/99/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'), # expect 'i' for read info
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), 
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(b'{"message": "Device responded but response was not recognizable.", "error_code": "UNEXPECTED_DEVICE_RESPONSE"}\n', response.data)

if __name__ == '__main__':
    unittest.main()
