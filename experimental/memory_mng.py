# -*- coding: utf-8 -*-
import gc
import weakref
import sys
import ctypes
import time

gc.enable()


class a:
    q = 23
    pass


def check_ref_by_id(instance_id):
    print(sys.getrefcount(ctypes.cast(instance_id, ctypes.py_object)), ctypes.c_long.from_address(instance_id).value)


def check_ref_by_instance(instance):
    print(sys.getrefcount(instance), ctypes.c_long.from_address(id(instance)).value)


print("Created A, B, C")
A = B = C = a()
check_ref_by_instance(A)

b = [A, B, C]
print("Added ABC to b[]")

b.append(weakref.proxy(A))
b.append(weakref.proxy(B))
b.append(weakref.proxy(C))
print("added ABC proxies to b[]")
# ids = [
#     id(A),
#     id(B),
#     id(C),
# ]

check_ref_by_instance(A)

del A
del B
del C
print("deleted A B C")
time.sleep(1)
check_ref_by_instance(b[-1])
b.pop(0)
b.pop(0)
b.pop(0)
print("deleted b[A, B, C]")
time.sleep(1)
gc.collect()
23
print(f"b = {b}")
check_ref_by_instance(b[-1])
b.pop(0)
b.pop(0)
print(f"b = {b}")
b[0]
b[0]
b[0]
#print(f"a.q = {b[0].q}")
print(f"b = {b}")
check_ref_by_instance(b[-1])
