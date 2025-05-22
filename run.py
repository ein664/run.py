import sys
import time
import warnings
import untitled
#导入控件
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget, QMessageBox, QCheckBox)
from SAVE_INFO import JsonDataSaver
from PyQt5.QtCore import (QTimer,QThread, QSettings, Qt, QObject,pyqtSignal)
from Mouse_move import mouse_move
import pydirectinput
import pyautogui
import pandas.io.clipboard as cb
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
#导入保存控件状态类
from saveQtWidgetsState import StateSaver
from kou_tu_jin import TuJin
class pages_window(untitled.Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(pages_window, self).__init__()
        self.setupUi(self)
        # 获取时间控制对象
        self.timer = QTimer(self)

        # 计时器开始后每1s触发一次timeout
        self.timer.timeout.connect(self.update_counter)
        # 是否第一次调用改造函数，涉及按住shift连续点击
        self.IsFirstGaiZao = False
        self.laytime = 0.04 #延时时间设置

        # 初始化状态保存器
        self.state_saver = StateSaver(self)
        #循环退出是否由杀死鼠标激活
        self.kill_window = False
        # 设置信号与槽
        for i in range(1, 10):
            # print(i)
            mod = getattr(self, f"mod{i}_1")
            mod.textChanged.connect(self.modSave)
            mod.setPlainText(self.loadText(f"mod{i}_1"))

            mod = getattr(self, f"mod{i}_1_1")
            mod.textChanged.connect(self.modSave)
            mod.setPlainText(self.loadText(f"mod{i}_1_1"))

            mod = getattr(self, f"mod{i}_2")
            mod.textChanged.connect(self.modSave)
            mod.setPlainText(self.loadText(f"mod{i}_2"))

            mod = getattr(self, f"mod{i}_2_1")
            mod.textChanged.connect(self.modSave)
            mod.setPlainText(self.loadText(f"mod{i}_2_1"))

            mod = getattr(self, f"mod{i}_3")
            mod.textChanged.connect(self.modSave)
            mod.setPlainText(self.loadText(f"mod{i}_3"))

            mod = getattr(self, f"mod{i}_3_1")
            mod.textChanged.connect(self.modSave)
            mod.setPlainText(self.loadText(f"mod{i}_3_1"))

            if i <= 4:
                mod = getattr(self, f"item_name_{i}")
                mod.textChanged.connect(self.modSave)
                mod.setPlainText(self.loadText(f"item_name_{i}"))

                mod = getattr(self, f"item_name_{i}_1")
                mod.textChanged.connect(self.modSave)
                mod.setPlainText(self.loadText(f"item_name_{i}_1"))

        #洗药剂
        for i in range(1, 18):
            mod = getattr(self, f"mod{i}_4")
            mod.textChanged.connect(self.modSave)
            mod.setPlainText(self.loadText(f"mod{i}_4"))
        for i in range(1, 13):
            mod = getattr(self, f"mod{i}_4_1")
            mod.textChanged.connect(self.modSave)
            mod.setPlainText(self.loadText(f"mod{i}_4_1"))

        self.alteration.textChanged.connect(self.alterationSave)
        self.augmentation.textChanged.connect(self.augmentationSave)
        self.item_posi.textChanged.connect(self.item_posi_Save)


        # 获取特定文本框历史内容
        # self.primeText_plainTextEdit0 = self.loadText('plainTextEdit0')

        # self.primeText_mod1 = self.loadText('mod1')
        # self.primeText_mod2 = self.loadText('mod2')
        # self.primeText_mod3 = self.loadText('mod3')
        # self.primeText_mod4 = self.loadText('mod4')
        # self.primeText_mod5 = self.loadText('mod5')
        # self.primeText_mod6 = self.loadText('mod6')
        # self.primeText_mod7 = self.loadText('mod7')
        # self.primeText_mod8 = self.loadText('mod8')
        # self.primeText_mod9 = self.loadText('mod9')
        #改造位置
        self.primeText_alteration = self.loadText('alteration')
        # 增幅位置
        self.primeText_augmentation = self.loadText('augmentation')
        # 装备位置
        self.primeText_item_posi = self.loadText('item_posi')
        # self.primeText_item_name = self.loadText('item_name')

        #价格表数据文件路径
        self.file_path_pattern = fr'C:\PythonCode\poe\items_price.txt'
        # 设置文本框内容
        # self.plainTextEdit0.setPlainText(self.primeText_plainTextEdit0)

        self.alteration.setPlainText(self.primeText_alteration)
        self.augmentation.setPlainText(self.primeText_augmentation)
        self.item_posi.setPlainText(self.primeText_item_posi)

        self.item_name_text = ''

        # 按钮
        self.counter = 3
        # 按钮4关联计时器实现点击按钮，按钮禁用，按钮上数字递减
        #按钮4 鼠标移动 是洗装备启动按钮
        self.pushButton_4.clicked.connect(self.start_countdown)
        self.pushButton_8.clicked.connect(self.start_countdown)
        self.pushButton_9.clicked.connect(self.start_countdown)
        self.pushButton_10.clicked.connect(self.start_countdown)
        self.pushButton_3.clicked.connect(self.pushButton_3_action)

        # 提取数字并赋值
        self.alteration_x, self.alteration_y = map(int, self.primeText_alteration.split(','))
        self.augmentation_x, self.augmentation_y = map(int, self.primeText_augmentation.split(','))
        self.item_x, self.item_y = map(int, self.primeText_item_posi.split(','))

        #洗多件装备时，控制位置的变量
        self.items_position = 0
        #目标词缀信息的数组
        self.mods_info = []
        #加载信息 2025/4/16 改成按完按钮才加载对应信息
        # self.load_mods_info()
        #装备信息
        self.item_info = ''
        # 恢复之前的状态
        self.state_saver.restore_all_states(self)

        #用于储存触发洗装备按钮的名称 不同tab中的 鼠标移动
        self.widget_name = ''
        #按钮对象
        self.widget = ''
        #背包位置信息
        self.a = [(1430, 590), (1541, 593), (1626, 596), (1729, 598), (1840, 598)]
        self.b = [(1381, 590), (1426, 596), (1485, 594), (1537, 594), (1584, 596), (1637, 597), (1683, 597), (1736,597),(1785, 597), (1844, 602), (1877, 597), (1335, 696), (1381, 692), (1427, 692), (1483, 694), (1528, 694),(1574, 695), (1635, 696), (1676, 693), (1777, 694), (1823, 698), (1862, 698)]
        self.c = [(1337, 592), (1427, 587), (1525, 591), (1623, 596), (1725, 591), (1831, 593), (1334, 698), (1450, 691), (1532, 687), (1627, 686), (1719, 689), (1831, 684)]
        # 连接自动保存
        self.state_saver.connect_auto_save(self)
        #创建工作线程
        self.TuJin = TuJin()
        #TuJin线程在找不到价格时发送信号，触发红框提示要添加价格
        self.TuJin.call_D_signal.connect(self.set_red_border)
        #砍图金按钮 触发tujin线程中的run函数，开始工作
        self.pushButton_6.clicked.connect(self.start_process)
        # pushButton_5添加新物品，添加新物品后，解锁阻塞的线程时期继续运行
        self.pushButton_5.clicked.connect(self.add_new_items)
        #关闭
        self.pushButton_7.clicked.connect(self.tujin_stop)

        self.thread = QThread()
        self.worker = self.TuJin
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

    def toggle_pause(self):
        """ 暂停/继续按钮切换 """
        if self.TuJin.paused:
            #触发Tujin线程的resume()继续函数，使线程继续运行
            self.TuJin.resume()  # 如果已暂停，则继续
        else:
            self.TuJin.pause()  # 如果运行中，则暂停
    def tujin_stop(self):
        #能用鼠标点击按钮触发该函数，主线程一定是挂起的
        self.set_black_border()
        self.TuJin.current_status = '停止工作'#requestInterruption()
        if self.TuJin.paused :
            self.toggle_pause()


        # self.TuJin.wait()
    def start_process(self):
        """ 开始按钮点击事件 """
        #自动调用重写的run方法
        time.sleep(3)
        self.TuJin._is_running = True
        print('self.TuJin._is_running'+str(self.TuJin._is_running))
        print('self.TuJin.start()')
        self.TuJin.start()  # 启动工作线程


    def add_new_items(self):
        itemName = self.itemName1.toPlainText()
        itemPrice = self.itemPrice.toPlainText()

        with open(self.file_path_pattern, 'a', encoding='utf-8') as big_file:
            big_file.write(itemName + ':' + itemPrice + '\n')
        self.itemName1.setPlainText('')
        self.itemPrice.setPlainText('')
        self.set_black_border()
        time.sleep(3)#睡眠3s后触发线程阻塞/继续函数
        self.TuJin.current_status = '已添加物品及价格'
        self.toggle_pause()



    def set_red_border(self):
        #用于图金页边框变红
        self.frame_square.setStyleSheet("""
            QFrame#frame_square {
                background-color: transparent;
                border: 3px solid red;
            }
        """)

    def set_black_border(self):
        #用于图金页边框变黑
        self.frame_square.setStyleSheet("""
               QFrame#frame_square {
                   background-color: transparent;
                   border: 1px solid black;
               }
           """)

    def closeEvent(self, event):
        """窗口关闭时保存所有状态"""
        self.TuJin.stop()
        self.state_saver.save_all_states(self)
        super().closeEvent(event)

    def start_countdown(self):
        #获取触发计时器的组件名称
        self.widget = QApplication.instance().sender()
        self.widget_name = self.widget.objectName()

        # 计时器开始工作，每1s，触发一次timeout，timeout调用update_counter
        self.widget.setEnabled(False)  # 禁用按钮防止重复点击
        self.timer.start(1000)  # 1000毫秒=1秒

    def update_counter(self):
        # 当counter<0 时，计时器停止工作

        self.widget.setText('鼠标移动' + '(' + str(self.counter) + ')')
        self.counter -= 1

        if self.counter < 0:
            self.counter = 3
            self.timer.stop()
            self.widget.setText('鼠标移动')


            match self.widget_name:
                case 'pushButton_4':
                    #获取该页装备名称
                    self.item_name_text = self.item_name_1.toPlainText()
                    self.mods_info = []

                    # 将词缀编入数组
                    for i in range(1, 10):
                        self.get_mods_info(f"mod{i}")
                    self.label_69.setText(str(self.mods_info))
                    self.execute_mouse_action()


                case 'pushButton_8':
                    self.item_name_text = self.item_name_2.toPlainText()
                    # 将词缀编入数组
                    self.mods_info = []
                    for i in range(1, 10):
                        self.get_mods_info(f"mod{i}_2")
                    self.label_68.setText(str(self.mods_info))
                    self.execute_mouse_action()

                case 'pushButton_9':
                    self.item_name_text = self.item_name_3.toPlainText()
                    # 将词缀编入数组
                    self.mods_info = []
                    for i in range(1, 10):
                        self.get_mods_info(f"mod{i}_3")
                    self.label_72.setText(str(self.mods_info))
                    self.execute_mouse_action()

                case 'pushButton_10':
                    # self.item_name_text = self.item_name_4.toPlainText()
                    # 将词缀编入数组
                    self.mods_info = []
                    for i in range(1, 18):
                        self.get_mods_info(f"mod{i}_4")
                    self.label_74.setText(str(self.mods_info))
                    #调用洗药剂
                    self.yaoji_execute_mouse_action()
                case _:
                    print('baocuo')


            self.widget_name = ''

            self.widget.setEnabled(True)

    def execute_mouse_action(self):
        """执行鼠标操作序列
            检查是否第一次使用改造，是，更改self.IsFirstGaiZao为True，执行后续操作
            不是，直接左键点击装备
        """
        try:
            # 禁用按钮防止重复点击
            self.widget.setEnabled(False)
            QTimer.singleShot(100, lambda: [


                #开始洗装备
                self._xi_zhuangbei(),

                self.widget.setEnabled(True)  # 重新启用按钮
            ])

        except Exception as e:
            QMessageBox.critical(self, "错误", f"操作失败: {str(e)}")
            self.widget.setEnabled(True)
    def yaoji_execute_mouse_action(self):
        """执行鼠标操作序列
            检查是否第一次使用改造，是，更改self.IsFirstGaiZao为True，执行后续操作
            不是，直接左键点击装备
        """
        try:
            # 禁用按钮防止重复点击
            self.widget.setEnabled(False)
            QTimer.singleShot(100, lambda: [


                #开始洗装备
                self.xi_yaoji(),

                self.widget.setEnabled(True)  # 重新启用按钮
            ])

        except Exception as e:
            QMessageBox.critical(self, "错误", f"操作失败: {str(e)}")
            self.widget.setEnabled(True)
    def use_gaizao(self):
        """
        检查是否第一次使用改造，是，更改self.IsFirstGaiZao为True，执行后续操作
            不是，直接左键点击装备
        :return:
        """
        if self.kill_while_with_mouse():
            self.progessOver()
        else:
            if self.IsFirstGaiZao == False:
                # 移动鼠标到指定位置
                # 移至改造
                pydirectinput.moveTo(self.alteration_x, self.alteration_y)
                # 点击改造    使用QTimer实现延迟点击（避免阻塞主线程）
                pydirectinput.click(button="right"),

                # 按住shift
                pyautogui.keyDown('shift')
                # 移至装备
                pydirectinput.moveTo(self.item_x, self.item_y)
                time.sleep(0.01)
                # 左键点击
                pydirectinput.click(button="left")
                self.IsFirstGaiZao = True
            else:
                # 移至装备
                pydirectinput.moveTo(self.item_x, self.item_y)
                # 左键点击
                pydirectinput.click(button="left")
    def use_zengfu(self):
        """
            更改self.IsFirstGaiZao为False
            松开shift
            0.1s
            移动到增幅石
            0.1s
            右键点击
            0.1s
            移动到装备
            0.1s
            左键点击
            :return:
        """
        if self.kill_while_with_mouse():
            self.progessOver()
        else:
            self.IsFirstGaiZao = False
            # 松开shift
            pyautogui.keyUp('shift')
            time.sleep(self.laytime)
            # 移动到增幅石
            pydirectinput.moveTo(self.augmentation_x, self.augmentation_y)
            time.sleep(self.laytime)
            # 右键点击
            pydirectinput.click(button="right")
            time.sleep(self.laytime)
            # 移动到装备
            pydirectinput.moveTo(self.item_x, self.item_y)
            time.sleep(self.laytime)
            # 左键点击
            pydirectinput.click(button="left")
            time.sleep(self.laytime)


    def get_mods_info(self, widget):
        """
        获取非空词缀栏信息并编成数组
        :return:
        """
        Text_Edit_Obj = getattr(self, widget)
        text = Text_Edit_Obj.toPlainText()
        if text != '':
            self.mods_info.append(text)

    def xi_zhuangbei(self,callback):
        """
        鼠标移至装备
        获取装备信息
        匹配
        :return:
        """
        while True:
            #保险
            if self.kill_while_with_mouse():
                self.progessOver()
                break
            #获取装备信息
            self.get_item_info()
            #检测装备词缀是否为目标词缀
            if self.check_item():
                print('目标词缀已得到')
                pyautogui.keyUp('shift')
                self.IsFirstGaiZao = False
                break
            # 在装备没有目标词缀时
            #否则检查装备名是否已填
            elif self.item_name_text == '':
                #装备名未填
                print('空装备名')
                continue
            #在装备没有目标词缀时
            #装备名已填，继续确认需不需要增幅
            else:
                self.item_info = self.item_info.split('\r\n')
                #检查是否要空前增幅
                if self.checkBox_1.isChecked():
                    # 已确认需要空前增幅
                    # 检查是否空前物品信息列表一行一行开抽

                    for line in self.item_info:
                        if self.item_name_text in line:
                        # 检查物品名是否在该行
                            line = line.strip()  # 移除首尾空白字符
                            index = line.find(self.item_name_text)
                            # 检查前面是否有非空白字符
                            front_empty = (index == 0)

                            # 检查后面是否有非空白字符
                            back_empty = (index + len(self.item_name_text) == len(line))
                            if front_empty:  # 确认空前
                                self.use_zengfu()  # 上增幅
                            elif back_empty:  # 不空前就检查是否空后
                                #确认空后
                                if self.checkBox_2.isChecked():  # 确认是否要空后增幅
                                    #确认空后且需要空后增幅
                                    self.use_zengfu()
                                    continue
                                else:#确认空后但不需要空后增幅
                                    self.use_gaizao()
                                    continue
                            else:#既不空前也不空后
                                self.use_gaizao()
                                continue
                    #for循环跑完都没发现物品名称
                    # print("检查物品名是否正确，装备信息中找不到物品名称")
                    # break
                # 不需要空前增幅
                # 检查是否要空后增幅
                elif self.checkBox_2.isChecked():
                    # 已确认要空后增幅
                    # 开始抽物品信息
                    for line in self.item_info:
                        # 物品名在该行
                        if self.item_name_text in line:
                            line = line.strip()  # 移除首尾空白字符
                            index = line.find(self.item_name_text)
                            # 检查后面是否有非空白字符
                            back_empty = (index + len(self.item_name_text) == len(line))
                            if back_empty:
                                # 确认空后
                                self.use_zengfu()
                                #结束本轮循环，防止触发后面洗多件装备；开启新一轮循环匹配词缀
                                continue
                            else:  # 需要空后增幅，但装备不空后
                                self.use_gaizao()
                                #结束本轮循环，防止触发后面洗多件装备；开启新一轮循环匹配词缀
                                continue


                    # print("2检查物品名是否正确，装备信息中找不到物品名称")
                    # break
                else:#不需要增幅直接改造
                    self.use_gaizao()

        #检查是否要洗多件装备，是的话更换装备，再次调用他自己
        if self.kill_window:
            #由鼠标位置触发，检查循环退出是否由杀死窗口提出
            self.kill_window = False
        else:
            if self.checkBox_3.isChecked():
                self.oneXsix(self.a, callback)
            elif self.checkBox_4.isChecked():
                self.twoXtwelve(self.b,callback)
            elif self.checkBox_5.isChecked():
                self.twoXtwelve(self.c,callback)


        #重置状态
        self.items_position = 0
        self.IsFirstGaiZao = False
############################################################################################
    def old_xi_zhuangbei(self):
        """
        鼠标移至装备
        获取装备信息
        匹配
        :return:
        """

        # 保险
        if self.kill_while_with_mouse():
            m = '停止工作'
        else:
            pydirectinput.moveTo(self.item_x, self.item_y)
            # 获取装备信息
            self.get_item_info()

            # 检测装备词缀是否为目标词缀
            if self.check_item():
                # 发现目标词缀
                m = '发现目标词缀'
            # 在装备没有目标词缀时，检查装备名是否已填
            elif self.item_name_text == '':
                # 装备名未填
                m = '空装备名'
            # 在装备没有目标词缀时，装备名已填，继续确认需不需要增幅
            else:

                self.item_info = self.item_info.split('\r\n')
                # 检查是否要空前增幅
                if self.checkBox_1.isChecked():
                    # 需要空前增幅,检查是否空前
                    m = self.is_if_have_empty_modifier()
                    if m == '空前':
                        m = '增幅'
                    else:
                        m = '改造'
                # 不需要空前增幅.检查是否要空后增幅
                elif self.checkBox_2.isChecked():
                    # 需要空后增幅，检查是否空后
                    m = self.is_if_have_empty_modifier()
                    if m == '空后':
                        m = '增幅'
                    else:
                        m = '改造'
                else:  # 不需要增幅直接改造
                    m = '改造'
        match m:
            case '改造':
                self.use_gaizao()#_xi_zhuangbei
                time.sleep(0.01)
                self._xi_zhuangbei()
            case '增幅':
                self.use_zengfu()
                time.sleep(self.laytime)
                self._xi_zhuangbei()
            case '发现目标词缀':
                print('目标词缀已得到')
                pyautogui.keyUp('shift')
                self.IsFirstGaiZao = False
                self.xi_duo_jian_zhuangbei(self._xi_zhuangbei)
            case '空装备名':
                print('空装备名')
            case '停止工作':
                self.progessOver()
        #重置状态
        self.items_position = 0
        self.IsFirstGaiZao = False

    def _xi_zhuangbei(self):
        """装备处理方法（字典映射版）"""
        action_handlers = {
            '改造': self._handle_gaizao,
            '增幅': self._handle_zengfu,
            '发现目标词缀': self._handle_found_target,
            '空装备名': self._handle_empty_name,
            '停止工作': self._handle_stop_work,
        }
        #这小代码整的，只能说ds牛逼坏了
        while True:
            m = self._determine_action()  # 提取判断逻辑到单独方法
            handler = action_handlers.get(m)
            if not handler:
                print(f"未知操作: {m}")
                break
            if handler():  # 返回 False 时继续循环，返回True,退出循环
                break

    def _determine_action(self):
        """判断当前应该执行什么操作"""
        if self.kill_while_with_mouse():
            return '停止工作'

        pydirectinput.moveTo(self.item_x, self.item_y)
        self.get_item_info()

        if self.check_item():
            return '发现目标词缀'
        if self.item_name_text == '':
            return '空装备名'

        self.item_info = self.item_info.split('\r\n')
        if self.checkBox_1.isChecked():
            m = self.is_if_have_empty_modifier()
            return '增幅' if m == '空前' else '改造'
        elif self.checkBox_2.isChecked():
            m = self.is_if_have_empty_modifier()
            return '增幅' if m == '空后' else '改造'
        else:
            return '改造'

    def _handle_gaizao(self):
        """处理改造操作"""
        self.use_gaizao()
        time.sleep(0.01)
        return False  # 继续循环

    def _handle_zengfu(self):
        """处理增幅操作"""
        self.use_zengfu()
        time.sleep(self.laytime)
        return False  # 继续循环

    def _handle_found_target(self):
        """发现目标词缀"""
        print('目标词缀已得到')
        pyautogui.keyUp('shift')
        self.IsFirstGaiZao = False
        self.xi_duo_jian_zhuangbei(self._xi_zhuangbei)
        return True  # 退出循环

    def _handle_empty_name(self):
        """空装备名处理"""
        print('空装备名')
        return True  # 退出循环

    def _handle_stop_work(self):
        """停止工作"""
        self.progessOver()
        return True  # 退出循环
############################################################################################

    def xi_yaoji(self):
        """
        鼠标移至药剂
        获取装备信息
        匹配
        :return:
        """

        # 保险
        if self.kill_while_with_mouse():
            m = '停止工作'
        else:
            pydirectinput.moveTo(self.item_x, self.item_y)
            # 检测装备词缀是否为目标词缀
            yaoji_modifiers = self.check_yaoji()
            if yaoji_modifiers == 2:
                # 发现目标词缀
                m = '发现目标词缀'
            # 在装备没有目标词缀时，检查装备名是否已填

            elif yaoji_modifiers == 1:
                m = '增幅'
            else:
                m = '改造'

        match m:
            case '改造':
                self.use_gaizao()
                time.sleep(self.laytime-0.01)
                self.xi_yaoji()
            case '增幅':

                self.use_zengfu()
                time.sleep(self.laytime)
                yaoji_modifiers = self.check_yaoji()
                if yaoji_modifiers ==2:
                    print('目标词缀已得到')
                    pyautogui.keyUp('shift')
                    pyautogui.keyUp('ctrl')
                    self.IsFirstGaiZao = False
                    self.xi_duo_jian_zhuangbei(self.xi_yaoji)
                else:
                    self.use_gaizao()
                    self.xi_yaoji()
            case '发现目标词缀':
                print('目标词缀已得到')
                pyautogui.keyUp('shift')
                pyautogui.keyUp('ctrl')
                self.IsFirstGaiZao = False
                #触发洗多件装备鼠标移动后触发洗药剂函数检测
                self.xi_duo_jian_zhuangbei(self.xi_yaoji)
            case '空装备名':
                print('空装备名')
            case '停止工作':
                pyautogui.keyUp('shift')
                pyautogui.keyUp('ctrl')
                self.IsFirstGaiZao = False
                self.progessOver()
            # 重置状态
        self.items_position = 0
        self.IsFirstGaiZao = False


    def xi_duo_jian_zhuangbei(self, callback):
        # 检查是否要洗多件装备，是的话更换装备，再次调用他自己
        if self.checkBox_3.isChecked():
            self.oneXsix(self.a, callback)

        elif self.checkBox_4.isChecked():
            self.twoXtwelve(self.b, callback)
        elif self.checkBox_5.isChecked():
            self.twoXtwelve(self.c, callback)

    def is_if_have_empty_modifier(self):
        for line in self.item_info:
            # 检查物品名是否在该行
            if self.item_name_text in line:
                line = line.strip()  # 移除首尾空白字符
                index = line.find(self.item_name_text)
                # 检查前面是否有非空白字符
                front_empty = (index == 0)
                # 检查后面是否有非空白字符
                back_empty = (index + len(self.item_name_text) == len(line))
                if front_empty:  # 确认空前
                    return '空前'
                elif back_empty:  # 不空前就检查是否空后
                    return '空后'
                else:  # 既不空前也不空后
                    return '改造'

        print('is_if_have_empty_modifier未找到物品名')
    def if_need_zengfu(self):
        pass

    def progessOver(self):
        self.label_4.setText("检测到鼠标离开工作区域,程序中断")
        # QMessageBox.information(None, "Title", "检测到鼠标离开工作区域,程序中断")
        pyautogui.keyUp('shift')
        pyautogui.keyUp('ctrl')
        self.items_position = 0
        self.IsFirstGaiZao = False
        self.kill_window = True

    def twoXtwelve(self, posi, callback ):
        """
        操纵鼠标在背包中移动并点击的函数
        :param posi:位置数组
        :return:
        """
        if self.items_position == len(posi):
            self.items_position = 0
            pyautogui.keyUp('shift')
            pyautogui.keyUp('ctrl')
            self.IsFirstGaiZao = False
        else:
            # 鼠标移动，点击
            # 通过全局变量self.items_position控制鼠标点击位置
            # 释放shift
            pyautogui.keyUp('shift')

            # 重置改造状态函数
            self.IsFirstGaiZao = False
            # 按下ctrl
            pyautogui.keyDown('ctrl')
            # 将装备放回背包
            pydirectinput.click(button="left")

            x, y = posi[self.items_position]
            self.items_position += 1
            # 鼠标移动至下一个位置

            pyautogui.moveTo(x, y)
            time.sleep(self.laytime)
            pydirectinput.click(button="left")

            mouse_move.mouse_mov(self, 300, 454)
            pyautogui.keyUp('ctrl')
            callback()
    def oneXsix(self,posi,callback):
        if self.items_position == len(posi):
            self.items_position = 0
        else:
            # 鼠标移动，点击
            # 通过全局变量self.items_position控制鼠标点击位置
            # 释放shift
            pyautogui.keyUp('shift')

            # 重置改造状态函数
            self.IsFirstGaiZao = False
            # 按下ctrl
            pyautogui.keyDown('ctrl')
            # 将装备放回背包
            pydirectinput.click(button="left")

            x, y = posi[self.items_position]
            self.items_position += 1
            if self.items_position == 6:
                self.items_position = 0
            # 鼠标移动至下一个位置

            pyautogui.moveTo(x, y)
            time.sleep(self.laytime)
            pydirectinput.click(button="left")

            mouse_move.mouse_mov(self, 300, 454)
            pyautogui.keyUp('ctrl')
            # 调用自己
            callback()


    def call_after(func_to_call):
        #装饰器 函数结束后调用其他函数
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)  # 执行原函数
                    return result
                finally:
                    func_to_call()  # 无论原函数是否报错，都会在结束后调用

            return wrapper

        return decorator

    def kill_while_with_mouse(self):
        """
                    if kill_while_with_mouse() == True:
                    # records_item_msg_from_tujin(a_list, filename='stor_itme_info')
                    input('<func_main()>检测到鼠标离开工作区域,程序中断')
                    time.sleep(5)
                    break
        鼠标移动到区域外, 返回True
        :return: True
        """
        self.widget_name = ''
        kx, ky = pyautogui.position()
        # if kx < 325 or ky < 159:
        #     return True
        if kx > 670 or ky > 739:
            return True

    def check_item(self):
        """
        与装备信息相比较
        返回True/False
        :return:
        """
        # 从目标词缀池中抽词缀
        for mod in self.mods_info:
            if mod in self.item_info:
                self.label_4.setText(self.item_info + mod)
                return True
        #for结束没true， 返回false
        return False
    def check_yaoji(self):
        """
        与装备信息相比较
        返回True/False
        :return:
        """
        # 从目标词缀池中抽词缀
        self.get_item_info()
        i = 0
        for mod in self.mods_info:
            if mod in self.item_info:
                # self.label_4.setText(self.item_info + mod)
                i += 1
        return i
    def get_item_info(self):
        """
            鼠标移至装备处
            ctrl+c
            为self.item_info赋值
            导包import pandas.io.clipboard as cb
        """
        cb.copy('111')
        pydirectinput.moveTo(self.item_x, self.item_y)
        time.sleep(0.05)
        # print('time.sleep')
        self.simulate_keyboard_ctrl_c()
        time.sleep(0.05)

        #从剪贴板黏贴值至item_info
        self.item_info = cb.paste()

    def simulate_keyboard_ctrl_c(self):
        """
        用于复制的函数
        :return:
        """
        pyautogui.hotkey("ctrl", "c")
        time.sleep(random.randint(8, 13) * 0.01)

    def loadText(self, target_key):
        """
        建立JsonDataSaver实例，通过它
        寻找并返回json文件中target_key对应的值
        :param target_key:
        :return: text
        """
        # 建立类实例
        save_text = JsonDataSaver("DataFile")
        # 调用类方法保存值
        text = save_text.search_key_in_json(target_key)  # target_key
        return text

    def alterationSave(self):
        """
        保存改造位置，当改造位置改变时触发
        将id与内容保存下来
        :return:
        """
        # 获取文本作为值
        text = self.alteration.toPlainText()
        # 初始化保存数据的类，并给出键
        save_text = JsonDataSaver("DataFile")
        # 调用类方法保存值
        data = {'alteration': text}
        save_text.save_data(data)

    def augmentationSave(self):
        """
        将id与内容保存下来
        :return:
        """
        # 获取文本作为值
        text = self.augmentation.toPlainText()
        # 初始化保存数据的类，并给出键
        save_text = JsonDataSaver("DataFile")
        # 调用类方法保存值
        data = {'augmentation': text}
        save_text.save_data(data)

    def item_posi_Save(self):
        """
        将id与内容保存下来
        :return:
        """
        # 获取文本作为值
        text = self.item_posi.toPlainText()
        # 初始化保存数据的类，并给出键
        save_text = JsonDataSaver("DataFile")
        # 调用类方法保存值
        data = {'item_posi': text}
        save_text.save_data(data)

    #item_nameSave


    def modSave(self):
        """
        将id与内容保存下来
        :return:
        """
        #获取被触发的组件对象
        button = QApplication.instance().sender()
        #获取组件对象名称
        # button_name = button.objectName()
        # 获取文本作为值
        try:
            #获取text文本
            text = button.toPlainText()
            # 初始化保存数据的类，并给出键
            save_text = JsonDataSaver("DataFile")
            # 调用类方法保存值
            data = {button.objectName(): text}
            save_text.save_data(data)
        except:
            print('modSave-wrong')

    def display_page1(self):
        self.stackedWidget.setCurrentIndex(0)

    def display_page2(self):
        self.stackedWidget.setCurrentIndex(1)

    def display_page3(self):
        self.stackedWidget.setCurrentIndex(2)

    def cmd_run(self):
        # 运行程序主体
        try:
            # 代码
            # input('输入任意键程序启动, 按t结束程序')
            mouse = mouse_move()
            mouse.mouse_mov(106, 277)
            mouse.mouse_click()
            # self.label_4.setText('运行结束')
            print('运行结束')

        except Exception as e:
            # ZMailObject('程序报错')#发邮件
            # self.label_4.setText(str(e))
            print(str(e))
            QMessageBox.information(None, "Title", "程序报错"),  # 弹出窗口 程序报错
    def pushButton_3_action(self):

        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = pages_window()
    # 下面untitled是刚通过ui文件生成的py文件，Ui_MainWindow()是其中的一个类
    mainWindow.show()
    sys.exit(app.exec_())