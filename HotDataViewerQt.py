
from PyQt5.QtWidgets import QWidget,QApplication, QMainWindow,QLabel,QLineEdit, QPushButton, QCheckBox, QComboBox, QLayout, QHBoxLayout, QVBoxLayout, QGridLayout, QFileDialog, QColorDialog
from PyQt5.QtCore import QThreadPool, Qt
import sys

import numpy as np

import time

import pyqtgraph as pg

# from pint import UnitRegistry

sys.path.append("/Users/oneminimax/Documents/Projets Programmation")

from AsciiDataFile.Readers import MDDataFileReader as Reader
from AsciiDataFile.HotReader import HotReader
from HotDataFollowerQt import DataFileFollower, DataPathFollower
import UnitModule as UM

# default_path = r'/Users/maximedion/Documents/Projets Physique/2019/PCCO Hall/Data Files/20180705A/isotherms'
default_path = r'/Users/maximedion/Documents/Projets Programmation/HotData/Data'

class DataHandle(object):

    def __init__(self,HDV,dataReader):

        self.HDV = HDV
        self.dataReader = dataReader

        self.column_names = self._get_column_names()
        self.column_units = self._get_column_units()
        
        self.follower = DataFileFollower(dataReader)
        self.follower.newDataSignal.connect(self.newData)
        self.following = False

        self.pen = pg.mkPen()
        
        self.maxValues = np.zeros((len(self.column_names),))
        self.dataPlot = []
        self.dataItem = []

        self.description = self.follower.getDescription()
        self.visible = True

    def __del__(self):
        
        if self.dataPlot:
            del(self.dataPlot)
        if self.dataItem:
            del(self.dataItem)

    def _get_column_names(self):

        return self.dataReader.data_container.get_column_names()

    def _get_column_units(self):

        unitLabelList = self.dataReader.data_container.get_column_units()
        column_units = list()
        for unitLabel in unitLabelList:
            column_units.append(UM.makeUnit(unitLabel))

        return column_units

    def setDataPlot(self,dataPlot):

        self.dataPlot = dataPlot

    def setDataItem(self,dataItem):

        self.dataItem = dataItem

    def setColor(self,color):

        self.pen.setColor(color)
        self.dataPlot.setPen(self.pen)

    def follow(self):

        if not self.following:
            self.follower.start()
            self.following = True
        else:
            self.follower.unpause()

    def pauseFollow(self):

        self.follower.pause()

    def stopFollow(self):

        if self.following:
            self.follower.stop()
            self.following = False

    def newData(self):

        self.HDV.updatePlot(self)

    def show(self):

        if not self.visible:
            self.HDV.axes.addItem(self.dataPlot)
            self.visible = True

    def hide(self):

        if self.visible:
            self.HDV.axes.removeItem(self.dataPlot)
            self.visible = False

    def getXY(self,XFieldName,YFieldName):

        X = self.dataReader.data_container.get_column_by_name(XFieldName)
        Y = self.dataReader.data_container.get_column_by_name(YFieldName)
        
        return X,Y

    def remove(self):

        self.HDV.removeDataHandle(self)

