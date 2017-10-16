import threading
import os
import sys
import wx
import time
import numpy as np

import matplotlib as mpl
mpl.use('WXAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigureCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar

sys.path.append("/Users/oneminimax/Documents/Projets Programmation/Slave")
sys.path.append("/Users/oneminimax/Documents/Projets Programmation/DataFileIO")

import DataFileIO as DFIO

class HDV(wx.App):
    
    def OnInit(self):
        self.mainFrame = HDVFrame()

        self.mainFrame.Show()


        return True


class HDVFrame(wx.Frame):
    colorList = [
            'red',
            'blue',
            'green',
            'orange',
            'pink',
            'plum']

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY,"Hot Data Viewer",size=(700,600))

        self._makeWidget()
        self._makeSizer()
        self._makeBinding()

        self.autoAxes = [True,True]
        self.xplotlim = [0,1]
        self.yplotlim = [0,1]

        self.dataFileList = list()
        self.dataPlotList = list()
        self.dataFollowerList = list()

        dataFile = self.openDataFile('/Users/oneminimax/Documents/Projets Programmation/DataFileIO/workfile.txt')
        self.dataFileList.append(dataFile)
        self.currentDataFileIndex = 0

        self.updateAxisChoice()

        dataPlot = self.newPlot(dataFile)
        dataFollower = DataFileFollower(dataFile,dataPlot,self)
        dataFollower.start()

        self.dataPlotList.append(dataPlot)
        self.dataFollowerList.append(dataFollower)

    def _makeWidget(self):

        self.figure = Figure(facecolor=(0.9,0.9,0.9,1))
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.axes = self.figure.add_axes((0.1,0.1,0.8,0.8))

        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        self.toolbar.update()

        self.controlPanel = wx.StaticBox(self, -1, "Axes control")
        
        self.FieldLabel = wx.StaticText(self.controlPanel, -1, "Field",size = (40,20))
        
        self.AutoLimLabel = wx.StaticText(self.controlPanel, -1, "Auto",size = (40,20),style = wx.TE_CENTRE)

        self.XAxisLabel = wx.StaticText(self.controlPanel, -1, "X : ",size = (30,20))
        self.XAxisChoice = wx.Choice(self.controlPanel, -1,size = (100,20))
        self.XAutoLimCheckBox = wx.CheckBox(self.controlPanel, -1,size = (20,20))
        self.XAutoLimCheckBox.SetValue(1)

        self.YAxisLabel = wx.StaticText(self.controlPanel, -1, "Y :",size = (30,20))
        self.YAxisChoice = wx.Choice(self.controlPanel, -1,size = (100,20))
        self.YAutoLimCheckBox = wx.CheckBox(self.controlPanel, -1,size = (20,20))
        self.YAutoLimCheckBox.SetValue(1)
        
    def _makeSizer(self):

        controlSizer = wx.StaticBoxSizer(self.controlPanel,wx.HORIZONTAL)

        axisLabelSizer = wx.BoxSizer(wx.VERTICAL)
        axisLabelSizer.Add((20,20),0,wx.ALL,1)
        axisLabelSizer.Add(self.XAxisLabel,0,wx.ALL,1)
        axisLabelSizer.Add(self.YAxisLabel,0,wx.ALL,1)

        axisChoiceSizer = wx.BoxSizer(wx.VERTICAL)
        axisChoiceSizer.Add(self.FieldLabel,0,wx.ALL,1)
        axisChoiceSizer.Add(self.XAxisChoice,0,wx.ALL,1)
        axisChoiceSizer.Add(self.YAxisChoice,0,wx.ALL,1)

        axisAutoLimSizer = wx.BoxSizer(wx.VERTICAL)
        axisAutoLimSizer.Add(self.AutoLimLabel,0,wx.CENTER | wx.ALL,1)
        axisAutoLimSizer.Add(self.XAutoLimCheckBox,0,wx.CENTER | wx.ALL,1)
        axisAutoLimSizer.Add(self.YAutoLimCheckBox,0,wx.CENTER | wx.ALL,1)

        controlSizer.Add(axisLabelSizer,0)
        controlSizer.Add(axisChoiceSizer,0)
        controlSizer.Add(axisAutoLimSizer,0)

        topSizer = wx.BoxSizer(wx.HORIZONTAL)

        middleSizer = wx.BoxSizer(wx.HORIZONTAL)
        middleSizer = wx.BoxSizer(wx.HORIZONTAL)
        middleSizer.Add(self.canvas, 1, wx.EXPAND|wx.ALL, 0)

        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomSizer.Add(controlSizer, 0, wx.EXPAND|wx.ALL, 0)
        bottomSizer.Add(self.toolbar, 0, wx.RIGHT | wx.EXPAND)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(topSizer, 0, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(middleSizer, 1, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(bottomSizer, 0, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(mainSizer)

    def _makeBinding(self):

        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.XAxisChoice.Bind(wx.EVT_CHOICE, self.onSelectAxis)
        self.YAxisChoice.Bind(wx.EVT_CHOICE, self.onSelectAxis)

        self.XAutoLimCheckBox.Bind(wx.EVT_CHECKBOX, self.onAutoLimCheckBox)
        self.YAutoLimCheckBox.Bind(wx.EVT_CHECKBOX, self.onAutoLimCheckBox)

    def openDataFile(self,dataFileName):

        dataFile = DFIO.DataFileReader(dataFileName)

        return dataFile

    def getXY(self,dataFile):

        indexX = self.XAxisChoice.GetSelection()
        indexY = self.YAxisChoice.GetSelection()
        X = dataFile.getDataByIndex(indexX)
        Y = dataFile.getDataByIndex(indexY)
        
        return X,Y

    def getXYDataLimit(self):

        indexX = self.XAxisChoice.GetSelection()
        indexY = self.YAxisChoice.GetSelection()

        minXList = list()
        maxXList = list()
        minYList = list()
        maxYList = list()

        for dataFile in self.dataFileList:
            X = dataFile.getDataByIndex(indexX)
            Y = dataFile.getDataByIndex(indexY)
            minXList.append(X.min())
            maxXList.append(X.max())
            minYList.append(Y.min())
            maxYList.append(Y.max())

        xplotlim = [np.array(minXList).min(),np.array(maxXList).max()]
        yplotlim = [np.array(minYList).min(),np.array(maxYList).max()]

        return xplotlim, yplotlim

    def newPlot(self,dataFile):

        X,Y = self.getXY(dataFile)

        dataPlot = self.axes.plot(X, Y, color = self.colorList[0], linestyle = "solid", marker = "o")[0]

        self.updatePlotLim()
        self.canvas.draw()

        return dataPlot

    def updatePlot(self,plot,dataFile):

        X,Y = self.getXY(dataFile)

        plot.set_xdata(X)
        plot.set_ydata(Y)

        self.updatePlotLim()
        self.canvas.draw()

    def updatePlotLim(self):

        xplotlim, yplotlim = self.getXYDataLimit()

        if self.XAutoLimCheckBox.IsChecked():
            self.xplotlim = xplotlim
            xmargin = 0.02 * (self.xplotlim[1] - self.xplotlim[0])
            self.axes.set_xlim((self.xplotlim[0] - xmargin,self.xplotlim[1] + xmargin))
        else:
            pass

        if self.YAutoLimCheckBox.IsChecked():
            self.yplotlim = yplotlim
            ymargin = 0.02 * (self.yplotlim[1] - self.yplotlim[0])
            self.axes.set_ylim((self.yplotlim[0] - ymargin,self.yplotlim[1] + ymargin))
        else:
            pass

    def updateAxisChoice(self):

        dataFile =  self.dataFileList[self.currentDataFileIndex]
        fieldNameList = dataFile.dataFieldNameList

        if len(fieldNameList) >= 2:

            self.XAxisChoice.SetItems(fieldNameList)
            self.YAxisChoice.SetItems(fieldNameList)

            self.XAxisChoice.SetSelection(0)
            self.YAxisChoice.SetSelection(1)

    def updateAxesLabel(self):

        pass

    def onClose(self,event):
        self.Destroy()
        for dataFollower in self.dataFollowerList:
            dataFollower.stop()

        print("Hot Data Viewer Closed!")

    def onAutoLimCheckBox(self,event):

        pass

    def onSelectAxis(self,event):
        
        self.updatePlot(self.dataPlotList[self.currentDataFileIndex],self.dataFileList[self.currentDataFileIndex])
        self.updatePlotLim()




class DataFileFollower(threading.Thread):
    lapse = 0.1
    def __init__(self,dataFile,dataPlot,hdvframe):
        threading.Thread.__init__(self)

        self.keepRunning = True
        self.onPause = False

        self.dataFile = dataFile
        self.dataPlot = dataPlot
        self.hdvframe = hdvframe

    def run(self):

        nbNewLine = 0
        while self.keepRunning:
            if self.onPause:
                time.sleep(self.lapse)
                continue
            newLine = self.dataFile._readADataLine()
            if newLine:
                nbNewLine += 1
            else:
                if nbNewLine > 0:
                    wx.CallAfter(self.hdvframe.updatePlot,self.dataPlot,self.dataFile)
                    nbNewLine = 0
                time.sleep(self.lapse)
                continue



    def stop(self):

        self.keepRunning = False

    def pause(self):

        self.onPause = True

    def unpause(self):

        self.onPause = False





def main():

    print("Starting Hot Data Viewer")
    app = HDV()
    app.MainLoop()
    


if __name__ == '__main__':
    main()