import xmlrpc.client
import numpy as np

server = xmlrpc.client.ServerProxy("http://192.168.10.71:50051", allow_none=True)

def get_car_pos(arm_id, car_id):
    return server.get_car_postion(car_id)

def get_arm_status(arm_id):
    return server.get_arm_status(arm_id)

def set_arm_status(arm_id, status):
    while True:
        server.set_arm_status(arm_id, status, 'arm2')
        if get_arm_status(arm_id) == status:
            break

def get_conveyor_status():
    return server.get_conveyor_status()

def set_conveyor_status(status):
    while True:
        server.set_conveyor_status(status)
        if get_conveyor_status() == status:
            break

def get_set_arm_status_not(arm_id, not_status, status):
    return server.get_set_arm_status_not(arm_id, not_status, status)