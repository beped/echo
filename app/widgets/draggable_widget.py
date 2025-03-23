# app/widgets/draggable_widget.py

from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint, Qt

class DraggableWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_dragging = False
        self._drag_position = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_position = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging and event.buttons() & Qt.LeftButton:
            self.window().move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
