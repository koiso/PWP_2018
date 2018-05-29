# -*- coding: utf-8 -*-

import sqlite3, unittest
from wind import dbhandler
from shutil import copy2
import os

# DB restore
#dirname = os.path.dirname(__file__)
#print(dirname)
#copy2(dirname+'/db/PWP_DATA_restore.db', dirname+'/db/PWP_DATA.db')
copy2('db/PWP_DATA_restore.db', 'db/PWP_DATA.db')

DB_BATH = 'db/PWP_DATA.db'
ENGINE = dbhandler.Engine(DB_BATH)

# FOR WIND_DATA
SPEED = {'timestamp': 1, 'speed': 3.01}
DIRECTION = {'timestamp': 1, 'direction': 176.0}
BATTERY = {'timestamp': 1, 'battery': 1234}
TEMPERATURE = {'timestamp': 1, 'temperature': 114}
HUMIDITY = {'timestamp': 1, 'humidity': 97}
PRESSURE = {'timestamp': 1, 'pressure': 923}
STD_SPEED = {'timestamp': 1, 'std_speed': 0.43}
VV = {'timestamp': 1, 'vertical_velocity': -0.05}
STD_VV = {'timestamp': 1, 'std_vertical_velocity': 0.19}
QUALITY = {'timestamp': 1,'quality': 108}

# FOR WIND_DEVICES
DEVICE = {'device_id': 1, 'reg_nro': 'ABC-123', 'type': 'Met Mast', 'location': 'Ahvenanmaa', 'data_id': 1}

# PARAMS
ID = 1
TIMESTAMP = 1
ROWCOUNT = 145

def extractDictAFromB(A,B):
    return dict([(k,B[k]) for k in A.keys() if k in B.keys()])


class DbCreateObjectsTests(unittest.TestCase):

    #test object creation
    def test_create_objects(self):
        self.connection = ENGINE.connect()

        print('('+self.test_create_objects.__name__+')', \
                  self.test_create_objects.__doc__ , "\n")

        # create SQL query
        query = 'SELECT * FROM WIND_DATA WHERE date = 1'

        con = self.connection.con
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Execute main SQL Statement
            cur.execute(query)
            #Extrac the row
            row = cur.fetchone()

        #deprecated method assertDictContains...
        #self.assertDictContainsSubset(object, SPEED_OBJ)
        #assert set(SPEED_OBJ.items()).issubset(set(object.items()))

        #test object creations
        print("Create speed object\n")
        object = self.connection._create_speed_object(row)
        self.assertEqual(object, extractDictAFromB(object, SPEED))

        print("Create direction object\n")
        object = self.connection._create_direction_object(row)
        self.assertEqual(object, extractDictAFromB(object, DIRECTION))

        print("Create battery object\n")
        object = self.connection._create_battery_object(row)
        self.assertEqual(object, extractDictAFromB(object, BATTERY))

        print("Create temperature object\n")
        object = self.connection._create_temperature_object(row)
        self.assertEqual(object, extractDictAFromB(object, TEMPERATURE))

        print("Create humidity object\n")
        object = self.connection._create_humidity_object(row)
        self.assertEqual(object, extractDictAFromB(object, HUMIDITY))

        print("Create pressure object\n")
        object = self.connection._create_pressure_object(row)
        self.assertEqual(object, extractDictAFromB(object, PRESSURE))

        print("Create std_speed object\n")
        object = self.connection._create_std_speed_object(row)
        self.assertEqual(object, extractDictAFromB(object, STD_SPEED))

        print("Create vertical_velocity object\n")
        object = self.connection._create_vertical_velocity_object(row)
        self.assertEqual(object, extractDictAFromB(object, VV))

        print("Create std_vv object\n")
        object = self.connection._create_std_vertical_velocity_object(row)
        self.assertEqual(object, extractDictAFromB(object, STD_VV))

        print("Create quality object\n")
        object = self.connection._create_quality_object(row)
        self.assertEqual(object, extractDictAFromB(object, QUALITY))

        # create SQL query to test device
        query = 'SELECT * FROM WIND_DEVICES WHERE device_id = 1'

        con = self.connection.con
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Execute main SQL Statement
            cur.execute(query)
            #Extrac the row
            row = cur.fetchone()

        print("Create device object\n")
        object = self.connection._create_device_object(row)
        self.assertEqual(object, extractDictAFromB(object, DEVICE))



