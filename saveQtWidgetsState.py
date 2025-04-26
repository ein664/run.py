import json
from PyQt5.QtWidgets import (QCheckBox, QRadioButton, QLineEdit,
                             QComboBox, QSpinBox, QDoubleSpinBox,
                             QSlider, QDial)
from PyQt5.QtCore import QSettings, Qt, QObject


class StateSaver(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("my_config.ini", QSettings.IniFormat)

    def save_all_states(self, window):
        """保存窗口中所有支持组件的状态"""
        for widget in window.findChildren(QObject):
            if isinstance(widget, QCheckBox):
                self.settings.setValue(widget.objectName(), widget.isChecked())
            elif isinstance(widget, QRadioButton):
                self.settings.setValue(widget.objectName(), widget.isChecked())
            elif isinstance(widget, QLineEdit):
                self.settings.setValue(widget.objectName(), widget.text())
            elif isinstance(widget, QComboBox):
                self.settings.setValue(widget.objectName(), widget.currentIndex())
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                self.settings.setValue(widget.objectName(), widget.value())
            elif isinstance(widget, (QSlider, QDial)):
                self.settings.setValue(widget.objectName(), widget.value())

    def restore_all_states(self, window):
        """恢复窗口中所有支持组件的状态"""
        for widget in window.findChildren(QObject):
            if isinstance(widget, QCheckBox):
                value = self.settings.value(widget.objectName())
                if value is not None:
                    widget.setChecked(value.lower() == 'true')
            elif isinstance(widget, QRadioButton):
                value = self.settings.value(widget.objectName())
                if value is not None:
                    widget.setChecked(value.lower() == 'true')
            elif isinstance(widget, QLineEdit):
                value = self.settings.value(widget.objectName())
                if value is not None:
                    widget.setText(value)
            elif isinstance(widget, QComboBox):
                value = self.settings.value(widget.objectName())
                if value is not None:
                    widget.setCurrentIndex(int(value))
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                value = self.settings.value(widget.objectName())
                if value is not None:
                    widget.setValue(float(value))
            elif isinstance(widget, (QSlider, QDial)):
                value = self.settings.value(widget.objectName())
                if value is not None:
                    widget.setValue(int(value))

    def connect_auto_save(self, window):
        """连接所有组件的状态改变信号"""
        for widget in window.findChildren(QObject):
            if isinstance(widget, (QCheckBox, QRadioButton)):
                widget.toggled.connect(lambda _, w=widget: self.save_all_states(window))
            elif isinstance(widget, QLineEdit):
                widget.textChanged.connect(lambda _, w=widget: self.save_all_states(window))
            elif isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(lambda _, w=widget: self.save_all_states(window))
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox, QSlider, QDial)):
                widget.valueChanged.connect(lambda _, w=widget: self.save_all_states(window))