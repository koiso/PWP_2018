# -*- coding: utf-8 -*-

import sqlite3, unittest
from wind import dbhandler

DB_BATH = 'db/PWP_DATA.db'
ENGINE = dbhandler.Engine(DB_BATH)

SPEED_OBJ = {'timestamp': 1, 'speed': 3.01}

class DbCreateObjectsTests(unittest.TestCase):
    def test_create_speed_object(self):
        self.connection = ENGINE.connect()

        print('('+self.test_create_speed_object.__name__+')', \

                  self.test_create_speed_object.__doc__)

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

        object = self.connection._create_speed_object(row)
        self.assertDictContainsSubset(object, SPEED_OBJ)



'''
class DbGetTests(unittest.TestCase):
    def test_get_device(self):
'''


if __name__ == '__main__':
    print('Start running message tests')
    unittest.main()