class DbGetDeviceFromDB(unittest.TestCase):

    def test_get_device(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_device.__name__+')', \
              self.test_get_device.__doc__)

        device = self.connection.get_device(ID)
        self.assertEqual(device, extractDictAFromB(device, DEVICE))


    def test_get_device_noexisting_id(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_device_noexisting_id.__name__+')', \
              self.test_get_device_noexisting_id.__doc__)

        device = self.connection.get_device(3)
        self.assertIsNone(device)


    def test_get_device_malformed_id(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_device_malformed_id.__name__+')', \
              self.test_get_device_malformed_id.__doc__)

        device = self.connection.get_device("j")
        self.assertIsNone(device)


    def test_get_devices(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_devices.__name__+')', \
              self.test_get_devices.__doc__)

        devices = self.connection.get_devices()
        self.assertEqual(len(devices), 2)
        for device in devices:
            if device['device_id'] == ID:
                self.assertEqual(len(device), 4)
                self.assertEqual(device, extractDictAFromB(device, DEVICE))


class DbGetSpeedFromDB(unittest.TestCase):

    def test_get_speed(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_speed.__name__+')', \
              self.test_get_speed.__doc__)

        speed = self.connection.get_speed(ID, TIMESTAMP)
        self.assertEqual(speed, extractDictAFromB(speed, SPEED))


    def test_get_speed_noexisting_timestamp(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_speed_noexisting_timestamp.__name__+')', \
              self.test_get_speed_noexisting_timestamp.__doc__)

        speed = self.connection.get_speed(ID, 876)
        self.assertIsNone(speed)


    def test_get_speed_malformed_timestamp(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_speed_malformed_timestamp.__name__+')', \
              self.test_get_speed_malformed_timestamp.__doc__)

        speed = self.connection.get_speed(ID, "j")
        self.assertIsNone(speed)


    def test_get_speeds(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_speeds.__name__+')', \
              self.test_get_speeds.__doc__)

        speeds = self.connection.get_speeds(ID)
        self.assertEqual(len(speeds), ROWCOUNT)
        for speed in speeds:
            if speed['timestamp'] == TIMESTAMP:
                self.assertEqual(len(speed), 2)
                self.assertEqual(speed, extractDictAFromB(speed, SPEED))


class DbGetDirectionFromDB(unittest.TestCase):

    def test_get_direction(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_direction.__name__+')', \
              self.test_get_direction.__doc__)

        direction = self.connection.get_direction(ID, TIMESTAMP)
        self.assertEqual(direction, extractDictAFromB(direction, DIRECTION))


    def test_get_direction_noexisting_timestamp(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_direction_noexisting_timestamp.__name__+')', \
              self.test_get_direction_noexisting_timestamp.__doc__)

        direction = self.connection.get_direction(ID, 876)
        self.assertIsNone(direction)


    def test_get_direction_malformed_timestamp(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_direction_malformed_timestamp.__name__+')', \
              self.test_get_direction_malformed_timestamp.__doc__)

        direction = self.connection.get_direction(ID, "j")
        self.assertIsNone(direction)


    def test_get_directions(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_directions.__name__+')', \
              self.test_get_directions.__doc__)

        directions = self.connection.get_directions(ID)
        self.assertEqual(len(directions), 145)
        for direction in directions:
            if direction['timestamp'] == TIMESTAMP:
                self.assertEqual(len(direction), 2)
                self.assertEqual(direction, extractDictAFromB(direction, DIRECTION))


class DbGetBatteryFromDB(unittest.TestCase):

    def test_get_battery(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_battery.__name__+')', \
              self.test_get_battery.__doc__)

        battery = self.connection.get_battery(ID, TIMESTAMP)
        self.assertEqual(battery, extractDictAFromB(battery, BATTERY))


    def test_get_battery_noexisting_timestamp(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_battery_noexisting_timestamp.__name__+')', \
              self.test_get_battery_noexisting_timestamp.__doc__)

        battery = self.connection.get_battery(ID, 876)
        self.assertIsNone(battery)


    def test_get_battery_malformed_timestamp(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_battery_malformed_timestamp.__name__+')', \
              self.test_get_battery_malformed_timestamp.__doc__)

        battery = self.connection.get_battery(ID, "j")
        self.assertIsNone(battery)


    def test_get_batteries(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_batteries.__name__+')', \
              self.test_get_batteries.__doc__)

        batteries = self.connection.get_batteries(ID)
        self.assertEqual(len(batteries), ROWCOUNT)
        for battery in batteries:
            if battery['timestamp'] == TIMESTAMP:
                self.assertEqual(len(battery), 2)
                self.assertEqual(battery, extractDictAFromB(battery, BATTERY))
                
                
