import json

from urllib.parse import unquote

from flask import Flask, request, Response, g, _request_ctx_stack, redirect, send_from_directory, jsonify, make_response
from flask_restful import Resource, Api, abort
from werkzeug.exceptions import NotFound,  UnsupportedMediaType

#from wind.utils import RegexConverter
import dbhandler

#Constants for formats
JSON = "application/json"


#for testing
app = Flask(__name__)
app.config.update({"Engine": dbhandler.Engine()})
api = Api(app)
#@app.route('/')
#def index():
#    return "Hello, World!"
#

#for later use
'''
#Define the application and the api
app = Flask(__name__, static_folder="static", static_url_path="/.")
app.debug = True
# Set the database Engine. In order to modify the database file (e.g. for
# testing) provide the database path   app.config to modify the
#database to be used (for instance for testing)

#Start the RESTful API.
api = Api(app)
'''

#Define the resources
class Speeds(Resource):
    '''
    Implements resource speeds
    '''

    #@app.route('/wind/api/speeds/', methods=['GET'])
    def get(self):
        '''
        get all speeds

        INPUT params:
            optional start, end.

        '''
        #extract speeds from db
        speeds_db = g.con.get_speeds()
        make_response()
        return jsonify(speeds_db)


"""
    ENVELOPE SHAIT HERE IF NEEDED....NOPE
    envelope = []
    for speed in speeds_db:
        timestamp = speed["timestamp"],
        value = speed["speed"]
        envelope.append(timestamp, value)
        envelope.append(timestamp)
    
    return Response(json.dumps(envelope), status_code, mimetype=MASON+";"+ERROR_PROFILE)
    return Response(json.dumps(speeds_db))
"""

class Batteries(Resource):
    #@app.route('/wind/api/batteries/', methods=['GET'])
    def get(self):
        batteries_db = g.con.get_batteries()
        make_response
        return jsonify(batteries_db)


class Directions(Resource):
    #@app.route('/wind/api/directions/', methods=['GET'])
    def get(self):
        directions_db = g.con.get_directions()
        make_response
        return jsonify(directions_db)


class Temperatures(Resource):
    #@app.route('/wind/api/temperatures/', methods=['GET'])
    def get(self):
        temperatures_db = g.con.get_temperatures()
        make_response
        return jsonify(temperatures_db)


class Speed(Resource):
    #@app.route('/wind/api/speed/', methods=['GET'])
    #@app.route('/wind/api/speed/<timestamp>', methods=['GET'])
    def get(self, timestamp):
        '''
        :param timestamp:
        '''
        #time = request.params('timestamp')
        #time = request.args.get('timestamp')
        speed_db = g.con.get_speed(timestamp)

        if not speed_db:
            #why not 404, still 200?--> CHECK
            #return create_error_response(400, "Wrong request format", "Be sure you include message title and body")

            abort(404, message="There is no speed data with timestamp %s" % timestamp,
                  resource_type="Speed",
                  resource_url=request.path,
                  resource_id=timestamp)

        return jsonify(speed_db)



'''
#@app.route('/wind/api/speed/<timestamp>/<speed>', methods=['POST'])
@app.route('/wind/api/speed/<timestamp>', methods=['POST'])
#def add_speed(timestamp):
def add_speed(timestamp):
    speed_db = g.con.add_speed(timestamp)

    return jsonify(speed_db)
'''



#still working on this
@app.route('/wind/api/speed/<timestamp>', methods=['DELETE'])
def delete_speed(timestamp):
    if g.con.delete_speed(timestamp):
        return "", 204
    else:
        return create_error_response(404, "Unknown timestamp",
                                     "There is no a speed value with timestamp %s"
                                     % nickname)




#fix errorr händling, should return correct codes to flask too? return RESPONSE DO THIS
#ERROR HANDLERS Borrowed slightly from exercises...
def create_error_response(status_code, title, message):
    """
    : param integer status_code: The HTTP status code of the response
    : param str title: A short description of the problem
    : param message: A long description of the problem
    : rtype:: py: class:`flask.Response`
    """

    resource_url = None
    #We need to access the context in order to access the request.path
    ctx = _request_ctx_stack.top
    if ctx is not None:
        resource_url = request.path
    ##envelope = MasonObject(resource_url=resource_url)
    ##envelope.add_error(title, message)

    return make_response(jsonify(title, message, resource_url), status_code)

@app.errorhandler(404)
def resource_not_found(error):
    return create_error_response(404, "Resource not found",
                                 "This resource url does not exist")

@app.errorhandler(400)
def resource_not_found(error):
    return create_error_response(400, "Malformed input format",
                                 "The format of the input is incorrect")

@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(500, "Error",
                    "The system has failed. Please, contact the administrator")

@app.before_request
def connect_db():
    """
    Creates a database connection before the request is proccessed.

    The connection is stored in the application context variable flask.g .
    Hence it is accessible from the request object.
    """

    g.con = app.config["Engine"].connect()

#HOOKS
@app.teardown_request
def close_connection(exc):
    """
    Closes the database connection
    Check if the connection is created. It migth be exception appear before
    the connection is created.
    """

    if hasattr(g, "con"):
        g.con.close()


#routes: should get class as a first param instead of method?

#api.add_resource(Speeds, "/wind/api/speeds/", endpoint="speeds")
#api.add_resource(get_speed, "/wind/api/speed:timestamp", endpoint="speed")
api.add_resource(Speeds, '/wind/api/speeds/')
api.add_resource(Batteries, '/wind/api/batteries/')
api.add_resource(Temperatures, '/wind/api/temperatures/')
api.add_resource(Directions, '/wind/api/directions/')

api.add_resource(Speed, '/wind/api/speed/<timestamp>')


#run app
if __name__ == '__main__':
    app.run(debug=True)
