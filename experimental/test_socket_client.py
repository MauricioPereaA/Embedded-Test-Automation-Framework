# -*- coding: utf-8 -*-
import DTAF.server as server
from DTAF.logger import SystemLogger as Logger
import queue
import time

socket = server.SocketInterface(host="192.168.0.217", uid=0, duid=1)
print(f"TEST: \t socket.thread.socket: {socket.thread.Socket}")

socket.write(b"\006")
time.sleep(0.1)
socket.write(b"Hello world!!!\n")
time.sleep(0.1)
socket.write(b"world heloooooo!!!\n")
time.sleep(0.1)
socket.write(b"This is another Example!!!\n")

cc = 0
msg = b''

while cc < 6:
    Logger.info(f"iter: {cc}")
    try:
        msg = socket.read()
        if not msg:
            time.sleep(0.01)
            cc += 1
            continue
        else:
            cc = 0
        Logger.info(f"TEST: LOOP \t message: {msg}")
        socket.write(b" ")
        Logger.info(f"TEST: LOOP \t sent message.")
    except queue.Empty as error:
        if cc < 5:
            cc += 1
            continue
        break
    if msg:
        Logger.info("TEST: \t message found!")
        break

Logger.info("sleeping timer...")
time.sleep(0.1)

# Waits for the thread to send all
while (empty := socket.thread.outbound_queue.empty()) is False:
    Logger.info(f"TEST: \t Empty: {empty} sleeping, Zzz...")
    #message = socket.thread.output_queue.get_nowait()
    #print(f"TEST: \t Took message: {message}")
    time.sleep(0.01)

socket.close()
#
Logger.info(f"TEST: waiting for thread to stop")
socket.stop_thread()
socket.join()

Logger.info(f"TEST: \t message: {msg}")
Logger.info("--- <PROGRAM END> ---")