class HotDataViewer(QMainWindow):

    colorList = [
        'red',
        'blue',
        'green',
        'orange',
        'pink',
        'plum']

    def __init__(self,app):
        super().__init__()

        self.app = app

        self.dataHandleList = list()
        self.numberOfData = 0

        self.AxisFieldNameList = list()
        self.AxisFieldUnitList = list()
        self.XAxisFieldName = None
        self.YAxisFieldName = None

        self.Xdatalim = [0,1]
        self.Ydatalim = [0,1]

        self.Xscale = 1
        self.Yscale = 1

        self.folderFollowerList = list()

        self._initUI()

    def __del__(self):

        print('close')

    def _initUI(self):

        self.setGeometry(300, 300, 700, 500)
        self.setWindowTitle('Hot Data Viewer')
        self.setStyleSheet("background-color: black;")

        self._makeWidgets()
        self._makeLayout()
        self._makeConnect()

    def _makeWidgets(self):

        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)
        
        self.buttonOpenFile = QPushButton("Open File",self.cw)
        self.buttonFollowFile = QPushButton("Follow File",self.cw)
        self.buttonFollowFolder = QPushButton("Follow Folder",self.cw)

        self.buttonSelectData = QPushButton("Select Data")
        self.buttonSelectAxis = QPushButton("Select Axis")

        self.buttonOpenFile.setStyleSheet("background-color: gray;")
        self.buttonFollowFile.setStyleSheet("background-color: gray;")
        self.buttonFollowFolder.setStyleSheet("background-color: gray;")
        self.buttonSelectData.setStyleSheet("background-color: gray;")
        self.buttonSelectAxis.setStyleSheet("background-color: gray;")

        self.axes = pg.PlotWidget()

        self.axisConfigWindow = SelectAxis(self)
        self.dataConfigWindow = SelectData(self)

    def _makeLayout(self):

        hbox = QHBoxLayout()
        hbox.addWidget(self.buttonOpenFile)
        hbox.addWidget(self.buttonFollowFile)
        hbox.addWidget(self.buttonFollowFolder)
        hbox.addStretch(1)
        hbox.addWidget(self.buttonSelectData)
        hbox.addWidget(self.buttonSelectAxis)

        vbox = QVBoxLayout(self.cw)
        vbox.addWidget(self.axes)
        vbox.addLayout(hbox)

    def _makeConnect(self):

        self.buttonOpenFile.clicked.connect(self.onButtonOpenFile)
        self.buttonFollowFile.clicked.connect(self.onButtonFollowFile)
        self.buttonFollowFolder.clicked.connect(self.onButtonFollowFolder)
        self.buttonSelectData.clicked.connect(self.onButtonSelectData)
        self.buttonSelectAxis.clicked.connect(self.onButtonSelectAxis)

    def onButtonOpenFile(self):

        filePath = QFileDialog.getOpenFileName(self, 'Open File',default_path)[0]

        if filePath:
            self.newDataHandle(filePath)

    def onButtonFollowFile(self):

        filePath = QFileDialog.getOpenFileName(self, 'Open File',default_path)[0]

        if filePath:
            self.newDataHandle(filePath,follow = True)

    def onButtonFollowFolder(self):

        dataPath = QFileDialog.getExistingDirectory(self, 'Select a directory',default_path)

        if dataPath:
            newFolderFollower = DataPathFollower(dataPath)
            newFolderFollower.newFileSignal.connect(lambda: self.detectNewFile(newFolderFollower,follow = True))
            newFolderFollower.start()
            self.folderFollowerList.append(newFolderFollower)

    def onButtonSelectData(self):

        self.dataConfigWindow.show()
        self.dataConfigWindow.raise_()
        self.dataConfigWindow.activateWindow()

    def onButtonSelectAxis(self):

        self.axisConfigWindow.show()
        self.axisConfigWindow.raise_()
        self.axisConfigWindow.activateWindow()

    def detectNewFile(self,folderFollower,follow = False):

        self.newDataHandle(folderFollower.getLastNewFilePath(),follow)
                
    def newDataHandle(self,filePath,follow = False):

        reader = Reader()
        dataReader = HotReader(reader,filePath)

        newDataHandle = DataHandle(self,dataReader)
        if self.addDataHandle(newDataHandle):
            if follow:
                newDataHandle.follow()
            self.dataConfigWindow.addDataHandle(newDataHandle)

    def addDataHandle(self,newDataHandle):

        if len(self.dataHandleList) == 0:
            self.AxisFieldNameList = newDataHandle.column_names
            self.AxisFieldUnitList = newDataHandle.column_units

            for unit in self.AxisFieldUnitList:
                print(unit)

            self.XAxisFieldName = self.AxisFieldNameList[0]
            self.YAxisFieldName = self.AxisFieldNameList[1]
            self.updateXAxisChoice()
            self.updateYAxisChoice()
            self.changeXAxisChoice()
            self.changeYAxisChoice()
            self.updateXAxesLabel()
            self.updateYAxesLabel()

            addIt = True
        else:
            duplicate = False
            for dataHandle in self.dataHandleList:
                if dataHandle.dataReader.file_path == newDataHandle.dataReader.file_path:
                    duplicate = True
                    break
            
            if duplicate:
                addIt = False
                print('File already opened')
            # If the datafile contains the same field name
            elif set(self.AxisFieldNameList) == set(newDataHandle.column_names):
                addIt = True
            else:
                addIt = False

        if addIt:
            self.dataHandleList.append(newDataHandle)
            self.newPlot(newDataHandle)
            
            self.numberOfData += 1

        return addIt

    def removeDataHandle(self,dataHandle):

        self.axes.removeItem(dataHandle.dataPlot)
        self.dataConfigWindow.removeDataHandle(dataHandle)
        self.dataHandleList.remove(dataHandle)
        del(dataHandle)

    def newPlot(self,dataHandle):

        dataHandle.pen = pg.mkPen(self.numberOfData,width = 2)
        X,Y = dataHandle.getXY(self.XAxisFieldName,self.YAxisFieldName)
        dataPlot = self.axes.plot(X, Y, pen = dataHandle.pen)
        # self.axes.removeItem(dataPlot) #Need to remove it so it can be added when the visible checkbox is automatically checked at creation
        dataHandle.setDataPlot(dataPlot)

    def updateAllPlot(self):

        for dataHandle in self.dataHandleList:
            self.updatePlot(dataHandle)

    def updatePlot(self,dataHandle):

        X,Y = dataHandle.getXY(self.XAxisFieldName,self.YAxisFieldName)

        dataHandle.dataPlot.setData(X/self.Xscale,Y/self.Yscale)

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

        Xdatalim = [np.array(minXList).min(),np.array(maxXList).max()]
        Ydatalim = [np.array(minYList).min(),np.array(maxYList).max()]

        return Xdatalim, Ydatalim

    def updateXAxesLabel(self):

        indexX = self.AxisFieldNameList.index(self.XAxisFieldName)
        XAxisUnit = self.AxisFieldUnitList[indexX]
        
        xLabel = '{0:s} ({1:s})'.format(self.XAxisFieldName,XAxisUnit.getScaledLabel(self.Xscale))
        self.axes.setLabel('bottom', text = xLabel)
        
    def updateYAxesLabel(self):

        indexY = self.AxisFieldNameList.index(self.YAxisFieldName)
        YAxisUnit = self.AxisFieldUnitList[indexY]

        yLabel = '{0:s} ({1:s})'.format(self.YAxisFieldName,YAxisUnit.getScaledLabel(self.Yscale))
        self.axes.setLabel('left', text = yLabel)

    def updateXAxisChoice(self):

        indexX = self.AxisFieldNameList.index(self.XAxisFieldName)

        self.axisConfigWindow.XaxisComboBox.clear()
        self.axisConfigWindow.XaxisComboBox.addItems(self.AxisFieldNameList)
        self.axisConfigWindow.XaxisComboBox.setCurrentIndex(indexX)

    def updateYAxisChoice(self):

        indexY = self.AxisFieldNameList.index(self.YAxisFieldName)

        self.axisConfigWindow.YaxisComboBox.clear()
        self.axisConfigWindow.YaxisComboBox.addItems(self.AxisFieldNameList)
        self.axisConfigWindow.YaxisComboBox.setCurrentIndex(indexY)

    def changeXAxisChoice(self):

        indexX = self.axisConfigWindow.XaxisComboBox.currentIndex()
        
        self.XAxisFieldName = self.AxisFieldNameList[indexX]
        XAxisUnit = self.AxisFieldUnitList[indexX]
        
        self.axisConfigWindow.XunitComboBox.clear()
        self.axisConfigWindow.XunitComboBox.addItems(XAxisUnit.getAllScaleLabelList())

        self.Xscale = 1
        
        XUnitIndex = self.axisConfigWindow.XunitComboBox.findText(XAxisUnit.getScaledLabel(self.Xscale))
        if XUnitIndex > -1:
            self.axisConfigWindow.XunitComboBox.setCurrentIndex(XUnitIndex)

        self.updateXAxesLabel()
        self.updateAllPlot()

    def changeYAxisChoice(self):

        indexY = self.axisConfigWindow.YaxisComboBox.currentIndex()
        
        self.YAxisFieldName = self.AxisFieldNameList[indexY]
        YAxisUnit = self.AxisFieldUnitList[indexY]

        self.axisConfigWindow.YunitComboBox.clear()
        self.axisConfigWindow.YunitComboBox.addItems(YAxisUnit.getAllScaleLabelList())

        self.Yscale = 1

        YUnitIndex = self.axisConfigWindow.YunitComboBox.findText(YAxisUnit.getScaledLabel(self.Yscale))
        if YUnitIndex > -1:
            self.axisConfigWindow.YunitComboBox.setCurrentIndex(YUnitIndex)

        self.updateYAxesLabel()
        self.updateAllPlot()

    def updateXScale(self):

        indexX = self.axisConfigWindow.XaxisComboBox.currentIndex()
        
        XAxisUnit = self.AxisFieldUnitList[indexX]
        indexUnitX = self.axisConfigWindow.XunitComboBox.currentIndex()
        if indexUnitX > -1:
            currentXUnitLabel = XAxisUnit.getAllScaleLabelList()[indexUnitX]
            self.Xscale = XAxisUnit.relativeScale(currentXUnitLabel)
            
        self.updateXAxesLabel()
        self.updateAllPlot()
            
    def updateYScale(self):

        indexY = self.axisConfigWindow.YaxisComboBox.currentIndex()

        YAxisUnit = self.AxisFieldUnitList[indexY]
        indexUnitY = self.axisConfigWindow.YunitComboBox.currentIndex()
        if indexUnitY > -1:
            currentYUnitLabel = YAxisUnit.getAllScaleLabelList()[indexUnitY]
            self.Yscale = YAxisUnit.relativeScale(currentYUnitLabel)
            
        self.updateYAxesLabel()
        self.updateAllPlot()

            

