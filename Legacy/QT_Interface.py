
from PyQt5.QtWidgets import QWidget,QApplication, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QSizePolicy
from PyQt5.QtCore import QThreadPool
import sys

import numpy as np

import time

import matplotlib as mpl
mpl.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_wxagg import \
#     FigureCanvasWxAgg as FigureCanvas, \
#     NavigationToolbar2WxAgg as NavigationToolbar

import pyqtgraph as pg

sys.path.append("/Users/oneminimax/Documents/Projets Programmation")

from AsciiFileReader.Readers import GenericDataReader as Reader
from HotDataFollowerQt import DataFileFollower

class DataHandle(object):

    def __init__(self,HDV,dataFile):

        self.HDV = HDV
        self.dataFile = dataFile
        self.follower = DataFileFollower(dataFile)
        self.follower.newDataSignal.connect(self.updatePlot)
        self.following = False

        self.color = None

    def setDataPlot(self,dataPlot):

        self.dataPlot = dataPlot

    def follow(self):

        self.follower.start()
        self.following = True

    def stopFollow(self):

        self.follower.stop()
        self.following = False

    def updatePlot(self):

        self.HDV.updatePlot(self)

    def getXY(self,XFieldName,YFieldName):

        X = self.dataFile.getFieldByName(XFieldName)
        Y = self.dataFile.getFieldByName(YFieldName)
        
        return X,Y

class HotDataViewer(QWidget):

    colorList = [
        'red',
        'blue',
        'green',
        'orange',
        'pink',
        'plum']

    def __init__(self):
        super().__init__()

        self.dataHandleList = list()
        self.numberOfData = 0

        self.AxisFieldNameList = list()
        self.XAxisFieldName = None
        self.YAxisFieldName = None

        self.XAutoLim = True
        self.YAutoLim = True

        self.xplotlim = [0,1]
        self.yplotlim = [0,1]

        self._initUI()

    def __del__(self):

        print('close')

    def _initUI(self):

        self.setGeometry(300, 300, 700, 500)
        self.setWindowTitle('Hot Data Viewer')

        self._makeWidgets()
        self._makeLayout()
        self._makeConnect()

    def _makeWidgets(self):
        
        self.buttonOpenFile = QPushButton("Open File")
        self.buttonFollowFile = QPushButton("Follow File")

        self.figure = Figure(facecolor=(0.9,0.9,0.9,1))
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_axes((0.1,0.1,0.8,0.8))

    def _makeLayout(self):

        self.buttonOpenFile.resize(self.buttonOpenFile.sizeHint())
        self.buttonFollowFile.resize(self.buttonFollowFile.sizeHint())

        hbox = QHBoxLayout()
        hbox.addWidget(self.buttonOpenFile)
        hbox.addWidget(self.buttonFollowFile)
        hbox.addStretch(1)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.canvas)
        vbox.addLayout(hbox)

        self.setLayout(vbox) 

        self.show()

    def _makeConnect(self):

        self.buttonOpenFile.clicked.connect(self.onButtonOpenFile)
        self.buttonFollowFile.clicked.connect(self.onButtonFollowFile)

    def onButtonOpenFile(self):

        filePath = QFileDialog.getOpenFileName(self, 'Open File')[0]

        if filePath:
        
            newDataHandle = self.newDataHandle(filePath)
            self.addDataHandle(newDataHandle)
            self.updatePlotLim()
            self.canvas.draw()

    def onButtonFollowFile(self):

        filePath = QFileDialog.getOpenFileName(self, 'Open File')[0]

        if filePath:
        
            newDataHandle = self.newDataHandle(filePath)
            self.addDataHandle(newDataHandle)
            newDataHandle.follow()
            self.updatePlotLim()
            self.canvas.draw()
                
    def newDataHandle(self,filePath):

        dataFile = Reader(filePath,' ',['index','value'])

        return DataHandle(self,dataFile)

    def addDataHandle(self,newDataHandle):

        if len(self.dataHandleList) == 0:
            self.AxisFieldNameList = newDataHandle.dataFile.getFieldNameList()
            self.XAxisFieldName = self.AxisFieldNameList[0]
            self.YAxisFieldName = self.AxisFieldNameList[1]
            addIt = True
        else:
            duplicate = False
            for dataHandle in self.dataHandleList:
                if dataHandle.dataFile.filePath == newDataHandle.dataFile.filePath:
                    duplicate = True
                    break
            
            if duplicate:
                addIt = False
                print('File already opened')
            # If the datafile contains the same field name
            elif set(self.AxisFieldNameList) == set(newDataHandle.dataFile.getFieldNameList()):
                addIt = True
            else:
                addIt = False

        if addIt:
            self.dataHandleList.append(newDataHandle)
            self.newPlot(newDataHandle)
            self.numberOfData += 1

    def newPlot(self,dataHandle):

        dataHandle.color = self.colorList[self.numberOfData]
        X,Y = dataHandle.getXY(self.XAxisFieldName,self.YAxisFieldName)
        dataPlot = self.axes.plot(X, Y, color = dataHandle.color, linestyle = "solid", marker = "o")[0]
        dataHandle.setDataPlot(dataPlot)

        return dataPlot

    def updatePlot(self,dataHandle):

        X,Y = self.getXY(dataHandle.dataFile)

        dataHandle.dataPlot.set_xdata(X)
        dataHandle.dataPlot.set_ydata(Y)

        self.updatePlotLim()
        # self.updateAxesLabel()
        self.canvas.draw()

    def getXYDataLimit(self):

        minXList = list()
        maxXList = list()
        minYList = list()
        maxYList = list()

        for dataHandle in self.dataHandleList:
            X,Y = dataHandle.getXY(self.XAxisFieldName,self.YAxisFieldName)
            minXList.append(X.min())
            maxXList.append(X.max())
            minYList.append(Y.min())
            maxYList.append(Y.max())

        xplotlim = [np.array(minXList).min(),np.array(maxXList).max()]
        yplotlim = [np.array(minYList).min(),np.array(maxYList).max()]

        return xplotlim, yplotlim

    def updatePlotLim(self):

        xplotlim, yplotlim = self.getXYDataLimit()

        if self.XAutoLim:
            self.xplotlim = xplotlim
            xmargin = 0.02 * (self.xplotlim[1] - self.xplotlim[0])
            self.axes.set_xlim((self.xplotlim[0] - xmargin,self.xplotlim[1] + xmargin))
        else:
            pass

        if self.YAutoLim:
            self.yplotlim = yplotlim
            ymargin = 0.02 * (self.yplotlim[1] - self.yplotlim[0])
            self.axes.set_ylim((self.yplotlim[0] - ymargin,self.yplotlim[1] + ymargin))
        else:
            pass

    # def updateAxesLabel(self):

    #     dataFile =  self.dataFileList[self.currentDataFileIndex]
    #     fieldNameList = dataFile.nameList
    #     unitNameList = dataFile.unitList

    #     XLabel = '{0:s} ({1:s})'.format(fieldNameList[self.XAxisIndex],unitNameList[self.XAxisIndex])
    #     YLabel = '{0:s} ({1:s})'.format(fieldNameList[self.YAxisIndex],unitNameList[self.YAxisIndex])

    #     self.axes.set_xlabel(XLabel)
    #     self.axes.set_ylabel(YLabel)



def main():
    app = QApplication(sys.argv)
    HDV = HotDataViewer()
    HDV.show()
    sys.exit(app.exec_())






if __name__ == '__main__':
    main()

