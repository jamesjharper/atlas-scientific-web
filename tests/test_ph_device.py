import unittest
from unittest.mock import Mock, call, patch

from atlas_scientific.device import AtlasScientificDeviceBus
from datetime import datetime, timezone
import api
from api import i2cbus

class PhDeviceTests(unittest.TestCase):
 
    def setUp(self):
        self.app = api.create_app().test_client()
        i2cbus.read = Mock()
        i2cbus.write = Mock()
        i2cbus.ping = Mock()

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_ph_device(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 99

        i2cbus.read.side_effect = [
                b'\x01?i,pH,1.98\00', # first call should be for the device info
                b'\x019.560\00'  # second call should be for reading the device sample
            ]

        # Act
        response = self.app.get('/api/device/99/sample', follow_redirects=True)

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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "pH", "timestamp": "2020-02-25 23:08:13+00:00", "value": "9.56", "value_type": "float"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_ph_device_with_temperature_compensation(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 99

        i2cbus.read.side_effect = [
                b'\x01?i,pH,1.98\00', # first call should be for the device info
                b'\x019.560\00'  # second call should be for reading the device sample
            ]

        request_body = [{
            'factor': 'temperature',
            'symbol': '°C', 
            'value': '25.5'
        }]

        # Act
        response = self.app.post('/api/device/99/sample', json=request_body, follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'), # expect 'i' for read info
                call(device_address, b'rt,25.5\00')  # expect 'r' for read device sample
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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "pH", "timestamp": "2020-02-25 23:08:13+00:00", "value": "9.56", "value_type": "float"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    def test_reading_sample_twice_should_only_resolve_device_infomation_once(self, patched_time_sleep):

        # Arrange
        device_address = 99

        i2cbus.read.side_effect = [
                b'\x01?I,pH,1.98\00', # first call should be for the device info
                b'\x019.560\00',  # second call should be for reading the device sample
                b'\x019.760\00',  # second call should be for reading the device sample
            ]

        # Act
        response1 = self.app.get(f'/api/device/{device_address}/sample', follow_redirects=True)
        response2 = self.app.get(f'/api/device/{device_address}/sample', follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'), # expect 'i' for read info
                call(device_address, b'r\00'),  # expect 'r' for read device sample
                call(device_address, b'r\00'),  # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), 
                call(0.9),
                call(0.9),
            ], 
            any_order=False)

        # expect device info to be read from bus
        i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address),
                call(device_address),
            ], 
            any_order=False)

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

    @patch('time.sleep', return_value=None)
    def test_can_resolve_supported_outputs_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        i2cbus.read.side_effect = [
                b'\x01?i,pH,1.98\00', # first call should be for the device info
            ]

        # Act
        response = self.app.get('/api/device/99/sample/output', follow_redirects=True)

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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"is_enable": true, "symbol": "pH", "unit": "Power of Hydrogen", "value_type": "float"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    def test_can_compensate_for_temperature_in_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        i2cbus.read.side_effect = [
                b'\x01?i,pH,1.98\00', # first call should be for the device info             
                b'\x01\00',            # call should be to read the result from setting the temperature compensation
            ]

        # Act
        request_body = [{
            'factor': 'temperature',
            'symbol': '°C', 
            'value': '19.5'
        }]

        response = self.app.post('/api/device/99/sample/compensation', json=request_body, follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'T,19.5\00'), # expect 'T,19.5' for setting the temperature compensation
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "T,19.5"
            ], 
            any_order=False)

        # expect device info to be read from bus
        i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)

    @patch('time.sleep', return_value=None)
    def test_can_calibrate_low_point_in_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        i2cbus.read.side_effect = [
            b'\x01?i,pH,1.98\00', # first call should be for the device info             
            b'\x01\00',            # call should be to read the result from setting the calibration point
        ]

        request_body = {
            'point': 'low',
            'actual_value': '4.0'
        }

        response = self.app.put('/api/device/99/sample/calibration', json=request_body, follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'Cal,low,4.0\00'), # expect 'Cal,low,4.00' for setting  the calibration point
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.9), # "Cal,low,4.00"
            ], 
            any_order=False)

        # expect device info to be read from bus
        i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)

    @patch('time.sleep', return_value=None)
    def test_can_calibrate_mid_point_in_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        i2cbus.read.side_effect = [
            b'\x01?i,pH,1.98\00', # first call should be for the device info             
            b'\x01\00',            # call should be to read the result from setting the calibration point
        ]

        request_body = {
            'point': 'mid',
            'actual_value': '7.0'
        }

        response = self.app.put('/api/device/99/sample/calibration', json=request_body, follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'Cal,mid,7.0\00'), # expect 'Cal,mid,7.00' for setting  the calibration point
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.9), # "Cal,low,4.00"
            ], 
            any_order=False)

        # expect device info to be read from bus
        i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)

    @patch('time.sleep', return_value=None)
    def test_can_calibrate_high_point_in_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        i2cbus.read.side_effect = [
            b'\x01?i,pH,1.98\00', # first call should be for the device info             
            b'\x01\00',            # call should be to read the result from setting the calibration point
        ]

        request_body = {
            'point': 'high',
            'actual_value': '10.0'
        }

        response = self.app.put('/api/device/99/sample/calibration', json=request_body, follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'Cal,high,10.0\00'), # expect 'Cal,mid,7.00' for setting  the calibration point
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.9), # "Cal,high,10.0"
            ], 
            any_order=False)

        # expect device info to be read from bus
        i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