class DbGetTemperatureFromDB(unittest.TestCase):

    def test_get_temperature(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_temperature.__name__+')', \
              self.test_get_temperature.__doc__)

        temperature = self.connection.get_temperature(ID, TIMESTAMP)
        self.assertEqual(temperature, extractDictAFromB(temperature, TEMPERATURE))


    def test_get_temperature_noexisting_timestamp(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_temperature_noexisting_timestamp.__name__+')', \
              self.test_get_temperature_noexisting_timestamp.__doc__)

        temperature = self.connection.get_temperature(ID, 876)
        self.assertIsNone(temperature)


    def test_get_temperature_malformed_timestamp(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_temperature_malformed_timestamp.__name__+')', \
              self.test_get_temperature_malformed_timestamp.__doc__)

        temperature = self.connection.get_temperature(ID, "j")
        self.assertIsNone(temperature)


    def test_get_temperatures(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_temperatures.__name__+')', \
              self.test_get_temperatures.__doc__)

        temperatures = self.connection.get_temperatures(ID)
        self.assertEqual(len(temperatures), ROWCOUNT)
        for temperature in temperatures:
            if temperature['timestamp'] == TIMESTAMP:
                self.assertEqual(len(temperature), 2)
                self.assertEqual(temperature, extractDictAFromB(temperature, TEMPERATURE))
                
                
class DbGetHumidityFromDB(unittest.TestCase):

    def test_get_humidity(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_humidity.__name__+')', \
              self.test_get_humidity.__doc__)

        humidity = self.connection.get_humidity(ID, TIMESTAMP)
        self.assertEqual(humidity, extractDictAFromB(humidity, HUMIDITY))


    def test_get_humidity_noexisting_timestamp(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_humidity_noexisting_timestamp.__name__+')', \
              self.test_get_humidity_noexisting_timestamp.__doc__)

        humidity = self.connection.get_humidity(ID, 876)
        self.assertIsNone(humidity)


    def test_get_humidity_malformed_timestamp(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_humidity_malformed_timestamp.__name__+')', \
              self.test_get_humidity_malformed_timestamp.__doc__)

        humidity = self.connection.get_humidity(ID, "j")
        self.assertIsNone(humidity)


    def test_get_humidities(self):
        self.connection = ENGINE.connect()

        print('('+self.test_get_humidities.__name__+')', \
              self.test_get_humidities.__doc__)

        humidities = self.connection.get_humidities(ID)
        self.assertEqual(len(humidities), ROWCOUNT)
        for humidity in humidities:
            if humidity['timestamp'] == TIMESTAMP:
                self.assertEqual(len(humidity), 2)
                self.assertEqual(humidity, extractDictAFromB(humidity, HUMIDITY))


class DbPostDeleteAddHumidityToDB(unittest.TestCase):
    def test_delete_humidity(self):
        self.connection = ENGINE.connect()

        print('('+self.test_delete_humidity.__name__+')', \
              self.test_delete_humidity.__doc__)

        resp = self.connection.delete_humidity(1, 56)
        self.assertTrue(resp)


    def test_delete_humidity_malformed_id(self):
        self.connection = ENGINE.connect()

        print('('+self.test_delete_humidity_malformed_id.__name__+')', \
              self.test_delete_humidity_malformed_id.__doc__)

        with self.assertRaises(ValueError):
            resp = self.connection.delete_humidity(1, "k")

    def test_delete_humidity_noexisting_id(self):
        self.connection = ENGINE.connect()

        print('('+self.test_delete_humidity_noexisting_id.__name__+')', \
              self.test_delete_humidity_noexisting_id.__doc__)

        with self.assertRaises(TypeError):
            resp = self.connection.delete_humidity(1, 1600)


    def test_add_humidity(self):
        self.connection = ENGINE.connect()

        print('('+self.test_add_humidity.__name__+')', \
              self.test_add_humidity.__doc__)

        value_to_add = 99

        resp = self.connection.add_humidity(1, 1111, value_to_add)
        resp2 = self.connection.get_humidity(1, 1111)
        resp2.update({'device_id': 1})

        self.assertEqual(resp, extractDictAFromB(resp, resp2))


    def test_add_humidity_malformed_id(self):
        self.connection = ENGINE.connect()

        print('('+self.test_add_humidity_malformed_id.__name__+')', \
              self.test_add_humidity_malformed_id.__doc__)

        value_to_add = 99

        with self.assertRaises(ValueError):
            self.connection.add_humidity(1, "j", value_to_add)


    def test_add_humidity_existing_id(self):
        self.connection = ENGINE.connect()

        print('('+self.test_add_humidity_existing_id.__name__+')', \
              self.test_add_humidity_existing_id.__doc__)

        value_to_add = 99

        resp = self.connection.add_humidity(1, 23, value_to_add)
        self.assertTrue(resp)


    def test_modify_humidity(self):
        self.connection = ENGINE.connect()

        print('('+self.test_modify_humidity.__name__+')', \
              self.test_modify_humidity.__doc__)

        value_to_modify = 99

        resp = self.connection.modify_humidity(1, 56, value_to_modify)
        resp2 = self.connection.get_humidity(1, 56)

        test = {'humidity': 99, 'timestamp': 56}
        self.assertTrue(resp)
        self.assertEqual(resp2, extractDictAFromB(resp2, test))


    def test_modify_humidity_malformed_id(self):
        self.connection = ENGINE.connect()

        print('('+self.test_modify_humidity_malformed_id.__name__+')', \
              self.test_modify_humidity_malformed_id.__doc__)

        value_to_modify = 99

        with self.assertRaises(ValueError):
            self.connection.modify_humidity(1, "j", value_to_modify)


    def test_modify_humidity_noexisting_id(self):
        self.connection = ENGINE.connect()

        print('('+self.test_modify_humidity_noexisting_id.__name__+')', \
              self.test_modify_humidity_noexisting_id.__doc__)

        value_to_modify = 99

        resp = self.connection.modify_humidity(1, 1234, value_to_modify)
        self.assertFalse(resp)



