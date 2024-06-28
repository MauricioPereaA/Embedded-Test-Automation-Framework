# -*- coding: utf-8 -*-
import socket
import queue
import threading
import typing
import functools
import time
import inspect
import json
import atexit
import logging
import copy
import traceback
import weakref
import math

from DTAF.config import Config
from DTAF.logger import InterfaceLogger as Logger
from DTAF.interfaces.base import InterfaceBase
"""
Sockets Module
This socket module
"""

_needed_keys: dict = {
    "name",
    "port",
}
"""
These keys are the template for the yaml file to define the protocol and
server capabilities.

these attributes will either be boolean or a sub dictionary.
True means that they're required
False, means that they're optional
a subset of dictionaries will define a sub set to check on, the special key "required" will be present in subsets.z
"""

default_model: dict = {
    "name": "UNAMED_SOCKET",
    "port": 8081,
    "protocol": "ipv4",
    "heartbeat": False,
}
# Typing
Socket = typing.NewType("Socket", socket.socket)
# Logger.setLevel(logging.DEBUG)


class ServiceNotStarted(Exception):
    pass


class SocketThread(threading.Thread):
    """
    Threaded Socket.

    This class modifies a socket to allow us to interact within the socket in
    another thread.

    Allowing flexibility to the end user by removing some of the work in
    maniging threads and reducing confussion between protocols.

    You can semingly patch some of the functions by provindig the thread these
    arguments with callable mehtods.

    ``["heartbeat", "read", "write", "message_manager"]``

    #. heartbeat:

        Method used by the server to keep alive the socket, usually done with a
        specific code, it implementation may vary, some are based on echo, and
        others in unique codes that completes the sended one.

    #. read:
        reads the buffer from the socket.

        * args:
            - socket: socket.socket bound object.

        * kwargs:
            - chars: int, number of characteres read from the socket's buffer.


    #. message_manager:
        manages the incomming message from server.

        * args:
            - socket: socket.socket bound object.
            - msg: message in bytes.cd d


    #. write:
        writes the message over to the server.

        * args:
            - msg: message in bytes.
            - socket: socket.socket bound object.

    """

    keep_alive: bool = False
    """
    Main reactor flag.

    This flag will tell the thread to stay alive, in case this changes to False,
    the reactor will stop, and you will need to start a new socket thread.
    """

    outbound_queue: queue.Queue = None
    """
    Output queue.

    This is where all outcomming messages are stored before sending.

    the reactor will pick one after the incomming buffer have been processed.
    """
    inbound_queue: queue.Queue = None
    """
    input queue.

    Here is where we're storing all incomming messages from the sender.
    """

    Socket: Socket = None
    """
    socket object, this is set by the loop and closed on exit.
    """

    method_patch: dict[typing.Callable] = {}
    """
    Storage for each method patched

    This is where we can look for all the methods we're using instead of the
    provided by the class.
    """

    empty_response: bytes = b""
    """
    This message will be sent as empty string when there is no item in queue.

    This is often used to keep the connection alive on most socket connections.
    """

    f_send_empty: bool = False
    """
    Flag to tell the thread to send an empty message when the queue is empty.
    """

    f_read_until_char: bool = True
    """
    flag to tell the thread to read from socket until we get a specific character.
    """

    endline: bytes = b'\n'
    """
    This is the delimeter the thread will be using to know when we have to
    spread the messages from the socket.
    """

    SOCKET_TIMEOUT: int = 1
    """
    This timeout defines the waiting period of any request.
    this will be used in read_until.
    """
    SOCKET_BLOCKING: bool = None
    """
    This will tell if the socket is either blocking or not.
    """

    # type definition.
    uid: int | str = None
    duid: int | str = None

    # internal memory
    __uid: int | str = None
    __duid: int | str = None

    @property
    def uid(self):
        """
        Unique ID of the interface.

        There can only be one interface with this ID, the UID and ID can't be
        the same, since they're part of the same numeric scale.
        """
        return self.__uid

    def set_uid(self, id) -> None:
        if self.__uid is None:
            self.__uid = id
        else:
            raise ValueError(f"SocketThread: Attribute `uid` already assigned. current: `{self.__uid}` new:`{id}`")

    @property
    def duid(self):
        """
        Device UID.

        This ID represents the device the interface is bound to.
        """
        return self.__duid

    def set_duid(self, id) -> None:
        if self.__duid is None:
            self.__duid = id
        else:
            raise ValueError(f"SocketThread: Attribute `duid` already assigned. current: `{self.__duid}` new:`{id}`")

    lock: threading.Lock = None
    """
    Threading Lock to aquire as we're working in a different thread.
    """

    reactor_sleep_time: float | int = 0.01
    """
    This is the timer the reactor will snooze each time a cycle is finished.
    """

    HOST: str = ""
    """
    Host of the socket to connect with.

    Set to ``""`` by **default**.
    """

    PORT: int = 8080
    """
    Port of the socket to connect with.

    Set to ``8080`` by **default**.
    """

    PROTOCOL: socket.AddressFamily = socket.AF_INET
    """
    kind of socket protocol to be used by the thread pointer.

    Set to ``socket.AF_INET`` (IPV4) by **default**.
    """
    SOCKET_TYPE: socket.SocketKind = socket.SOCK_STREAM
    """
    Type of the socket to be used for the thread pointer.

    Set to ``socket.SOCK_STREAM`` by **default**.
    """

    _initial_config: dict = None

    _closed: bool = False
    """
    Indicates if the socket is either open or closed.
    """

    def __init__(self, **kwargs) -> None:
        # Keeps a backup from the kwargs.
        self.kwargs = kwargs
        # Define new queues.
        self.inbound_queue = queue.Queue()
        self.outbound_queue = queue.Queue()
        # sets thread LOCK object.
        self.lock = threading.Lock()
        # stores initial config for diagnostics.

        # requests neccessary variables from kwargs, if not pressent, adds
        # deffault values.
        kwargs["uid"] = kwargs.get("uid", "UNKNOWN")
        kwargs["duid"] = kwargs.get("duid", "UNKNOWN")
        self.logger = logging.LoggerAdapter(Logger, {
            "uid": "{}-THREAD".format(kwargs["uid"]),
            "duid": str(kwargs["duid"])
        })
        #
        self.HOST = kwargs["host"] = kwargs.get("host", "")
        self.PORT = kwargs["port"] = kwargs.get("port", 8080)
        #
        self.PROTOCOL = kwargs["protocol"] = kwargs.get("protocol", socket.AF_INET)  # deffaults to ipv4.
        self.SOCKET_TYPE = kwargs["socket_type"] = kwargs.get("socket_type", socket.SOCK_STREAM)
        #
        self.SOCKET_BLOCKING = kwargs["blocking"] = kwargs.get("blocking", True)
        self.SOCKET_TIMEOUT = kwargs["timeout"] = kwargs.get("timeout", 1)
        #
        self.endline = kwargs["endline"] = kwargs.get("endline", b'\n')

        # copy initial values for tracing.
        self._initial_config = copy.copy(kwargs)

        # Set the tracking values, neither uid nor duid can be the same value
        self.set_uid(kwargs["uid"])  # Unique ID of the interface.
        self.set_duid(kwargs["duid"])  # Device UID

        exception_keys: list = [
            "uid",
            "duid",
            "host",
            "port",
            "protocol",
            "socket_type",
            "blocking",
            "timeout",
            "endline",
        ]
        self.logger.debug(f"SocketThread: __init__ :: HOST={self.HOST}, PORT = {self.PORT}")
        # copies over the key
        keylist = (key for key in kwargs if key not in exception_keys)
        self.__load_patched_methods(**{key: kwargs[key] for key in keylist})
        # self.logger.warning(f"SocketThread Attempting to connect with {(HOST, PORT)}")
        # self.socket = None #
        # self.Socket.connect((HOST, PORT))
        kwargs = {
            key: kwargs[key]
            for key in kwargs if key not in [
                # method patching reserved keys.
                "heartbeat",
                "read",
                "write",
                "message_manager",
            ] + exception_keys
        }
        super().__init__(**kwargs)

    def __load_patched_methods(self, **kwargs: dict[str:typing.Callable]):
        """
        Loads the patch memory to be unique for this socket.
        """
        keys = (
            "heartbeat",
            "read",
            "write",
            "message_manager",
        )
        for key in keys:
            method: typing.Callable | None = kwargs.get(key)
            if callable(method) is False:
                method = None
            self.method_patch[key] = method

    def run(self, *d, **dt):
        try:
            self.reactor()
        except Exception as error:
            self.logger.exception(
                f"SocketThread: run :: Unspected error happened.\nERROR:\t{error}\nTRACEBACK:\n{traceback.format_exc()}\n---<TRACEBACK END>---"
            )
            self.flush_input()
            self.flush_output()
            self.stop_reactor()
            raise error

    def reactor(self):
        """
        Internal reactor of the thread.

        This "reactor" is a specialized loop that will be in charge to keep
        the thread alive and responding.

        it will manage all input and output deppending on configuration, by
        deffault it will use read_line to know when it should stop looking
        forward for incomming messages.

        Logic:
        ______
        1. Takes one item from the `outgoing` queue and Sends it to `Remote`.

            ``output_queue -> remote``

        #. Reads incomming message from remote.

           ``remote -> local``

           A. If ``read_line`` is **ENABLED**:

              It will keep reading the input buffer looking for the scape
              sequence to be present in the inbound message.
              ``remote -> :var::msg``

              * If ``scape_sequence`` is different than ``"\\n"``:
                It will use the method ``read_until`` instead of ``read_line``.

              * Else:
                It will use the ``read_line`` method.

           B. if ``read_line`` is **DISABLED**:

              It will keep reading the inbound message until it times out,
              ``(timeout > 0)``.

        #. Manages the inbound message.

           A. If ``command_manager`` is **ENABLED**:
              It will parse the inbound message to the command manager.

              ``local -> command_manager``

           B. If ``command_manager`` is **DISABLED**:
              it will queue the message into the input queue

              ``local -> input_queue``

        """
        # self.output_queue are all messages that are going out.
        # self.input_queue are all messages that are comming in.
        empty: bool = False
        msg: bytes = b''
        self.keep_alive = True
        self.logger.debug("SocketThread: reactor :: DEBUG: loop started")
        with socket.socket(self.PROTOCOL, self.SOCKET_TYPE) as _Socket:
            # configures the socket.
            self.Socket = _Socket
            _Socket.setblocking(self.SOCKET_BLOCKING)
            self.Socket.connect((self.HOST, self.PORT))
            _Socket.settimeout(self.SOCKET_TIMEOUT)
            self.logger.debug(
                f"SocketThread: reactor :: Connecting with {self.HOST}:{self.PORT}, timeout: {self.SOCKET_TIMEOUT}, blocking: {self.SOCKET_BLOCKING}"
            )
            # starts loop.
            while self.keep_alive is True:
                msg = b''
                self.logger.debug("SocketThread: Reactor :: DEBUG: loop started")
                # ------------------
                # WRITES INTO SOCKET.
                # -------------------
                empty = self.outbound_queue.empty()
                self.logger.debug(f"SocketThread: Reactor :: DEBUG: requesting output message. queue.empty: {empty}.")
                if empty is False:
                    msg = self.outbound_queue.get_nowait() or b""
                #TODO: ADD EMPTY MESSAGE HERE OR HEARTBEAT.
                self.Socket.sendall(msg)
                self.logger.info(f"SocketThread: Reactor :: Sent msg: {msg}.")
                #
                # ------------------
                # READS FROM SOCKET.
                # ------------------
                try:
                    msg = self._read_line(self.Socket, timeout=self.SOCKET_TIMEOUT)
                except TimeoutError as error:
                    self.logger.debug(f"SocketThread: Reactor :: read method timed-out: \n\tERROR: {error}.")
                    msg = b''
                except Exception as error:
                    self.logger.error(
                        f"SocketThread: Reactor :: Unexpected error happened while hearing from socket\n\tERROR: \t{error}\nTRACEBACK: \n{traceback.format_exc()}.\n--- <EXCEPTION END> ---"
                    )
                    msg = b''
                self.inbound_queue.put(msg)
                time.sleep(self.reactor_sleep_time)
            self.logger.info("SocketThread: reactor :: reactor has stopped. closing the connection...")
            # TODO: add shutdown methods here
        self.logger.info("SocketThread: reactor :: Connection closed.")
        # TODO: Add any other finallizer and cleanup sequences here.

        # this is implicit because we're using the `with socket.socket` statement.
        # self.socket.close()
        self._closed = True

    def _read_line(self, socket: Socket, sequence: bytes = b"\n", timeout: float | int = 1) -> bytes:
        """
        reads the input from the socket until a new line is found.
        by default we're expecitng a simple `\\n` character.
        """
        self.logger.debug("SocketThread: _read_line :: DEBUG: Reading line")
        msg: bytes = b''
        if isinstance(timeout, (int, float)) is False:
            timeout = 120
        try:
            msg = self._read_until(socket, sequence=sequence, timeout=timeout)
        except TimeoutError as error:
            raise
        else:
            return msg

    def _read_until(self,
                    socket: Socket,
                    sequence: bytes = b"\n",
                    timeout: float | int = 1,
                    timeout_exception: bool = True) -> bytes:
        """
        Reads the socket until we have a matching sequence in the message.

        Set timoeut to 0 to wait forever.
        raise_exception: defaults to True, set this to false to avoid raising a timeout exception.
        """
        self.logger.debug(f"SocketThread:\t_read_until :: DEBUG: Reading until: {sequence}.")
        if isinstance(timeout, (int, float)) is False:
            timeout = 120
        timeout = time.time() + timeout
        msg: bytes = b''
        now: float = time.time()
        while (now := time.time()) < timeout:
            self.logger.debug(f"SocketThread:\t_read_until :: DEBUG: loop started.")
            dt = socket.recv(1)
            msg = msg + dt
            self.logger.debug(f"SocketThread:\t_read_until :: DEBUG: got message {msg}.")
            # self.logger.debug(f"SocketThread: DEBUG: _read_until msg = {msg}, type: {type(msg)}")
            if (msg == sequence) if len(msg) > 1 else (sequence in msg[-len(sequence):]):
                return msg
            # addded a delay to let the socket "breath" and process incomming messages
            if dt:
                continue
            time.sleep(0.01)
            # self.logger.debug(f"SocketThread: _read_until :: DEBUG: sleeping, looking for sequence, got: {msg}")
        if timeout_exception is False:
            return msg
        raise TimeoutError(f"SocketThread:\t_read_until :: socket Timed out. \tMESSAGE: {msg}")

    def _read(self, socket: Socket, chars: int = 2) -> bytes:
        """
        Reads the ammount of characteres parsed. set to 0 to read all buffered
        data from the socket.
        """
        if chars % 2 == 1:
            self.logger.warning(
                f"SocketThread: _read :: requested {chars}, Socket lib recommends using a power of 2 instead.")
        try:
            if self.method_patch.get("read", None):
                return self.method_patch["read"]
            else:
                return socket.recv(chars)
        except Exception as error:
            Logger.exception(error)
            raise

    def flush_input(self):
        """
        Flushes the input queue.
        """
        while self.inbound_queue.empty() is not True:
            self.inbound_queue.get_nowait()

    def flush_output(self):
        """
        Flushes the output queue.
        """
        while self.outbound_queue.empty() is not True:
            self.outbound_queue.get_nowait()

    def format_checker(self, msg: bytes) -> bool:
        """
        Checks the format of the message.

        This default method will only assure you're using bytes instead of an
        encoded string.
        """
        if self.method_patch.get("format_check", None):
            return self.method_patch["format_check"](msg)
        return isinstance(msg, bytes)

    def heartbeat(self, socket: Socket, msg: bytes) -> int:
        """
        This method is a simple implementation of an echo heartbeat.

        This method will echo the heartbeat back to the sender. to keep the
        connection alive.

        heartbeat must be True for this method to work.
        """
        # writes directly to the socket.
        socket.sendall(msg)
        return len(msg)

    def assign_method(self, name: str, method: typing.Callable, update: bool = False) -> bool | None:
        """
        Assigns a method to be used on certain calls.

        requires the method name, and the method, that should be callable.

        please refer to the call name table to check the arguents and other
        requirements.

        the method must be callable with arguments and key-arguments, which means
        that you can't use a partial method.
        """
        if name in self.method_patch:
            if update is False:
                raise RuntimeError("Name is already in use. name: `{name}`, bound to: {method}".format(
                    name=name, method=self.method_patch[name]))
        self.method_patch[name] = method
        return True

    def stop_reactor(self) -> None:
        self.keep_alive = False
        return

    def write(self, message: bytes) -> int:
        if isinstance(message, bytes) is False:
            raise ValueError(
                f"SocketThread: write :: Error, invalid message type, it must be bytes, `{type(message)}` found")
        self.outbound_queue.put(message)
        self.logger.debug(
            f"SocketThread: write :: put [{len(message)}] bytes into the outbound socket queue, message: `{message}`")
        return len(message)

    def manage_message(self, msg: bytes):
        """
        basic message manager.
        """
        if self.method_patch.get("manager", None):
            return self.method_patch["manager"](msg)
        return True

    def read(self, timeout: float | int = 1, blocking: bool = True) -> bytes:
        self.logger.debug("SocketThread: Read :: DEBUG: READ start")
        # Logic to wait for a new input. if empty is True.
        if self.inbound_queue.empty() is True:
            self.logger.debug("SocketThread: Read :: Queue is empty. waiting..")
            # waits a full cycle before attepmting to get a message.
            # time.sleep(self.reactor_sleep_time)
            # We're going to wait forever for any message.
            if timeout is None:
                self.logger.debug("SocketThread: Read :: queue blocking read. timeout=None")
                return self.inbound_queue.get(blocking)
            # We're only waiting until timeout.
            elif timeout > 0:
                self.logger.debug(f"SocketThread: Read :: queue blocking, awaiting queue. timeout > 0: {timeout}")
                # sleeps for a cycle
                # Blocks until timeout is breached.
                try:
                    return self.inbound_queue.get(blocking, timeout)
                except:
                    return b""
            # Tries to get the very next item immediately.
            else:
                try:
                    self.logger.debug(f"SocketThread: Read :: awaiting queue. timeout = {timeout}")
                    return self.inbound_queue.get(blocking, None)
                except queue.Empty as error:
                    self.logger.exception("SocketThread: Read :: Connection Read() timed out, no message was found.",
                                          error)
                    return b""
        # Queue was not empty, returns first item from queue.
        self.logger.debug(f"SocketThread: read :: queue is not empty.")
        return self.inbound_queue.get_nowait()