class SelectAxis(QWidget):
    def __init__(self,HDV):
        QWidget.__init__(self)
        
        self.HDV = HDV
        self._initUI()

        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)

    def _initUI(self):

        self.setGeometry(350, 350, 300, 150)
        self.setWindowTitle('Select Axis')
        self.setStyleSheet("background-color: gray;")

        self._makeWidgets()
        self._makeLayout()
        self._makeConnect()

    def closeEvent(self,event):

        print('closing select axis')

    def _makeWidgets(self):

        self.XaxisLabel = QLabel('X axis')
        self.YaxisLabel = QLabel('Y axis')

        self.XaxisComboBox = QComboBox()
        self.YaxisComboBox = QComboBox()

        self.XunitComboBox = QComboBox()
        self.YunitComboBox = QComboBox()

    def _makeLayout(self):

        grid = QGridLayout()
        grid.addWidget(self.XaxisLabel,1,1)
        grid.addWidget(self.YaxisLabel,2,1)
        grid.addWidget(self.XaxisComboBox,1,2)
        grid.addWidget(self.YaxisComboBox,2,2)
        grid.addWidget(self.XunitComboBox,1,3)
        grid.addWidget(self.YunitComboBox,2,3)

        vbox = QVBoxLayout(self)
        vbox.addLayout(grid)
        vbox.addStretch(1)

    def _makeConnect(self):
        
        self.XaxisComboBox.currentIndexChanged.connect(self.HDV.changeXAxisChoice)
        self.YaxisComboBox.currentIndexChanged.connect(self.HDV.changeYAxisChoice)

        self.XunitComboBox.currentIndexChanged.connect(self.HDV.updateXScale)
        self.YunitComboBox.currentIndexChanged.connect(self.HDV.updateYScale)

