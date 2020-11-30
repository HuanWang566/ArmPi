import xmlrpc.client
import numpy as np

server = xmlrpc.client.ServerProxy("http://192.168.10.71:50051", allow_none=True)

def get_car_pos(arm_id, car_id):
    car_pos = server.get_car_postion(car_id)
    return car_pos

def set_arm_status(arm_id, status):
    server.set_arm_status(arm_id, status)

def get_arm_status(arm_id):
    arm_status = server.get_arm_status(arm_id)
    return arm_status

def set_conveyor_status(status):
    server.set_conveyor_status(status):