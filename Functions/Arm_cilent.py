import urllib.parse
import httplib2

# url = 'http://localhost:11000/get_arm_status?arm_id=1'
url_root = 'http://192.168.10.71:11000/'
http = httplib2.Http()

# response, content = http.request(url, 'GET')
# v_response = content.decode("utf-8").replace('encoding=\"gb2312\"','encoding=\"utf-8\"')
# print(response)
# print(content)
# print(v_response)


# define GET_ROBOT_ARM_STATUS_URL_PATH "/get_arm_status"
# define GET_AGV_CAR_STATUS_URL_PATH   "/get_car_status"
# define GET_CONVEYOR_STATUS_URL_PATH  "/get_conveyor_status"
# define GET_BLOCK_COLOR_URL_PATH      "/get_block_color"

# define SET_ROBOT_ARM_STATUS_URL_PATH "/set_arm_status"
# define SET_AGV_CAR_STATUS_URL_PATH   "/set_car_status"
# define SET_CONVEYOR_STATUS_URL_PATH  "/set_conveyor_status"
# define SET_BLOCK_COLOR_URL_PATH      "/set_block_color"

# define GET_SET_ROBOT_ARM_NOT_STATUS_URL_PATH  "/get_set_arm_not_status"
# define GET_ROBOT_ARM_IS_STATUS_URL_PATH       "/get_set_arm_is_status"

def get_arm_status(arm_id):
    url = url_root + 'get_arm_status?arm_id=' + str(arm_id)
    response, content = http.request(url, 'GET')
    return content.decode("utf-8").replace('encoding=\"gb2312\"', 'encoding=\"utf-8\"')


def get_car_pos(arm_id, car_id):
    url = url_root + 'get_car_status?car_id=' + str(car_id)
    response, content = http.request(url, 'GET')
    return content.decode("utf-8").replace('encoding=\"gb2312\"', 'encoding=\"utf-8\"')


def get_conveyor_status(conveyor_id=1):
    url = url_root + 'get_conveyor_status?conveyor_id=' + str(conveyor_id)
    response, content = http.request(url, 'GET')
    return content.decode("utf-8").replace('encoding=\"gb2312\"', 'encoding=\"utf-8\"')


def get_color_status(arm_id):
    url = url_root + 'get_block_color?arm_id=' + str(arm_id)
    response, content = http.request(url, 'GET')
    return content.decode("utf-8").replace('encoding=\"gb2312\"', 'encoding=\"utf-8\"')


def set_arm_status(arm_id, status):
    while True:
        url = url_root + 'set_arm_status?arm_id=' + \
            str(arm_id) + '&status=' + status
        response, content = http.request(url, 'GET')
        if content.decode("utf-8").replace('encoding=\"gb2312\"', 'encoding=\"utf-8\"') == "SUCCESS":
            break


def set_car_position(car_id, pos):
    while True:
        url = url_root + 'set_car_status?car_id=' + \
            str(car_id) + '&status=' + pos
        response, content = http.request(url, 'GET')
        if content.decode("utf-8").replace('encoding=\"gb2312\"', 'encoding=\"utf-8\"') == "SUCCESS":
            break


def set_conveyor_status(status, conveyor_id=1):
    while True:
        url = url_root + 'set_conveyor_status?conveyor_id=' + \
            str(conveyor_id) + '&status=' + status
        response, content = http.request(url, 'GET')
        if content.decode("utf-8").replace('encoding=\"gb2312\"', 'encoding=\"utf-8\"') == "SUCCESS":
            break


def set_color_status(arm_id, color):
    while True:
        url = url_root + 'set_block_color?arm_id=' + \
            str(arm_id) + '&color=' + color
        response, content = http.request(url, 'GET')
        if content.decode("utf-8").replace('encoding=\"gb2312\"', 'encoding=\"utf-8\"') == "SUCCESS":
            break


def get_set_arm_status_not(arm_id, not_status, status):
    url = url_root + 'get_set_arm_not_status?arm_id=' + \
        str(arm_id) + '&status=' + status + "&not_status=" + not_status
    response, content = http.request(url, 'GET')
    return content.decode("utf-8").replace('encoding=\"gb2312\"', 'encoding=\"utf-8\"') == "SUCCESS"


def get_set_arm_status_is(arm_id, is_status, status):
    url = url_root + 'get_set_arm_is_status?arm_id=' + str(arm_id) + \
        '&status=' + status + "&is_status=" + is_status
    response, content = http.request(url, 'GET')
    return content.decode("utf-8").replace('encoding=\"gb2312\"', 'encoding=\"utf-8\"') == "SUCCESS"
