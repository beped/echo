# app/utils/qt_waiting_spinner.py

from PyQt5.QtCore import Qt, QTimer, QSize, QRectF
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QWidget

class QtWaitingSpinner(QWidget):
    def __init__(self, parent=None, centerOnParent=True, disableParentWhenSpinning=False):
        super(QtWaitingSpinner, self).__init__(parent)

        self._color = QColor(Qt.black)
        self._roundness = 100.0
        self._minimumTrailOpacity = 31.4159265358979323846
        self._trailFadePercentage = 80.0
        self._revolutionsPerSecond = 1.57079632679489661923
        self._numberOfLines = 12
        self._lineLength = 10
        self._lineWidth = 5
        self._innerRadius = 10
        self._currentCounter = 0
        self._isSpinning = False

        self._centerOnParent = centerOnParent
        self._disableParentWhenSpinning = disableParentWhenSpinning

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.updateSize()
        self.updateTimer()
        self.hide()

    def paintEvent(self, event):
        self.updatePosition()
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self._currentCounter >= self._numberOfLines:
            self._currentCounter = 0

        painter.setPen(Qt.NoPen)
        for i in range(self._numberOfLines):
            painter.save()
            painter.translate(self._innerRadius + self._lineLength,
                              self._innerRadius + self._lineLength)
            rotateAngle = float(360 * i) / float(self._numberOfLines)
            painter.rotate(rotateAngle)
            painter.translate(self._innerRadius, 0)
            distance = self.lineCountDistanceFromPrimary(i, self._currentCounter,
                                                         self._numberOfLines)
            color = self.currentLineColor(distance, self._numberOfLines,
                                          self._trailFadePercentage, self._minimumTrailOpacity,
                                          self._color)
            painter.setBrush(color)
            painter.drawRoundedRect(QRectF(0, -self._lineWidth / 2, self._lineLength,
                                           self._lineWidth), self._roundness,
                                    self._roundness, Qt.RelativeSize)
            painter.restore()

    def start(self):
        self.updatePosition()
        self._isSpinning = True
        self.show()

        if self.parentWidget() and self._disableParentWhenSpinning:
            self.parentWidget().setEnabled(False)

        self.timer.start()

    def stop(self):
        self._isSpinning = False
        self.hide()

        if self.parentWidget() and self._disableParentWhenSpinning:
            self.parentWidget().setEnabled(True)

        self.timer.stop()

    def setNumberOfLines(self, lines):
        self._numberOfLines = lines
        self._currentCounter = 0
        self.updateTimer()

    def setLineLength(self, length):
        self._lineLength = length
        self.updateSize()

    def setLineWidth(self, width):
        self._lineWidth = width
        self.updateSize()

    def setInnerRadius(self, radius):
        self._innerRadius = radius
        self.updateSize()

    def color(self):
        return self._color

    def setColor(self, color):
        self._color = color

    def roundness(self):
        return self._roundness

    def setRoundness(self, roundness):
        self._roundness = min(0.0, max(100.0, roundness))

    def minimumTrailOpacity(self):
        return self._minimumTrailOpacity

    def setMinimumTrailOpacity(self, minimumTrailOpacity):
        self._minimumTrailOpacity = minimumTrailOpacity

    def trailFadePercentage(self):
        return self._trailFadePercentage

    def setTrailFadePercentage(self, trail):
        self._trailFadePercentage = trail

    def revolutionsPerSecond(self):
        return self._revolutionsPerSecond

    def setRevolutionsPerSecond(self, revolutionsPerSecond):
        self._revolutionsPerSecond = revolutionsPerSecond
        self.updateTimer()

    def isSpinning(self):
        return self._isSpinning

    def rotate(self):
        self._currentCounter += 1
        if self._currentCounter >= self._numberOfLines:
            self._currentCounter = 0
        self.update()

    def updateSize(self):
        size = (self._innerRadius + self._lineLength) * 2
        self.setFixedSize(QSize(size, size))

    def updateTimer(self):
        interval = int(1000 / (self._numberOfLines * self._revolutionsPerSecond))
        self.timer.setInterval(interval)


    def updatePosition(self):
        if self.parentWidget() and self._centerOnParent:
            self.move((self.parentWidget().width() - self.width()) // 2,
                      (self.parentWidget().height() - self.height()) // 2)

    def lineCountDistanceFromPrimary(self, current, primary, totalNrOfLines):
        distance = primary - current
        if distance < 0:
            distance += totalNrOfLines
        return distance

    def currentLineColor(self, countDistance, totalNrOfLines,
                         trailFadePercentage, minOpacity, colorinput):
        color = QColor(colorinput)
        if countDistance == 0:
            color.setAlphaF(1.0)
        else:
            minAlphaF = minOpacity / 100.0
            distanceThreshold = int((totalNrOfLines - 1) * trailFadePercentage / 100.0)
            if countDistance > distanceThreshold:
                color.setAlphaF(minAlphaF)
            else:
                alphaDiff = 1.0 - minAlphaF
                gradient = alphaDiff / float(distanceThreshold + 1)
                resultAlpha = 1.0 - (countDistance * gradient)
                color.setAlphaF(resultAlpha)
        return color
