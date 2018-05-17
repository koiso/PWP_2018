#Provides the database API to access wind data

from datetime import datetime
import time, sqlite3, re, os

#Default path for db
DEFAULT_DB_PATH = '../db/PWP_DATA.db'


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
        return {'timestamp': row['date'], 'std_vertical_velocity': row['50_vertical_velocity']}

    def _create_quality_object(self, row):
        return {'timestamp': row['date'], 'quality': row['50_quality']}


    #API
    def get_speed(self, timestamp):
        '''
        Extracts speed from db
        :param timestamp:
            format yyyymmdd hh:mm ***
        :return: A dict with the format provided in
            :py:meth:`_create_speed_object` or None if speed with given timestamp does not exist or is 9999.

        '''

        #Query for speed
        query = 'SELECT * FROM WIND_DATA WHERE date = ?'

        #cursor & row init
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        #Execute main SQL statement
        qvalue = (timestamp,)
        cur.execute(query, qvalue)

        #Do the response shait
        row = cur.fetchone()
        if row is None:
            return None
        #build return object
        else:
            return self._create_speed_object(row)


    def get_temperature(self, timestamp):
        #Query for temp
        query = 'SELECT * FROM WIND_DATA WHERE date = ?'

        #cursor & row init
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        #Execute main SQL statement
        qvalue = (timestamp,)
        cur.execute(query, qvalue)

        #Do the response shait
        row = cur.fetchone()
        if row is None:
            return None
        #build return object
        else:
            return self._create_temperature_object(row)


    def delete_temperature(self, timestamp):
        '''
        deletes the temperature value with given timestamp
        :param timestamp:
        :return: True (204) if value was deleted, else False (if deleted already, or timestamp does not exist)
        '''

        query1 = 'SELECT temperature FROM WIND_DATA WHERE date = ?'
        query2 = 'UPDATE WIND_DATA SET temperature = "" WHERE date = ?'

        #check if temperature already deleted
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        qvalue = (timestamp,)
        cur.execute(query1, qvalue,)
        row = cur.fetchone()

        #if timestamp does not exist
        if row is None:
            return False
        else:
            temp = row["temperature"]
        #if temperature is already deleted
        if temp == "":
            return False
        else:
            #remove value
            self.con.row_factory = sqlite3.Row
            cur = self.con.cursor()
            qvalue = (timestamp,)
            try:
                cur.execute(query2, qvalue,)
                self.con.commit()
                return True
            except sqlite3.Error as e:
                print("Error %s:" % (e.args[0]))
                return False


    def add_speed(self, timestamp, speed):
        query1 = 'SELECT date FROM WIND_DATA where timestamp = ?'
        query2 = 'INSERT INTO WIND_DATA (timestamp, speed)) VALUES (?,?)'

        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        qvalue = (timestamp,)
        cur.execute(query1, qvalue)

        row = cur.fetchone()

        if row is None:
            qvalue = (timestamp, speed)
            cur.execute(query2, qvalue)
            self.con.commit()
            return speed
        else:
            return None



    def get_speeds(self, start=-1, end=-1):
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
        query = 'SELECT * FROM WIND_DATA'

        if start != -1 or end != -1:
            query += ' WHERE'

        #startpoint for dates if set
        if start != -1:
            query += ' date > %s' % str(start)

        if end != -1:
            query += ' AND'
            query += ' date < %s' % str(end)

        #sort
        query += ' ORDER BY date ASC'

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
        speeds = []
        for row in rows:
            speed = self._create_speed_object(row)
            speeds.append(speed)
        return speeds




    def get_battery(self, timestamp):
        '''
        Extracts battery voltage from db
        :param timestamp:
            format yyyymmdd hh:mm ***
        :return: A dict with the format provided in
            :py:meth:`_create_battery_` or None if speed with given timestamp does not exist or is 9999.

        '''

        #Query for battery
        query = 'SELECT * FROM WIND_DATA WHERE date = ?'

        #cursor & row init
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        #Execute main SQL statement
        pvalue = (timestamp,)
        cur.execute(query, pvalue)

        #Do the response shait
        row = cur.fetchone()
        if row  is None:
            return None
        #build return object
        return self._create_battery_object(row)


    def get_humidity(self, timestamp):
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
        return self._create_humidity_object(row)


    def delete_humidity(self, timestamp):
        '''
        deletes the humidity value with a given timestamp
        :param timestamp:
        :return: True (204) if value was deleted, else False (if deleted already, or timestamp does not exist)
        '''

        query1 = 'SELECT humidity FROM WIND_DATA WHERE date = ?'
        query2 = 'UPDATE WIND_DATA SET humidity = "" WHERE date = ?'

        #check if temperature already deleted
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        qvalue = (timestamp,)
        cur.execute(query1, qvalue,)
        row = cur.fetchone()

        #if timestamp does not exist
        if row is None:
            return False
        else:
            temp = row["humidity"]
        #if temperature is already deleted
        if temp == "":
            return False
        else:
            #remove value
            self.con.row_factory = sqlite3.Row
            cur = self.con.cursor()
            qvalue = (timestamp,)
            try:
                cur.execute(query2, qvalue,)
                self.con.commit()
                return True
            except sqlite3.Error as e:
                print("Error %s:" % (e.args[0]))
                return False


    def modify_humidity(self, timestamp, value):
        '''
        modifies the humidity value on timestamp with value given as argument
        :param timestamp:
        :param value:
        :return: True (204) if value was deleted, else False (if deleted already, or timestamp does not exist)
        '''
        query1 = 'SELECT humidity FROM WIND_DATA WHERE date = ?'
        query2 = 'UPDATE WIND_DATA SET humidity = ? WHERE date = ?'

        #check if temperature already deleted
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        qvalue = (timestamp,)
        cur.execute(query1, qvalue,)
        row = cur.fetchone()

        #if timestamp does not exist
        if row is None:
            return False
        else:
            temp = row["humidity"]
        #if temperature is already deleted
        if temp == "":
            return False
        else:
            #remove value
            self.con.row_factory = sqlite3.Row
            cur = self.con.cursor()
            qvalue = (timestamp,)
            try:
                cur.execute(query2, qvalue,)
                self.con.commit()
                return True
            except sqlite3.Error as e:
                print("Error %s:" % (e.args[0]))
                return False


    def get_batteries(self, start=-1, end=-1):
        #Create SQL statement
        #query = 'SELECT * FROM WIND_DATA WHERE date > %s AND date < %s ORDER BY date ASC' % str(start) % str(end)
        query = 'SELECT * FROM WIND_DATA'

        if start != -1 or end != -1:
            query += ' WHERE'

        #startpoint for dates if set
        if start != -1:
            query += ' date > %s' % str(start)

        if end != -1:
            query += ' AND'
            query += ' date < %s' % str(end)

        #sort
        query += ' ORDER BY date ASC'

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
        batteries = []
        for row in rows:
            battery = self._create_battery_object(row)
            batteries.append(battery)
        return batteries


    def get_direction(self, timestamp):
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
        return self._create_direction_object(row)


    def get_directions(self, start=-1, end=-1):
        #Create SQL statement
        #query = 'SELECT * FROM WIND_DATA WHERE date > %s AND date < %s ORDER BY date ASC' % str(start) % str(end)
        query = 'SELECT * FROM WIND_DATA'

        if start != -1 or end != -1:
            query += ' WHERE'

        #startpoint for dates if set
        if start != -1:
            query += ' date > %s' % str(start)

        if end != -1:
            query += ' AND'
            query += ' date < %s' % str(end)

        #sort
        query += ' ORDER BY date ASC'

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


    def get_humidities(self, start=-1, end=-1):
        # Create SQL statement
        # query = 'SELECT * FROM WIND_DATA WHERE date > %s AND date < %s ORDER BY date ASC' % str(start) % str(end)
        query = 'SELECT * FROM WIND_DATA'

        if start != -1 or end != -1:
            query += ' WHERE'

        # startpoint for dates if set
        if start != -1:
            query += ' date > %s' % str(start)

        if end != -1:
            query += ' AND'
            query += ' date < %s' % str(end)

        # sort
        query += ' ORDER BY date ASC'

        # cursor & row init
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # Execute SQL statement
        cur.execute(query)

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


    def get_temperatures(self, start=-1, end=-1):
        #Create SQL statement
        #query = 'SELECT * FROM WIND_DATA WHERE date > %s AND date < %s ORDER BY date ASC' % str(start) % str(end)
        query = 'SELECT * FROM WIND_DATA'

        if start != -1 or end != -1:
            query += ' WHERE'

        #startpoint for dates if set
        if start != -1:
            query += ' date > %s' % str(start)

        if end != -1:
            query += ' AND'
            query += ' date < %s' % str(end)

        #sort
        query += ' ORDER BY date ASC'

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
    def contains_timestamp(self, timestamp):
        query1 = 'SELECT humidity FROM WIND_DATA WHERE date = ?'
        #check if there is timestamp in DB
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        qvalue = (timestamp,)
        cur.execute(query1, qvalue,)
        row = cur.fetchone()

        #if timestamp does not exist
        if row is None:
            return False
        else:

    '''
        TODO: 
        create other methods for modifying (put) and create(post)
            
        
#this query might need correction...Perkels DELETING WHOLE ROW
query = 'DELETE FROM WIND_DATA WHERE date = ?'
self.con.row_factory = sqlite3.Row
cur = self.con.cursor()
qvalue = (timestamp,)
try:
    cur.execute(query, qvalue,)
    self.con.commit()
except sqlite3.Error as e:
    print("Error %s:" % (e.args[0]))
if cur.rowcount < 1:
    return False
else:
    return True
        
    '''



