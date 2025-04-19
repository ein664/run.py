import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QColor, QMouseEvent, QPainter, QBrush, QPen, QCursor
from PyQt5.QtCore import Qt, QPoint, QRect


class PagesWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置窗口无边框、置顶
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint
        )

        # 初始窗口大小和位置
        self.setGeometry(100, 100, 300, 300)

        # 用于拖动窗口的变量
        self.dragging = False
        self.offset = QPoint()

        # 记录窗口是否正在调整大小
        self.resizing = False
        self.resize_edge = None
        self.resize_start_pos = QPoint()
        self.resize_start_geometry = QRect()

        # 边缘检测宽度
        self.resize_margin = 10

    def focusOutEvent(self, event):
        """失去焦点时关闭窗口"""
        self.close()
        super().focusOutEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            edge = self.get_resize_edge(event.pos())
            if edge:
                self.resizing = True
                self.resize_edge = edge
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self.geometry()
                self.update_cursor_shape(edge)  # 按下时锁定光标样式
            else:
                self.dragging = True
                self.offset = event.pos()
                self.setCursor(Qt.ArrowCursor)  # 拖动时使用默认光标
        elif event.button() == Qt.RightButton:
            self.close()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(event.globalPos() - self.offset)
        elif self.resizing:
            self.handle_resize(event.globalPos())
        else:
            # 实时检测边缘并更新光标
            edge = self.get_resize_edge(event.pos())
            if edge:
                self.update_cursor_shape(edge)
            else:
                self.setCursor(Qt.ArrowCursor)  # 非边缘区域恢复默认

    def update_cursor_shape(self, edge):
        """根据边缘位置更新光标形状"""
        cursor_map = {
            "left": Qt.SizeHorCursor,
            "right": Qt.SizeHorCursor,
            "top": Qt.SizeVerCursor,
            "bottom": Qt.SizeVerCursor,
            "top-left": Qt.SizeFDiagCursor,
            "bottom-right": Qt.SizeFDiagCursor,
            "top-right": Qt.SizeBDiagCursor,
            "bottom-left": Qt.SizeBDiagCursor
        }
        self.setCursor(cursor_map.get(edge, Qt.ArrowCursor))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.resizing = False
            self.print_window_info()
            # 释放后检查是否需要恢复边缘光标
            edge = self.get_resize_edge(event.pos())
            if edge:
                self.update_cursor_shape(edge)
            else:
                self.setCursor(Qt.ArrowCursor)

    def get_resize_edge(self, pos):
        """精确边缘检测（10像素范围内）"""
        rect = self.rect()
        x, y = pos.x(), pos.y()
        margin = self.resize_margin

        # 检测四个角和四条边
        if x < margin and y < margin:
            return "top-left"
        elif x > rect.width() - margin and y < margin:
            return "top-right"
        elif x < margin and y > rect.height() - margin:
            return "bottom-left"
        elif x > rect.width() - margin and y > rect.height() - margin:
            return "bottom-right"
        elif x < margin:
            return "left"
        elif x > rect.width() - margin:
            return "right"
        elif y < margin:
            return "top"
        elif y > rect.height() - margin:
            return "bottom"
        return None

    def handle_resize(self, global_pos):
        """处理窗口大小调整（保持当前光标样式）"""
        delta = global_pos - self.resize_start_pos
        geo = self.resize_start_geometry

        if self.resize_edge == "left":
            self.setGeometry(geo.x() + delta.x(), geo.y(),
                             geo.width() - delta.x(), geo.height())
        elif self.resize_edge == "right":
            self.setGeometry(geo.x(), geo.y(),
                             geo.width() + delta.x(), geo.height())
        elif self.resize_edge == "top":
            self.setGeometry(geo.x(), geo.y() + delta.y(),
                             geo.width(), geo.height() - delta.y())
        elif self.resize_edge == "bottom":
            self.setGeometry(geo.x(), geo.y(),
                             geo.width(), geo.height() + delta.y())
        elif self.resize_edge == "top-left":
            self.setGeometry(geo.x() + delta.x(), geo.y() + delta.y(),
                             geo.width() - delta.x(), geo.height() - delta.y())
        elif self.resize_edge == "top-right":
            self.setGeometry(geo.x(), geo.y() + delta.y(),
                             geo.width() + delta.x(), geo.height() - delta.y())
        elif self.resize_edge == "bottom-left":
            self.setGeometry(geo.x() + delta.x(), geo.y(),
                             geo.width() - delta.x(), geo.height() + delta.y())
        elif self.resize_edge == "bottom-right":
            self.setGeometry(geo.x(), geo.y(),
                             geo.width() + delta.x(), geo.height() + delta.y())

    def print_window_info(self):
        """打印窗口信息"""
        geo = self.geometry()
        print(f"窗口位置: ({geo.x()}, {geo.y()}), 大小: {geo.width()}x{geo.height()}")

    def paintEvent(self, event):
        """绘制半透明背景"""
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(255, 182, 193, 100)))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawRect(self.rect())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = PagesWindow()
    mainWindow.show()
    sys.exit(app.exec_())