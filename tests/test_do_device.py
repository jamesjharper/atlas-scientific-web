import unittest
from unittest.mock import Mock, call, patch

from atlas_scientific.device import AtlasScientificDeviceBus
from datetime import datetime, timezone
import api
from api import i2cbus

class DoDeviceTests(unittest.TestCase):
 
    def setUp(self):
        self.app = api.create_app().test_client()
        i2cbus.read = Mock()
        i2cbus.write = Mock()
        i2cbus.ping = Mock()
 
    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_do_device_with_all_output_units_enabled(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 97

        i2cbus.read.side_effect = [ 
                b'\x01?I,D.O.,1.98\00', # first call should be for the device info
                b'\x01?O,MG,%\00',      # second call should be to read the current device outputs
                b'\x01238.15,419.6\00'  # second call should be for reading the device sample
            ]

        # Act
        response = self.app.get('/api/device/97/sample', follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'o,?\00'), # expect 'o,?' for reading current device output
                call(device_address, b'r\00')    # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.9)  # "r"
            ], 
            any_order=False)

        # expect device info to be read from bus
        i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address), 
                call(device_address)  
            ], 
            any_order=False)

        # expect a empty json list 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "mg/L", "timestamp": "2020-02-25 23:08:13+00:00", "value": 238.15, "value_type": "float"}, {"symbol": "%", "timestamp": "2020-02-25 23:08:13+00:00", "value": 419.6, "value_type": "float"}]', response.data)

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_do_device_with_only_percent_saturation_enabled(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 97

        i2cbus.read.side_effect = [ 
                b'\x01?I,D.O.,1.98\00', # first call should be for the device info
                b'\x01?O,%\00',      # second call should be to read the current device outputs
                b'\x01419.6\00'  # second call should be for reading the device sample
            ]

        # Act
        response = self.app.get('/api/device/97/sample', follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'o,?\00'), # expect 'o,?' for reading current device output
                call(device_address, b'r\00')    # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.9)  # "r"
            ], 
            any_order=False)

        # expect device info to be read from bus
        i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address), 
                call(device_address)  
            ], 
            any_order=False)

        # expect a empty json list 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "%", "timestamp": "2020-02-25 23:08:13+00:00", "value": 419.6, "value_type": "float"}]', response.data)

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_do_device_with_only_mg_enabled(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 97

        i2cbus.read.side_effect = [ 
                b'\x01?I,D.O.,1.98\00', # first call should be for the device info
                b'\x01?O,MG\00',      # second call should be to read the current device outputs
                b'\x01238.15\00'  # second call should be for reading the device sample
            ]

        # Act
        response = self.app.get('/api/device/97/sample', follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'o,?\00'), # expect 'o,?' for reading current device output
                call(device_address, b'r\00')    # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.9)  # "r"
            ], 
            any_order=False)

        # expect device info to be read from bus
        i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address), 
                call(device_address)  
            ], 
            any_order=False)

        # expect a empty json list 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "mg/L", "timestamp": "2020-02-25 23:08:13+00:00", "value": 238.15, "value_type": "float"}]', response.data)

    @patch('time.sleep', return_value=None)
    def test_can_enable_mg_unit_on_atlas_scientific_do_device(self, patched_time_sleep):

        # Arrange
        device_address = 97

        i2cbus.read.side_effect = [ 
                b'\x01?I,D.O.,1.98\00', # call should be for the device info
                b'\x01?O,%\00',         # call should be to read the current device outputs
                b'\x01\00',             # call should be to read the result from adding mg to device output
                b'\x01\00',             # call should be to read the result from removing % device output
                b'\x01?O,MG\00',        # call should be to RE-read the current device outputs
                b'\x01238.15\00'        # call should be for reading the device sample
            ]

        # body should be a list of all the units to be enabled.
        # Note, all other units not in this list will be disabled 
        request_body = ['mg']

        # Act
        enable_mg_response = self.app.post('/api/device/97/sample/output', json=request_body, follow_redirects=True)
        read_response = self.app.get('/api/device/97/sample', follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),      # expect 'i' for read info
                call(device_address, b'o,?\00'),    # expect 'o,?' for reading current device output
                call(device_address, b'o,MG,1\00'), # expect 'o,mg,1 to enable mg
                call(device_address, b'o,%,0\00'),  # expect 'o,%,0 to disable mg
                call(device_address, b'o,?\00'),    # expect 'o,?' for Re-reading current device output
                call(device_address, b'r\00')       # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.3), # "o,mg,1"
                call(0.3), # "o,%,0"
                call(0.3), # "o,?"
                call(0.9)  # "r"
            ], 
            any_order=False)

        # expect device info to be read from bus
        i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address), 
                call(device_address),
                call(device_address),
                call(device_address) 
            ], 
            any_order=False)

        self.assertEqual(enable_mg_response.status_code, 200)
        self.assertEqual(read_response.status_code, 200)

    @patch('time.sleep', return_value=None)
    def test_can_enable_mg_case_insensitive_unit_on_atlas_scientific_do_device(self, patched_time_sleep):

        # Arrange
        device_address = 97

        i2cbus.read.side_effect = [ 
                b'\x01?I,D.O.,1.98\00', # call should be for the device info
                b'\x01?O,%\00',         # call should be to read the current device outputs
                b'\x01\00',             # call should be to read the result from adding mg to device output
                b'\x01\00',             # call should be to read the result from removing % device output
            ]

        # Act
         # body should be a list of all the units to be enabled.
        # Note, all other units not in this list will be disabled 
        request_body = ['Mg']

        # Act
        enable_mg_response = self.app.post('/api/device/97/sample/output', json=request_body, follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),          # expect 'i' for read info
                call(device_address, b'o,?\00'),        # expect 'o,?' for reading current device output
                call(device_address, b'o,MG,1\00'),     # expect 'o,mg,1
                call(device_address, b'o,%,0\00'),      # expect 'o,mg,0
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.3), # "o,mg,1"
                call(0.3), # "o,%,0"
            ], 
            any_order=False)
        
        # expect device info to be read from bus
        i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address), 
                call(device_address), 
                call(device_address),
            ], 
            any_order=False)

        self.assertEqual(enable_mg_response.status_code, 200)

    @patch('time.sleep', return_value=None)
    def test_can_enable_both_percent_saturation_and_mg_unit_on_atlas_scientific_do_device(self, patched_time_sleep):

        # Arrange
        device_address = 97

        i2cbus.read.side_effect = [ 
                b'\x01?I,D.O.,1.98\00', # call should be for the device info
                b'\x01?O,%\00',         # call should be to read the current device outputs
                b'\x01\00',             # call should be to read the result from adding mg to device output
                b'\x01?O,MG,%\00',      # call should be to RE-read the current device outputs
                b'\x01238.15,419.6\00'  # call should be for reading the device sample
            ]

        # body should be a list of all the units to be enabled.
        # Note, all other units not in this list will be disabled 
        request_body = ['mg', '%']

        # Act
        enable_response = self.app.post('/api/device/97/sample/output', json=request_body, follow_redirects=True)
        read_response = self.app.get('/api/device/97/sample', follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),      # expect 'i' for read info
                call(device_address, b'o,?\00'),    # expect 'o,?' for reading current device output
                call(device_address, b'o,MG,1\00'), # expect 'o,mg,1 to enable mg
                call(device_address, b'o,?\00'),    # expect 'o,?' for Re-reading current device output
                call(device_address, b'r\00')       # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.3), # "o,mg,1"
                call(0.3), # "o,?"
                call(0.9)  # "r"
            ], 
            any_order=False)

        # expect device info to be read from bus
        i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address), 
                call(device_address),
                call(device_address),
                call(device_address) 
            ], 
            any_order=False)

        self.assertEqual(enable_response.status_code, 200)
        self.assertEqual(read_response.status_code, 200)


    @patch('time.sleep', return_value=None)
    def test_can_resolve_supported_outputs_atlas_scientific_do_device(self, patched_time_sleep):

        # Arrange
        device_address = 97

        i2cbus.read.side_effect = [
                b'\x01?I,D.O.,1.98\00', # call should be for the device info
                b'\x01?O,%\00',         # call should be to read the current device outputs
            ]

        # Act
        response = self.app.get('/api/device/97/sample/output', follow_redirects=True)

        # Assert
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
        self.assertEqual(b'[{"is_enable": true, "symbol": "%", "unit": "Percent saturation", "value_type": "float"}, {"is_enable": false, "symbol": "mg/L", "unit": "milligram per litre", "value_type": "float"}]', response.data)

    @patch('time.sleep', return_value=None)
    def test_can_compensate_for_kpa_Pressure_in_atlas_scientific_do_device(self, patched_time_sleep):

        # Arrange
        device_address = 97

        i2cbus.read.side_effect = [ 
                b'\x01?I,D.O.,1.98\00', # first call should be for the device info
                b'\x01\00',             # call should be to read the result from setting the μS compensation
            ]

        # Act
        request_body = [{
            'factor': 'pressure',
            'symbol': 'kPa', 
            'value': 90.25
        }]

        response = self.app.post('/api/device/97/sample/compensation', json=request_body, follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),      # expect 'i' for read info
                call(device_address, b'P,90.25\00'), # expect 'P,90.25' for setting the μS compensation
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "P,90.25"
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

    @patch('time.sleep', return_value=None)
    def test_can_compensate_for_temperature_in_atlas_scientific_do_device(self, patched_time_sleep):

        # Arrange
        device_address = 97

        i2cbus.read.side_effect = [ 
                b'\x01?I,D.O.,1.98\00', # first call should be for the device info
                b'\x01\00',             # call should be to read the result from setting the μS compensation
            ]

        # Act
        request_body = [{
            'factor': 'temperature',
            'symbol': '°C', 
            'value': 19.5
        }]

        response = self.app.post('/api/device/97/sample/compensation', json=request_body, follow_redirects=True)

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

        # expect a empty json list 
        self.assertEqual(response.status_code, 200)

    @patch('time.sleep', return_value=None)
    def test_can_compensate_for_us_salinity_in_atlas_scientific_do_device(self, patched_time_sleep):

        # Arrange
        device_address = 97

        i2cbus.read.side_effect = [ 
                b'\x01?I,D.O.,1.98\00', # first call should be for the device info
                b'\x01\00',             # call should be to read the result from setting the μS compensation
            ]

        # Act
        request_body = [{
            'factor': 'salinity',
            'symbol': 'μS', 
            'value': 50000
        }]

        response = self.app.post('/api/device/97/sample/compensation', json=request_body, follow_redirects=True)

        # Assert
        i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'S,50000\00'), # expect 'S,50000' for setting the μS compensation
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "S,50000"
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

# TODO: add test for when attempting to enable unit which is not supported