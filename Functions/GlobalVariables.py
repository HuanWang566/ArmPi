#!/usr/bin/python3
# coding=utf8

camera_number = 2
_stop = False
__isRunning = False

detect_color = []
start_pick_up = []
rotation_angle = []
world_X, world_Y = [], []
get_roi = []

def global_variables_init():
    global detect_color
    global start_pick_up
    global rotation_angle
    global world_X
    global world_Y 
    global get_roi
    for i in range(camera_number):
        get_roi.append(False)
        detect_color.append('None')
        start_pick_up.append(False)
        rotation_angle .append(0)
        world_X.append(0)
        world_Y.append(0)