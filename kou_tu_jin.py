import pyautogui
import pydirectinput
import time
import pandas.io.clipboard as cb
from ctypes import *
import re
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from PyQt5.QtCore import QObject, pyqtSignal
import random
from datetime import date
import zmail


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
        self.action_handlers_func = {

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
            '处理裂隙戒指':self.deal_breach_ring,
            '处理圣甲虫':self.deal_scarab,
            '处理地图':self.deal_map,
            '处理孕育石':self.deal_incubator,
            '处理星团珠宝':self.deal_cluster_jewel,
            '处理技能石':self.deal_gems,
            '处理蓝图':self.deal_blueprint,
            '处理地图碎片':self.deal_map_fragments,
            '处理深渊珠宝':self.abyss_jew,
            '清理背包':self.clean_stash,
            '重新获取神器数量':self.retry_get_artifact_number,

        }
        self.action_handlers = {
            '0':'加载价格表',#状态0代表程序刚开始运行
            '已载入数据包':'移至下一个物品',
            '鼠标已移至物品上':'获取物品信息',
            '已获取物品信息':'抽取物品名称','获取物品信息失败':'获取物品信息',

            '已取得物品名称':'获取物品种类',
            '已获取物品种类': '排除特殊种类物品',

            '没有需要特殊处理的物品':'查找物品价格',
            '裂隙戒指':'处理裂隙戒指',
            '圣甲虫':'查找物品价格',#'处理圣甲虫'
            '地图': '处理地图',
            '圣油':'重置参数',
            '孕育石':'处理孕育石',
            '星团珠宝':'处理星团珠宝',
            '技能石':'处理技能石',
            '蓝图':'处理蓝图',
            '地图碎片':'处理地图碎片',
            '深渊珠宝':'处理深渊珠宝',

            '未找到物品价格':'添加物品及价格',
            '因价格缺失未找到物品价格':'移至下一个物品',
            '已取得物品价格':'获取神器种类及数量',
            '已获取神器种类及数量': '判断是否购买',
            '已添加物品及价格':'更新价格表',
            '价格表已更新':'移至下一个物品',
            '获取神器数量失败':'重新获取神器数量',


            '购买':'购买',  '放弃购买':'关闭神器页面',

            '购买完毕':'重置参数',
            '购买成功':'重置参数',
            '重置参数':'重置参数',
            '参数已重置':'移至下一个物品',

            '神器页面已关闭':'重置参数',
            '需要换页':'进行换页',#进行换页里包含重置鼠标移动的代码
            '图金页面已切换完成':'重置参数',
            '包满了':'清理背包',#'停止工作'
            '移至下一个物品':'重置参数',
            '停止工作':'停止工作',


        }

        self._json = {}
        self.x = 377
        self.y = 292
        self.current_status = '0'
        self.get_item_info_fail_times = 0

        #记录赚了多少总c数，总神器数，神器种类，翻了几次页
        self.data_record = [{'次级总c':0,'次级神器数':0},{'高级总c':0,'高级神器数':0},
                            {'至高总c':0,'至高神器数':0},{'卓越总c':0,'卓越神器数':0},{'翻页数':0}]

        #动作停顿时间
        self.duration_time = 0.03+random.randint(1,3)*0.02
        #关闭购买页面按钮的位置
        self.close_artifact_page_button_position = (808, 223)
        #图金页面左侧两列通货坐标
        self.tujin_items_position = [(374, 293), (378, 343), (381, 394), (377, 441), (369, 484), (375, 536), (375, 579), (373, 633), (373, 678), (370, 734), (371, 782), (428, 292), (434, 355), (430, 401), (429, 439), (421, 490), (422, 537), (423, 583), (418, 632), (417, 683), (423, 744), (421, 781)]
        #背包格子坐标
        self.position = [(1336, 598), (1334, 648), (1332, 689), (1335, 734), (1329, 799), (1386, 598), (1393, 645),
                    (1386, 688), (1383, 737), (1380, 794), (1432, 594), (1435, 643), (1441, 707), (1438, 746),
                    (1425, 801), (1478, 597), (1491, 650), (1488, 693), (1478, 749), (1484, 795), (1537, 595),
                    (1531, 643), (1530, 693), (1527, 748), (1532, 804), (1582, 593), (1587, 643), (1586, 699),
                    (1581, 753), (1584, 796), (1629, 597), (1630, 650), (1630, 696), (1632, 744), (1632, 800),
                    (1678, 597), (1680, 650), (1681, 702), (1681, 748), (1685, 799), (1726, 594), (1732, 650),
                    (1736, 698), (1733, 756), (1733, 803), (1778, 595), (1777, 645), (1780, 694), (1782, 757),
                    (1791, 809), (1829, 589), (1831, 647), (1831, 704), (1830, 746), (1824, 790), (1869, 599),
                    (1876, 645), (1877, 693), (1877, 739), (1883, 794)]
        self.change_page_position = (941, 841)#图金换页位置
        self.price_box = (688, 733)#代币价格栏
        self.count = 0.65

        #记录软件对通货的判断行为
        self.print_currency_date = {}#用于记录购买时物品信息，价格，神器数等，已弃用

        self.tiaoShi = ''

        self.filter_item_names = ['Contract', 'Armourer', 'Essence', 'Orb of Chance',
                                  'Blacksmith\'s Whetstone', 'Orb of Transmutation', 'Orb of Alchemy',
                                  'Orb of Horizons', 'Harbinger\'s Shard', 'Orb of Binding']

        self.tujin_times = 0#记录取到第几个图金的位置了
        #线程相关
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.paused = False
        self.stopped = False

        #黑镰神器折算c
        self.lesser_artifiact = 0.025#50个换1c是0.02，代币多就调高数值，神器多就减小数值
        self.greater_artifiact = 0.017#应该和次级差不多
        self.exceptional_artifiact = 0.01#0.046
        self.grand_artifiact = 0.128

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
        self.prime_text = ''#用于存储剪贴板原始内容

    def reset_pamar(self):
        self.print_currency_date = {}#用于记录购买时物品信息，价格，神器数等，已弃用
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
        self.prime_text = ''

    def sent_signal(self):
        #发射信号用的函数
        self.call_D_signal.emit()

    def get_item_Class(self):
        for result in self.copy_results:
            self.item_Class = re.search(r'Item Class: (.*)', result).group()
            if self.item_Class:
                # self.print_currency_date['物品种类'] = self.item_Class
                self.current_status = '已获取物品种类'
                return False
        print('种类不详')
        return True

        # 成功购买一次就清零购买失败的频率

    def get_item_name(self):
        """
        从self.copy_results中获取物品名称
        :return:
        """
        #空字符串为假


        if self.copy_results:

            for result in self.copy_results:
                if re.findall('--', result):
                    break
                # 保存该次循环的前一个结果,即该次循环匹配到----就break了, item_name 的值是上次循环的
                self.item_name = result
                # self.print_currency_date['name'] = self.item_name
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
        #正则空格敏感
        item_number = re.findall(r"Stack Size: (\d+)/", self.prime_text)
        # a_result格式是字符串，不是列表
        if item_number:
            self.item_number = int(item_number[0])
        else:
            self.item_number = 1



    def get_item_level(self):
        for a_result in self.copy_results:
            item_level = re.findall(r"Item Level:(\d+)", a_result)
            if item_level:
                self.item_level = int(item_level[0])
                self.current_status = '已获取物品等级'
            else:
                self.current_status = '获取物品等级失败'
        return False

    def load_date_file(self,file_path=r"C:\PythonCode\poe\items_price_2.txt"):
        # 载入数据文件

        with open(file_path, 'r',encoding='utf-8') as f:
            for line in f:
                if line:
                    # 假设每行包含键值对，如 "key:value"
                    try:
                        # key, value = line.strip().split(':')
                        key = re.findall(r"name:\s*['\"](.*?)['\"],", line)
                        if key:
                            value = re.findall(r"(?:chaosValue|chaosEquivalent):\s*([\d.]+)", line)
                            self.lookup[key[0]] = value[0]
                        else:
                            pass
                    except Exception as e :
                        print('load_date_file:',e)
                        print('载入数据文件报错')
                        self.stop()
                        return True

        self.current_status = '已载入数据包'
        return False
    def reload_date_file(self):
        # 重新载入数据文件

        self.load_date_file()
        self.tujin_times -= 1
        self.current_status = '价格表已更新'
        return False

    def mouse_mov(self,x, y, duration=0.15):
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
        self.prime_text = cb.paste()
        #获取剪贴板并返回
        self.copy_results = self.get_clipboard()
        if self.copy_results[0] == '清除剪贴板儿':
            self.current_status = '获取物品信息失败'
            return False
        self.get_item_info_fail_times_2 = 0
        self.get_item_info_fail_times = 0
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
        pyautogui.moveTo(949, 844, duration = 0.3)
        pydirectinput.click()
        return '已换页'
    def _buy_item(self):
        pass

    def find_item_price(self):
        # 获取物品价格
        result = self.lookup.get(self.item_name, None)
        # self.print_currency_date['物品价格：'] = result

        if result == None:
            # print(self.item_name+":未在价格表中出现")
            self.current_status = '因价格缺失未找到物品价格'#'未找到物品价格'
            return False

        self.item_price = float(result)
        self.current_status = '已取得物品价格'
        return False

    def add_item_and_price(self):
        ##添加物品价格后重新运行程序
        #向主线程发送信号，使其出现红框提示添加新的物品及价格
        # ZMailObject('未知物品需要添加价格')
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

        try:
            self.artifact_number = int(a)
            return False
            # self.print_currency_date['神器数量：'] = self.artifact_number
        except Exception as e :
            print('get_artifact_number:', e)
            self.current_status = '获取神器数量失败'
            return False

    def retry_get_artifact_number(self):
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

        try:
            self.artifact_number = int(a)
            return False
        except Exception as e:
            print('retry_get_artifact_number:',e)
            self.current_status = '停止工作'
            return False

    def get_artifact_type(self):
        pixel = self.get_pixel(649, 663)
        # 4 527116
        # 3 2105887
        # 2 2105374
        # 1 13683638
        if pixel == 527116:
            # print('<get_artifact_type>         4卓越神器')
            self.artifact_type = 4
            # self.print_currency_date['神器种类：'] = '卓越'
        elif pixel == 2105887:
            # print('<get_artifact_type>         3至高神器')
            self.artifact_type = 3
            # self.print_currency_date['神器种类：'] = '至高'
        elif pixel == 2105374:
            # print('<get_artifact_type>         2高级神器')
            self.artifact_type = 2
            # self.print_currency_date['神器种类：'] = '高级'
        elif pixel == 13683638:
            # print('<get_artifact_type>         1次级神器')
            self.artifact_type = 1
            # self.print_currency_date['神器种类：'] = '次级'
        else:
            # ZMailObject()  # 发邮件
            if self.kill_while_with_mouse():
                print('<func_main()>检测到鼠标离开工作区域,程序中断')

                time.sleep(2)
                self.current_status = '停止工作'
            else:
                print('<get_artifact_type>报错, 未匹配到先祖通货类型')
                self.stop()

    def record_price(self):
        #物品名，价格，堆叠，神器数目，神器种类
        with open(r'C:\PythonCode\pyqt\Record_price.txt', 'a', encoding='utf-8') as big_file:
            big_file.write(self.item_name + ':' + str(self.item_price) +' '+'堆叠:'+str(self.item_number)+' '
                           +'神器:'+str(self.artifact_number)+' '+'神器种类:'+str(self.artifact_type)+'\n')


    def buy_is_or_not(self):
        #通货=多少c，乘以堆叠数量 等于这一堆儿通货的价值；

        #算出每个神器约等于多少c，神器数量除以通货总价 大于某个值就买
        try:
            self.item_price = float(self.item_price)
        except:
            print('报错def buy_is_or_not(self):')
            self.item_price = 0
        self.get_item_number()
        #记录价格
        # self.record_price()
        items_total_price = self.item_number*self.item_price
        # print('items_total_price:'+str(items_total_price))


        if items_total_price == 0:
            artifact_convert_chaos= 0
            # self.print_currency_date['神器/混沌：'] = artifact_convert_chaos
        else:#35=1c 0.0028
            artifact_convert_chaos = round(items_total_price / self.artifact_number, 5)
            # self.print_currency_date['神器/混沌：'] = artifact_convert_chaos
        # print('\n'+'item_name:'+self.item_name)
        # print('artifact_convert_chaos:'+str(artifact_convert_chaos))
        # print('self.lesser_artifiact:'+str(self.lesser_artifiact))
        # print('self.artifact_type:' + str(self.artifact_type))
        items_total_price = round(items_total_price,2)
        match self.artifact_type:
            case 1:
                # print('1')

                if artifact_convert_chaos >= self.lesser_artifiact:
                    self.current_status = '购买'

                    self.record_data(number=0, kind_1='次级总c',kind_2='次级神器数',items_total_price=items_total_price,
                                     artifact_number=self.artifact_number)

                    # self.print_currency_date['判断结果：'] = self.current_status
            case 2:
                if artifact_convert_chaos >= self.greater_artifiact:
                    self.current_status = '购买'

                    self.record_data(number=1, kind_1='高级总c',kind_2='高级神器数', items_total_price=items_total_price,
                                     artifact_number=self.artifact_number)

                    # self.print_currency_date['判断结果：'] = self.current_status
            case 3:
                if artifact_convert_chaos >= self.exceptional_artifiact:
                    self.current_status = '购买'

                    self.record_data(number=2, kind_1='至高总c',kind_2='至高神器数', items_total_price=items_total_price,
                                     artifact_number=self.artifact_number)

                    # self.print_currency_date['判断结果：'] = self.current_status
            case 4:
                if artifact_convert_chaos >= self.grand_artifiact:
                    self.current_status = '购买'

                    self.record_data(number=3, kind_1='卓越总c',kind_2='卓越神器数', items_total_price=items_total_price,
                                     artifact_number=self.artifact_number)

                # self.print_currency_date['判断结果：'] = self.current_status
        if self.current_status != '购买':
            self.current_status = '放弃购买'
            # self.print_currency_date['判断结果：'] = self.current_status
        # print(self.current_status)
        # if self.tiaoShi == '通货':
        #     print(self.print_currency_date)
        return False

    def record_data(self,number=0, kind_1='次级总c',kind_2='次级神器数',items_total_price=0,
                    artifact_number=0,turn_page = 0):
        #用于记录买了多少c，花了多少神器
        #在停止工作状态下，自动记录，每翻页10次自动记录
        #from datetime import date

        self.data_record[number][kind_1] += round(items_total_price,2)
        self.data_record[number][kind_2] += round(artifact_number,2)
        self.data_record[4]['翻页数'] += turn_page
        today = date.today()

        # 停止工作时，自动记录
        if self.current_status == '停止工作':
            try:
                with open(fr'C:\PythonCode\pyqt\{today}.txt', 'a', encoding='utf-8') as big_file:
                    big_file.write(self.data_record.__str__() + '\n')
            except Exception as e:
                print('record_data:', e)

        #每翻页10次，自动记录
        if self.data_record[4]['翻页数']>=50:

            try:
                with open(fr'C:\PythonCode\pyqt\{today}.txt', 'a', encoding='utf-8') as big_file:
                    big_file.write(self.data_record.__str__() + '\n')
                    big_file.write('\n'+'*************************************************' + '\n' + '\n' )

                #清零
                self.data_record[0]['次级总c'] = 0
                self.data_record[0]['次级神器数'] = 0

                self.data_record[1]['高级总c'] = 0
                self.data_record[1]['高级神器数'] = 0

                self.data_record[2]['至高总c'] = 0
                self.data_record[2]['至高神器数'] = 0

                self.data_record[3]['卓越总c'] = 0
                self.data_record[3]['卓越神器数'] = 0

                self.data_record[4]['翻页数'] = 0
                # self.current_status = '停止工作'

            except Exception as e:
                print('record_data:',e)



    def buy(self):

        match self.buy_times:
            case 0:
                self.buy_times += 1
                self.buy_action(0.65)
                time.sleep(0.2)
                if self.check_if_buy_success():
                    self._handle_buy_success()
                else:
                    # print("第一次购买失败")
                    self._retry_buy()

            case 1:
                self.buy_times += 1
                self.buy_action(0.55)
                time.sleep(0.2)
                if self.check_if_buy_success():
                    self._handle_buy_success()
                else:
                    # print("第2次购买失败")
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
                    # print("第3次购买失败")
                    self._retry_buy()

            case 3:
                self.buy_times = 0
                print('包满了')
                # ZMailObject('包满了')
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
        # 取色判断是否购买成功729, 396处颜色(729, 396), RGB: (93, 93, 94)
        pixel = self.get_pixel(729, 396)
        # print(pixel)
        # if 成功 break
        # 不等于6184285说明购买成功
        if pixel != 263429:
            # d = 2 / 3
            # print('false pix')
            return False
        else:
            # print('true pix')
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
        #count为砍价力度
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
        #记录换页次数
        self.record_data(turn_page=1)
        time.sleep(0.7)

        return False
    def delete_special_item(self):
        if 'Support Gems' in self.item_Class or 'Skill Gems' in self.item_Class:
            self.current_status = '技能石'
            # self.print_currency_date['物品种类：'] = self.current_status
            return False
        if 'Rings' in self.item_Class:
            self.current_status = '裂隙戒指'
            # self.print_currency_date['物品种类：'] = self.current_status
            return False
        if 'Scarab' in self.item_name:
            self.current_status = '圣甲虫'
            # self.print_currency_date['物品种类：'] = self.current_status
            return False
        if 'Map' in self.item_name:
            self.current_status = '地图'
            # self.print_currency_date['物品种类：'] = self.current_status
            return False
        if 'Oil' in self.item_name:
            self.current_status = '圣油'
            # self.print_currency_date['物品种类：'] = self.current_status
            return False
        if 'Incubator' in self.item_name:
            self.current_status = '孕育石'
            # self.print_currency_date['物品种类：'] = self.current_status
            return False
        if 'Cluster' in self.item_name:
            self.current_status = '星团珠宝'
            # self.print_currency_date['物品种类：'] = self.current_status
            return False
        if 'Blueprint' in self.item_name:
            self.current_status = '蓝图'
            # self.print_currency_date['物品种类：'] = self.current_status
            return False
        if 'Item Class: Map Fragments' in self.copy_results:
            self.current_status = '地图碎片'
            # self.print_currency_date['物品种类：'] = self.current_status
            return False
        if 'Eye Jewel'in self.item_name:
            self.current_status = '深渊珠宝'
            # self.print_currency_date['物品种类：'] = self.current_status
            return False

        self.current_status = '没有需要特殊处理的物品'
        # self.print_currency_date['物品种类：'] = self.current_status
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
        #处理圣甲虫
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
    def deal_map_fragments(self):
        self.item_price = 1
        self.current_status = '已取得物品价格'
        return False
    def abyss_jew(self):
        self.item_price = 0.001
        self.current_status = '已取得物品价格'
        return False
    def deal_cluster_jewel(self):
        text = cb.paste()

        item_level_line = [line for line in text.split('\n') if 'Item Level:' in line][0]
        item_level = int(item_level_line.split(':')[1].strip())

        adds_line = [line for line in text.split('\n') if line.startswith('Adds')][0]
        adds_number = int(adds_line.split()[1])

        if item_level >=84 and adds_number >=11:
            print('应该购买大星团')
            self.current_status = '已取得物品价格'
            self.item_price = 150
            return False
        self.current_status = '重置参数'
        return False
    def deal_blueprint(self):
        self.item_price = 20
        self.current_status = '已取得物品价格'
        return False
