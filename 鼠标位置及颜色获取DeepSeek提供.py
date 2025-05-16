import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout,
                             QWidget, QPushButton, QHBoxLayout, QTextEdit,
                             QScrollArea, QComboBox, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QColor, QPixmap, QPainter, QKeySequence
import pyautogui
from PIL import ImageGrab
import colorsys


class ColorPickerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("高级颜色拾取器")
        self.setFixedSize(650, 600)

        # 初始化变量
        self.current_rgb = (255, 255, 255)
        self.current_pos = (0, 0)
        self.color_format = "RGB"
        self.is_active = False  # 标记程序是否处于活动状态

        # 主控件和布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # 创建控制按钮区域
        self.create_control_section()

        # 创建监测区域
        self.create_monitor_section()

        # 创建颜色格式选择区域
        self.create_format_selector()

        # 创建记录区域
        self.create_record_section()

        # 设置快捷键
        self.setup_shortcuts()

        # 启动定时器(但不立即开始工作)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)

    def create_control_section(self):
        """创建控制按钮区域"""
        control_group = QGroupBox("程序控制")
        self.main_layout.addWidget(control_group)
        control_layout = QHBoxLayout(control_group)

        self.toggle_button = QPushButton("开始监测 (F5)")
        self.toggle_button.setStyleSheet("font-weight: bold;")
        self.toggle_button.clicked.connect(self.toggle_monitoring)
        control_layout.addWidget(self.toggle_button)

    def create_monitor_section(self):
        """创建监测区域"""
        monitor_group = QGroupBox("实时监测")
        self.main_layout.addWidget(monitor_group)
        monitor_layout = QVBoxLayout(monitor_group)

        # 坐标显示
        self.coord_label = QLabel("坐标: (0, 0)")
        self.coord_label.setAlignment(Qt.AlignCenter)
        self.coord_label.setStyleSheet("font-size: 16px;")
        monitor_layout.addWidget(self.coord_label)

        # 颜色显示区域
        self.color_display = QLabel()
        self.color_display.setFixedSize(120, 120)
        self.color_display.setStyleSheet("border: 2px solid black; background-color: #f0f0f0;")
        monitor_layout.addWidget(self.color_display, alignment=Qt.AlignCenter)

        # 颜色值显示
        self.color_value_label = QLabel("")
        self.color_value_label.setAlignment(Qt.AlignCenter)
        self.color_value_label.setStyleSheet("font-size: 14px; color: gray;")
        monitor_layout.addWidget(self.color_value_label)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.copy_button = QPushButton("复制颜色值 (Ctrl+C)")
        self.copy_button.clicked.connect(self.copy_color_value)
        self.copy_button.setEnabled(False)
        self.record_button = QPushButton("记录当前信息 (F2)")
        self.record_button.clicked.connect(self.record_current_info)
        self.record_button.setEnabled(False)
        btn_layout.addWidget(self.copy_button)
        btn_layout.addWidget(self.record_button)
        monitor_layout.addLayout(btn_layout)

    def create_format_selector(self):
        """创建颜色格式选择区域"""
        format_group = QGroupBox("颜色表示方式")
        self.main_layout.addWidget(format_group)
        format_layout = QHBoxLayout(format_group)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["RGB", "HEX", "HSV", "HSL", "CMYK"])
        self.format_combo.currentTextChanged.connect(self.change_color_format)
        self.format_combo.setEnabled(False)
        format_layout.addWidget(QLabel("选择格式:"))
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()

    def create_record_section(self):
        """创建记录区域"""
        record_group = QGroupBox("记录的信息 (F2键记录)")
        self.main_layout.addWidget(record_group)
        record_layout = QVBoxLayout(record_group)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.record_text = QTextEdit()
        self.record_text.setReadOnly(True)
        self.scroll_area.setWidget(self.record_text)
        record_layout.addWidget(self.scroll_area)

        self.clear_button = QPushButton("清空记录")
        self.clear_button.clicked.connect(self.clear_records)
        record_layout.addWidget(self.clear_button)

    def setup_shortcuts(self):
        """设置快捷键"""
        self.copy_shortcut = QKeySequence(Qt.CTRL + Qt.Key_C)
        self.copy_button.setShortcut(self.copy_shortcut)
        self.record_shortcut = QKeySequence(Qt.Key_F2)
        self.record_button.setShortcut(self.record_shortcut)
        self.toggle_shortcut = QKeySequence(Qt.Key_F5)
        self.toggle_button.setShortcut(self.toggle_shortcut)

    def toggle_monitoring(self):
        """切换监测状态"""
        self.is_active = not self.is_active

        if self.is_active:
            self.timer.start(100)
            self.toggle_button.setText("停止监测 (F5)")
            self.toggle_button.setStyleSheet("font-weight: bold; color: red;")
            self.color_value_label.setStyleSheet("font-size: 14px; color: black;")
            self.copy_button.setEnabled(True)
            self.record_button.setEnabled(True)
            self.format_combo.setEnabled(True)
        else:
            self.timer.stop()
            self.toggle_button.setText("开始监测 (F5)")
            self.toggle_button.setStyleSheet("font-weight: bold; color: green;")
            self.color_value_label.setText("程序未激活")
            self.color_value_label.setStyleSheet("font-size: 14px; color: gray;")
            self.copy_button.setEnabled(False)
            self.record_button.setEnabled(False)
            self.format_combo.setEnabled(False)

    def update_data(self):
        """更新鼠标位置和颜色信息"""
        if not self.is_active:
            return

        pos = pyautogui.position()
        self.current_pos = (pos.x, pos.y)
        self.coord_label.setText(f"({pos.x}, {pos.y})")

        try:
            # 获取所有屏幕的完整截图
            screen = ImageGrab.grab(all_screens=True)
            rgb = screen.getpixel((pos.x, pos.y))
            self.current_rgb = rgb

            # 更新颜色显示
            color = QColor(*rgb)
            pixmap = QPixmap(self.color_display.size())
            pixmap.fill(color)
            self.color_display.setPixmap(pixmap)

            # 更新颜色值文本
            self.update_color_value_label(rgb)
        except Exception as e:
            pass

    def update_color_value_label(self, rgb):
        """根据选择的格式更新颜色值显示"""
        r, g, b = rgb
        if self.color_format == "RGB":
            text = f"RGB: ({r}, {g}, {b})"
        elif self.color_format == "HEX":
            text = f"HEX: #{r:02x}{g:02x}{b:02x}".upper()
        elif self.color_format == "HSV":
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            text = f"HSV: ({h * 360:.1f}°, {s * 100:.1f}%, {v * 100:.1f}%)"
        elif self.color_format == "HSL":
            h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            text = f"HSL: ({h * 360:.1f}°, {s * 100:.1f}%, {l * 100:.1f}%)"
        elif self.color_format == "CMYK":
            k = 1 - max(r / 255, g / 255, b / 255)
            if k == 1:
                c, m, y = 0, 0, 0
            else:
                c = (1 - r / 255 - k) / (1 - k)
                m = (1 - g / 255 - k) / (1 - k)
                y = (1 - b / 255 - k) / (1 - k)
            text = f"CMYK: ({c * 100:.1f}%, {m * 100:.1f}%, {y * 100:.1f}%, {k * 100:.1f}%)"

        # self.color_value_label.setText(text)

    def change_color_format(self, format_name):
        """更改颜色表示格式"""
        self.color_format = format_name
        if self.is_active:
            self.update_color_value_label(self.current_rgb)

    def copy_color_value(self):
        """复制当前颜色值"""
        if not self.is_active:
            return

        clipboard = QApplication.clipboard()
        clipboard.setText(self.color_value_label.text().split(": ")[1])
        self.copy_button.setText("已复制!")
        QTimer.singleShot(1000, lambda: self.copy_button.setText("复制颜色值 (Ctrl+C)"))

    def record_current_info(self):
        """记录当前信息"""
        if not self.is_active:
            return

        info = f"{self.coord_label.text()}, {self.color_value_label.text()}\n"
        self.record_text.append(info)

    def clear_records(self):
        """清空记录"""
        self.record_text.clear()

    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key_F2 and self.is_active:
            self.record_current_info()
        elif event.key() == Qt.Key_F5:
            self.toggle_monitoring()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """关闭事件"""
        self.timer.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ColorPickerApp()
    window.show()
    sys.exit(app.exec_())