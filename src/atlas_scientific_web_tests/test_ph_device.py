import unittest
from unittest.mock import Mock, call, patch
from datetime import datetime, timezone

from atlas_scientific_web.hardware.device import AtlasScientificDeviceBus
from atlas_scientific_web.hardware.i2c import I2CBusIo
from atlas_scientific_web.api import create_app

date_time_patch = 'atlas_scientific_web.hardware.device.get_datetime_now'

class PhDeviceTests(unittest.TestCase):
 
    def setUp(self):
        self.i2cbus = I2CBusIo()
        self.i2cbus.read = Mock()
        self.i2cbus.write = Mock()
        self.i2cbus.ping = Mock() 
        
        self.app = create_app(self.i2cbus).test_client()

    # sample tests

    @patch('time.sleep', return_value=None)
    @patch(date_time_patch, return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_ph_device(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
                b'\x01?i,pH,1.98\00', # first call should be for the device info
                b'\x019.560\00'  # second call should be for reading the device sample
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
                call(device_address)  
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "", "timestamp": "2020-02-25 23:08:13+00:00", "value": "9.560", "value_type": "float", "unit_code": "PH"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    @patch(date_time_patch, return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_ph_device_with_temperature_compensation(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
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
        self.i2cbus.write.assert_has_calls([
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
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)  
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "", "timestamp": "2020-02-25 23:08:13+00:00", "value": "9.560", "value_type": "float", "unit_code": "PH"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    def test_reading_sample_twice_should_only_resolve_device_infomation_once(self, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
                b'\x01?I,pH,1.98\00', # first call should be for the device info
                b'\x019.560\00',  # second call should be for reading the device sample
                b'\x019.760\00',  # second call should be for reading the device sample
            ]

        # Act
        response1 = self.app.get(f'/api/device/{device_address}/sample', follow_redirects=True)
        response2 = self.app.get(f'/api/device/{device_address}/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
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
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address),
                call(device_address),
            ], 
            any_order=False)

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)


    # Sample output tests

    @patch('time.sleep', return_value=None)
    def test_can_resolve_supported_outputs_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
                b'\x01?i,pH,1.98\00', # first call should be for the device info
            ]

        # Act
        response = self.app.get('/api/device/99/sample/output', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'), # expect 'i' for read info
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3)
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"is_enable": true, "symbol": "", "unit": "Power of Hydrogen", "unit_code": "PH", "value_type": "float"}]\n', response.data)

    # configuration tests

    @patch('time.sleep', return_value=None)
    def test_can_configure_device_leds_in_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [ 
                b'\x01?i,pH,1.98\00', # first call should be for the device info
                b'\x01\00',           # second call should be to read the result from setting the led value
            ]

        # Act
        request_body = {
            'parameter': 'led',
            'value': 'true'
        }

        response = self.app.post(f'/api/device/{device_address}/configuration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'l,1\00'), # expect 'l,1' for setting the device led state
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "l,1"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        # expect a empty json list 
        self.assertEqual(response.status_code, 200)

    @patch('time.sleep', return_value=None)
    def test_can_configure_device_name_in_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [ 
                b'\x01?i,pH,1.98\00', # first call should be for the device info
                b'\x01\00',             # second call should be to read the result from setting the device name
            ]

        # Act
        request_body = {
            'parameter': 'name',
            'value': 'ph_device'
        }

        response = self.app.post(f'/api/device/{device_address}/configuration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'name,ph_device\00'), # expect 'name,ph_device' for setting the device name
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "name,ph_device"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        # expect a empty json list 
        self.assertEqual(response.status_code, 200)


    # Compensation tests

    @patch('time.sleep', return_value=None)
    def test_can_compensate_for_temperature_in_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
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
        self.i2cbus.write.assert_has_calls([
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
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)

    @patch('time.sleep', return_value=None)
    def test_can_configure_device_name_in_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
                b'\x01?i,pH,1.98\00', # first call should be for the device info      
                b'\x01\00',           # second call should be to read the result from setting the device name
            ]

        # Act
        request_body = {
            'parameter': 'name',
            'value': 'ph_device'
        }

        response = self.app.post(f'/api/device/{device_address}/configuration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),              # expect 'i' for read info
                call(device_address, b'name,ph_device\00'), # expect 'name,ph_device' for setting the device name
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "name,ph_device"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        # expect a empty json list 
        self.assertEqual(response.status_code, 200)

    # Calibration tests

    @patch('time.sleep', return_value=None)
    def test_can_calibrate_low_point_in_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
            b'\x01?i,pH,1.98\00', # first call should be for the device info             
            b'\x01\00',            # call should be to read the result from setting the calibration point
        ]

        request_body = {
            'point': 'low',
            'actual_value': '4.0'
        }

        response = self.app.put('/api/device/99/sample/calibration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
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
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)

    @patch('time.sleep', return_value=None)
    def test_can_calibrate_mid_point_in_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
            b'\x01?i,pH,1.98\00', # first call should be for the device info             
            b'\x01\00',            # call should be to read the result from setting the calibration point
        ]

        request_body = {
            'point': 'mid',
            'actual_value': '7.0'
        }

        response = self.app.put('/api/device/99/sample/calibration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
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
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)

    @patch('time.sleep', return_value=None)
    def test_can_calibrate_high_point_in_atlas_scientific_ph_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
            b'\x01?i,pH,1.98\00', # first call should be for the device info             
            b'\x01\00',            # call should be to read the result from setting the calibration point
        ]

        request_body = {
            'point': 'high',
            'actual_value': '10.0'
        }

        response = self.app.put('/api/device/99/sample/calibration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
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
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
