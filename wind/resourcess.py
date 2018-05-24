# -*- coding: utf-8 -*-
import json

from urllib.parse import unquote

from flask import Flask, request, g, _request_ctx_stack, redirect, send_from_directory, jsonify, make_response
from flask_restful import Resource, Api, abort

from flask_hal import HALResponse as Response
from flask_hal.link import Collection, Link, Self

from werkzeug.exceptions import NotFound,  UnsupportedMediaType

import dbhandler

#Constants for formats
#input
JSON = "application/json"

#output
JSONHAL = "application/hal+json"

#for testing
#app = Flask(__name__)
app = Flask(__name__, static_folder="static", static_url_path="/.")
app.debug = True
app.config.update({"Engine": dbhandler.Engine()})

#for hal
app.response_class = Response

#atart api
api = Api(app)


#for later use maybe...
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
class Device(Resource):
    '''
    implements resource devices
    '''
    def get(self, id):
        '''
        Get device with given id from db
        :param id
        '''

        device_db = g.con.get_device(id)

        if not device_db:
            return create_error_response(404, "No device found",
                                     'There is no device info on given device id %s' % id, 'Device')

        #create collection of links
        links = Collection(
            Self(),
            Link('list', '/wind/api/devices/'),
            Link('data:speeds-all', request.path + '/speeds/')
        )

        #links to dict
        l = links.to_dict()

        #combine links and speed to one dict to be returned in response
        #dump = dict(list(device_db.items()) + list(l.items()))
        dump = dict(list(l.items()) + list(device_db.items()))

        #return Response
        return Response(json.dumps(dump), 200, mimetype=JSONHAL)


class Devices(Resource):
    '''
    implements resource devices
    '''

    def get(self):
        '''
        Get all devices available
        '''

        devices_db = g.con.get_devices()

        if not devices_db:
            return create_error_response(404, "No devices found",
                                     'There is no devices in DB', 'Devices')

        # create collection of links
        links = Collection(
            Self(),
            Link('device', '/wind/api/device/{id}')
        )

        # links to dict
        l = links.to_dict()

        # combine links and speed to one dict and add items where the actual values are
        dump = l
        dump.update({'items': devices_db})

        # return Response
        return Response(json.dumps(dump), 200, mimetype=JSONHAL)


class Speed(Resource):
    '''
    Implements resource speed
    '''
    def get(self, id, timestamp):
        '''
        :param id, timestamp:
        '''

        speed_db = g.con.get_speed(id, timestamp)

        if not speed_db:
             return create_error_response(404, "No speed found",
                                'There is no speed data on device id %s with timestamp %s' % (id, timestamp), 'Speed')

        #create collection of links
        links = Collection(
            Self(),
            Link('device', '/wind/api/device/' + id + '/'),
            Link('list', '/wind/api/device/' + id + '/speeds/'),
            Link('temperatures-all', '/wind/api/device/' + id + '/temperatures/')
        )

        #links to dict
        l = links.to_dict()

        #combine links and speed to one dict
        dump = dict(list(l.items()) + list(speed_db.items()))

        #return Response
        return Response(json.dumps(dump), 200, mimetype=JSONHAL)


class Battery(Resource):
    '''
    Implements resource battery
    '''
    def get(self, id, timestamp):
        '''
        :param id, timestamp:
        '''

        battery_db = g.con.get_battery(id, timestamp)

        if not battery_db:
            return create_error_response(404, "No battery data found",
                                         'There is no battery data on device id %s with timestamp %s' % (id, timestamp),
                                         'Battery')

        #create collection of links
        links = Collection(
            Self(),
            Link('device', '/wind/api/device/' + id + '/'),
            Link('list', '/wind/api/device/' + id + '/batteries/')
            # last one, no links to other resources except device and collection
        )

        #links to dict
        l = links.to_dict()

        #combine links and speed to one dict
        dump = dict(list(l.items()) + list(battery_db.items()))

        #return Response
        return Response(json.dumps(dump), 200, mimetype=JSONHAL)


class Direction(Resource):
    '''
    Implements resource direction
    '''
    def get(self, id, timestamp):
        '''
        :param id, timestamp:
        '''

        direction_db = g.con.get_direction(id, timestamp)

        if not direction_db:
            return create_error_response(404, "No direction data found",
                                         'There is no direction data on device id %s with timestamp %s' % (id, timestamp),
                                         'Direction')

        #create collection of links
        links = Collection(
            Self(),
            Link('device', '/wind/api/device/' + id + '/'),
            Link('list', '/wind/api/device/' + id + '/directions/'),
            Link('all-batteries', '/wind/api/device/' + id + '/batteries/')
        )

        #links to dict
        l = links.to_dict()

        #combine links and speed to one dict
        dump = dict(list(l.items()) + list(direction_db.items()))

        #return Response
        return Response(json.dumps(dump), 200, mimetype=JSONHAL)


