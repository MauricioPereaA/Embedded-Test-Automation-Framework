# -*- coding: utf-8 -*-
from .sockets import SocketInterface, JsonSocketInterface

from DTAF.factory import Factory

Factory.register("SocketInterface", SocketInterface)
Factory.register("JsonSocketInterface", JsonSocketInterface)
