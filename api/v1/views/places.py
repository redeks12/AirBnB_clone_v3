#!/usr/bin/python3
"""handles all default RESTFul API actions"""
from flasgger.utils import swag_from
from flask import abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.state import State
from models.user import User


@app_views.route(
    "/cities/<string:city_id>/places", methods=["GET"], strict_slashes=False
)
def get_place_cities(city_id):
    """return a list of places in the city object"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    place = city.places
    if not place:
        abort(404)
    else:
        return jsonify([cit.to_dict() for cit in place])


@app_views.route("/places/<string:place_id>", methods=["GET"], strict_slashes=False)
@swag_from("documentation/place/get_id.yml", methods=["GET"])
def get_place_id(place_id):
    """Retrieves a specific place by id"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route("/places/<string:place_id>", methods=["DELETE"], strict_slashes=False)
@swag_from("documentation/place/delete.yml", methods=["DELETE"])
def delete_place(place_id):
    """Deletes a  place by id"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    place.delete()
    storage.save()
    return jsonify({})


@app_views.route(
    "/cities/<string:city_id>/places", methods=["POST"], strict_slashes=False
)
@swag_from("documentation/place/post_place.yml", methods=["POST"])
def post_place(city_id):
    """
    Creates a City object
    """
    if not storage.get(City, city_id):
        abort(404)
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    if "name" not in request.get_json():
        return make_response(jsonify({"error": "Missing name"}), 400)

    if "user_id" not in request.get_json():
        return make_response(jsonify({"error": "Missing user_id"}), 400)
    body = request.get_json()

    if not storage.get(User, body["user_id"]):
        abort(404)

    instance = Place(**body)
    instance.city_id = city_id
    instance.save()
    return (jsonify(instance.to_dict()), 201)


@app_views.route("/places/<string:place_id>", methods=["PUT"], strict_slashes=False)
@swag_from("documentation/place/put_place.yml", methods=["PUT"])
def put_place(place_id):
    """put place change the values of the place"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    for key, val in request.get_json().items():
        if key not in ["id", "user_id", "city_id", "created_at", "updated_at"]:
            setattr(place, key, val)

    storage.save()

    return jsonify(place.to_dict())


@app_views.route("/places_search", methods=["POST"], strict_slashes=False)
@swag_from("documentation/places/search_place.yml", methods=["POST"])
def search_place():
    """
    Creates a City object
    """
    if request.get_json() is not None:
        params = request.get_json()
        states = params.get("states", [])
        cities = params.get("cities", [])
        amenities = params.get("amenities", [])
        amenity_objects = []
        for amenity_id in amenities:
            amenity = storage.get(Amenity, amenity_id)
            if amenity:
                amenity_objects.append(amenity)
        if states == cities == []:
            places = storage.all(Place).values()
        else:
            places = []
            for state_id in states:
                state = storage.get(State, state_id)
                state_cities = state.cities
                for city in state_cities:
                    if city.id not in cities:
                        cities.append(city.id)
            for city_id in cities:
                city = storage.get(City, city_id)
                for place in city.places:
                    places.append(place)
        confirmed_places = []
        for place in places:
            place_amenities = place.amenities
            confirmed_places.append(place.to_dict())
            for amenity in amenity_objects:
                if amenity not in place_amenities:
                    confirmed_places.pop()
                    break
        jj = []
        for conf in confirmed_places:
            del conf["amenities"]
            jj.append(conf)
        return jsonify(jj)
    else:
        return make_response(jsonify({"error": "Not a JSON"}), 400)


# curl -X POST http://0.0.0.0:5000/api/v1/places_search -H "Content-Type: application/json" -d '{"states": ["d2398800-dd87-482b-be21-50a3063858ad", "0e391e25-dd3a-45f4-bce3-4d1dea83f3c7"], "cities": ["14e49d0b-7363-40e3-8854-a89e96481f67", "3ffd4ed8-b645-46bc-8bc3-40c0e51f2b44", "c5bbe76a-87f0-44f8-8b4d-e805e6cd757c"], "amenities": ["98850f9d-0835-46df-90e3-5fef156724a0"]}' -vvv
