import json

from urllib.parse import unquote

from flask import Flask, request, Response, g, _request_ctx_stack, redirect, send_from_directory, jsonify, make_response
from flask_restful import Resource, Api, abort
from werkzeug.exceptions import NotFound,  UnsupportedMediaType

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

        #prettier output with jsonify, BOTH GIVES HEADERS STILL, MAYBE NOT A PROBLEM
        #return jsonify(speeds_db)

        return Response(json.dumps(speeds_db), 200, mimetype=JSON)


class Batteries(Resource):
    #@app.route('/wind/api/batteries/', methods=['GET'])
    def get(self):
        batteries_db = g.con.get_batteries()
        #make_response
        #return jsonify(batteries_db)
        return Response(json.dumps(batteries_db), 200, mimetype=JSON)


class Directions(Resource):
    #@app.route('/wind/api/directions/', methods=['GET'])
    def get(self):
        directions_db = g.con.get_directions()
        #make_response
        #return jsonify(directions_db)
        return Response(json.dumps(directions_db), 200, mimetype=JSON)


class Temperatures(Resource):
    #@app.route('/wind/api/temperatures/', methods=['GET'])
    def get(self):
        temperatures_db = g.con.get_temperatures()
        #make_response
        #return jsonify(temperatures_db)
        return Response(json.dumps(temperatures_db), 200, mimetype=JSON)


class Humidities(Resource):
    def get(self):
        humidities_db = g.con.get_humidities()
        #make_response
        #return jsonify(humidities_db)
        return Response(json.dumps(humidities_db), 200, mimetype=JSON)


class Humidity(Resource):
    #delete humidity value
    def delete(self, timestamp):
        if g.con.delete_humidity(timestamp):
            return "", 204
        else:
            return create_error_response(404, "Unknown timestamp", "There is no a humidity value with timestamp %s" % timestamp)

    #get humidity value
    def get(self, timestamp):
        humidity_db = g.con.get_humidity(timestamp)
        if not humidity_db:

            abort(404, message="There is no humidity data with timestamp %s" % timestamp,
                  resource_type="Humidity",
                  resource_url=request.path,
                  resource_id=timestamp)
        #return jsonify(humidity_db)
        return Response(json.dumps(humidity_db), 200, mimetype=JSON)

    #modifies the humidity value with @ timestamp
    def put(self, timestamp):
        '''
        REQUEST HUMIDITY VALUE:
        * Media type: JSON

        OUTPUT:
         * Returns 204 if the message is modified correctly
         * Returns 400 if the request is not well formed or it is
           empty.
         * Returns 404 if there is no timestamp with given value
         * Returns 415 if the input is not JSON.
         * Returns 500 if the database cannot be modified
        '''

        #eli napataaan urin perästä json ja puretaan se parametreiksi: timestamp ja value, ja passataan deebeelle
        if not g.con.contains_timestamp(timestamp):
            return create_error_response(404, "timestamp not found", "there is no humidity value with given timsstamp %s" %timestamp)

        if JSON != request.headers.get("Content-Type",""):
            return create_error_response(415, "UnsupportedMediaType", "Use a JSON compatible format")
        request_body = request.get_json(force=True)

        try:
            value = request_body["humidity"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "Be sure you include new humidity value")

        else:
            if not g.con.modify_humidity(timestamp, value):
                return create_error_response(500, "Internal error", "Humidity information for %s cannot be updated" % value)
            return "", 204


class Temperature(Resource):
    def delete(self, timestamp):
        if g.con.delete_temperature(timestamp):
            return "", 204
        else:
            return create_error_response(404, "Unknown timestamp", "There is no a temperature value with timestamp %s" % timestamp)

    def get(self, timestamp):
        temperature_db = g.con.get_temperature(timestamp)
        if not temperature_db:
            abort(404, message="There is no temperature data with timestamp %s" % timestamp,
                  resource_type="Temperature",
                  resource_url=request.path,
                  resource_id=timestamp)
        #return jsonify(temperature_db)
        return Response(json.dumps(temperature_db), 200, mimetype=JSON)

    def put(self, timestamp):
        '''
        REQUEST TEMPERATURE VALUE:
        * Media type: JSON

        OUTPUT:
         * Returns 204 if the message is modified correctly
         * Returns 400 if the request is not well formed or it is
           empty.
         * Returns 404 if there is no timestamp with given value
         * Returns 415 if the input is not JSON.
         * Returns 500 if the database cannot be modified
        '''

        #eli napataaan urin perästä json ja puretaan se parametreiksi: timestamp ja value, ja passataan deebeelle
        if not g.con.contains_timestamp(timestamp):
            return create_error_response(404, "timestamp not found", "there is no temperature value with given timsstamp %s" %timestamp)

        if JSON != request.headers.get("Content-Type",""):
            return create_error_response(415, "UnsupportedMediaType", "Use a JSON compatible format")
        request_body = request.get_json(force=True)

        try:
            value = request_body["temperature"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "Be sure you include new temperature value")

        else:
            if not g.con.modify_temperature(timestamp, value):
                return create_error_response(500, "Internal error", "Temperature information for %s cannot be updated" % value)
            return "", 204


class Speed(Resource):
    #@app.route('/wind/api/speed/<timestamp>', methods=['GET'])
    def get(self, timestamp):
        '''
        :param timestamp:
        '''
        #time = request.params('timestamp')
        #time = request.args.get('timestamp')

        speed_db = g.con.get_speed(timestamp)

        if not speed_db:
            abort(404, message="There is no speed data with timestamp %s" % timestamp,
                  resource_type="Speed",
                  resource_url=request.path,
                  resource_id=timestamp)
        #return jsonify(speed_db)
        return Response(json.dumps(speed_db), 200, mimetype=JSON)


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

    #Muotoillaan errorin palautus ja pistellään responsensa
    dump = {"resource_url": resource_url, "message": title, "info": message}
    return Response(json.dumps(dump), status_code, mimetype=JSON)

    #old response for later use...never
    #return make_response(jsonify(title, message, resource_url), status_code)


@app.errorhandler(404)
def resource_not_found(error):
    return create_error_response(404, "Resource not found", "This resource url does not exist!!!!")

@app.errorhandler(400)
def resource_not_found(error):
    return create_error_response(400, "Malformed input format", "The format of the input is incorrect")

@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(500, "Error", "The system has failed. Please, contact the administrator")

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
    Check if the connection is created. It might be exception appear before
    the connection is created.
    """

    if hasattr(g, "con"):
        g.con.close()


#routes for resources

api.add_resource(Speeds, '/wind/api/speeds/', endpoint='speeds')
api.add_resource(Batteries, '/wind/api/batteries/', endpoint='batteries')
api.add_resource(Temperatures, '/wind/api/temperatures/', endpoint='temperature')
api.add_resource(Directions, '/wind/api/directions/', endpoint='directions')
api.add_resource(Humidities, '/wind/api/humidities/', endpoint='humidities')

api.add_resource(Temperature, '/wind/api/temperature/<timestamp>', endpoint='temperature')
api.add_resource(Speed, '/wind/api/speed/<timestamp>', endpoint='speed')
api.add_resource(Humidity, '/wind/api/humidity/<timestamp>', endpoint='humidity')


#run app
if __name__ == '__main__':
    app.run(debug=True)

