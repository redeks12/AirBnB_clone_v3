#!/usr/bin/python3
"""handles all default RESTFul API actions"""
from flasgger.utils import swag_from
from flask import abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.city import City
from models.place import Place
from models.state import State
from models.user import User
from models.amenity import Amenity


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
    unique_list = []
    seen = set()
    places_obs = []
    body = request.get_json()
    newest = []

    if not body:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    if len(body) == 0:
        places = storage.all(Place).values()
        return jsonify([cit.to_dict() for cit in places])

    if "states" in body:
        for state in body["states"]:
            st = storage.get(State, state)
            for city in st.cities:
                cit = storage.get(City, city.id)
                for pl in cit.places:
                    places_obs.append(pl)

    if "cities" in body:
        for city in body["cities"]:
            citt = storage.get(City, city)
            for ci in citt.places:
                places_obs.append(ci)

    if "amenities" in body:
        there = True
        if places_obs:
            ttt = places_obs
        else:
            ttt = storage.all(Place).values()
        for pl in ttt:
            for amenity in body["amenities"]:
                amm = storage.get(Amenity, amenity)
                if amm not in pl.amenities:
                    there = False
            if there:
                newest.append(pl)

    if newest:
        pls = newest
    else:
        pls = places_obs

    pls = [p.to_dict() for p in pls]

    for d in pls:
        d_tuple = tuple(sorted(d.items()))

        print(d)
        print("---------------------------------------")
        print(d_tuple)
        if d_tuple not in seen:
            unique_list.append(d)
            seen.add(d_tuple)

    return jsonify(unique_list)
