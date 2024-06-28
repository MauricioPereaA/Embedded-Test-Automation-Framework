# -*- coding: utf-8 -*-
# General Imports.
import unittest
import pytest
import socket
import time
import logging
import weakref
import threading

# imports DTAF
import DTAF
from DTAF.server import SocketInterface
from DTAF.server.sockets import SocketThread
from DTAF.logger import SystemLogger, InterfaceLogger

InterfaceLogger.setLevel(logging.DEBUG)

# Looks for all the protocols that are available for this platform.
supported_socket_protocols = [getattr(socket, obj) for obj in dir(socket._socket) if obj[:3] == 'AF_']

supported_socket_types = [getattr(socket, obj) for obj in dir(socket._socket) if obj[:5] == 'SOCK_']

SystemLogger.warning("current protocols: {}".format("\n".join((str(obj) for obj in supported_socket_protocols))))
SystemLogger.setLevel(logging.DEBUG)

# Template that will be used to store the design coverage.
coverage_template: dict = {
    "SocketInterface": {
        "attributes": (
            # (name, type_list, default_value)
            ("thread", (SocketThread, )),
            ("socket_class", (SocketThread, )),
            ("endline", (bytes, )),
            ("logger", (logging.Logger, )),
            ("uid", (int, )),
            ("duid", (int, )),
            ("port", (int, )),
            ("host", (str, )),
            ("protocol", tuple((type(x) for x in supported_socket_protocols)), socket.AF_INET),
            ("socket_type", tuple((type(x) for x in supported_socket_types)), socket.SOCK_STREAM),
            ("endline", (bytes, ), b"\n"),
            ("connection", (socket.socket, )),
            ("kwargs", (dict, )),
        ),
        "methods": (
            "read_impl",
            "write_impl",
            "connectoin_impl",
            "connect",
            "join",
            "stop_thread",
            "connect",
            "disconnect_impl",
            "reconnect",
        )
    },
    "SocketThread": {
        "attributes": ()
    },
}