class SelectData(QWidget):
    def __init__(self,HDV):
        QWidget.__init__(self)
        
        self.HDV = HDV
        self.dataListItemList = list()

        self._initUI()

        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)

    def _initUI(self):

        self.setGeometry(350, 350, 400, 300)
        self.setWindowTitle('Select Data')
        # self.setStyleSheet("background-color: gray;")

        self._makeWidgets()
        self._makeLayout()
        self._makeConnect()

    def closeEvent(self,event):

        print('closing select data')

    def _makeWidgets(self):

        pass

    def _makeLayout(self):

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addStretch()

    def _makeConnect(self):
        
        pass
        # self.dataTree.itemChanged.connect(self.onChangeHandler)

    def addFolder(self,folder):

        pass

    def addDataHandle(self,dataHandle):

        self.dataListItemList.append(DataListItem(dataHandle,parent=self))
        dataHandle.setDataItem(self.dataListItemList[-1])
        self.layout.insertWidget(self.layout.count()-1,self.dataListItemList[-1])

    def removeDataHandle(self,dataHandle):

        self.layout.removeWidget(dataHandle.dataItem)
        self.dataListItemList.remove(dataHandle.dataItem)
        dataHandle.dataItem.deleteLater()

class DataListItem(QWidget):

    def __init__(self,dataHandle, parent = None):

        super(DataListItem, self).__init__(parent)

        self.dataHandle = dataHandle

        self._makeWidgets()
        self._makeLayout()
        self._makeConnect()

    def _makeWidgets(self):
        
        self.descriptionEdit = QLineEdit(self.dataHandle.description,parent = self)

        self.visibleCheckBox = QCheckBox('Visible',parent = self)
        if self.dataHandle.visible:
            self.visibleCheckBox.setCheckState(2)

        self.followCheckBox = QCheckBox('Follow',parent = self)
        if self.dataHandle.following:
            self.followCheckBox.setCheckState(2)

        self.buttonColorPick = QPushButton("",parent = self)
        self.buttonColorPick.setMaximumWidth(32)
        self.setButtonColor(self.dataHandle.pen.color())

        self.buttonRemove = QPushButton("Remove",parent = self)

    def _makeLayout(self):

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        self.layout.addWidget(self.descriptionEdit)
        self.layout.addWidget(self.visibleCheckBox)
        self.layout.addWidget(self.followCheckBox)
        self.layout.addWidget(self.buttonColorPick)
        self.layout.addWidget(self.buttonRemove)
        
    def _makeConnect(self):

        self.visibleCheckBox.stateChanged.connect(self.onChangeVisible)
        self.followCheckBox.stateChanged.connect(self.onChangeFollow)
        self.descriptionEdit.editingFinished.connect(self.onChangeDescription)
        self.buttonColorPick.clicked.connect(self.onColorPick)
        self.buttonRemove.clicked.connect(self.onRemoveHandle)

    def setButtonColor(self,color):

        self.buttonColorPick.setStyleSheet("background-color: {0:s};".format(color.name()))

    def onChangeVisible(self):

        if self.visibleCheckBox.isChecked():
            self.dataHandle.show()
        else:
            self.dataHandle.hide()

    def onChangeFollow(self):

        if self.followCheckBox.isChecked():
            self.dataHandle.follow()
        else:
            self.dataHandle.pauseFollow()

    def onChangeDescription(self):

        self.dataHandle.description = self.descriptionEdit.text()

    def onColorPick(self):

        dlg = QColorDialog(self)
        # if self._color:
            # dlg.setCurrentColor(QColor(self._color))

        if dlg.exec_():
            newColor = dlg.currentColor()
            self.setButtonColor(newColor)
            self.dataHandle.setColor(newColor)


            # self.setColor(dlg.currentColor().name())

    def onRemoveHandle(self):

        self.dataHandle.remove()



def main():
    app = QApplication(sys.argv)
    HDV = HotDataViewer(app)
    HDV.show()
    sys.exit(app.exec_())






if __name__ == '__main__':
    main()

