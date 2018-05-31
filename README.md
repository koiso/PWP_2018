INSTALL
-------

Python version 3.5 / 3.6 supported

To get the necessary Python modules:

pip install flask

pip install flask-restful

pip install flask-restful-hal

pip install flask-cors

OR depending the python version & OS & Installation


python -m pip install flask

python -m pip install flask-restful

python -m pip install flask-restful-hal

python - pip install flask-cors


RUNNING THE SERVER
------------------

In the project wind folder:

python resourcess.py


RUNNING THE CLIENT
------------------

In the client folder:

Open the index.html file with your web browser


TESTING
-------

DB unit testing is made by python + unittest library

The test will run from root folder with command: python DB_unittest.py


Functional test for API need to have pyresttest installed

python -m pip install pyresttest

The test will run from root folder with command: pyresttest.py http://localhost:5000 func_test.yaml

more info and help for installation can be found from: 
https://github.com/svanoort/pyresttest

You should run the DB_unittest before resttest to reset the state of DB
