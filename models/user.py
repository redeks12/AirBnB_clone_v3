#!/usr/bin/python3
""" holds class User"""
from typing import Any
import models
from models.base_model import BaseModel, Base
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from hashlib import md5


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

    def __setattr__(self, __name: str, __value: Any) -> None:
        """sets the attribute on the password"""
        if __name == "password":
            __value = md5(__value).hexdigest()
        return super().__setattr__(__name, __value)
