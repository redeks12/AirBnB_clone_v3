#!/usr/bin/python3
""" holds class User"""
from hashlib import md5
from os import getenv
from typing import Any

import sqlalchemy
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

import models
from models.base_model import Base, BaseModel


class User(BaseModel, Base):
    """Representation of a user"""

    if models.storage_t == "db":
        __tablename__ = "users"
        email = Column(String(128), nullable=False)
        password = Column(String(128), nullable=False)
        first_name = Column(String(128), nullable=True)
        last_name = Column(String(128), nullable=True)
        places = relationship("Place", backref="user", cascade="all, delete")
        reviews = relationship("Review", backref="user", cascade="all, delete")
    else:
        email = ""
        password = ""
        first_name = ""
        last_name = ""

    def __init__(self, *args, **kwargs):
        """initializes user"""
        super().__init__(*args, **kwargs)

    def __setattr__(self, name, value) -> None:
        """sets the attribute on the password"""
        if name == "password":
            value = md5(value.encode()).hexdigest()
        return super().__setattr__(name, value)