class DbPostDeleteAddTemperatureToDB(unittest.TestCase):
    def test_delete_temperature(self):
        self.connection = ENGINE.connect()

        print('('+self.test_delete_temperature.__name__+')', \
              self.test_delete_temperature.__doc__)

        resp = self.connection.delete_temperature(1, 56)
        self.assertTrue(resp)


    def test_delete_temperature_malformed_id(self):
        self.connection = ENGINE.connect()

        print('('+self.test_delete_temperature_malformed_id.__name__+')', \
              self.test_delete_temperature_malformed_id.__doc__)

        with self.assertRaises(ValueError):
            self.connection.delete_temperature(1, "j")


    def test_delete_temperature_noexisting_id(self):
        self.connection = ENGINE.connect()

        print('('+self.test_delete_temperature_noexisting_id.__name__+')', \
              self.test_delete_temperature_noexisting_id.__doc__)

        resp = self.connection.delete_temperature(1, 1601)
        self.assertFalse(resp)


    def test_add_temperature(self):
        self.connection = ENGINE.connect()

        print('('+self.test_add_temperature.__name__+')', \
              self.test_add_temperature.__doc__)

        value_to_add = 99

        resp = self.connection.add_temperature(1, 1112, value_to_add)
        resp2 = self.connection.get_temperature(1, 1112)
        resp2.update({'device_id': 1})

        self.assertEqual(resp, extractDictAFromB(resp, resp2))


    def test_add_temperature_malformed_id(self):
        self.connection = ENGINE.connect()

        print('('+self.test_add_temperature_malformed_id.__name__+')', \
              self.test_add_temperature_malformed_id.__doc__)

        value_to_add = 99

        with self.assertRaises(ValueError):
            self.connection.add_temperature(1, "j", value_to_add)


    def test_add_temperature_existing_id(self):
        self.connection = ENGINE.connect()

        print('('+self.test_add_temperature_existing_id.__name__+')', \
              self.test_add_temperature_existing_id.__doc__)

        value_to_add = 99

        resp = self.connection.add_temperature(1, 23, value_to_add)
        self.assertTrue(resp)


    def test_modify_temperature(self):
        self.connection = ENGINE.connect()

        print('('+self.test_modify_temperature.__name__+')', \
              self.test_modify_temperature.__doc__)

        value_to_modify = 99

        resp = self.connection.modify_temperature(1, 56, value_to_modify)
        resp2 = self.connection.get_temperature(1, 56)

        test = {'temperature': 99, 'timestamp': 56}
        self.assertTrue(resp)
        self.assertEqual(resp2, extractDictAFromB(resp2, test))


    def test_modify_temperature_malformed_id(self):
        self.connection = ENGINE.connect()

        print('('+self.test_modify_temperature_malformed_id.__name__+')', \
              self.test_modify_temperature_malformed_id.__doc__)

        value_to_modify = 99

        with self.assertRaises(ValueError):
            self.connection.modify_temperature(1, "j", value_to_modify)


    def test_modify_temperature_noexisting_id(self):
        self.connection = ENGINE.connect()

        print('('+self.test_modify_temperature_noexisting_id.__name__+')', \
              self.test_modify_temperature_noexisting_id.__doc__)

        value_to_modify = 99

        resp = self.connection.modify_temperature(1, 1234, value_to_modify)
        self.assertFalse(resp)



if __name__ == '__main__':
    print('Start running message tests')
    unittest.main()
