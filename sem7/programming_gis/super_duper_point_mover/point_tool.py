# -*- coding: utf-8 -*-

from qgis.core import QgsPointXY
from qgis.gui import QgsMapTool
from qgis.PyQt.QtCore import pyqtSignal

class PointTool(QgsMapTool):
    moved = pyqtSignal(QgsPointXY)
    clicked = pyqtSignal(QgsPointXY)

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas


    def canvasPressEvent(self, event):
        pass


    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.moved.emit(point)


    def canvasReleaseEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.clicked.emit(point)


    def activate(self):
        pass


    def deactivate(self):
        pass


    def isZoomTool(self):
        return False


    def isTransient(self):
        return False


    def isEditTool(self):
        return True