# Provides the database API to access wind data

from datetime import datetime
import time, sqlite3, re, os

# Default path for db
DEFAULT_DB_PATH = '../db/PWP_DATA.db'


# slightly borrowed from exercises
class Engine(object):
    '''
    Abstraction of the database.

    It includes tools to create, configure,
    populate and connect to the sqlite file. You can access the Connection
    instance, and hence, to the database interface itself using the method
    :py:meth:`connection`.

    :Example:

    >>> engine = Engine()
    >>> con = engine.connect()

    :param db_path: The path of the database file (always with respect to the
        calling script. If not specified, the Engine will use the file located
        at *db/forum.db*

    '''
    def __init__(self, db_path=None):
        '''
        '''

        super(Engine, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH

    def connect(self):
        '''
        Creates a connection to the database.

        :return: A Connection instance
        :rtype: Connection

        '''
        return Connection(self.db_path)

#little bit borrowed from exercise
class Connection(object):
    '''
       API to access the PWP_DATA database.

       The sqlite3 connection instance is accessible to all the methods of this
       class through the :py:attr:`self.con` attribute.

       An instance of this class should not be instantiated directly using the
       constructor. Instead use the :py:meth:`Engine.connect`.

       Use the method :py:meth:`close` in order to close a connection.
       A :py:class:`Connection` **MUST** always be closed once when it is not going to be
       utilized anymore in order to release internal locks.

       :param db_path: Location of the database file.
       :type dbpath: str

       '''

    def __init__(self, db_path):
        super(Connection, self).__init__()
        self.con = sqlite3.connect(db_path)
        self._isclosed = False

    def isclosed(self):
        '''
        :return: ``True`` if connection has already being closed.
        '''
        return self._isclosed

    def close(self):
        '''
        Closes the database connection, commiting all changes.
        '''
        if self.con and not self._isclosed:
            self.con.commit()
            self.con.close()
            self._isclosed = True


    # HELPERS
    # Here the helpers that transform database rows into dictionary. They work
    # Helper for speed
    def _create_speed_object(self, row):
        timestamp = row['date']
        value = row['50_speed']
        speed = {'timestamp': timestamp, 'speed': value}
        return speed

    def _create_direction_object(self, row):
        return {'timestamp': row['date'], 'direction': row['50_direction']}

    def _create_battery_object(self, row):
        return {'timestamp': row['date'], 'battery': row['battery_voltage']}

    def _create_temperature_object(self, row):
        timestamp = row['date']
        value = row['temperature']
        temperature = {'timestamp': timestamp, 'temperature': value}
        return temperature

    def _create_humidity_object(self, row):
        return {'timestamp': row['date'], 'humidity': row['humidity']}

    def _create_pressure_object(self, row):
        return {'timestamp': row['date'], 'pressure': row['pressure']}

    def _create_std_speed_object(self, row):
        return {'timestamp': row['date'], 'std_speed': row['50_std_speed']}

    def _create_vertical_velocity_object(self, row):
        return {'timestamp': row['date'], 'vertical_velocity': row['50_vertical_velocity']}

    def _create_std_vertical_velocity_object(self, row):
        return {'timestamp': row['date'], 'std_vertical_velocity': row['50_std_w']}

    def _create_quality_object(self, row):
        return {'timestamp': row['date'], 'quality': row['50_quality']}

    def _create_device_object(self, row):
        return {'device_id': row['device_id'], 'reg_nro': row['reg_nro'],
                'type': row['device_type'], 'location': row['location']}


    #API

    def get_device(self, id):
        '''
        extracts device from db
        :param id:
            integer value of device_id
        :return A dict with device information of given id
            :py:meth:`_create_device_object` or None if device with given id does not exist
        '''

        #match = int(id)
        #if match is None:
        #    raise ValueError("The id is malformed")

        #Query for speed
        query = 'SELECT * FROM WIND_DEVICES WHERE device_id = ?'

        #cursor & row init
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        #Execute main SQL statement
        qvalue = (id,)
        cur.execute(query, qvalue)

        #Do the response shait
        row = cur.fetchone()
        if row is None:
            return None
        #build return object
        else:
            return self._create_device_object(row)


    def get_devices(self):
        '''
        return a list of all devices from DB
        '''

        #Create SQL statement
        #query = 'SELECT * FROM WIND_DATA WHERE date > %s AND date < %s ORDER BY date ASC' % str(start) % str(end)
        query = 'SELECT * FROM WIND_DEVICES'

        #cursor & row init
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        #Execute SQL statement
        cur.execute(query)

        #results
        rows = cur.fetchall()
        if rows is None:
            return None
        #build return object
        devices = []
        for row in rows:
            device = self._create_device_object(row)
            devices.append(device)
        return devices


    def get_speed(self, id, timestamp):
        '''
        Extracts speed from db
        :param timestamp:
            format integer value
        :return: A dict with the format provided in
            :py:meth:`_create_speed_object` or None if speed with given timestamp does not exist

        '''

        #Query for speed
        query = 'SELECT * FROM WIND_DATA WHERE device_id = ? AND date = ?'

        #cursor & row init
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        #Execute main SQL statement
        qvalue = (id, timestamp,)
        cur.execute(query, qvalue)

        #Do the response shait
        row = cur.fetchone()
        if row is None:
            return None
        #build return object
        else:
            return self._create_speed_object(row)


    def get_temperature(self, id, timestamp):
        #Query for temp
        query = 'SELECT * FROM WIND_DATA WHERE device_id = ? AND date = ?'

        #cursor & row init
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        #Execute main SQL statement
        qvalue = (id, timestamp,)
        cur.execute(query, qvalue)

        #Do the response shait
        row = cur.fetchone()
        if row is None:
            return None
        #build return object
        else:
            return self._create_temperature_object(row)


    def delete_temperature(self, id, timestamp):
        '''
        deletes the temperature value with given timestamp
        :param timestamp:
        :return: True (204) if value was deleted, else False (if deleted already, or timestamp does not exist)
        '''

        try:
            id = int(id)
            timestamp = int(timestamp)
        except(ValueError):
            raise ValueError("The deviceid is malformed")

        query1 = 'SELECT temperature FROM WIND_DATA WHERE device_id = ? AND date = ?'
        query2 = 'UPDATE WIND_DATA SET temperature = "" WHERE device_id = ? AND date = ?'

        #check if temperature already deleted
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        qvalue = (id, timestamp,)
        cur.execute(query1, qvalue, )
        row = cur.fetchone()
        #print(row)

        #if timestamp does not exist
        if row is None:
            return False
        else:
            temp = row["temperature"]
        #if temperature is already deleted
        if temp == "" or temp == None:
            return False
        else:
            #remove value
            self.con.row_factory = sqlite3.Row
            cur = self.con.cursor()
            qvalue = (id, timestamp,)
            try:
                cur.execute(query2, qvalue,)
                self.con.commit()
                return True
            except sqlite3.Error as e:
                print("Error %s:" % (e.args[0]))
                return False


    def modify_temperature(self, id, timestamp, value):
        '''
        modifies the temperature value on timestamp with value given
        :param timestamp:
        :param value:
        :return: True (204) if value was deleted, else False (if deleted already, or timestamp does not exist)
        '''

        try:
            id = int(id)
            timestamp = int(timestamp)
        except(ValueError):
            raise ValueError("The deviceid is malformed")

        #check if noexisting timestamp
        query2 = 'SELECT * FROM WIND_DATA WHERE device_id = ? AND date = ?'
        qvalue2 = (id, timestamp,)

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        cur.execute(query2, qvalue2,)

        #Do the response shait
        row = cur.fetchone()
        if row is None:
            return False


        query = 'UPDATE WIND_DATA SET temperature = ? WHERE device_id = ? AND date = ?'
        qvalue = (value, id, timestamp,)

        #modify value
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        try:
            cur.execute(query, qvalue)
            self.con.commit()
            return True
        except sqlite3.Error as e:
            print("Error %s:" % (e.args[0]))
            return False


    def add_temperature(self, id, timestamp, value):
        '''
        Adds the temperature value with given timestamp
        :param timestamp:
        :param value:
        :return: False if not added. dict with timestamp and value if added
        '''

        # if there is a timestamp: temperature value is checked to be null already in method call
        # add value to temperature with given timestamp
        # created this for usability, we want to add value even if there is a timestamp already (RESTISH?)

        try:
            id = int(id)
            timestamp = int(timestamp)
        except(ValueError):
            raise ValueError("The messageid is malformed")

        test = self.contains_timestamp(id, timestamp)
        if test:
            returnable_boolean = self.modify_temperature(id, timestamp, value)
            return returnable_boolean

        # if there is no timestamp create new entry
        else:
            query = 'INSERT INTO WIND_DATA (date, temperature, device_id) VALUES(?,?,?)'
            qvalue = (timestamp, value, id)

            #Add new entry
            self.con.row_factory = sqlite3.Row
            cur = self.con.cursor()
            try:
                cur.execute(query, qvalue)
                self.con.commit()
                return {"timestamp": timestamp, "temperature": value, "device_id": id}
            except sqlite3.Error as e:
                print("Error %s:" % (e.args[0]))
                return False



    def get_speeds(self, id):
        '''
        return a list of all speed values from DB filtere by conditions provided in parameters
        start: starting timestamp
        end: ending timestamp

        :param start: timestamp
        :param end: timestamp
        :return: a list of speed values. each value is is a dict containing timestamp & speed value
        '''

        #Create SQL statement
        #query = 'SELECT * FROM WIND_DATA WHERE date > %s AND date < %s ORDER BY date ASC' % str(start) % str(end)
        #query = 'SELECT * FROM WIND_DATA'
        query = 'SELECT * FROM WIND_DATA WHERE device_ID = ?'

        qvalue = (id,)

        #sort
        query += ' ORDER BY date ASC'

        #cursor & row init
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        #Execute SQL statement
        cur.execute(query, qvalue)

        #results
        rows = cur.fetchall()
        if rows is None:
            return None
        #build return object
        speeds = []
        for row in rows:
            speed = self._create_speed_object(row)
            speeds.append(speed)
        return speeds


    def get_battery(self, id, timestamp):
        '''
        Extracts battery voltage from db
        :param timestamp:
            format yyyymmdd hh:mm ***
        :return: A dict with the format provided in
            :py:meth:`_create_battery_` or None if speed with given timestamp does not exist or is 9999.

        '''

        #Query for battery
        query = 'SELECT * FROM WIND_DATA WHERE device_id = ? AND date = ?'

        #cursor & row init
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        #Execute main SQL statement
        pvalue = (id, timestamp,)
        cur.execute(query, pvalue)

        #Do the response shait
        row = cur.fetchone()
        if row  is None:
            return None
        #build return object
        return self._create_battery_object(row)


    def get_humidity(self, id, timestamp):
        query = 'SELECT * FROM WIND_DATA WHERE device_id = ? AND date = ?'
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (id, timestamp,)
        cur.execute(query, pvalue)

        #Do the response shait
        row = cur.fetchone()
        if row  is None:
            return None
        #build return object
        return self._create_humidity_object(row)


    def delete_humidity(self, id, timestamp):
        '''
        deletes the humidity value with a given timestamp
        :param timestamp:
        :return: True (204) if value was deleted, else False (if deleted already, or timestamp does not exist)
        '''

        try:
            id = int(id)
            timestamp = int(timestamp)
        except(ValueError):
            raise ValueError("The deviceid is malformed")

        query1 = 'SELECT humidity FROM WIND_DATA WHERE device_id = ? AND date = ?'
        query2 = 'UPDATE WIND_DATA SET humidity = "" WHERE device_id = ? AND date = ?'

        #check if temperature already deleted
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        qvalue = (id, timestamp,)
        cur.execute(query1, qvalue,)
        row = cur.fetchone()

        #if timestamp does not exist
        if row is None:
            #print("1")
            return False
        else:
            #print("2")
            humi = row["humidity"]
        #if temperature is already deleted
        if humi == "" or None:
            print("3")
            return False
        else:
            #print("4")
            #remove value
            self.con.row_factory = sqlite3.Row
            cur = self.con.cursor()
            qvalue = (id, timestamp,)
            try:
                #print("5")
                cur.execute(query2, qvalue,)
                self.con.commit()
                return True
            except sqlite3.Error as e:
                #print("6")
                print("Error %s:" % (e.args[0]))
                return False


    def modify_humidity(self, id, timestamp, value):
        '''
        modifies the humidity value on timestamp with value given as argument
        :param id
        :param timestamp:
        :param value:
        :return: True (204) if value was deleted, else False (if deleted already, or timestamp does not exist)
        '''

        try:
            id = int(id)
            timestamp = int(timestamp)
        except(ValueError):
            raise ValueError("The deviceid is malformed")

        #check if noexisting timestamp
        query2 = 'SELECT * FROM WIND_DATA WHERE device_id = ? AND date = ?'
        qvalue2 = (id, timestamp,)

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        cur.execute(query2, qvalue2,)

        #Do the response shait
        row = cur.fetchone()
        if row is None:
            return False

        query = 'UPDATE WIND_DATA SET humidity = ? WHERE device_id = ? AND date = ?'

        #check if temperature already deleted
        qvalue = (value, id, timestamp,)

        #modify value
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        try:
            cur.execute(query, qvalue)
            self.con.commit()
            return True
        except sqlite3.Error as e:
            print("Error %s:" % (e.args[0]))
            return False


    def add_humidity(self, id, timestamp, value):
        '''
        Adds the humidity value with given timestamp
        :param timestamp:
        :param value:
        :return: False if not added. dict with timestamp and value if added
        '''

        # if there is a timestamp: humidity value is checked to be null already in method call
        # add value to humidity with given timestamp
        # created this for usability, we want to add value even if there is a timestamp already (RESTISH?)

        try:
            id = int(id)
            timestamp = int(timestamp)
        except(ValueError):
            raise ValueError("The messageid is malformed")

        test = self.contains_timestamp(id, timestamp)
        if test:
            returnable_boolean = self.modify_humidity(id, timestamp, value)
            return returnable_boolean

        # if there is no timestamp create new entry
        else:
            query = 'INSERT INTO WIND_DATA (date, humidity, device_id) VALUES(?,?,?)'
            qvalue = (timestamp, value, id)

            #Add new entry
            self.con.row_factory = sqlite3.Row
            cur = self.con.cursor()
            try:
                cur.execute(query, qvalue)
                self.con.commit()
                return {"timestamp": timestamp, "humidity": value, "device_id": id}
            except sqlite3.Error as e:
                print("Error %s:" % (e.args[0]))
                return False


    def get_batteries(self, id):
        #Create SQL statement
        #query = 'SELECT * FROM WIND_DATA WHERE date > %s AND date < %s ORDER BY date ASC' % str(start) % str(end)
        query = 'SELECT * FROM WIND_DATA WHERE device_id = ?'
        #sort
        query += ' ORDER BY date ASC'
        qvalue = (id,)

        #cursor & row init
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        #Execute SQL statement
        cur.execute(query, qvalue)

        #results
        rows = cur.fetchall()
        if rows is None:
            return None
        #build return object
        batteries = []
        for row in rows:
            battery = self._create_battery_object(row)
            batteries.append(battery)
        return batteries


    def get_direction(self, id, timestamp):
        query = 'SELECT * FROM WIND_DATA WHERE device_id = ? AND date = ?'
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (id, timestamp,)
        cur.execute(query, pvalue)

        #Do the response shait
        row = cur.fetchone()
        if row  is None:
            return None
        #build return object
        return self._create_direction_object(row)


    def get_directions(self, id):
        #Create SQL statement
        #query = 'SELECT * FROM WIND_DATA WHERE date > %s AND date < %s ORDER BY date ASC' % str(start) % str(end)
        query = 'SELECT * FROM WIND_DATA WHERE device_id = ?'

        #sort
        query += ' ORDER BY date ASC'

        qvalue = (id,)

        #cursor & row init
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        #Execute SQL statement
        cur.execute(query, qvalue)

        #results
        rows = cur.fetchall()
        if rows is None:
            return None
        #build return object
        directions = []
        for row in rows:
            dir = self._create_direction_object(row)
            directions.append(dir)
        return directions


    def get_std_speed(self, timestamp):
        query = 'SELECT * FROM WIND_DATA WHERE date = ?'
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (timestamp,)
        cur.execute(query, pvalue)

        #Do the response shait
        row = cur.fetchone()
        if row  is None:
            return None
        #build return object
        return self._create_std_speed_object(row)

    def get_vertical_velocity(self, timestamp):
        query = 'SELECT * FROM WIND_DATA WHERE date = ?'
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (timestamp,)
        cur.execute(query, pvalue)

        # Do the response shait
        row = cur.fetchone()
        if row is None:
            return None
        # build return object
        return self._create_vertical_velocity_object(row)

    def get_std_vertical_velocity(self, timestamp):
        query = 'SELECT * FROM WIND_DATA WHERE date = ?'
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (timestamp,)
        cur.execute(query, pvalue)

        # Do the response shait
        row = cur.fetchone()
        if row is None:
            return None
        # build return object
        return self._create_std_vertical_velocity_object(row)


    def get_quality(self, timestamp):
        query = 'SELECT * FROM WIND_DATA WHERE date = ?'
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (timestamp,)
        cur.execute(query, pvalue)

        # Do the response shait
        row = cur.fetchone()
        if row is None:
            return None
        # build return object
        return self._create_quality_object(row)


    def get_pressure(self, timestamp):
        query = 'SELECT * FROM WIND_DATA WHERE date = ?'
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (timestamp,)
        cur.execute(query, pvalue)

        #Do the response shait
        row = cur.fetchone()
        if row  is None:
            return None
        #build return object
        return self._create_pressure_object(row)


    def get_humidities(self, id):
        # Create SQL statement
        # query = 'SELECT * FROM WIND_DATA WHERE date > %s AND date < %s ORDER BY date ASC' % str(start) % str(end)
        query = 'SELECT * FROM WIND_DATA WHERE device_id = ?'

        # sort
        query += ' ORDER BY date ASC'

        qvalue = (id,)

        # cursor & row init
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # Execute SQL statement
        cur.execute(query, qvalue)

        # results
        rows = cur.fetchall()
        if rows is None:
            return None
        # build return object
        humidities = []
        for row in rows:
            humi = self._create_humidity_object(row)
            humidities.append(humi)
        return humidities


    def get_temperatures(self, id):
        #Create SQL statement
        #query = 'SELECT * FROM WIND_DATA WHERE date > %s AND date < %s ORDER BY date ASC' % str(start) % str(end)
        query = 'SELECT * FROM WIND_DATA WHERE device_id = ?'

        #sort
        query += ' ORDER BY date ASC'

        qvalue = (id,)

        #cursor & row init
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        #Execute SQL statement
        cur.execute(query, qvalue)

        #results
        rows = cur.fetchall()
        if rows is None:
            return None
        #build return object
        temperatures = []
        for row in rows:
            temp = self._create_temperature_object(row)
            temperatures.append(temp)
        return temperatures


    def get_pressure(self, timestamp):
        query = 'SELECT * FROM WIND_DATA WHERE date = ?'
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (timestamp,)
        cur.execute(query, pvalue)

        #Do the response shait
        row = cur.fetchone()
        if row  is None:
            return None
        #build return object
        return self._create_pressure_object(row)


    #STUFF
    def contains_timestamp(self, id, timestamp):
        query = 'SELECT * FROM WIND_DATA WHERE device_id = ? AND date = ?'
        #check if there is timestamp in DB
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        qvalue = (id, timestamp,)
        cur.execute(query, qvalue,)
        row = cur.fetchone()

        #if timestamp does not exist
        if row is None:
            return False
        else:
            return True

    def contains_value(self, id, timestamp, column):
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #NO plaeholders for tables or column names - WTF!
        #Ok, might be valid idea for security reasons, however  roundabout -->
        cur.execute('SELECT {} FROM WIND_DATA WHERE device_id = {} AND date = {}'.format(column, id, timestamp))
        row = cur.fetchone()
        #if value in column does not exist
        #print(row[0])
        if row is None:
            #print("1")
            return False
        elif row[0] is "" or row[0] is None:
            #print(2)
            return False
        else:
            #print(3)
            return True




