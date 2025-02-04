#!/usr/bin/python3
"""handles all default RESTFul API actions"""
from flasgger.utils import swag_from
from flask import Flask, abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.state import State


@app_views.route("/states", methods=["GET"], strict_slashes=False)
@swag_from("documentation/state/get.yml", methods=["GET"])
def get_all_states():
    """
    Retrieves the list of all State objects
    """
    all_states = storage.all(State).values()
    list_states = []
    for state in all_states:
        list_states.append(state.to_dict())
    return jsonify(list_states)


@app_views.route("/states/<string:state_id>", methods=["GET"], strict_slashes=False)
@swag_from("documentation/state/get_id.yml", methods=["GET"])
def get_state_id(state_id):
    """Retrieves a specific state by id"""
    state = storage.get(State, state_id)
    if state is None:
        abort(404)
    return jsonify(state.to_dict())


@app_views.route("/states/<string:state_id>", methods=["DELETE"], strict_slashes=False)
@swag_from("documentation/state/delete.yml", methods=["DELETE"])
def delete_state(state_id):
    """Deletes a  state by id"""
    state = storage.get(State, state_id)
    if state is None:
        abort(404)
    state.delete()
    storage.save()
    return (jsonify({}), 200)


@app_views.route("/states", methods=["POST"], strict_slashes=False)
@swag_from("documentation/state/post_state.yml", methods=["POST"])
def post_state():
    """
    Creates a State
    """
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    if "name" not in request.get_json():
        return make_response(jsonify({"error": "Missing name"}), 400)

    body = request.get_json()
    instance = State(**body)
    instance.save()
    return (jsonify(instance.to_dict()), 201)


@app_views.route("/states/<string:state_id>", methods=["PUT"], strict_slashes=False)
@swag_from("documentation/state/put.yml", methods=["PUT"])
def put_state(state_id):
    """PUTs a  state by id"""
    state = storage.get(State, state_id)
    if state is None:
        abort(404)
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    ignore = ["id", "created_at", "updated_at"]
    for key, val in dict(request.get_json()).items():
        if key not in ignore:
            setattr(state, key, val)

    storage.save()

    return jsonify(state.to_dict())
