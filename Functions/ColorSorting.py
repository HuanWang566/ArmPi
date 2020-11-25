#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

AK = ArmIK()

range_rgb = {
    'red':   (0, 0, 255),
    'blue':  (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

__target_color = ('red')
# 设置检测颜色
def setTargetColor(target_color):
    global __target_color

    print("COLOR", target_color)
    __target_color = target_color
    return (True, ())

#找出面积最大的轮廓
#参数为要比较的轮廓的列表
def getAreaMaxContour(contours) :
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours : #历遍所有轮廓
            contour_area_temp = math.fabs(cv2.contourArea(c))  #计算轮廓面积
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  #只有在面积大于300时，最大面积的轮廓才是有效的，以过滤干扰
                    area_max_contour = c

        return area_max_contour, contour_area_max  #返回最大的轮廓

# 夹持器夹取时闭合的角度
servo1 = 500

# 初始位置
def initMove():
    Board.setBusServoPulse(1, servo1 - 50, 300)
    Board.setBusServoPulse(2, 500, 500)
    AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

def setBuzzer(timer):
    Board.setBuzzer(0)
    Board.setBuzzer(1)
    time.sleep(timer)
    Board.setBuzzer(0)

#设置扩展板的RGB灯颜色使其跟要追踪的颜色一致
def set_rgb(color):
    if color == "red":
        Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
        Board.RGB.show()
    elif color == "green":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
        Board.RGB.show()
    elif color == "blue":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
        Board.RGB.show()
    else:
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
        Board.RGB.show()

count = [0, 0]
_stop = False
color_list = [[], []]
get_roi = [False, False]
__isRunning = False
detect_color = ['None', 'None']
start_pick_up = [False, False]
start_count_t1 = [True, True]
def reset():
    global _stop
    global count
    global get_roi
    global color_list
    global detect_color
    global start_pick_up
    global __target_color
    global start_count_t1

    count = [0, 0]
    _stop = False
    color_list = [[], []]
    get_roi = [False, False]
    __target_color = ()
    detect_color = ['None', 'None']
    start_pick_up = [False, False]
    start_count_t1 = [True, True]

def init():
    print("ColorSorting Init")
    initMove()

def start():
    global __isRunning
    reset()
    __isRunning = True
    print("ColorSorting Start")

def stop():
    global _stop
    global __isRunning
    _stop = True
    __isRunning = False
    print("ColorSorting Stop")

def exit():
    global _stop
    global __isRunning
    _stop = True
    __isRunning = False
    print("ColorSorting Exit")

camera_number = 2
rect = [None, None]
size = (640, 480)
rotation_angle = [0, 0]
world_X, world_Y = [0, 0], [0, 0]
block_idx = 1
def move():
    global _stop
    global get_roi
    global __isRunning
    global start_pick_up
    global world_X
    global world_Y
    global rotation_angle
    global detect_color
    global camera_number
    global block_idx
    ajust_x = [27.5, -23]
    ajust_y = [27, 20]
    
    #放置坐标
    # coordinate = {
    #     'red':   ( 0 + 0.5,  20 - 0.5, 1.5),
    #     'green': ( 5 + 0.5,  20 - 0.5,  1.5),
    #     'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
    # }

    coordinate = {
        '1':  ( -9 + 0.5,  20 - 0.5,  1.5),
        '2':  ( -4 + 0.5,  20 - 0.5,  1.5),
        '3':  (  1 + 0.5,  20 - 0.5,  1.5),
        '4':  (  6 + 0.5,  20 - 0.5,  1.5),
    }
    # print(detect_color[1])
    # print(coordinate[detect_color[1]][0])
    while True:
        if __isRunning:       
            for i in range(camera_number): 
                if detect_color[i] != 'None' and start_pick_up[i]:  #如果检测到方块没有移动一段时间后，开始夹取
                    #移到目标位置，高度6cm, 通过返回的结果判断是否能到达指定位置
                    #如果不给出运行时间参数，则自动计算，并通过结果返回
                    # print(detect_color[i])
                    # print(coordinate[str(block_idx)][0])
                    set_rgb(detect_color)
                    setBuzzer(0.1)
                    result = AK.setPitchRangeMoving((world_X[i], world_Y[i], 7), -90, -90, 0)  
                    if result == False:
                        print('can not reach this place')
                    else:
                        time.sleep(result[2]/1000) #如果可以到达指定位置，则获取运行时间

                        if not __isRunning:
                            continue
                        servo2_angle = getAngle(world_X[i] + ajust_x[0], world_Y[i] + ajust_y[0], rotation_angle[i]) #计算夹持器需要旋转的角度
                        Board.setBusServoPulse(1, servo1 - 280, 500)  # 爪子张开
                        if (world_X[i] * world_X[i] + world_Y[i] * world_Y[i]) < 1800:
                            Board.setBusServoPulse(2, servo2_angle, 500)  # 注释掉这一行可以取消夹持器的角度旋转
                        time.sleep(0.5)
                    
                        if not __isRunning:
                            continue
                        AK.setPitchRangeMoving((world_X[i], world_Y[i], -0.5), -90, -90, 0, 1000)
                        time.sleep(1.5)

                        if not __isRunning:
                            continue
                        Board.setBusServoPulse(1, servo1, 500)  #夹持器闭合
                        time.sleep(0.8)

                        if not __isRunning:
                            continue
                        Board.setBusServoPulse(2, 500, 500)
                        AK.setPitchRangeMoving((world_X[i], world_Y[i], 12), -90, -90, 0, 1000)  #机械臂抬起
                        time.sleep(1)

                        if not __isRunning:
                            continue
                        result = AK.setPitchRangeMoving((coordinate[str(block_idx)][0], coordinate[str(block_idx)][1], 12), -90, -90, 0)   
                        time.sleep(result[2]/1000)
                    
                        if not __isRunning:
                            continue                   
                        servo2_angle = getAngle(coordinate[str(block_idx)][0], coordinate[str(block_idx)][1], -90)
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.5)

                        if not __isRunning:
                            continue
                        AK.setPitchRangeMoving((coordinate[str(block_idx)][0], coordinate[str(block_idx)][1], coordinate[str(block_idx)][2] + 3), -90, -90, 0, 500)
                        time.sleep(0.5)
                    
                        if not __isRunning:
                            continue                    
                        AK.setPitchRangeMoving((coordinate[str(block_idx)]), -90, -90, 0, 1000)
                        time.sleep(0.8)

                        if not __isRunning:
                            continue
                        Board.setBusServoPulse(1, servo1 - 200, 500)  # 爪子张开  ，放下物体
                        time.sleep(0.8)

                        if not __isRunning:
                            continue 
                        AK.setPitchRangeMoving((coordinate[str(block_idx)][0], coordinate[str(block_idx)][1], 12), -90, -90, 0, 800)
                        time.sleep(0.8)

                        initMove()  # 回到初始位置
                        time.sleep(1.5)

                        detect_color[i] = 'None'
                        get_roi[i] = False
                        start_pick_up[i] = False
                        set_rgb(detect_color)
                        block_idx += 1
                        if block_idx == 5:
                            block_idx = 1
            else:
                if _stop:
                    _stop = False
                    Board.setBusServoPulse(1, servo1 - 70, 300)
                    time.sleep(0.5)
                    Board.setBusServoPulse(2, 500, 500)
                    AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
                    time.sleep(1.5)
                time.sleep(0.01)
          
#运行子线程
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()    

t1 = [0, 0]
roi = [(),()]
center_list = [[],[]]
last_x, last_y = [0,0], [0,0]
draw_color = [range_rgb["black"], range_rgb["black"]]
def run(img, img_idx):
    global roi
    global rect
    global count
    global get_roi
    global center_list
    global __isRunning
    global start_pick_up
    global rotation_angle
    global last_x, last_y
    global world_X, world_Y
    global start_count_t1, t1
    global detect_color, draw_color, color_list
    
    img_copy = img.copy()
    img_h, img_w = img.shape[:2]
    cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
    cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

    if not __isRunning:
        return img

    frame_resize = cv2.resize(img_copy, size, interpolation=cv2.INTER_NEAREST)
    frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
    #如果检测到某个区域有识别到的物体，则一直检测该区域直到没有为止
    if get_roi[img_idx] and not start_pick_up[img_idx]:
        get_roi[img_idx] = False
        frame_gb = getMaskROI(frame_gb, roi[img_idx], size)      
    frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # 将图像转换到LAB空间

    color_area_max = None
    max_area = 0
    areaMaxContour_max = 0
    
    if not start_pick_up[img_idx]:
        for i in color_range:
            if i in __target_color:
                frame_mask = cv2.inRange(frame_lab, color_range[i][0], color_range[i][1])  #对原图像和掩模进行位运算
                opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6,6),np.uint8))  #开运算
                closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6,6),np.uint8)) #闭运算
                contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  #找出轮廓
                areaMaxContour, area_max = getAreaMaxContour(contours)  #找出最大轮廓
                if areaMaxContour is not None:
                    if area_max > max_area:#找最大面积
                        max_area = area_max
                        color_area_max = i
                        areaMaxContour_max = areaMaxContour
        if max_area > 2500:  # 有找到最大面积
            rect[img_idx] = cv2.minAreaRect(areaMaxContour_max)
            box = np.int0(cv2.boxPoints(rect[img_idx]))
            
            roi[img_idx] = getROI(box) #获取roi区域
            get_roi[img_idx] = True
            img_centerx, img_centery = getCenter(rect[img_idx], roi[img_idx], size, square_length)  # 获取木块中心坐标
             
            world_x, world_y = convertCoordinate(img_centerx, img_centery, size) #转换为现实世界坐标
            if img_idx == 0:
                world_x -= 27.5
                world_y -= 27
            elif img_idx == 1:
                world_x += 23
                world_y -= 20
            
            cv2.drawContours(img, [box], -1, range_rgb[color_area_max], 2)
            cv2.putText(img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, range_rgb[color_area_max], 1) #绘制中心点
            
            distance = math.sqrt(pow(world_x - last_x[img_idx], 2) + pow(world_y - last_y[img_idx], 2)) #对比上次坐标来判断是否移动
            last_x[img_idx], last_y[img_idx] = world_x, world_y
            if not start_pick_up[img_idx]:
                if color_area_max == 'red':  #红色最大
                    color = 1
                elif color_area_max == 'green':  #绿色最大
                    color = 2
                elif color_area_max == 'blue':  #蓝色最大
                    color = 3
                else:
                    color = 0
                color_list[img_idx].append(color)
                # 累计判断
                if distance < 0.5:
                    count[img_idx] += 1
                    center_list[img_idx].extend((world_x, world_y))
                    if start_count_t1[img_idx]:
                        start_count_t1[img_idx] = False
                        t1[img_idx] = time.time()
                    if time.time() - t1[img_idx] > 1:
                        rotation_angle[img_idx] = rect[img_idx][2] 
                        start_count_t1[img_idx] = True
                        world_X[img_idx], world_Y[img_idx] = np.mean(np.array(center_list[img_idx]).reshape(count[img_idx], 2), axis=0)
                        center_list[img_idx] = []
                        count[img_idx] = 0
                        start_pick_up[img_idx] = True
                else:
                    t1[img_idx] = time.time()
                    start_count_t1[img_idx] = True
                    center_list[img_idx] = []
                    count[img_idx] = 0

                if len(color_list[img_idx]) == 3:  #多次判断
                    # 取平均值
                    color = int(round(np.mean(np.array(color_list[img_idx]))))
                    color_list[img_idx] = []
                    if color == 1:
                        detect_color[img_idx] = 'red'
                        draw_color[img_idx] = range_rgb["red"]
                    elif color == 2:
                        detect_color[img_idx] = 'green'
                        draw_color[img_idx] = range_rgb["green"]
                    else:
                        detect_color[img_idx] = 'None'
                        draw_color[img_idx] = range_rgb["black"]
        else:
            if not start_pick_up[img_idx]:
                draw_color[img_idx] = (0, 0, 0)
                detect_color[img_idx] = "None"

    cv2.putText(img, "Color: " + detect_color[img_idx], (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, draw_color[img_idx], 2)
    return img

if __name__ == '__main__':
    init()
    start()
    __target_color = ('red', 'green')
    my_camera1 = Camera.Camera()
    my_camera2 = Camera.Camera()
    my_camera1.camera_open(0)
    my_camera2.camera_open(2)
    while True:
        img1 = my_camera1.frame
        if img1 is not None:
            frame1 = img1.copy()
            Frame1 = run(frame1, 0)  
            cv2.imshow('Frame1', Frame1)  
            # cv2.imshow('Frame1', frame1)
        img2 = my_camera2.frame
        if img2 is not None:
            frame2 = img2.copy()
            Frame2 = run(frame2, 1)       
            cv2.imshow('Frame2', Frame2)
            # cv2.imshow('Frame2', frame2)

        key = cv2.waitKey(1)
        if key == 27:
            break
    my_camera1.camera_close()
    my_camera2.camera_close()
    cv2.destroyAllWindows()