class Speeds(Resource):
    '''
    Implements resource speeds
    '''

    def get(self, id):
        '''
        get all speeds
        params: id

        '''
        #extract speeds from db
        speeds_db = g.con.get_speeds(id)
        if not speeds_db:
            return create_error_response(404, "No speeds found",
                                     'There is no speeds data on given device id %s' % id, 'Speeds')

        # create collection of links
        links = Collection(
            Self(),
            Link('device', '/wind/api/device/' + id + '/'),
            Link('speed', '/wind/api/device/' + id + '/speed/{timestamp}')
        )

        # links to dict
        l = links.to_dict()

        # combine links and speed to one dict
        dump = l
        dump.update({'items': speeds_db})

        # return Response
        return Response(json.dumps(dump), 200, mimetype=JSONHAL)


class Batteries(Resource):
    def get(self, id):
        '''
        get all battery values on device
        :param id:
        '''

        batteries_db = g.con.get_batteries(id)

        if not batteries_db:
            return create_error_response(404, "No batteries found",
                                     'There is no batteries data on given device id %s' % id, 'Batteries')

        # create collection of links
        links = Collection(
            Self(),
            Link('device', '/wind/api/device/' + id + '/'),
            Link('battery', '/wind/api/device/' + id + '/battery/{timestamp}')
        )

        # links to dict
        l = links.to_dict()

        # combine links and speed to one dict
        dump = l
        dump.update({'items': batteries_db})

        # return Response
        return Response(json.dumps(dump), 200, mimetype=JSONHAL)


class Directions(Resource):
    def get(self, id):
        directions_db = g.con.get_directions(id)

        if not directions_db:
            return create_error_response(404, "No directions found",
                                     'There is no directions data on given device id %s' % id, 'Diretions')

        # create collection of links
        links = Collection(
            Self(),
            Link('device', '/wind/api/device/' + id + '/'),
            Link('direction', '/wind/api/device/' + id + '/direction/{timestamp}')
        )

        # links to dict
        l = links.to_dict()

        # combine links and speed to one dict
        dump = l
        dump.update({'items': directions_db})

        # return Response
        return Response(json.dumps(dump), 200, mimetype=JSONHAL)


class Temperatures(Resource):
    def get(self, id):
        temperatures_db = g.con.get_temperatures(id)

        if not temperatures_db:
            return create_error_response(404, "No temperatures found",
                                         'There is no temperatures data on given device id %s' % id, 'Temperatures')

        # create collection of links
        links = Collection(
            Self(),
            Link('device', '/wind/api/device/' + id + '/'),
            Link('temperature', '/wind/api/device/' + id + '/temperature/{timestamp}')
        )

        # links to dict
        l = links.to_dict()

        # combine links and speed to one dict
        dump = l
        dump.update({'items': temperatures_db})

        # return Response
        return Response(json.dumps(dump), 200, mimetype=JSONHAL)


class Humidities(Resource):
    def get(self, id):
        humidities_db = g.con.get_humidities(id)

        if not humidities_db:
            return create_error_response(404, "No humidities found",
                                     'There is no humidities data on given device id %s' % id, 'Humidities')

        # create collection of links
        links = Collection(
            Self(),
            Link('device', '/wind/api/device/' + id + '/'),
            Link('humidity', '/wind/api/device/' + id + '/humidity/{timestamp}')
        )

        # links to dict
        l = links.to_dict()

        # combine links and speed to one dict
        dump = l
        dump.update({'items': humidities_db})

        # return Response
        return Response(json.dumps(dump), 200, mimetype=JSONHAL)


