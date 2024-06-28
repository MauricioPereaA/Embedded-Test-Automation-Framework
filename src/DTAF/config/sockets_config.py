# -*- coding: utf-8 -*-
from DTAF.config import Config
import socket

g_error_msg: tuple[str] = (
    "SOCKET :: Invalid model. Unknown issue.",  # 0
    "SOCKET :: Invalid model. Missing required entry. entry: `{entry}`.",  # 1
    "SOCKET :: Invalid model. invalid protocol. protocol: `{protocol}`.",  # 2
    "SOCKET :: Invalid model. wrong keyname. keyname: {keynamex}",  # 3
    "SOCKET :: Invalid model. missing value. name: `{value}`",  # 4
    "SOCKET :: ",  # X
)
protocols_names: dict[str] = {
    "ipv4": {
        "AF_INET": socket.AF_INET,
        "SOCK_DGRAM": socket.SOCK_DGRAM,
        "IPPROTO_UDPLITE": socket.IPPROTO_UDP
    },
    "ipv6": {
        "AF_INET6": socket.AF_INET6,
        "SOCK_DGRAM": socket.SOCK_DGRAM,
        "IPPROTO_UDPLITE": socket.IPPROTO_UDP,
    },
    "protocol": {
        "SOCK_STREAM": socket.SOCK_STREAM,
        "SOCK_DGRAM": socket.SOCK_DGRAM,
        "SOCK_RAW": socket.SOCK_RAW,
        "SOCK_RDM": socket.SOCK_RDM,
        "SOCK_SEQPACKET": socket.SOCK_SEQPACKET
    }
}

Section_name: str = "Sockets"

base_pattern: dict = {
    "start_port": 8080,
    "end_port": 9090,
    "protocol": "ipv4",
}

required: tuple[str] = (
    "start_port",
    "end_port",
)


def check_model(model: dict):
    if any((n not in model for n in required)):
        raise ValueError(g_error_msg[0])


#TODO: añadir patron base
#TODO: añadir logica de carga
#TODO: añadir metodos de verificacion de datos
#TODO: añadir configuracion global de sockets.
#TODO: añadir metodos de verificacion de hardware (cargar el backend correcto)
