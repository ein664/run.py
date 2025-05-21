import pyautogui
import pydirectinput
import time
import pandas.io.clipboard as cb
from ctypes import *
import re
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUi
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from PyQt5.QtCore import QObject, pyqtSignal
import random


class TuJin(QThread):
    # 定义一个信号，用于触发A类的D函数
    call_D_signal = pyqtSignal()
    #线程用
    update_signal = pyqtSignal(str)  # 用于更新UI的信号
    def __init__(self):
        super().__init__()
        self.get_item_info_fail_times_2=0
        self._is_running = True#退出标志
        #购买频率，连续三个空格停止购买，四孔共振俩空格
        self.purchase_frequency = 0
        self.tu_jin = 0
        self._json = {}
        self.x = 377
        self.y = 292
        self.current_status = '0'
        self.get_item_info_fail_times = 0
        #动作停顿时间
        self.duration_time = 0.05+random.randint(1,3)*0.03
        #关闭购买页面按钮的位置
        self.close_artifact_page_button_position = (808, 223)
        #图金页面左侧两列通货坐标
        self.tujin_items_position = [(374, 293), (378, 343), (381, 394), (377, 441), (369, 484), (375, 536), (375, 579), (373, 633), (373, 678), (370, 734), (371, 782), (428, 292), (434, 355), (430, 401), (429, 439), (421, 490), (422, 537), (423, 583), (418, 632), (417, 683), (423, 744), (421, 781)]
        self.change_page_position = (941, 841)#图金换页位置
        self.price_box = (688, 733)#代币价格栏
        self.count = 0.65

        self.filter_item_names = ['Contract', 'Armourer', 'Essence', 'Eye Jewel', 'Orb of Chance',
                                  'Blacksmith\'s Whetstone', 'Orb of Transmutation', 'Orb of Alchemy',
                                  'Orb of Horizons', 'Harbinger\'s Shard', 'Orb of Binding']

        self.tujin_times = 0#记录取到第几个图金的位置了
        #线程相关
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.paused = False
        self.stopped = False

        #黑镰神器折算c
        self.lesser_artifiact = 0.015#50个换1c是0.02，代币多就调高数值，神器多就减小数值
        self.greater_artifiact = 0.025#应该和次级差不多
        self.exceptional_artifiact = 0.02#0.046
        self.grand_artifiact = 0.16

        #每个物品重置
        self.artifact_type = 0
        self.artifact_number = 0
        self.item_name = ''
        self.item_level = 0
        self.item_number = 0
        self.copy_results = ''
        self.lookup = {}#数据文件
        self.item_price = 0
        self.buy_times = 0#记录一个物品购买几次的参数
        self.item_Class= ''

    def reset_pamar(self):
        self.artifact_type = 0
        self.artifact_number = 0
        self.item_name = ''
        self.item_level = 0
        self.item_number = 0
        self.copy_results = ''
        self.item_price = 0
        self.buy_times = 0  # 记录一个物品购买几次的参数
        # self.get_item_info_fail_times = 0
        # 购买频率，连续三个空格停止购买，四孔共振俩空格
        self.purchase_frequency = 0
        self.current_status = '参数已重置'

    def sent_signal(self):
        #发射信号用的函数
        self.call_D_signal.emit()

    def get_item_Class(self):
        for result in self.copy_results:
            self.item_Class = re.search(r'Item Class: (.*)', result).group()
            if self.item_Class:
                self.current_status = '已获取物品种类'
                return False
        print('种类不详')
        return True

        # 成功购买一次就清零购买失败的频率


    def reset_state(self):
        self.artifact_type = 0
        self.artifact_number = 0
        self.item_name = ''
        self.item_level = 0
        self.item_number = 0
        self.copy_results = ''
        self.lookup = {}  # 数据文件
        self.item_price = 0
        self.buy_times = 0  # 记录一个物品购买几次的参数
        self.item_Class = ''

    def get_item_name(self):
        """
        从self.copy_results中获取物品名称
        :return:
        """
        #空字符串为假

        if self.copy_results[0] =='清除剪贴板儿':
            self.current_status = '获取物品信息失败'
            return False
        if self.copy_results:

            for result in self.copy_results:
                if re.findall('--', result):
                    break
                # 保存该次循环的前一个结果,即该次循环匹配到----就break了, item_name 的值是上次循环的
                self.item_name = result
            #成功购买一次就清零购买失败的频率
            self.purchase_frequency = 0
        else:
            # print('get_item_name报错，复制结果有问题')
            return True#
            #'清除剪贴板儿'
        # print('item_name:'+self.item_name)

        if self.filter_name():
            self.current_status = '购买完毕'
            return False

        self.current_status = '已取得物品名称'
        return False
    def filter_name(self):
        #匹配到契约返回真，使过滤名字为条件的if进入重置参数阶段

        for i in self.filter_item_names:
            if i in self.item_name:
                return True
        return False
    def get_item_number(self):
        for a_result in self.copy_results:
            #正则结果以list结果返回['xxx'],先list[0]取值,再进行int转换格式
            item_number = re.findall(r"Stack Size: (\d+)/", a_result)#a_result格式是字符串，不是列表
            if item_number:

                try:
                    self.item_number = int(item_number[0])
                except:
                    print('get_item_number报错')
                    item_number = item_number[0].replace(',', '')
                    self.item_number = int(item_number)
                self.current_status = '已获取堆叠数量'

        return False

    def get_item_level(self):
        for a_result in self.copy_results:
            item_level = re.findall(r"Item Level:(\d+)", a_result)
            if item_level:
                self.item_level = int(item_level[0])
                self.current_status = '已获取物品等级'
            else:
                self.current_status = '获取物品等级失败'
        return False

    def load_date_file(self,file_path=r"C:\PythonCode\poe\items_price.txt"):
        # 载入数据文件

        with open(file_path, 'r') as f:
            for line in f:
                if line:
                    # 假设每行包含键值对，如 "key:value"
                    try:
                        key, value = line.strip().split(':')
                        self.lookup[key] = value
                    except Exception:
                        print('载入数据文件报错')

        self.current_status = '已载入数据包'
        return False
    def reload_date_file(self):
        # 重新载入数据文件

        self.load_date_file()
        self.tujin_times -= 1
        self.current_status = '价格表已更新'
        return False

    def mouse_mov(self,x, y, duration=0.25):
        """
        鼠标移动函数
        """
        pyautogui.moveTo(x, y, duration)

    def mouse_move(self):
        self.current_status == '鼠标位于物品上'
        return False



    def simulate_keyboard_ctrl_c(self):
        pyautogui.hotkey("ctrl", "c")
        # time.sleep(0.05)

    def get_item_info(self):
        """
        从剪切板取得信息
        :return: 包含信息的对象
        """
        #ctrl+c复制
        self.simulate_keyboard_ctrl_c()
        #获取剪贴板并返回
        self.copy_results = self.get_clipboard()
        self.current_status = '已获取物品信息'
        return False
    def get_clipboard(self):
        """获取剪切板并按行分割,
        返回一个 数组对象
        """
        #import pandas.io.clipboard as cb
        #不进行切割的话，运用for循环，会单个字母单崩出来
        copy_results = cb.paste().split('\r\n')
        return copy_results

    def next_page(self):
        #鼠标移动到949, 844
        pyautogui.moveTo(949, 844, duration = 0.4)
        pydirectinput.click()
        return '已换页'
    def _buy_item(self):
        pass

    def find_item_price(self):
        # 获取物品价格
        result = self.lookup.get(self.item_name, None)

        if result == None:
            self.current_status = '未找到物品价格'
            return False

        self.item_price = result
        self.current_status = '已取得物品价格'
        return False

    def add_item_and_price(self):
        ##添加物品价格后重新运行程序
        #向主线程发送信号，使其出现红框提示添加新的物品及价格
        self.sent_signal()
        #阻塞线程运行
        self.paused = True
        return False
    def get_artifact_type_and_number(self):
        pydirectinput.click()
        self.get_artifact_type()
        self.get_artifact_number()

        self.current_status = '已获取神器种类及数量'
        return False

    def get_pixel(self, x, y):
        """
        取x,y处像素的函数
        :param x:
        :param y:
        :return:
        """
        #from ctypes import *
        gdi32 = windll.gdi32
        user32 = windll.user32
        hdc = user32.GetDC(None)
        pixel = gdi32.GetPixel(hdc, x, y)
        return pixel

    def get_artifact_number(self):
        """
        :return: 返回数字,代表神器数量
        """
        pyautogui.moveTo(688, 733, duration = self.duration_time)
        pydirectinput.click()
        time.sleep(self.duration_time)

        # 复制价格
        pyautogui.hotkey("ctrl", "a")
        time.sleep(self.duration_time)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(self.duration_time)
        # 获取剪切板
        a = self.get_clipboard()[0]
        self.artifact_number = int(a)

    def get_artifact_type(self):
        pixel = self.get_pixel(649, 663)
        # 4 527116
        # 3 2105887
        # 2 2105374
        # 1 13683638
        if pixel == 527116:
            # print('<get_artifact_type>         4卓越神器')
            self.artifact_type = 4
        elif pixel == 2105887:
            # print('<get_artifact_type>         3至高神器')
            self.artifact_type = 3
        elif pixel == 2105374:
            # print('<get_artifact_type>         2高级神器')
            self.artifact_type = 2
        elif pixel == 13683638:
            # print('<get_artifact_type>         1次级神器')
            self.artifact_type = 1
        else:
            # ZMailObject()  # 发邮件
            input('<get_artifact_type>报错, 未匹配到先祖通货类型')
    def record_price(self):
        with open(r'C:\PythonCode\pyqt\Record_price.txt', 'a', encoding='utf-8') as big_file:
            big_file.write(self.item_name + ':' + str(self.item_price) +' '+'堆叠:'+str(self.item_number)+' '
                           +'神器:'+str(self.artifact_number)+' '+'神器种类:'+str(self.artifact_type)+'\n')


    def buy_is_or_not(self):
        #通货=多少c，乘以堆叠数量 等于这一堆儿通货的价值；

        #算出每个神器约等于多少c，神器数量除以通货总价 大于某个值就买

        # print(type(self.item_number))
        self.item_price = float(self.item_price)
        # print(type(self.item_price))
        self.get_item_number()
        items_total_price = self.item_number*self.item_price
        # print('items_total_price:'+str(items_total_price))
        if items_total_price == 0:
            artifact_convert_chaos= 0
        else:#35=1c 0.0028
            artifact_convert_chaos = round(items_total_price / self.artifact_number, 4)
        # print('buy_is_or_not')
        match self.artifact_type:
            case 1:
                if artifact_convert_chaos >= self.lesser_artifiact:
                    self.current_status = '购买'
                    self.record_price()
                    return False
            case 2:
                if artifact_convert_chaos >= self.greater_artifiact:
                    self.current_status = '购买'
                    self.record_price()
                    return False
            case 3:
                if artifact_convert_chaos >= self.exceptional_artifiact:
                    self.current_status = '购买'
                    self.record_price()
                    return False
            case 4:
                if artifact_convert_chaos >= self.grand_artifiact:
                    self.current_status = '购买'
                    self.record_price()
                    return False

        self.current_status = '放弃购买'
        return False

    def buy(self):
        match self.buy_times:
            case 0:
                self.buy_times += 1
                self.buy_action(0.65)
                time.sleep(0.2)
                if self.check_if_buy_success():
                    self._handle_buy_success()
                else:
                    self._retry_buy()

            case 1:
                self.buy_times += 1
                self.buy_action(0.55)
                time.sleep(0.2)
                if self.check_if_buy_success():
                    self._handle_buy_success()
                else:
                    self._retry_buy()

            case 2:
                self.buy_times += 1
                pyautogui.moveTo(674, 830, duration=self.duration_time)
                pydirectinput.click()
                time.sleep(0.2)
                pydirectinput.click()
                time.sleep(0.2)
                if self.check_if_buy_success():
                    self._handle_buy_success()
                else:
                    self._retry_buy()

            case 3:
                self.buy_times = 0
                print('包满了')
                self.current_status = '包满了'
                return False
            case _:
                self.buy_times = 0
                print('buy函数报错')
                self.current_status = '停止工作'
                return False

    def _handle_buy_success(self):
        self.buy_times = 0
        self.current_status = '购买成功'
        return False

    def _retry_buy(self):
        return self.buy()



    def check_if_buy_success(self):
        # 取色判断是否购买成功659,211处颜色
        pixel = self.get_pixel(659, 211)
        # if 成功 break
        # 不等于2174256说明购买成功
        if pixel != 2174256:
            # d = 2 / 3

            return False
        else:
            return True

    def buy_action(self,count):
        """
        点击价格框
        包括复制价格
        粘贴砍价后的价格
        点击购买
        :param count:
        :return:
        """
        x, y = self.price_box
        pyautogui.moveTo(x, y, duration=self.duration_time)
        pydirectinput.click()
        # 复制价格
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "c")
        # 获取剪切板
        a = self.get_clipboard()[0]
        b = int(int(a) * count)  # 0.65
        cb.copy(b)
        pyautogui.hotkey("ctrl", "v")
        # 鼠标移动至确定按钮674,830
        pyautogui.moveTo(674, 830, duration=self.duration_time)
        pydirectinput.click()


        # self.current_status = '购买完毕'
        # return False
    def close_artifact_page(self):
        x,y = self.close_artifact_page_button_position
        pyautogui.moveTo(x,y , duration = self.duration_time)
        pydirectinput.click()
        self.current_status = '神器页面已关闭'
        return False
    def exchange_tujin_page(self):
        """
        切换图金页面
        :return:
        """
        x, y = self.change_page_position
        pyautogui.moveTo(x,y, duration=self.duration_time)
        pydirectinput.click()
        self.current_status = '图金页面已切换完成'
        ##重置鼠标移动的代码
        self.tujin_times = 0

        return False
    def delete_special_item(self):
        if 'Support Gems' in self.item_Class or 'Skill Gems' in self.item_Class:
            self.current_status = '当前物品为技能宝石'
        else:
            self.current_status = '不是技能宝石'
        if 'Rings' in self.item_Class:
            self.current_status = '裂隙戒指'
        if 'Scarab' in self.item_name:
            self.current_status = '圣甲虫'
        if 'Map' in self.item_name:
            self.current_status = '地图'
        if 'Oil' in self.item_name:
            self.current_status = '圣油'
        if 'Incubator' in self.item_name:
            self.current_status = '孕育石'
        if 'Cluster' in self.item_name:
            self.current_status = '星团珠宝'
        return False
    def buy_special_gems(self):
        if self.item_name == 'Enlighten Support':
            self.current_status = '购买'
            return False
        if self.item_name == 'Empower Support':
            self.current_status = '购买'
            return False
        if self.item_name == 'Enhance Support':
            self.current_status = '购买'
            return False
        self.current_status = '购买完毕'
        return False

    def deal_breach_ring(self):
        self.item_level = self.get_item_level()
        match self.item_level:
            case 82:
                self.item_price = 0
            case 83:
                self.item_price = 0.3
            case 83:
                self.item_price = 0.6
            case 84:
                self.item_price = 1
            case 86:
                self.item_price = 2
            case _:
                self.item_price = 0
        self.current_status = '已取得物品价格'
        return False

    def deal_scarab(self):
        self.find_item_price()
        if self.current_status == '未找到物品价格':
            self.item_price = 1
            self.current_status = '已取得物品价格'
    def deal_incubator(self):
        self.find_item_price()
        if self.current_status == '未找到物品价格':
            self.item_price = 0
            self.current_status = '已取得物品价格'
    def deal_map(self):
        a = cb.paste()
        if 'Cortex' in a:
            self.item_price = 50
            self.current_status = '已取得物品价格'
            return False
        if 'Synthesised' in self.item_name:
            self.item_price = 20
            self.current_status = '已取得物品价格'
            return False
        self.current_status = '购买完毕'
        return False
    def deal_cluster_jewel(self):
        text = cb.paste()

        item_level_line = [line for line in text.split('\n') if 'Item Level:' in line][0]
        item_level = int(item_level_line.split(':')[1].strip())

        adds_line = [line for line in text.split('\n') if line.startswith('Adds')][0]
        adds_number = int(adds_line.split()[1])

        if item_level >=84 and adds_number >=11:
            self.current_status = '已取得物品价格'
            self.item_price = 150
            return False
        self.current_status = '重置参数'
        return False

    def run(self):
        #主线程执行函数
        action_handlers = {

            '移至下一个物品': self.mouse_move_in_tujin,#
            '停止工作': self.stop,
            '获取物品信息': self.get_item_info,
            '抽取物品名称': self.get_item_name,
            '获取物品种类': self.get_item_Class,
            '排除特殊种类物品':self.delete_special_item,
            '查找物品价格': self.find_item_price,
            '添加物品及价格':self.add_item_and_price,
            '获取神器种类及数量':self.get_artifact_type_and_number,
            '判断是否购买':self.buy_is_or_not,
            '购买':self.buy,
            '关闭神器页面':self.close_artifact_page,
            '进行换页':self.exchange_tujin_page,
            '加载价格表':self.load_date_file,
            '更新价格表':self.reload_date_file,
            '重置参数':self.reset_pamar,
            '排除特殊种类物品':self.delete_special_item,
            '匹配三个特殊辅助宝石购买':self.buy_special_gems,
            '处理裂隙戒指':self.deal_breach_ring,
            '处理圣甲虫':self.deal_scarab,
            '处理地图':self.deal_map,
            '处理孕育石':self.deal_incubator,
            '处理星团珠宝':self.deal_cluster_jewel,



        }

        while self._is_running:

            # 暂停检查区块（需要线程安全）
            self.mutex.lock()
            if self.paused:
                # 如果暂停，则等待（会释放mutex，被唤醒时重新获取）
                self.condition.wait(self.mutex)
            self.mutex.unlock()


            m = self._determine_action()  # 提取判断逻辑到单独方法
            handler = action_handlers.get(m)
            if not handler:
                print(f"未知操作: {m}")
                break
            if handler():  # 返回 False 时继续循环，返回True,退出循环
                break
    def _determine_action(self):

        if self.kill_while_with_mouse():
            print('<func_main()>检测到鼠标离开工作区域,程序中断')

            time.sleep(2)
            return '停止工作'

        if self.current_status == '获取物品信息失败':
            self.get_item_info_fail_times += 1
            self.get_item_info_fail_times_2 += 1
            if self.get_item_info_fail_times_2 > 2:
                self.current_status = '移至下一个物品'
                self.get_item_info_fail_times_2 = 0
            if self.get_item_info_fail_times > 7:
                self.get_item_info_fail_times = 0
                print('需要换页')
                self.current_status = '需要换页'
                ##重置鼠标位置##
                self.tujin_times = 0


        if self.current_status == '获取物品等级失败':
            ##失败未添加处理的代码##
            self.current_status = '已获取物品等级'
        action_handlers = {
            '0':'加载价格表',#状态0代表程序刚开始运行
            '已载入数据包':'移至下一个物品',
            '鼠标已移至物品上':'获取物品信息',
            '已获取物品信息':'抽取物品名称','获取物品信息失败':'获取物品信息',

            '已取得物品名称':'获取物品种类',
            '已获取物品种类': '排除特殊种类物品',

            '当前物品为技能宝石':'匹配三个特殊辅助宝石购买',
            '不是技能宝石':'查找物品价格',
            '裂隙戒指':'处理裂隙戒指',
            '圣甲虫':'处理圣甲虫',
            '地图': '处理地图',
            '圣油':'重置参数',
            '孕育石':'处理孕育石',
            '星团珠宝':'处理星团珠宝',

            '未找到物品价格':'添加物品及价格','已取得物品价格':'获取神器种类及数量',
            '已获取神器种类及数量': '判断是否购买',
            '已添加物品及价格':'更新价格表',
            '价格表已更新':'移至下一个物品',


            '购买':'购买',  '放弃购买':'关闭神器页面',

            '购买完毕':'重置参数',
            '购买成功':'重置参数',
            '重置参数':'重置参数',
            '参数已重置':'移至下一个物品',

            '神器页面已关闭':'重置参数',
            '需要换页':'进行换页',#进行换页里包含重置鼠标移动的代码
            '图金页面已切换完成':'重置参数',
            '包满了':'停止工作',
            '移至下一个物品':'重置参数',
            '停止工作':'停止工作',







        }
        handlers = action_handlers[self.current_status]
        return handlers

    def pause(self):
        """ 暂停线程 """
        self.mutex.lock()
        self.paused = True
        self.mutex.unlock()

    def resume(self):
        """ 继续线程 """
        self.mutex.lock()
        self.paused = False
        self.condition.wakeAll()  # 唤醒所有等待的线程
        self.mutex.unlock()

    def mouse_move_in_tujin(self):
        #tujin_times 加1， 鼠标移动
        cb.copy('清除剪贴板儿')
        x,y = self.tujin_items_position[self.tujin_times]
        self.tujin_times += 1
        pyautogui.moveTo(x, y, duration=self.duration_time)
        if self.tujin_times == 21:
            print('mouse_move_in_tujin(self) 坐标全用完了')
            return True
        self.current_status = '鼠标已移至物品上'
        return False

    def kill_while_with_mouse(self):
        """
        鼠标移动到区域外, 返回True
        :return: True
        """
        kx, ky = pyautogui.position()
        if kx < 325 or ky < 159:
            return True
        elif kx > 999 or ky > 870:
            return True

    def stop(self):
        """ 停止线程 """
        self._is_running = False
        self.wait()  # 等待线程结束
        # self.stopped = True
        # self.resume()  # 如果处于暂停状态，先唤醒