#Quality: +19%
    def deal_gems(self):

        if self.item_name == 'Enlighten Support':
            self.item_price = 320
            self.current_status = '已取得物品价格'
            # self.print_currency_date['宝石过滤，设定价格：']=320
            return False
        if self.item_name == 'Empower Support':
            self.item_price = 320
            self.current_status = '已取得物品价格'
            # self.print_currency_date['宝石过滤，设定价格：']=320

            return False
        if self.item_name == 'Enhance Support':
            self.item_price = 320
            self.current_status = '已取得物品价格'
            # self.print_currency_date['宝石过滤，设定价格：']=320
            return False

        #不是赋予、启蒙、增幅，则根据品质换算c
        text = cb.paste()
        try:
            text_quality = [line for line in text.split('\n') if 'Quality:' in line][0]
            quality = int(re.findall(r'\d+', text_quality)[0])
        except:
            quality = 0
        self.item_name = 'Gemcutter\'s Prism'
        self.find_item_price()
        if quality ==20:
            self.current_status = '已取得物品价格'

        else:
            self.item_price = round((self.item_price / 70) * quality, 5)
            self.current_status = '已取得物品价格'
        return False

        #round((self.item_price / 20) * quality, 2)
        # print('gem_quality:'+str(quality))
        # print('gem_pirce:'+str(self.item_price))


    def clean_stash(self):
        #清理背包
        pyautogui.keyDown('esc')
        time.sleep(0.3)
        pyautogui.keyUp('esc')
        time.sleep(0.3)
        pyautogui.keyDown('esc')
        time.sleep(0.3)
        pyautogui.keyUp('esc')
        #鼠标移动到stash上，点开仓库
        pyautogui.moveTo(966, 491, duration=0.2)
        pyautogui.click()

        #按下ctrl
        pyautogui.keyDown('ctrl')
        z = 0
        a = True
        while a:
            x, y = self.position[z]
            z += 1
            if z == 60:
                break

            pyautogui.moveTo(x, y, duration=0.15)
            # 此处为软件停止功能，鼠标每移动到一个位置后，经过0.1s后再次获取鼠标位置
            # 若位置不一样则软件退出
            pos = pyautogui.position()  # 该函数获取鼠标位置
            if (pos.x, pos.y) == (x, y):
                pass
            else:
                pyautogui.keyUp('ctrl')
                a = False

            pydirectinput.click()  # 鼠标左键点击

        # pyautogui.keyUp('ctrl')

        # 鼠标移动到图金上，ctrl点击
        pyautogui.moveTo(989, 358, duration=0.2)

        pyautogui.click()

        self.current_status = '移至下一个物品'
        self.tujin_times = 0  # 记录取到第几个图金的位置了




    def run(self):
        #主线程执行函数

        # print(self._is_running)
        while self._is_running:

            # 暂停检查区块（需要线程安全）
            self.mutex.lock()

            if self.paused:
                # 如果暂停，则等待（会释放mutex，被唤醒时重新获取）
                self.condition.wait(self.mutex)
            self.mutex.unlock()

            # self.tiaoShi = '通货'

            m = self._determine_action()  # 提取判断逻辑到单独方法
            # print(m)
            #m内储存由def _determine_action(self):返回来的，下一步该干什么，由下面代码在action_handlers_func中找对应的函数
            handler = self.action_handlers_func.get(m)
            # print('handler :'+handler.__str__())
            if not handler:
                #检测handler是否由对应的函数来执行
                print(f"未知操作: {m}")
                break
            if handler():  # 返回 False 时继续循环，返回True,退出循环
                #执行函数的默认返回值都为False，特殊情况需要强行停止该程序返回值为True
                break
    def _determine_action(self):
        #返回一个handers，用于判断下一步该干什么

        if self.kill_while_with_mouse():
            print('<func_main()>检测到鼠标离开工作区域,程序中断')

            time.sleep(2)
            self.current_status ='停止工作'

        if self.current_status =='停止工作':
            # 调用记录函数，记录买了多少c，花了多少神器
            if self.data_record[4]['翻页数'] ==0:
                pass
            else:
                self.record_data()

        if self.current_status == '获取物品信息失败':
            self.get_item_info_fail_times += 1
            self.get_item_info_fail_times_2 += 1
            if self.get_item_info_fail_times_2 > 2:
                self.current_status = '移至下一个物品'
                self.get_item_info_fail_times_2 = 0
            if self.get_item_info_fail_times > 7:
                self.get_item_info_fail_times = 0
                # print('需要换页')
                self.current_status = '需要换页'
                ##重置鼠标位置##
                self.tujin_times = 0


        if self.current_status == '获取物品等级失败':
            ##失败未添加处理的代码##
            self.current_status = '已获取物品等级'
        # print('self.current_status:'+self.current_status)

        try:

            handlers = self.action_handlers[self.current_status]
        except Exception as e:
            print('_determine_action:',e)
            handlers = '停止工作'


        # print('_determine_action:',handlers)

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
            self.current_status = '需要换页'
            return False
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

        self.tujin_times = 0
        self.reset_pamar()
        self._is_running = False
        self.finished.emit()
        return True
        # self.wait()  # 等待线程结束
        # self.stopped = True
        # self.resume()  # 如果处于暂停状态，先唤醒
