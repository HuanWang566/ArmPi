import xmlrpc.client
import numpy as np

server = xmlrpc.client.ServerProxy("http://192.168.10.71:50051")

def get_car_pos(arm_id, car_id):
    car_pos = server.get_car_postion(car_id)
    return car_pos