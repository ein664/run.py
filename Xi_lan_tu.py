# pyautogui.moveTo(949, 844, duration = 0.4)
#         pydirectinput.click()
# pyautogui.hotkey("ctrl", "a")
# pyautogui.keyDown('shift')
import time
import pydirectinput
import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab
def get_color_block_centers_from_screen(target_color=(155, 186, 207) , threshold=50, min_area=500):
    """
    从当前屏幕截图中获取色块中心点坐标
    :param target_color: 目标颜色(BGR格式)
    :param threshold: 颜色差异阈值
    :param min_area: 最小区域面积(过滤小噪点)
    :return: 色块中心点坐标列表
    """
    # 截取屏幕
    screenshot = ImageGrab.grab()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # 定义颜色范围
    lower = np.array([max(0, target_color[0] - threshold),
                      max(0, target_color[1] - threshold),
                      max(0, target_color[2] - threshold)])
    upper = np.array([min(255, target_color[0] + threshold),
                      min(255, target_color[1] + threshold),
                      min(255, target_color[2] + threshold)])

    # 颜色阈值处理
    mask = cv2.inRange(img, lower, upper)

    # 形态学操作
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    centers = []
    for contour in contours:
        # 过滤小面积区域
        if cv2.contourArea(contour) < min_area:
            continue

        # 计算中心点
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            centers.append((cX, cY))

    return centers
global x,y,a,z,position
#背包每个格子坐标，竖着取位置呦~~
position= [(1336, 598), (1334, 648), (1332, 689), (1335, 734), (1329, 799), (1386, 598), (1393, 645), (1386, 688), (1383, 737), (1380, 794), (1432, 594), (1435, 643), (1441, 707), (1438, 746), (1425, 801), (1478, 597), (1491, 650), (1488, 693), (1478, 749), (1484, 795), (1537, 595), (1531, 643), (1530, 693), (1527, 748), (1532, 804), (1582, 593), (1587, 643), (1586, 699), (1581, 753), (1584, 796), (1629, 597), (1630, 650), (1630, 696), (1632, 744), (1632, 800), (1678, 597), (1680, 650), (1681, 702), (1681, 748), (1685, 799), (1726, 594), (1732, 650), (1736, 698), (1733, 756), (1733, 803), (1778, 595), (1777, 645), (1780, 694), (1782, 757), (1791, 809), (1829, 589), (1831, 647), (1831, 704), (1830, 746), (1824, 790), (1869, 599), (1876, 645), (1877, 693), (1877, 739), (1883, 794) ]

z = 0
x , y = position[z]
a = True

if __name__ == "__main__":
    time.sleep(3)

    while a:
        x, y = position[z]
        z += 1
        if z>50 :
            break

        pyautogui.moveTo(x, y, duration=0.1)
        # 此处为软件停止功能，鼠标每移动到一个位置后，经过0.1s后再次获取鼠标位置
        # 若位置不一样则软件退出
        time.sleep(0.1)
        pos = pyautogui.position()#该函数获取鼠标位置
        if (pos.x,pos.y) == (x , y):
            pass
        else:
            pyautogui.keyUp('ctrl')
            a = False

        pyautogui.keyDown('ctrl')#ctrl键持续按下，后面还有ctrl抬起
        pydirectinput.click()#鼠标左键点击
        time.sleep(0.5)#睡眠  注意此软件延迟敏感，不可以没有延迟，因为游戏有延迟，每个操作的结果不是瞬间出来的

        centers = get_color_block_centers_from_screen()
        for x1, y1 in centers:
            #此处为检索的区域 不要整个屏幕都检索，划定一个区域检索要点击的方块，不设置可能会有bug
            if 1695> x1 and x1>318 and y1 >132 and 857> y1:
                pass
            else:
                continue
            pyautogui.moveTo(x1, y1, duration=0.2)
            print(x1,y1)#可以删掉的没用代码

            pos = pyautogui.position()
            if pos.x == x1 and pos.y == y1:

                pass
            else:
                a = False
                pyautogui.keyUp('ctrl')
                break
            pydirectinput.click()#点击要选人前的位置

            pyautogui.keyUp('ctrl')
            #鼠标移动到第一个人上
            pyautogui.moveTo(874, 500,
                             duration=0.1)#该坐标是三个人中第一个人的位置，若有两个人，该位置也能点到第一个人，自己多试试，设置的偏一点儿别取正中心，这样即使两个人也能选中第一个人
            time.sleep(0.1)
            pos = pyautogui.position()
            if pos.x == 874 and pos.y == 500:#别忘了改

                pass
            else:
                a = False
                pyautogui.keyUp('ctrl')
                break
            pydirectinput.click()
            time.sleep(0.1)
            # 确认蓝图

        pyautogui.moveTo(946, 946, duration=0.1)
        time.sleep(0.1)
        pos = pyautogui.position()
        if pos.x == 946 and pos.y == 946:

            pass
        else:
            a = False
            pyautogui.keyUp('ctrl')
            break
        pydirectinput.click()
        time.sleep(0.1)
        # 移走蓝图
        pyautogui.keyDown('ctrl')
        pyautogui.moveTo(955, 877, duration=0.1)
        time.sleep(0.2)
        pos = pyautogui.position()
        if pos.x == 955 and pos.y == 877:
            pass
        else:
            a = False
            pyautogui.keyUp('ctrl')
            break
        pydirectinput.click()




    pyautogui.keyUp('ctrl')
if __name__ == "__main__1":
    time.sleep(2)
    pyautogui.hotkey("esc")
#     pyautogui.moveTo(874, 500, duration=0.3)
#免费工具








