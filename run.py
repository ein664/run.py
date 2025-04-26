import sys
import time
import warnings
import untitled
#导入控件
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget, QMessageBox, QCheckBox)
from SAVE_INFO import JsonDataSaver
from PyQt5.QtCore import (QTimer, QSettings, Qt, QObject)
from Mouse_move import mouse_move
import pydirectinput
import pyautogui
import pandas.io.clipboard as cb
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
#导入保存控件状态类
from saveQtWidgetsState import StateSaver

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
        self.laytime = 0.1 #延时时间设置

        # 初始化状态保存器
        self.state_saver = StateSaver(self)
        #循环退出是否由杀死鼠标激活
        self.kill_window = False
        # 设置信号与槽

        self.mod1.textChanged.connect(self.mod1Save)
        self.mod2.textChanged.connect(self.mod2Save)
        self.mod3.textChanged.connect(self.mod3Save)
        self.mod4.textChanged.connect(self.mod4Save)
        self.mod5.textChanged.connect(self.mod5Save)
        self.mod6.textChanged.connect(self.mod6Save)
        self.mod7.textChanged.connect(self.mod7Save)
        self.mod8.textChanged.connect(self.mod8Save)
        self.mod9.textChanged.connect(self.mod9Save)
        self.item_name.textChanged.connect(self.item_nameSave)
        self.alteration.textChanged.connect(self.alterationSave)
        self.augmentation.textChanged.connect(self.augmentationSave)
        self.item_posi.textChanged.connect(self.item_posi_Save)

        # 获取特定文本框历史内容
        # self.primeText_plainTextEdit0 = self.loadText('plainTextEdit0')

        self.primeText_mod1 = self.loadText('mod1')
        self.primeText_mod2 = self.loadText('mod2')
        self.primeText_mod3 = self.loadText('mod3')
        self.primeText_mod4 = self.loadText('mod4')
        self.primeText_mod5 = self.loadText('mod5')
        self.primeText_mod6 = self.loadText('mod6')
        self.primeText_mod7 = self.loadText('mod7')
        self.primeText_mod8 = self.loadText('mod8')
        self.primeText_mod9 = self.loadText('mod9')
        #改造位置
        self.primeText_alteration = self.loadText('alteration')
        # 增幅位置
        self.primeText_augmentation = self.loadText('augmentation')
        # 装备位置
        self.primeText_item_posi = self.loadText('item_posi')
        self.primeText_item_name = self.loadText('item_name')


        # 设置文本框内容
        # self.plainTextEdit0.setPlainText(self.primeText_plainTextEdit0)
        self.mod1.setPlainText(self.primeText_mod1)
        self.mod2.setPlainText(self.primeText_mod2)
        self.mod3.setPlainText(self.primeText_mod3)
        self.mod4.setPlainText(self.primeText_mod4)
        self.mod5.setPlainText(self.primeText_mod5)
        self.mod6.setPlainText(self.primeText_mod6)
        self.mod7.setPlainText(self.primeText_mod7)
        self.mod8.setPlainText(self.primeText_mod8)
        self.mod9.setPlainText(self.primeText_mod9)
        self.alteration.setPlainText(self.primeText_alteration)
        self.augmentation.setPlainText(self.primeText_augmentation)
        self.item_posi.setPlainText(self.primeText_item_posi)
        self.item_name.setPlainText(self.primeText_item_name)
        self.item_name_text = self.item_name.toPlainText()
        # 按钮
        self.counter = 3
        # 按钮4关联计时器实现点击按钮，按钮禁用，按钮上数字递减
        self.pushButton_4.clicked.connect(self.start_countdown)
        self.pushButton_3.clicked.connect(self.pushButton_3_action)
        # 提取数字并赋值
        self.alteration_x, self.alteration_y = map(int, self.primeText_alteration.split(','))
        self.augmentation_x, self.augmentation_y = map(int, self.primeText_augmentation.split(','))
        self.item_x, self.item_y = map(int, self.primeText_item_posi.split(','))

        #洗多件装备时，控制位置的变量
        self.items_position = 0
        #目标词缀信息的数组
        self.mods_info = []
        #加载信息
        self.load_mods_info()
        #装备信息
        self.item_info = ''
        # 恢复之前的状态
        self.state_saver.restore_all_states(self)

        # 连接自动保存
        self.state_saver.connect_auto_save(self)

    def closeEvent(self, event):
        """窗口关闭时保存所有状态"""
        self.state_saver.save_all_states(self)
        super().closeEvent(event)

    def start_countdown(self):
        # 计时器开始工作，每1s，触发一次timeout，timeout调用update_counter
        self.pushButton_4.setEnabled(False)  # 禁用按钮防止重复点击
        self.timer.start(1000)  # 1000毫秒=1秒

    def update_counter(self):
        # 当counter<0 时，计时器停止工作
        self.pushButton_4.setText('鼠标移动' + '(' + str(self.counter) + ')')
        self.counter -= 1

        if self.counter < 0:
            self.counter = 3
            self.timer.stop()
            self.pushButton_4.setText('鼠标移动')
            # self.cmd_run()
            # 鼠标移动事件
            self.execute_mouse_action()
            self.pushButton_4.setEnabled(True)

    def execute_mouse_action(self):
        """执行鼠标操作序列
            检查是否第一次使用改造，是，更改self.IsFirstGaiZao为True，执行后续操作
            不是，直接左键点击装备
        """
        try:
            # 禁用按钮防止重复点击
            self.pushButton_4.setEnabled(False)
            QTimer.singleShot(100, lambda: [

                # 将词缀编入数组
                self.load_mods_info(),
                #开始洗装备
                self.xi_zhuangbei(),

                # print('1'),


                self.pushButton_4.setEnabled(True)  # 重新启用按钮
            ])

        except Exception as e:
            QMessageBox.critical(self, "错误", f"操作失败: {str(e)}")
            self.pushButton_4.setEnabled(True)
    def use_gaizao(self):
        """
        检查是否第一次使用改造，是，更改self.IsFirstGaiZao为True，执行后续操作
            不是，直接左键点击装备
        :return:
        """
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
            time.sleep(self.laytime)
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
        self.IsFirstGaiZao = False
        # 松开shift
        pyautogui.keyUp('shift')
        time.sleep(self.laytime)
        #移动到增幅石
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

    def xxget_item_name(self):
        # 获得物品名称
        time.sleep(0.1)  # import time
        copy_results = self.get_clipboard()
        copy_results = copy_results.split('\r\n')
        item_name = copy_results[2]
        # *************************************************************
        modifier_name = copy_results[13]  # 13

        if modifier_name == '--------':
            pass
        elif modifier_name == 'Fractured Item':
            pass
        elif modifier_name == 'b':
            pass
        else:

            print(modifier_name)  # 打印错误词缀
        return item_name, copy_results

    def load_mods_info(self):
        """
        获取非空词缀栏信息并编成数组
        :return:
        """
        if self.primeText_mod1 != '':
            self.mods_info.append(self.primeText_mod1)
        if self.primeText_mod2 != '':
            self.mods_info.append(self.primeText_mod2)
        if self.primeText_mod3 != '':
            self.mods_info.append(self.primeText_mod3)
        if self.primeText_mod4 != '':
            self.mods_info.append(self.primeText_mod4)
        if self.primeText_mod5 != '':
            self.mods_info.append(self.primeText_mod5)
        if self.primeText_mod6 != '':
            self.mods_info.append(self.primeText_mod6)
        if self.primeText_mod7 != '':
            self.mods_info.append(self.primeText_mod7)
        if self.primeText_mod8 != '':
            self.mods_info.append(self.primeText_mod8)
        if self.primeText_mod9 != '':
            self.mods_info.append(self.primeText_mod9)
        # print(self.mods_info)

    def xi_zhuangbei(self):
        """
        鼠标移至装备
        获取装备信息
        匹配
        :return:
        """
        a = [(1430, 590), (1541, 593), (1626, 596), (1729, 598), (1840, 598)]
        while True:
            #保险
            if self.kill_while_with_mouse():
                self.label_4.setText("检测到鼠标离开工作区域,程序中断")
                # QMessageBox.information(None, "Title", "检测到鼠标离开工作区域,程序中断")
                pyautogui.keyUp('shift')
                pyautogui.keyUp('ctrl')
                self.items_position = 0
                self.IsFirstGaiZao = False
                time.sleep(2)
                self.kill_window = True
                break

            self.get_item_info()

            if self.check_item():
                print('目标词缀已得到')
                pyautogui.keyUp('shift')
                self.IsFirstGaiZao = False
                break
            #否则检查装备名是否已填
            elif self.item_name_text == '':
                #装备名未填
                print('空装备名')
                continue

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
                                continue
                            else:  # 需要空后增幅，但装备不空后
                                self.use_gaizao()
                                continue


                    # print("2检查物品名是否正确，装备信息中找不到物品名称")
                    # break
                else:#不需要增幅直接改造
                    self.use_gaizao()
        #检查是否要洗多件装备，是的话更换装备，再次调用他自己
        if self.kill_window:
            #检查循环退出是否由杀死窗口提出
            self.kill_window = False
        else:
            if self.checkBox_3.isChecked():
                if self.items_position == 5:
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

                    x, y = a[self.items_position]
                    self.items_position += 1
                    if self.items_position == 6:
                        self.items_position = 0
                    # 鼠标移动至下一个位置

                    pyautogui.moveTo(x, y)
                    time.sleep(1)
                    pydirectinput.click(button="left")

                    mouse_move.mouse_mov(self, 300, 454)
                    pyautogui.keyUp('ctrl')
                    # 调用自己
                    self.xi_zhuangbei()


        #重置状态
        self.items_position = 0
        self.IsFirstGaiZao = False
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
    def item_nameSave(self):
        """
        将id与内容保存下来
        :return:
        """
        # 获取文本作为值
        text = self.item_name.toPlainText()
        # 初始化保存数据的类，并给出键
        save_text = JsonDataSaver("DataFile")
        # 调用类方法保存值
        data = {'item_name': text}
        save_text.save_data(data)
    def mod1Save(self):
        """
        将id与内容保存下来
        :return:
        """
        # 获取文本作为值
        text = self.mod1.toPlainText()
        # 初始化保存数据的类，并给出键
        save_text = JsonDataSaver("DataFile")
        # 调用类方法保存值
        data = {'mod1': text}
        save_text.save_data(data)

    def mod2Save(self):
        """
        将id与内容保存下来
        :return:
        """
        # 获取文本作为值
        text = self.mod2.toPlainText()
        # 初始化保存数据的类，并给出键
        save_text = JsonDataSaver("DataFile")
        # 调用类方法保存值
        data = {'mod2': text}
        save_text.save_data(data)

    def mod3Save(self):
        """
        将id与内容保存下来
        :return:
        """
        # 获取文本作为值
        text = self.mod3.toPlainText()
        # 初始化保存数据的类，并给出键
        save_text = JsonDataSaver("DataFile")
        # 调用类方法保存值
        data = {'mod3': text}
        save_text.save_data(data)

    def mod4Save(self):
        """
        将id与内容保存下来
        :return:
        """
        # 获取文本作为值
        text = self.mod4.toPlainText()
        # 初始化保存数据的类，并给出键
        save_text = JsonDataSaver("DataFile")
        # 调用类方法保存值
        data = {'mod4': text}
        save_text.save_data(data)

    def mod5Save(self):
        """
        将id与内容保存下来
        :return:
        """
        # 获取文本作为值
        text = self.mod5.toPlainText()
        # 初始化保存数据的类，并给出键
        save_text = JsonDataSaver("DataFile")
        # 调用类方法保存值
        data = {'mod5': text}
        save_text.save_data(data)

    def mod6Save(self):
        """
        将id与内容保存下来
        :return:
        """
        # 获取文本作为值
        text = self.mod6.toPlainText()
        # 初始化保存数据的类，并给出键
        save_text = JsonDataSaver("DataFile")
        # 调用类方法保存值
        data = {'mod6': text}
        save_text.save_data(data)
    def mod7Save(self):
        """
        将id与内容保存下来
        :return:
        """
        # 获取文本作为值
        text = self.mod7.toPlainText()
        # 初始化保存数据的类，并给出键
        save_text = JsonDataSaver("DataFile")
        # 调用类方法保存值
        data = {'mod7': text}
        save_text.save_data(data)
    def mod8Save(self):
        """
        将id与内容保存下来
        :return:
        """
        # 获取文本作为值
        text = self.mod8.toPlainText()
        # 初始化保存数据的类，并给出键
        save_text = JsonDataSaver("DataFile")
        # 调用类方法保存值
        data = {'mod8': text}
        save_text.save_data(data)
    def mod9Save(self):
        """
        将id与内容保存下来
        :return:
        """
        # 获取文本作为值
        text = self.mod9.toPlainText()
        # 初始化保存数据的类，并给出键
        save_text = JsonDataSaver("DataFile")
        # 调用类方法保存值
        data = {'mod9': text}
        save_text.save_data(data)

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