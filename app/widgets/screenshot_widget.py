# app/widgets/screenshot_widget.py

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal

# Classe para a janela de seleção de área para captura de tela
class ScreenshotWidget(QtWidgets.QWidget):
    selection_made = pyqtSignal(QRect)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Selecione a área')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowOpacity(0.3)
        self.showFullScreen()
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.5);")
        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.current_rect = QRect()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
            self.rubberBand.show()

    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            rect = QtCore.QRect(self.origin, event.pos()).normalized()
            self.rubberBand.setGeometry(rect)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.current_rect = QtCore.QRect(self.origin, event.pos()).normalized()
            self.rubberBand.hide()
            self.close()
            self.selection_made.emit(self.current_rect)
