import unittest
from unittest.mock import Mock, call, patch
from datetime import datetime, timezone

from atlas_scientific_web.hardware.device import AtlasScientificDeviceBus
from atlas_scientific_web.hardware.i2c import I2CBusIo
from atlas_scientific_web.api import create_app

date_time_patch = 'atlas_scientific_web.hardware.device.get_datetime_now'

class EcDeviceTests(unittest.TestCase):
 
    def setUp(self):
        self.i2cbus = I2CBusIo()
        self.i2cbus.read = Mock()
        self.i2cbus.write = Mock()
        self.i2cbus.ping = Mock() 
        
        self.app = create_app(self.i2cbus).test_client()

    # sample tests

    @patch('time.sleep', return_value=None)
    @patch(date_time_patch, return_value=datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_ec_device_with_ec_enabled(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [
                b'\x01?i,EC,2.10\00',   # first call should be for the device info
                b'\x01?O,EC\00',        # second call should be to read the current device outputs
                b'\x011.2\00'           # third call should be for reading the device sample
            ]

        # Act
        response = self.app.get('/api/device/100/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'o,?\00'), # expect 'o,?' for reading current device output
                call(device_address, b'r\00')    # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.6)  # "r"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address),
                call(device_address),
                call(device_address),
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "\u03bcS/cm", "timestamp": "2020-02-25 23:08:13+00:00", "value": "1.2", "value_type": "float", "unit_code": "EC"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    @patch(date_time_patch, return_value=datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_ec_device_with_tds_enabled(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [
                b'\x01?i,EC,2.10\00',   # first call should be for the device info
                b'\x01?O,TDS\00',        # second call should be to read the current device outputs
                b'\x012000\00'           # third call should be for reading the device sample
            ]

        # Act
        response = self.app.get('/api/device/100/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'o,?\00'), # expect 'o,?' for reading current device output
                call(device_address, b'r\00')    # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.6)  # "r"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address),
                call(device_address),
                call(device_address),
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "ppm", "timestamp": "2020-02-25 23:08:13+00:00", "value": "2000", "value_type": "float", "unit_code": "TDS"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    @patch(date_time_patch, return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_ec_device_with_us_enabled(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [
                b'\x01?i,EC,2.10\00',   # first call should be for the device info
                b'\x01?O,S\00',        # second call should be to read the current device outputs
                b'\x0150000\00'           # third call should be for reading the device sample
            ]

        # Act
        response = self.app.get('/api/device/100/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'o,?\00'), # expect 'o,?' for reading current device output
                call(device_address, b'r\00')    # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.6)  # "r"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address),
                call(device_address),
                call(device_address),
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "ppt", "timestamp": "2020-02-25 23:08:13+00:00", "value": "50000", "value_type": "float", "unit_code": "S"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    @patch(date_time_patch, return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_ec_device_with_sg_enabled(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [
                b'\x01?i,EC,2.10\00',   # first call should be for the device info
                b'\x01?O,SG\00',        # second call should be to read the current device outputs
                b'\x0150000\00'           # third call should be for reading the device sample
            ]

        # Act
        response = self.app.get('/api/device/100/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'o,?\00'), # expect 'o,?' for reading current device output
                call(device_address, b'r\00')    # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.6)  # "r"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address),
                call(device_address),
                call(device_address),
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "", "timestamp": "2020-02-25 23:08:13+00:00", "value": "50000", "value_type": "float", "unit_code": "SG"}]\n', response.data)

    # sample output tests

    @patch('time.sleep', return_value=None)
    def test_can_resolve_supported_outputs_atlas_scientific_ec_device(self, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [
                b'\x01?i,EC,2.10\00',   # first call should be for the device info
                b'\x01?O,EC\00',        # second call should be to read the current device outputs
            ]

        # Act
        response = self.app.get('/api/device/100/sample/output', follow_redirects=True)

        # Assert
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

        # expect a empty json list
        self.assertEqual(response.status_code, 200)

        expected_response = '['\
                '{"is_enable": true, "symbol": "\\u03bcS/cm", "unit": "Conductivity", "unit_code": "EC", "value_type": "float"}, ' \
                '{"is_enable": false, "symbol": "ppm", "unit": "Total Dissolved Solids", "unit_code": "TDS", "value_type": "float"}, ' \
                '{"is_enable": false, "symbol": "ppt", "unit": "Salinity", "unit_code": "S", "value_type": "float"}, ' \
                '{"is_enable": false, "symbol": "", "unit": "Specific Gravity", "unit_code": "SG", "value_type": "float"}' \
            ']\n'

        self.assertEqual(expected_response.encode('utf8'), response.data)

    # compensation tests

    @patch('time.sleep', return_value=None)
    def test_can_compensate_for_temperature_in_atlas_scientific_ec_device(self, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [ 
                b'\x01?i,EC,2.10\00',   # first call should be for the device info
                b'\x01\00',             # secondcall should be to read the result from setting the T compensation
            ]

        # Act
        request_body = [{
            'factor': 'temperature',
            'symbol': '°C', 
            'value': '19.5'
        }]

        response = self.app.post('/api/device/100/sample/compensation', json=request_body, follow_redirects=True)

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

        # expect a empty json list 
        self.assertEqual(response.status_code, 200)

    # configuration tests

    @patch('time.sleep', return_value=None)
    def test_can_configure_k_value_in_atlas_scientific_ec_device(self, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [ 
                b'\x01?i,EC,2.10\00',   # first call should be for the device info
                b'\x01\00',             # secondcall should be to read the result from setting the K value
            ]

        # Act
        request_body = {
            'parameter': 'K',
            'value': '1.0'
        }

        response = self.app.post('/api/device/100/configuration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),     # expect 'i' for read info
                call(device_address, b'k,1.0\00'), # expect 'K,1.0' for setting the K value
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "K,1.0"
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
    def test_can_configure_device_leds_in_atlas_scientific_ec_device(self, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [ 
                b'\x01?i,EC,2.10\00',   # first call should be for the device info
                b'\x01\00',             # secondcall should be to read the result from setting the K value
            ]

        # Act
        request_body = {
            'parameter': 'led',
            'value': 'true'
        }

        response = self.app.post('/api/device/100/configuration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'l,1\00'), # expect 'l,1' for setting the device name
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
    def test_can_configure_device_name_in_atlas_scientific_ec_device(self, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [ 
                b'\x01?i,EC,2.10\00',   # first call should be for the device info
                b'\x01\00',             # secondcall should be to read the result from setting the K value
            ]

        # Act
        request_body = {
            'parameter': 'name',
            'value': 'ec_device'
        }

        response = self.app.post('/api/device/100/configuration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'name,ec_device\00'), # expect 'name,ec_device' for setting the device name
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "name,ec_device"
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

    # calibration tests

    @patch('time.sleep', return_value=None)
    def test_can_calibrate_dry_point_in_atlas_scientific_ec_device(self, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [
            b'\x01?i,EC,2.10\00',   # first call should be for the device info
            b'\x01\00',            # call should be to read the result from setting the calibration point
        ]

        request_body = {
            'point': 'dry'
        }

        response = self.app.put(f'/api/device/{device_address}/sample/calibration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'Cal,dry\00'), # expect 'Cal,low,4.00' for setting  the calibration point
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.6), # "Cal"
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
    def test_can_calibrate_any_point_in_atlas_scientific_ec_device(self, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [
            b'\x01?i,EC,2.10\00',  # first call should be for the device info
            b'\x01\00',            # call should be to read the result from setting the calibration point
        ]

        request_body = {
            'point': 'any',
            'actual_value': '84'
        }

        response = self.app.put(f'/api/device/{device_address}/sample/calibration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),
                call(device_address, b'Cal,84\00'),
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.6), # "Cal"
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
    def test_can_calibrate_low_point_in_atlas_scientific_ec_device(self, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [
            b'\x01?i,EC,2.10\00',  # first call should be for the device info
            b'\x01\00',            # call should be to read the result from setting the calibration point
        ]

        request_body = {
            'point': 'low',
            'actual_value': '12880'
        }

        response = self.app.put(f'/api/device/{device_address}/sample/calibration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),
                call(device_address, b'Cal,low,12880\00'),
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.6), # "Cal"
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
    def test_can_calibrate_low_point_in_atlas_scientific_ec_device(self, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [
            b'\x01?i,EC,2.10\00',  # first call should be for the device info
            b'\x01\00',            # call should be to read the result from setting the calibration point
        ]

        request_body = {
            'point': 'high',
            'actual_value': '80000'
        }

        response = self.app.put(f'/api/device/{device_address}/sample/calibration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),
                call(device_address, b'Cal,high,80000\00'),
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.6), # "Cal"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)


    # TODO: add support for selecting probe k value
if __name__ == '__main__':
    unittest.main()