def JsonSocketThread(SocketThread):
    """
    This is a simple Json based Socket.

    Where all messages are intepreted by a set of methods you may define
    in a new model.

    The operation of this socket is very simple, you send can send a json or
    raw message over the socket, and what you expect is a simple json string
    that has the command, the arguments and kword argument to operate.

    this is an example application of the SocketThread class.
    """

    def json_manager(self, msg: dict) -> bool:
        """
        Simple Json command message manager.

        This is a very basic json manager. it will use the standard:
        {
            "command": "command_name",
            args: [1,2,3,"123"],
            "kwargs": {
                "sample": 23,
                "dict": 56
            }
        }
        """
        command_name: str = msg.get("command", "")
        command = self.command_registry.get(command_name, None)
        args = (msg.get("args", []), msg.get("kwargs", {}))
        if command is None:
            raise RuntimeError(f"JsonSocket: Invalid Command: {command_name}")
        Logger.trace(f"executing command: {command_name}, with arguments {args}")
        result = command(*args[0], **args[1])
        return result

    def reg_json_command(self, command_name: str, command: typing.Callable) -> bool:
        if command_name in self.command_registry:
            raise RuntimeError("JsonSocket: Command name already in use.")
        self.command_name[command_name] = command
        pass


class SocketInterface(InterfaceBase):
    """
    This class encapsules a single thread for asynchronous communication
    between a linear programm and a socket.

    The socket will be stored within the thread while the thread is stored
    in this class.
    """

    thread: SocketThread = None
    """
    SocketThread starded and managed by this class.
    """

    socket_class: SocketThread = SocketThread
    """
    Socket Thread type, this will be changed deppending on which interface
    you're aiming to use.
    """
    endline: bytes = b'\n'
    """
    This is how any message will need to be ended. specially usefull for TCP
    protocols.
    """

    logger: logging.Logger = None
    """
    Logger pointer.

    This logger has been configured with the object metadata for precice
    logging messages.

    Use it as any other `logging.Logger` object.
    """

    connection: socket.socket = None
    """
    Weak Proxy to the socket connection object.

    You can interact with the object by calling the socket.socket methods
    directly on this attribute
    """
    kwargs: dict = None

    daemon: bool = None
    """
    Indicates wether we run the thread independently or as a daemon.

    Set to ``False`` by default.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initializes the Socket manager.

        port: int|str; port of the address where we're aiming to connect.
        address: str; address to stablish a connection to.
        protocol: str; Protocol to be used, use IPV4's AF_INET for general purposes
        socket_type: str; type of socket to be used, use SOCK_STREAM for general purposes.
        endline: bytes; type of the endline expected (used for read_line and read_until)


        See more at pythons socket documentation.

        """
        # sets uids.
        uid: int | str
        duid: int | str
        daemon: bool
        uid = kwargs["uid"] = kwargs.get("uid", "UNKNOWN")
        duid = kwargs["duid"] = kwargs.get("duid", "UNKNOWN")
        self.daemon = daemon = kwargs.get("daemon", False)
        self.logger = logging.LoggerAdapter(Logger, {"uid": str(uid), "duid": str(duid)})

        # calls super method.
        super().__init__(**kwargs)

        # set logger config.
        # self.set_uid(uid)
        # self.set_duid(duid)
        # note: REMOVED since this behavior now exists within interface base.

        # sets deffault variables.
        self.port = kwargs["port"] = kwargs.get("port", 8080)
        self.host = kwargs["host"] = kwargs.get("host", "192.168.1.168")

        # deffaults to IP-v4 AF_INET.
        self.protocol = kwargs["protocol"] = kwargs.get("protocol", socket.AF_INET)
        self.socket_type = kwargs["socket_type"] = kwargs.get("socket_type", socket.SOCK_STREAM)
        self.endline = kwargs["endline"] = kwargs.get("endline", b"\n")
        self.kwargs = copy.copy(kwargs)

        # Setup the threaded socket.
        self.thread = self.socket_class(**kwargs)
        self.thread.daemon = daemon
        self.thread.start()
        time.sleep(0.01)
        self.connection = weakref.proxy(self.thread.Socket, lambda *x: setattr(self, "connection", None))

    def __delete__(self, *k, **n):
        self.thread.stop_reactor()
        self.thread.join()
        self.thread = None
        self.connection = None
        super().__delete__(self, *k, **n)

    def read_impl(self, connection: object, timeout: int | float = 2):
        """
        Reading implementaion for the interface.

        this implementation requests an item from the thread's queue, if empty
        exception queue.EMPTY will be raised.

        """
        if self.thread.is_alive() is True:
            if self.thread.keep_alive is False:
                raise ServiceNotStarted(
                    "SocketInterface: read_impl :: Unable to connect with thread. the reactor is not running (thread.keep_alive = False)"
                )
        else:
            raise RuntimeError("SocketInterface: Unable to communicate with a dead thread.")

        self.logger.debug(f"SocketInterface: read_impl :: DEBUG: CONNECTION: {connection}, TIMEOUT {timeout}")
        return self.thread.read()
        # if timeout is None:
        #     self.logger.debug(f"SocketInterface: read_impl :: DEBUG: RUNNING LOGIC FROM: if timeout is None:")
        #     return self.thread.output_queue.get(True)
        # elif timeout and timeout > 0:
        #     self.logger.debug(f"SocketInterface: read_impl :: DEBUG: RUNNING LOGIC FROM: elif timeout and timeout > 0:")
        #     return self.thread.output_queue.get(True, timeout)
        # else:
        #     self.logger.debug(f"SocketInterface: read_impl :: DEBUG: RUNNING LOGIC FROM: else:")
        #     return self.thread.output_queue.get(True, None)

    def write_impl(self, connection: object, data: bytes):
        """
        Write implementation of the interface.

        This will put a message in the queue. all transmission errors will be
        managed inside the thread and logged directly into the logfile
        (managed by LoggerAdapter).
        """
        self.logger.debug(f"SocketInterface: write_impl :: DEBUG: CONNECTION: {connection}, DATA {data}")
        if isinstance(data, bytes) is False:
            raise TypeError(
                f"SocketInterface: write_impl :: wrong type for message, bytes was expected, got: `{type(data)}`")
        # makes sure that the message has an endline
        if b"\n" not in data[-len(self.endline):]:
            data = data + b"\n"
        #self.thread.output_queue.put(data)
        self.thread.write(data)

    def connectoin_impl(self, ) -> object:
        raise NotImplementedError(
            "SocketInterface: connectoin_impl :: Unavailable, This method is not used for this kind of interface.")

    def join(self):
        """
        Joins the thread into main.

        .. warning ::
            This will join the thread loop into the thread you invoque this
            method.

            Keep in mind that you should only join after you closed the
            reactor.

            you may lose control if you join the thread without killing the
            loop.

        """
        if self.thread.is_alive() is True:
            self.thread.join()

    def stop_thread(self, *dt):
        """
        Stops the thread.
        """
        if self.thread.is_alive() is True:
            if self.thread.keep_alive is True:
                self.thread.stop_reactor()
                time.sleep(0.1)
            else:
                raise RuntimeError("SocketInterface: stop_thread :: Thread still alive and reactor is down")

    def connect(self, *d, **dt):
        self.logger.warning(
            "SocketInterface: stop_thread :: This method does nothing, as we self managed the connection with the thread."
        )

    def disconnect_impl(self, connection: SocketThread = None):
        self.thread.stop_reactor()
        timeout = time.time() + 10
        while timeout > time.time():
            self.logger.info("SocketInterface: disconnect_impl :: Awaiting for reactor termination.")
            if self.thread._closed is True:
                break
            time.sleep(0.01)
        if self.thread._closed is False:
            raise TimeoutError("Socketinterface: disconnect_impl :: Thread has timed out disconnection wait.")

    def close(self):
        self.disconnect_impl(self.connection)

    def reconnect(self, ):
        self.logger.info("Socketinterface: reconnect :: Removing links to old object...")
        # clean up old proxy.
        self.stop_thread()
        self.connection = None
        # Create new thread.
        self.logger.info("Socketinterface: reconnect :: A new socket object has been created, trying to reconnect.")
        self.thread = self.socket_class(**self.kwargs)
        self.thread.start()
        time.sleep(0.1)
        # Create new proxy.
        self.connect = weakref.proxy(self.thread.socket, lambda *x: setattr(self, "connection", None))


class JsonSocketInterface(SocketInterface):
    socket_class: SocketThread = JsonSocketThread