class SimpleServer():
    stay_alive: bool = None
    conn: socket.socket = None
    addr = None
    socket_server: socket.socket = None
    logger: logging.Logger = SystemLogger
    #
    HOST: str = '0.0.0.0'
    PORT: int = 8080
    #
    lock = threading.Lock()
    #
    input: bytes = b""
    output: bytes = b""

    # def __init__(self, *args, **kwargs):
    #     self.logger = SystemLogger
    #     super().__init__(*args, **kwargs)

    @staticmethod
    def read_line(conn):
        """
        reads a line from the connection.
        """
        data: bytes = b''
        try:
            while b"\n" not in data:
                data = data + conn.recv(1)
        except TimeoutError:
            return data
        return data

    @classmethod
    def reactor(self):
        self.logger.info("SimpleServer: Reactor :: Starting thread...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_server:
            self.socket_server = socket_server
            self.logger.info("SimpleServer: Reactor :: Waiting for connection.")
            socket_server.bind((self.HOST, self.PORT))
            # waits and listen to a single client.
            socket_server.listen(1)
            conn, addr = socket_server.accept()
            self.conn = conn
            self.addr = addr
            time.sleep(0.1)
            self.logger.info("SimpleServer: Reactor :: Connection aquired: {} : {}.".format(conn, addr))
            with conn:
                data = b''
                self.logger.info(f"SimpleServer: Reactor :: Connected by: {addr}")
                cc = 0
                conn.send(b"\006")
                conn.setblocking(False)
                conn.settimeout(1)
                self.stay_alive = True
                while self.stay_alive is True and getattr(conn, "_closed", False) is False:
                    self.logger.info(f"SimpleServer: Reactor :: Loop started again. count={cc}")
                    try:
                        # data = self.read_line(conn)
                        # self.output = data
                        data = self.read()
                        # self.logger.debug(
                        #     f"SimpleServer: Reactor :: DEBUG :: stay_alive: {self.stay_alive}, conn:{self.conn}, add:{self.addr}, conn._closed:{getattr(conn, '_closed', False)}"
                        # )
                        self.logger.info(f"SimpleServer: Reactor :: Data Received: `{data}`")
                        # if not data:
                        #     cc += 1
                        #     if cc > 5:
                        #         self.stay_alive = False
                        #         self.logger.info("SimpleServer: no input found, closing server...")
                        #         continue
                        cc = 0
                        time.sleep(0.1)
                        msg = f"Data received: `{data}`".encode()
                        # self.write(msg)
                        # conn.sendall(msg)
                        self.logger.info(f"SimpleServer: Reactor :: Message sent: `{msg}` .")
                        cc = cc + 1
                    except Exception as error:
                        self.logger.error("SimpleServer: Reactor :: Unknown error has happened.", exc_info=error)

            self.logger.info("SimpleServer: Reactor :: --- <Simple Socket Server is now Closed> ---\n")

    @classmethod
    def close_server(self):
        self.stay_alive = False
        self.conn.close()
        self.socket_server.close()
        time.sleep(0.1)

    @classmethod
    def read(self, timeout: int | float = 1):
        if self.stay_alive is not True:
            raise RuntimeError(f"Server is not running: stay_alive: {self.stay_alive}")
        if not self.conn:
            raise RuntimeError(
                f"No connection avilable yet. stay_alive:{self.stay_alive}, conn:{self.conn}, self.addr:{self.addr}, socket_server: {self.socket_server}"
            )
        with self.lock:
            self.conn.settimeout(timeout)
            data = self.read_line(self.conn)
            self.input = data
            return data

    @classmethod
    def write(self, message: bytes, timeout: int | float = 1):
        if self.stay_alive is not True:
            raise RuntimeError(f"Server is not running: stay_alive: {self.stay_alive}")
        if not self.conn:
            raise RuntimeError(
                f"No connection avilable yet. stay_alive:{self.stay_alive}, conn:{self.conn}, self.addr:{self.addr}, socket_server: {self.socket_server}"
            )
        with self.lock:
            self.conn.settimeout(timeout)
            if b"\n" not in message:
                message = message + b"\n"
            self.conn.sendall(message)


@pytest.mark.server_socket
class SocketTest(unittest.TestCase):
    interface: SocketInterface = None
    mock_server: SimpleServer = None
    mock_server_thread: threading.Thread = None

    HOST = "192.168.0.217"
    UID = 0
    DUID = 1
    _socket: socket.socket = None
    initialized: bool = False

    @classmethod
    def init_environ(self, ):
        """
        initializes the environment.

        creates a socket server
        it will start a socket thread.
        it will provide funcionability
        """
        # initialize memories.
        self.mock_server = SimpleServer()

        # initializes mock server.
        self.mock_server_thread = threading.Thread(target=self.mock_server.reactor)
        self.mock_server_thread.daemon = True
        self.mock_server_thread.start()

        # sets other vars
        self.interface = SocketInterface(host=self.HOST, uid=self.UID, duid=self.DUID, daemon=True, timeout=10)
        time.sleep(0.1)
        self._socket = weakref.proxy(self.interface.thread.Socket)
        self.initialized = True

    def __init__(self, *dt, **ddt):
        if SocketTest.initialized is False:
            self.init_environ()
        time.sleep(1)
        super().__init__(*dt, **ddt)

    def test_thread(self):
        pass

    def test_coverage(self):
        # [total, ok, score]
        SocketInterface = self.interface
        coverage: list = [
            [len(coverage_template["SocketInterface"]["attributes"]), 0, 0.0],
            [len(coverage_template["SocketInterface"]["methods"]), 0, 0.0],
        ]
        errors: list = []
        for attr in coverage_template["SocketInterface"]["attributes"]:
            SystemLogger.warning("SocketTest: attribute coverage : attr: {}".format(attr))
            l = len(attr)
            # checks the ressence of the attr.
            if hasattr(SocketInterface, attr[0]):
                check = True
                if check is False:
                    errors.append("SocketTest: coverage error: missing attribute `{}` from class. {}".format(
                        attr[0], SocketInterface))
                    continue
            # checks that the value is the kind expected.
            if l >= 2:
                element = getattr(SocketInterface, attr[0], None)
                check = check and isinstance(element, attr[1])
                if check is False:
                    errors.append(
                        "SocketTest: coverage error: attribute `{}` is not type or instance of {}, current: {}".format(
                            attr[0], attr[1], type(element)))
                    continue

            # checks the default value is the same as defined.
            if l >= 3:
                check = check and (getattr(SocketInterface, attr[0], None) == attr[2])
                if check is False:
                    errors.append("SocketTest: coverage error: attribute `{}` default value is not `{}`".format(
                        attr[0], attr[2]))
                    continue
            # stores the score.
            coverage[0][1] += 1 if check is True else 0
            SystemLogger.info("SocketTest: attribute coverage :: attr: {} check: {}".format(attr[0], check))
        coverage[0][2] = (coverage[0][1] * 100) / (coverage[0][0])
        SystemLogger.info("SocketTest: attribute coverage: {}% [{}/{}]".format(coverage[0][2], coverage[0][1],
                                                                               coverage[0][0]))
        for attr in coverage_template["SocketInterface"]["methods"]:
            if hasattr(SocketInterface, attr):
                coverage[1][1] += 1
            else:
                errors.append("SocketTest: coverage error: missing attribute `{}` from class. {}".format(
                    attr[0], attr[1]))
        coverage[1][2] = (coverage[1][1] * 100) / (coverage[1][0])
        SystemLogger.info("SocketTest: method coverage: {}% [{}/{}]".format(coverage[1][2], coverage[1][1],
                                                                            coverage[1][0]))
        if errors:
            SystemLogger.warning("SocketTest: coverage :: error list : \n{}".format("\n".join(errors)))
        self.assertGreaterEqual(coverage[0][2], 50)
        self.assertGreaterEqual(coverage[1][2], 50)

    def test_send_message(self):
        msg = b"sample_message\n"
        try:
            SystemLogger.info(f"SocketTest: test_send_message :: sending message to server. msg:{msg}")
            self.interface.write(msg)
            self.interface.write(msg)
            time.sleep(5)
            SystemLogger.info(f"SocketTest: test_send_message :: reading response from server.")
            mock_server_message = self.interface.read()
            SystemLogger.info(f"SocketTest: test_send_message :: response: {mock_server_message}.")
        except Exception as error:
            SystemLogger.error("an error have occured", exc_info=error)
            mock_server_message = b''
            pass
        msg = f"Data received: `{msg}`".encode()
        SystemLogger.info("DEBUG ::: current memory on thread MAIN.\n\t"
                          f"msg:    {msg}\n\t"
                          f"mock_server_message:    {mock_server_message}\n\n\t"
                          #
                          f"self.mock_server: {self.mock_server}\n\t"
                          f"self.mock_server.output: {self.mock_server.output}\n\n\t"
                          #
                          f"self.interface: {self.interface}\n\t"
                          f"self.interface.thread.is_alive:{self.interface.thread.is_alive()}.")
        self.assertEqual(msg, mock_server_message)
        time.sleep(0.1)


# @pytest.mark.server_socket_thread
# class SocketThreadTest(unittest.TestCase):
#     thread: SocketThread = None
#     logger: logging.Logger = None
#     cov_count: int = 0
#     con_score: int = 0
#     con_total: int = 0

#     def f_missing_key(self, key: str, message: str = "Missing key: {key} from object SocketThread"):
#         self.logger.error(message.format(key))

#     def __init__(self, *dt, **ddt) -> None:
#         super().__init__(*dt, **ddt)
#         self.thread = SocketThread().start()
#         self.logger = SystemLogger

#     def test_coverage(self):
#         self.assertTrue(False)