class Humidity(Resource):
    #delete humidity value
    def delete(self, id, timestamp):
        if g.con.delete_humidity(id, timestamp):
            return "", 204
        else:
            return create_error_response(404, "Unknown timestamp", "There is no a humidity value with timestamp %s" % timestamp + " on given device id", 'Humidity')

    #get humidity value
    def get(self, id, timestamp):
        humidity_db = g.con.get_humidity(id, timestamp)
        if not humidity_db:
            return create_error_response(404, "No humidity found",
                                         'There is no humidity data on device id %s with timestamp %s' % (id, timestamp),
                                         'Humidity')

        #create collection of links
        links = Collection(
            Self(),
            Link('device', '/wind/api/device/' + id + '/'),
            Link('list', '/wind/api/humidities/'),
            Link('directions-all', '/wind/api/device/' + id + '/directions/')
        )

        #links to dict
        l = links.to_dict()

        #combine links and speed to one dict
        dump = dict(list(l.items()) + list(humidity_db.items()))

        #return Response
        return Response(json.dumps(dump), 200, mimetype=JSONHAL)

    #modifies the humidity value with @ timestamp
    def put(self, id, timestamp):
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
        if not g.con.contains_timestamp(id, timestamp):
            return create_error_response(404, "timestamp not found", "there is no humidity value with given timsstamp %s" %timestamp + " on given device id", 'Humidity')

        if JSON != request.headers.get("Content-Type",""):
            return create_error_response(415, "UnsupportedMediaType", "Use a JSON compatible format", 'Humidity')
        request_body = request.get_json(force=True)

        try:
            value = request_body["humidity"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "Be sure you include new humidity value", 'Humidity')

        else:
            if not g.con.modify_humidity(id, timestamp, value):
                return create_error_response(500, "Internal error", "Humidity information for %s cannot be updated" % value, 'Humidity')
            return "", 204


    def post(self, id, timestamp):
        '''
        Adds a a NEW humidity and timestamp. 
        If timestamp exists, but no humidity value, update instead.

        REQUEST ENTITY BODY:
         * Media type: JSON:

        RESPONSE STATUS CODE:
         * Returns 201 + the url of the new resource in the Location header
         * Returns 200 if the resource was updated, not created --> means that there was timestamp already, but no value
         * Returns 400 if the value is not well formed or is empty.
         * Returns 409 if there is already humidity value in with given timestamp.
         * Returns 415 if the format of the response is not json
         * Returns 500 if the message could not be added to database.
        '''

        #if there is already value on given timestamp
        column = 'humidity'
        if g.con.contains_value(id, timestamp, column):
            return create_error_response(409, "Humidity value exists", "There is already humidity value with given timestamp %s" %timestamp, 'Humidity')

        if JSON != request.headers.get("Content-Type", ""):
            return create_error_response(415, "UnsupportedMediaType", "Use a JSON compatible format", 'Humidity')
        request_body = request.get_json(force=True)

        try:
            value = request_body["humidity"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "Be sure you include new humidity value", 'Humidity')

        else:
            dump = g.con.add_humidity(id, timestamp, value)
            if dump is None:
                return create_error_response(500, "Internal error", "Humidity information for %s cannot be updated" % value, 'Humidity')

            #if value was only modified (because timestamp was already there)
            elif dump is True:
                return "", 200
            else:
                #The Location header should have an URL that points to the new resource
                # and you can return an entity with the details also.
                #return Response(json.dumps(dump), 201, mimetype=JSONHAL)
                return Response(status=201, headers={"URL": api.url_for(Humidity, id=id, timestamp=timestamp)})


