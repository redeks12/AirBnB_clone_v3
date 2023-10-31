#!/usr/bin/python3
""" objects that handle all default RestFul API actions for Users """
from flasgger.utils import swag_from
from flask import Flask, abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.user import User


@app_views.route("/users", methods=["GET"], strict_slashes=False)
@swag_from("documentation/user/get.yml", methods=["GET"])
def get_all_users():
    """Retrieves a list of all users"""
    all_users = storage.all(User).values()
    list_users = []
    for user in all_users:
        list_users.append(user.to_dict())
    return jsonify(list_users)


@app_views.route("/users/<string:user_id>", methods=["GET"], strict_slashes=False)
@swag_from("documentation/user/get_id.yml", methods=["GET"])
def get_a_user(user_id):
    """Retrieves a user by id"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    return jsonify(user.to_dict())


@app_views.route("/users/<string:user_id>", methods=["DELETE"], strict_slashes=False)
@swag_from("documentation/user/delete.yml", methods=["DELETE"])
def delete_user(user_id):
    """Deletes a user by id"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    user.delete()
    storage.save()
    return jsonify({})


@app_views.route("/users/", methods=["POST"], strict_slashes=False)
@swag_from("documentation/user/post.yml", methods=["POST"])
def create_user():
    """create a new user"""
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    if "email" not in request.get_json():
        return make_response(jsonify({"error": "Missing email"}), 400)
    if "password" not in request.get_json():
        return make_response(jsonify({"error": "Missing password"}), 400)
    body = request.get_json()
    instance = User(**body)
    instance.save()
    return (jsonify(instance.to_dict()), 201)


@app_views.route("/users/<string:user_id>", methods=["PUT"], strict_slashes=False)
@swag_from("documentation/user/put.yml", methods=["PUT"])
def put_user(user_id):
    """Update a user"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)

    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    for key, value in request.get_json().items():
        if key not in ["id", "email", "created_at", "updated"]:
            setattr(user, key, value)

    storage.save()
    return jsonify(user.to_dict())
