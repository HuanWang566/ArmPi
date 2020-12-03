import xmlrpc.client
import numpy as np

server = xmlrpc.client.ServerProxy("http://192.168.10.71:50051", allow_none=True)

def get_car_pos(arm_id, car_id):
    return server.get_car_postion(car_id)

def set_arm_status(arm_id, status):
    while True:
        server.set_arm_status(arm_id, status, "arm3")
        if get_arm_status(arm_id) == status:
            break

def get_arm_status(arm_id):
    return server.get_arm_status(arm_id)
