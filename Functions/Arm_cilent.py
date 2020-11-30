import xmlrpc.client
import numpy as np

server = xmlrpc.client.ServerProxy("http://192.168.10.71:50051")

def get_car_pos(arm_id, car_id):
    car_pos = server.get_car_postion(car_id)
    return car_pos

def get_arm_status(arm_id):
    return server.get_carm_status(arm_id)

def get_conveyor_status():
    return server.conveyor_status()