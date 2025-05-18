from PyQt5.QtCore import QObject, pyqtSignal

def add_info( new_item_name, new_item_price):
    file_path_pattern = fr'C:\PythonCode\poe\items_price.txt'
    with open(file_path_pattern, 'a', encoding='utf-8') as big_file:
        big_file.write(new_item_name+ ':'+ new_item_price+'\n')

add_info('aug2','15')


class Te(QObject):
    def __init__(self):
        super().__init__()

    # 定义一个信号，用于触发A类的D函数
    call_D_signal = pyqtSignal()
    def aaa(self):

        self.mainWindow.set_red_border()

    def C(self):
        print("B类的C函数被调用，现在将触发A类的D函数")
        self.call_D_signal.emit()  # 发射信号