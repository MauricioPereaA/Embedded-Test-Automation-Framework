# -*- coding: utf-8 -*-
# Echo server program
import socket
import time

HOST = '0.0.0.0'  # Symbolic name meaning all available interfaces
PORT = 8080  # Arbitrary non-privileged port


def read_line(conn):
    data: bytes = b''
    try:
        while b"\n" not in data:
            data = data + conn.recv(1)
    except TimeoutError:
        return data
    return data


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print("waiting for connection")
    conn, addr = s.accept()
    with conn:
        data = b''
        print('Connected by', addr)
        cc = 0
        conn.send(b"hi!")
        conn.setblocking(False)
        conn.settimeout(0.2)
        while True and getattr(conn, "_closed", False) is False:
            #data = conn.recv(1024)
            data = read_line(conn)
            print(f"TEST: \t Received: {data}")
            if not data:
                cc += 1
                if cc > 5:
                    print("no response found, closing server.")
                    break
                time.sleep(0.1)
                continue
            cc = 0
            time.sleep(0.01)
            conn.sendall(b"received: " + data)
            print(f"TEST: \t Sent: {data}")
            time.sleep(0.01)
            #print(conn)

print("\n--- <PROGRAM END> ---\n")
