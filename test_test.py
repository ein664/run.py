from ctypes import *
import re
import pandas.io.clipboard as cb

from ctypes import *
def get_pixel( x, y):
    """
    取x,y处像素的函数
    :param x:
    :param y:
    :return:
    """
    # from ctypes import *
    gdi32 = windll.gdi32
    user32 = windll.user32
    hdc = user32.GetDC(None)
    pixel = gdi32.GetPixel(hdc, x, y)
    return pixel
pixel = get_pixel(659, 211)
print(pixel)