class Temperature(Resource):
    def delete(self, id, timestamp):
        if g.con.delete_temperature(id, timestamp):
            return "", 204
        else:
            return create_error_response(404, "Unknown timestamp", "There is no a temperature value with timestamp %s" % timestamp + " on given device id", 'Temperature')

    def get(self, id, timestamp):
        temperature_db = g.con.get_temperature(id, timestamp)
        if not temperature_db:
            return create_error_response(404, "No temperature found",
                                         'There is no temperature data on device id %s with timestamp %s' % (id, timestamp),
                                         'Temperature')


        #create collection of links
        links = Collection(
            Self(),
            Link('device', '/wind/api/device/' + id + '/'),
            Link('list', '/wind/api/device/' + id + '/temperatures/'),
            Link('humidities-all', '/wind/api/device/' + id + '/humidities/')
        )

        #links to dict
        l = links.to_dict()

        #combine links and speed to one dict
        dump = dict(list(l.items()) + list(temperature_db.items()))

        #return Response
        return Response(json.dumps(dump), 200, mimetype=JSONHAL)

    #edit old value
    def put(self, id, timestamp):
        '''
        REQUEST TEMPERATURE VALUE:
        * Media type: JSON

        OUTPUT:
         * Returns 204 if the temperature is modified correctly
         * Returns 400 if the request is not well formed or it is
           empty.
         * Returns 404 if there is no timestamp with given value
         * Returns 415 if the input is not JSON.
         * Returns 500 if the database cannot be modified
        '''

        #Check, that timestamp is there, check that format is correct, get value from url (json), pass to db
        if not g.con.contains_timestamp(id, timestamp):
            return create_error_response(404, "timestamp not found",
                                         "there is no temperature value with given timsstamp %s"
                                         %timestamp + " on given device id", 'Temperature')

        if JSON != request.headers.get("Content-Type",""):
            return create_error_response(415, "UnsupportedMediaType", "Use a JSON compatible format", 'Temperature')
        request_body = request.get_json(force=True)

        try:
            value = request_body["temperature"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "Be sure you include new temperature value", 'Temperature')

        else:
            if not g.con.modify_temperature(id, timestamp, value):
                return create_error_response(500, "Internal error", "Temperature information for %s cannot be updated" % value, 'Temperature')
            return "", 204


    def post(self, id, timestamp):
        '''
        Adds a a NEW temperature and timestamp. 
        If timestamp exists, but no temperature value, update instead.

        REQUEST ENTITY BODY:
         * Media type: JSON:

        RESPONSE STATUS CODE:
         * Returns 201 + the url of the new resource in the Location header
         * Returns 200 if the resource was updated, not created --> means that there was timestamp already, but no value
         * Returns 400 if the value is not well formed or is empty.
         * Returns 409 if there is already temperature value in with given timestamp.
         * Returns 415 if the format of the response is not json
         * Returns 500 if the message could not be added to database.
        '''

        # check if there is already value on given timestamp
        column = 'temperature'
        if g.con.contains_value(id, timestamp, column):
            return create_error_response(409, "temperature value exists", "There is already temperature value with given timestamp %s" %timestamp, 'Temperature')

        if JSON != request.headers.get("Content-Type", ""):
            return create_error_response(415, "UnsupportedMediaType", "Use a JSON compatible format", 'Temperature')
        request_body = request.get_json(force=True)

        try:
            value = request_body["temperature"]
        except KeyError:
            return create_error_response(400, "Wrong request format", "Be sure you include new temperature value", 'Temperature')

        else:
            dump = g.con.add_temperature(id, timestamp, value)
            if dump is None:
                return create_error_response(500, "Internal error", "temperature information for %s cannot be updated" % value, 'Temperature')

            #if value was only modified (because timestamp was already there)
            elif dump is True:
                return "", 200
            else:
                #The Location header should have an URL that points to the new resource
                # and you can return an entity with the details also.
                #return Response(json.dumps(dump), 201, mimetype=JSONHAL)
                return Response(status=201, headers={"URL": api.url_for(Temperature, id=id, timestamp=timestamp)})


# ERROR HANDLERS Borrowed slightly from exercises...all errors go through this method --> response is application/hal+json
def create_error_response(status_code, title, message, resource_type=None):
    """
    : param integer status_code: The HTTP status code of the response
    : param str title: A short description of the problem
    : param message: A long description of the problem
    : rtype:: py: class:`flask.Response`
    """

    resource_url = None
    # We need the context in order to access the request.path
    ctx = _request_ctx_stack.top
    if ctx is not None:
        resource_url = request.path

    # Muotoillaan errorin palautus ja pistellään responsensa
    dump = {"resource_url": resource_url, "resource_type": resource_type, "message": title, "info": message}
    return Response(json.dumps(dump), status_code, mimetype=JSONHAL)


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

# HOOKS
@app.teardown_request
def close_connection(exc):
    """
    Closes the database connection
    Check if the connection is created. It might be exception appear before
    the connection is created.
    """

    if hasattr(g, "con"):
        g.con.close()


# routes for resources

# collections
api.add_resource(Speeds, '/wind/api/device/<id>/speeds/', endpoint='speeds')
api.add_resource(Batteries, '/wind/api/device/<id>/batteries/', endpoint='batteries')
api.add_resource(Temperatures, '/wind/api/device/<id>/temperatures/', endpoint='temperatures')
api.add_resource(Directions, '/wind/api/device/<id>/directions/', endpoint='directions')
api.add_resource(Humidities, '/wind/api/device/<id>/humidities/', endpoint='humidities')
api.add_resource(Devices, '/wind/api/devices/', endpoint='devices')


api.add_resource(Speed, '/wind/api/device/<id>/speed/<timestamp>', endpoint='speed')
api.add_resource(Temperature, '/wind/api/device/<id>/temperature/<timestamp>', endpoint='temperature')
api.add_resource(Humidity, '/wind/api/device/<id>/humidity/<timestamp>', endpoint='humidity')
api.add_resource(Device, '/wind/api/device/<id>', endpoint='device')
api.add_resource(Direction, '/wind/api/device/<id>/direction/<timestamp>', endpoint='direction')
api.add_resource(Battery, '/wind/api/device/<id>/battery/<timestamp>', endpoint='battery')


#run app
if __name__ == '__main__':
    app.run(debug=True)

