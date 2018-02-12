'''
Created on 21.01.2018

Database interface testing to check tables has been created correctly.

@author: ivan
'''

import sqlite3, unittest, collections

from forum import database

#Path to the database file, different from the deployment db
DB_PATH = 'db/forum_test.db'
ENGINE = database.Engine(DB_PATH)

INITIAL_SIZE = 20





class CreatedTablesTestCase(unittest.TestCase):
    '''
    Test cases for the created tables.
    '''
    #INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        ''' Creates the database structure. Removes first any preexisting
            database file
        '''
        print("Testing ", cls.__name__)
        ENGINE.remove_database()
        

    @classmethod
    def tearDownClass(cls):
        '''Remove the testing database'''
        print("Testing ENDED for ", cls.__name__)
        ENGINE.remove_database()

    def setUp(self):
        '''
        Populates the database
        '''
        pass

    def tearDown(self):
        '''
        Close underlying connection and remove all records from database
        '''
        self.connection.close()
        ENGINE.clear()

    def test_messages_table_schema(self):
        '''
        Checks that the messages table has the right schema.
        
        NOTE: Do not use Connection instance but
        call directly SQL.
        '''
        print('('+self.test_messages_table_created.__name__+')', \
                  self.test_messages_table_created.__doc__)

        ENGINE.create_tables()
         #This method load the initial values from forum_data_dump.sql
        ENGINE.populate_tables()
        #Creates a Connection instance to use the API
        self.connection = ENGINE.connect()
        con = self.connection.con
        with con:
            c = con.cursor()

            # Retrieve column information
            # Every column will be represented by a tuple with the following attributes:
            # (id, name, type, notnull, default_value, primary_key)
            c.execute('PRAGMA TABLE_INFO({})'.format('messages'))

            # collect names in a list
            result = c.fetchall()
            names = [tup[1] for tup in result]
            types = [tup[2] for tup in result]
            real_names=['message_id','title','body','timestamp','ip','timesviewed','reply_to','user_nickname','user_id','editor_nickname']
            real_types=['INTEGER','TEXT','TEXT','INTEGER','TEXT','INTEGER','INTEGER','TEXT','INTEGER','TEXT']  
            self.assertEquals(names, real_names)    
            self.assertEquals(types, real_types) 

            #Check that foreign keys are correctly set
            foreign_keys =[('users','user_id','user_id'),('users','user_nickname','nickname'),('messages','reply_to','message_id')]
            c.execute('PRAGMA FOREIGN_KEY_LIST({})'.format('messages'))
            result = c.fetchall()
            result_filtered = [(tup[2], tup[3],tup[4]) for tup in result]
            for tup in result_filtered:
                self.assertIn(tup,foreign_keys)

    def test_user_profile_table_schema(self):
        '''
        Checks that the messages table has the right schema.
        
        NOTE: Do not use Connection instance but
        call directly SQL.
        '''
        print('('+self.test_users_prifle_table_created.__name__+')', \
                  self.test_users_prifle_table_created.__doc__)

        ENGINE create_users_profile_table()
        #Creates a Connection instance to use the API
        self.connection = ENGINE.connect()
        con = self.connection.con
        with con:
            c = con.cursor()

            # Retrieve column information
            # Every column will be represented by a tuple with the following attributes:
            # (id, name, type, notnull, default_value, primary_key)
            c.execute('PRAGMA TABLE_INFO({})'.format('users_profile'))

            # collect names in a list
            result = c.fetchall()
            names = [tup[1] for tup in result]
            types = [tup[2] for tup in result]
            real_names=['user_id', 'firstname', 'lastname', 'email', 'website', 'picture', 'mobile', 'skype', 'age', 'residence', 'gender', 'signature', 'avatar']
            real_types=['INTEGER','TEXT','TEXT','TEXT','TEXT','TEXT','TEXT','TEXT','INTEGER','TEXT','TEXT','TEXT','TEXT']  
            self.assertEquals(names, real_names)    
            self.assertEquals(types, real_types) 

            #Check that foreign keys are correctly set
            foreign_keys =[('users','user_id','user_id')]
            c.execute('PRAGMA FOREIGN_KEY_LIST({})'.format('users_profile'))
            result = c.fetchall()
            result_filtered = [(tup[2], tup[3],tup[4]) for tup in result]
            for tup in result_filtered:
                self.assertIn(tup,foreign_keys)

    def test_messages_table_created(self):
        '''
        Checks that the table initially contains 20 messages (check
        forum_data_dump.sql). 
        
        NOTE: Do not use Connection instance but
        call directly SQL.
        '''
        print('('+self.test_messages_table_created.__name__+')', \
                  self.test_messages_table_created.__doc__)
        #This method load the initial values from forum_data_dump.sql
        ENGINE.populate_tables()
        #Creates a Connection instance to use the API
        self.connection = ENGINE.connect()
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM messages'
        #Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement
            cur.execute(query)
            users = cur.fetchall()
            #Assert
            self.assertEqual(len(users), INITIAL_SIZE)

    

if __name__ == '__main__':
    print('Start running database tests')
    unittest.main()
